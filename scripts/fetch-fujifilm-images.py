"""Download MTF charts and optical construction diagrams from Fujifilm specs pages.

Handles both old-style (named URLs like *_cross.webp, *Specifications-images002.webp)
and new-style (generic names like image-56.png) Fujifilm pages.

Uses Playwright to render the page fully, then identifies spec images by their
position relative to "Lens Configurations" and "MTF Chart" text sections.

Usage:
    py scripts/fetch-fujifilm-images.py              # fetch missing images
    py scripts/fetch-fujifilm-images.py --dry-run    # list what would be fetched
    py scripts/fetch-fujifilm-images.py --limit 5    # fetch first N missing lenses
    py scripts/fetch-fujifilm-images.py --all        # re-check all lenses, not just missing
"""

import re
import sys
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
MTF_DIR = ROOT / "docs" / "mtf-charts"
CONSTRUCTION_DIR = ROOT / "docs" / "optical-construction"


def extract_fujifilm_lenses() -> list[dict]:
    content = LENSES_TS.read_text(encoding="utf-8")
    pattern = re.compile(
        r'brand:\s*"Fujifilm"[\s\S]*?'
        r'model:\s*"([^"]+)"[\s\S]*?'
        r'officialUrl:\s*"([^"]+)"'
    )
    return [{"model": m.group(1), "url": m.group(2)} for m in pattern.finditer(content)]


def model_to_slug(model: str) -> str:
    slug = model.lower().replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return f"fujifilm-{slug}"


def has_mtf(slug: str) -> bool:
    return bool(list(MTF_DIR.glob(f"{slug}-*lp.*")))


def has_construction(slug: str) -> bool:
    return bool(list(CONSTRUCTION_DIR.glob(f"{slug}.*")))


def download_image(url: str, dest: Path) -> bool:
    if dest.exists():
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) < 500:
                return False
            dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"    WARN: download failed: {e}")
        return False


