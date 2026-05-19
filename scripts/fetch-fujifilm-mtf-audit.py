"""Audit all Fujifilm lens specs pages for MTF chart images.

For each lens missing MTF charts, renders the specs page and lists all
content images with their dimensions. Identifies likely MTF charts by
size (282x212 or similar) and position after "MTF Chart" text.

Saves identified MTF charts automatically.

Usage:
    py scripts/fetch-fujifilm-mtf-audit.py
"""

import re
import sys
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
MTF_DIR = ROOT / "docs" / "mtf-charts"


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


def has_both_mtf(slug: str) -> bool:
    has_15 = bool(list(MTF_DIR.glob(f"{slug}-15lp.*")))
    has_45 = bool(list(MTF_DIR.glob(f"{slug}-45lp.*")))
    return has_15 and has_45


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
        print(f"      WARN: download failed: {e}")
        return False


def fetch_and_identify(page, specs_url: str) -> dict:
    """Render specs page, find MTF chart images by position relative to text markers."""
    result = {"construction": None, "mtf_15": None, "mtf_45": None}

    try:
        page.goto(specs_url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(4000)

        # Scroll fully
        page.evaluate("""async () => {
            const delay = ms => new Promise(r => setTimeout(r, ms));
            for (let y = 0; y < document.body.scrollHeight; y += window.innerHeight) {
                window.scrollTo(0, y); await delay(300);
            }
            window.scrollTo(0, 0); await delay(500);
        }""")
        page.wait_for_timeout(2000)

        # Get text markers Y positions
        markers = page.evaluate("""() => {
            const result = {};
            const walk = document.createTreeWalker(
                document.body, NodeFilter.SHOW_TEXT, null
            );
            while (walk.nextNode()) {
                const text = walk.currentNode.textContent.trim();
                const el = walk.currentNode.parentElement;
                if (!el) continue;
                const rect = el.getBoundingClientRect();
                if (text === 'Lens Configurations' && !result.lensConfig)
                    result.lensConfig = rect.top;
                if (text === 'MTF Chart' && !result.mtfChart)
                    result.mtfChart = rect.top;
                if (/^Spatial frequency 15/.test(text) && !result.freq15)
                    result.freq15 = rect.top;
                if (/^Spatial frequency 45/.test(text) && !result.freq45)
                    result.freq45 = rect.top;
            }
            return result;
        }""")

        # Get all content images with positions
        imgs = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('img'))
                .map(img => ({
                    src: img.src.split('?')[0],
                    top: img.getBoundingClientRect().top,
                    w: img.naturalWidth || img.width,
                    h: img.naturalHeight || img.height,
                }))
                .filter(i => i.src.includes('b-cdn')
                    && !i.src.includes('thum') && !i.src.includes('flag')
                    && !i.src.includes('logo') && !i.src.includes('fujifilmX')
                    && i.h > 50 && i.w > 50);
        }""")

        if not markers.get("mtfChart") and not markers.get("freq15"):
            return result

        lc_y = markers.get("lensConfig", 0)
        mtf_y = markers.get("mtfChart", 0)
        f15_y = markers.get("freq15", 0)
        f45_y = markers.get("freq45", 0)

        for img in imgs:
            top = img["top"]
            src = img["src"]

            # Construction: between Lens Configurations and MTF Chart
            if lc_y and mtf_y and lc_y < top < mtf_y:
                if not result["construction"]:
                    result["construction"] = src

            # MTF 15lp: near freq15 text (within 300px)
            if f15_y and abs(top - f15_y) < 300:
                if not result["mtf_15"]:
                    result["mtf_15"] = src

            # MTF 45lp: near freq45 text (within 300px)
            if f45_y and abs(top - f45_y) < 300:
                if not result["mtf_45"]:
                    result["mtf_45"] = src

        # Fallback: if we have mtfChart marker but no freq markers,
        # take the first 2 images after mtfChart
        if mtf_y and not result["mtf_15"] and not result["mtf_45"]:
            after_mtf = [i for i in imgs if i["top"] > mtf_y and i["w"] > 100]
            if len(after_mtf) >= 2:
                result["mtf_15"] = after_mtf[0]["src"]
                result["mtf_45"] = after_mtf[1]["src"]
            elif len(after_mtf) == 1:
                result["mtf_15"] = after_mtf[0]["src"]

    except Exception as e:
        print(f"    WARN: {e}")

    return result


def main() -> None:
    lenses = extract_fujifilm_lenses()
    missing = [
        {**l, "slug": model_to_slug(l["model"])}
        for l in lenses
        if not has_both_mtf(model_to_slug(l["model"]))
    ]

    # Skip XF 18mm f/2.0 R — already saved manually
    missing = [l for l in missing if l["model"] != "XF 18mm f/2.0 R"]

    print(f"{len(missing)} lenses missing MTF charts\n")

    MTF_DIR.mkdir(parents=True, exist_ok=True)
    stats = {"saved": 0, "not_found": 0}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
        )

        for i, lens in enumerate(missing):
            model = lens["model"]
            slug = lens["slug"]
            specs_url = lens["url"].rstrip("/") + "/specifications/"

            print(f"[{i + 1}/{len(missing)}] {model}")

            pg = ctx.new_page()
            result = fetch_and_identify(pg, specs_url)
            pg.close()

            found = False
            for key, suffix in [("mtf_15", "-15lp"), ("mtf_45", "-45lp")]:
                if result[key]:
                    ext = result[key].rsplit(".", 1)[-1]
                    dest = MTF_DIR / f"{slug}{suffix}.{ext}"
                    if not dest.exists():
                        if download_image(result[key], dest):
                            print(f"    {suffix[1:]}: {dest.name}")
                            stats["saved"] += 1
                            found = True
                    else:
                        found = True

            if not found:
                print(f"    No MTF charts found")
                stats["not_found"] += 1

        browser.close()

    print(f"\nDone: {stats['saved']} charts saved, {stats['not_found']} lenses with no charts")


if __name__ == "__main__":
    main()