def fetch_spec_images(page, specs_url: str, url_slug: str) -> dict:
    """Render specs page and extract construction diagram + MTF chart URLs.

    Strategy:
    1. Try old-style named URLs (lens slug in filename).
    2. If not found, locate generic images between the "Lens Configurations"
       and "Specifications" (table) text sections. In that range, the images
       appear in order: construction, mtf-15, mtf-45, legend.
    """
    urls: dict[str, str] = {}

    try:
        page.goto(specs_url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)

        # Scroll to trigger lazy loading
        page.evaluate("""async () => {
            const delay = ms => new Promise(r => setTimeout(r, ms));
            for (let y = 0; y < document.body.scrollHeight; y += window.innerHeight) {
                window.scrollTo(0, y); await delay(300);
            }
            window.scrollTo(0, 0); await delay(500);
        }""")
        page.wait_for_timeout(2000)

        # Get all images with their index and source
        all_imgs = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('img'))
                .map((img, idx) => ({idx, src: img.src || ''}))
                .filter(i => i.src && !i.src.startsWith('data:'));
        }""")

        # Strategy 1: old-style named URLs
        for img in all_imgs:
            src = img["src"].split("?")[0]
            lower = src.lower()
            if url_slug.lower() not in lower:
                continue
            if "_cross." in lower or "-cross." in lower:
                urls["construction"] = src
            elif re.search(r"specifications-images?0*2\.", lower):
                urls["mtf_15"] = src
            elif re.search(r"specifications-images?0*3\.", lower):
                urls["mtf_45"] = src

        if urls:
            return urls

        # Strategy 2: find generic images by page position
        # Get the Y position of key text markers
        markers = page.evaluate("""() => {
            const body = document.body.innerText;
            const result = {};

            // Find elements containing marker text
            const walk = document.createTreeWalker(
                document.body, NodeFilter.SHOW_TEXT, null
            );
            while (walk.nextNode()) {
                const text = walk.currentNode.textContent.trim();
                const el = walk.currentNode.parentElement;
                if (!el) continue;
                const rect = el.getBoundingClientRect();

                if (text === 'Lens Configurations' && !result.lensConfig) {
                    result.lensConfig = rect.top;
                }
                if (text === 'MTF Chart' && !result.mtfChart) {
                    result.mtfChart = rect.top;
                }
                if (/^Spatial frequency 15/.test(text) && !result.freq15) {
                    result.freq15 = rect.top;
                }
                if (/^Spatial frequency 45/.test(text) && !result.freq45) {
                    result.freq45 = rect.top;
                }
            }
            return result;
        }""")

        if not markers.get("lensConfig"):
            return urls

        # Get image positions
        img_positions = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('img'))
                .map(img => ({
                    src: img.src.split('?')[0],
                    top: img.getBoundingClientRect().top,
                    height: img.naturalHeight || img.height,
                    width: img.naturalWidth || img.width,
                }))
                .filter(i => i.src.includes('b-cdn') && !i.src.includes('thum')
                    && !i.src.includes('flag') && !i.src.includes('logo')
                    && i.height > 50 && i.width > 50);
        }""")

        lens_config_y = markers.get("lensConfig", 0)
        mtf_chart_y = markers.get("mtfChart", 0)
        freq15_y = markers.get("freq15", 0)
        freq45_y = markers.get("freq45", 0)

        for img in img_positions:
            top = img["top"]
            src = img["src"]

            # Construction diagram: between "Lens Configurations" and "MTF Chart"
            if lens_config_y and mtf_chart_y and lens_config_y < top < mtf_chart_y:
                if "construction" not in urls:
                    urls["construction"] = src

            # MTF 15 lp/mm: near "Spatial frequency 15 lines/mm"
            if freq15_y and abs(top - freq15_y) < 300:
                if "mtf_15" not in urls:
                    urls["mtf_15"] = src

            # MTF 45 lp/mm: near "Spatial frequency 45 lines/mm"
            if freq45_y and abs(top - freq45_y) < 300:
                if "mtf_45" not in urls:
                    urls["mtf_45"] = src

    except Exception as e:
        print(f"    WARN: page error: {e}")

    return urls


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    check_all = "--all" in sys.argv
    limit = None
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])

    lenses = extract_fujifilm_lenses()

    # Filter to lenses missing images (unless --all)
    work = []
    for lens in lenses:
        slug = model_to_slug(lens["model"])
        needs_mtf = not has_mtf(slug)
        needs_constr = not has_construction(slug)
        if check_all or needs_mtf or needs_constr:
            work.append({
                **lens, "slug": slug,
                "needs_mtf": needs_mtf, "needs_constr": needs_constr,
            })

    print(f"{len(work)}/{len(lenses)} lenses to process")

    if limit:
        work = work[:limit]

    if dry_run:
        for lens in work:
            needs = []
            if lens["needs_mtf"]:
                needs.append("MTF")
            if lens["needs_constr"]:
                needs.append("construction")
            print(f"  {lens['model']}: needs {', '.join(needs)}")
        return

    MTF_DIR.mkdir(parents=True, exist_ok=True)
    CONSTRUCTION_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
        )

        stats = {"mtf": 0, "constr": 0, "failed": 0}

        for i, lens in enumerate(work):
            model = lens["model"]
            slug = lens["slug"]
            url_slug = lens["url"].rstrip("/").split("/")[-1]
            specs_url = lens["url"].rstrip("/") + "/specifications/"

            print(f"[{i + 1}/{len(work)}] {model}")

            pg = context.new_page()
            img_urls = fetch_spec_images(pg, specs_url, url_slug)
            pg.close()

            found_any = False

            if lens["needs_constr"] and "construction" in img_urls:
                ext = img_urls["construction"].rsplit(".", 1)[-1]
                dest = CONSTRUCTION_DIR / f"{slug}.{ext}"
                if download_image(img_urls["construction"], dest):
                    print(f"    Construction: {dest.name}")
                    stats["constr"] += 1
                    found_any = True

            if lens["needs_mtf"]:
                for key, label in [("mtf_15", "MTF 15lp"), ("mtf_45", "MTF 45lp")]:
                    if key in img_urls:
                        ext = img_urls[key].rsplit(".", 1)[-1]
                        suffix = "-15lp" if "15" in key else "-45lp"
                        dest = MTF_DIR / f"{slug}{suffix}.{ext}"
                        if download_image(img_urls[key], dest):
                            print(f"    {label}: {dest.name}")
                            stats["mtf"] += 1
                            found_any = True

            if not found_any:
                print(f"    No images found")
                stats["failed"] += 1

        browser.close()

    print(f"\nDone: {stats['constr']} construction, {stats['mtf']} MTF charts")
    print(f"{stats['failed']} lenses with no images on page")


if __name__ == "__main__":
    main()
