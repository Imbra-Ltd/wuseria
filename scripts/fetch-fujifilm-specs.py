"""Fetch optical specs, MTF charts, and construction diagrams from Fujifilm product pages.

Reads lens URLs from lenses.ts, fetches each /specifications/ page,
extracts optical data, and downloads images to docs/ directories.

Usage:
    py scripts/fetch-fujifilm-specs.py              # fetch all Fujifilm lenses
    py scripts/fetch-fujifilm-specs.py --dry-run    # print URLs without fetching
    py scripts/fetch-fujifilm-specs.py --limit 5    # fetch first N lenses only
"""

import hashlib
import re
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
MTF_DIR = ROOT / "docs" / "mtf-charts"
CONSTRUCTION_DIR = ROOT / "docs" / "optical-construction"
CACHE_DIR = ROOT / ".cache" / "fetch"
SPECS_OUT = ROOT / ".cache" / "fujifilm-specs"


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def read_cache(url: str) -> str | None:
    path = CACHE_DIR / (url_hash(url) + ".txt")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def write_cache(url: str, content: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / (url_hash(url) + ".txt")
    path.write_text(content, encoding="utf-8")


def read_html_cache(url: str) -> str | None:
    path = CACHE_DIR / (url_hash(url) + ".html")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def write_html_cache(url: str, content: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / (url_hash(url) + ".html")
    path.write_text(content, encoding="utf-8")


def extract_fujifilm_lenses() -> list[dict]:
    """Extract Fujifilm lens model + officialUrl from lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    pattern = re.compile(
        r'brand:\s*"Fujifilm"[\s\S]*?'
        r'model:\s*"([^"]+)"[\s\S]*?'
        r'officialUrl:\s*"([^"]+)"'
    )
    return [{"model": m.group(1), "url": m.group(2)} for m in pattern.finditer(content)]


def model_to_slug(model: str) -> str:
    """Convert model name to file slug: XF 14mm f/2.8 R -> fujifilm-xf-14mm-f2-8-r"""
    slug = model.lower()
    slug = slug.replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return f"fujifilm-{slug}"


def specs_url(official_url: str) -> str:
    """Derive specifications page URL from official product URL."""
    base = official_url.rstrip("/")
    return f"{base}/specifications/"


def download_image(url: str, dest: Path) -> bool:
    """Download an image if not already present."""
    if dest.exists():
        return True
    try:
        # Strip query params for cleaner download, keep original for CDN
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            dest.write_bytes(resp.read())
        return True
    except Exception as e:
        print(f"  WARN: failed to download {url}: {e}")
        return False


def extract_specs(text: str) -> dict:
    """Extract optical specs from page text content."""
    specs = {}

    # Lens construction/configuration: "10 elements in 7 groups" or "13 elements 11 groups"
    m = re.search(r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?", text, re.IGNORECASE)
    if m:
        specs["elements"] = int(m.group(1))
        specs["groups"] = int(m.group(2))

    # Special elements: look in the line with element/group counts and the 2 lines
    # after for parenthetical like "(includes 2 aspherical and 3 extra low dispersion elements)"
    construction_block = ""
    m2 = re.search(
        r"\d+\s*elements?\s+(?:in\s+)?\d+\s*groups?[^\n]*(?:\n[^\n]*){0,2}",
        text, re.IGNORECASE,
    )
    if m2:
        construction_block = m2.group(0)

    # Normalize text numbers to digits before matching
    TEXT_NUMS = {
        "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    }
    normalized_block = construction_block
    for word, digit in TEXT_NUMS.items():
        normalized_block = re.sub(rf"\b{word}\b", digit, normalized_block, flags=re.IGNORECASE)

    special = []
    for pat, label in [
        (r"(\d+)\s*aspherical", "aspherical"),
        (r"(\d+)\s*(?:extra[- ]low[- ]dispersion|ED)\b", "ED"),
        (r"(\d+)\s*(?:Super ED|super ED)", "Super ED"),
        (r"(\d+)\s*fluorite", "fluorite"),
    ]:
        m3 = re.search(pat, normalized_block, re.IGNORECASE)
        if m3:
            special.append(f"{m3.group(1)} {label}")
    specs["special"] = special

    return specs


def extract_image_urls(html: str, lens_slug_part: str) -> dict:
    """Extract MTF chart and construction diagram URLs from HTML."""
    urls = {}
    # Construction diagram: *_cross.webp or *_cross.png
    m = re.search(r'src="([^"]*' + re.escape(lens_slug_part) + r'[^"]*_cross\.[^"]+)"', html, re.IGNORECASE)
    if m:
        urls["construction"] = m.group(1).split("?")[0]

    # MTF charts: *Specifications-images002/003 or *Specifications-images02/03
    for suffix_pat, key in [(r"0*2", "mtf_15"), (r"0*3", "mtf_45")]:
        m2 = re.search(
            r'src="([^"]*' + re.escape(lens_slug_part) + r'[^"]*Specifications-images' + suffix_pat + r'\.[^"]+)"',
            html, re.IGNORECASE,
        )
        if m2:
            urls[key] = m2.group(1).split("?")[0]

    return urls


def fetch_page(browser, url: str, wait_ms: int = 3000) -> tuple[str, str]:
    """Fetch a page, return (text_content, html_content). Uses cache."""
    cached_text = read_cache(url)
    cached_html = read_html_cache(url)
    if cached_text and cached_html:
        return cached_text, cached_html

    page = browser.new_page()
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(wait_ms)
        text = page.inner_text("body")
        html = page.content()
        write_cache(url, text)
        write_html_cache(url, html)
        return text, html
    finally:
        page.close()


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    limit = None
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])

    lenses = extract_fujifilm_lenses()
    if limit:
        lenses = lenses[:limit]

    print(f"Found {len(lenses)} Fujifilm lenses")

    if dry_run:
        for lens in lenses:
            print(f"  {lens['model']} -> {specs_url(lens['url'])}")
        return

    MTF_DIR.mkdir(parents=True, exist_ok=True)
    CONSTRUCTION_DIR.mkdir(parents=True, exist_ok=True)
    SPECS_OUT.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser_instance = p.chromium.launch(headless=True)
        context = browser_instance.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
        )

        results = []

        for i, lens in enumerate(lenses):
            model = lens["model"]
            slug = model_to_slug(model)
            url = specs_url(lens["url"])

            # Derive the CDN slug part for image URL matching
            # e.g. "xf14mmf28-r" from the URL path
            url_slug = lens["url"].rstrip("/").split("/")[-1]

            print(f"[{i + 1}/{len(lenses)}] {model} ({url_slug})")

            text, html = fetch_page(context, url)

            # Extract specs
            specs = extract_specs(text)
            print(f"  Construction: {specs.get('elements', '?')} elements, "
                  f"{specs.get('groups', '?')} groups, "
                  f"special: {specs.get('special', [])}")

            # Extract and download images
            img_urls = extract_image_urls(html, url_slug)

            if "construction" in img_urls:
                ext = img_urls["construction"].rsplit(".", 1)[-1]
                dest = CONSTRUCTION_DIR / f"{slug}.{ext}"
                if download_image(img_urls["construction"], dest):
                    print(f"  Construction diagram: {dest.name}")

            for key, label in [("mtf_15", "MTF 15lp"), ("mtf_45", "MTF 45lp")]:
                if key in img_urls:
                    ext = img_urls[key].rsplit(".", 1)[-1]
                    suffix = "-15lp" if "15" in key else "-45lp"
                    dest = MTF_DIR / f"{slug}{suffix}.{ext}"
                    if download_image(img_urls[key], dest):
                        print(f"  {label}: {dest.name}")

            # Save extracted specs to cache for later use
            result = {"model": model, "slug": slug, "url": url, **specs}
            results.append(result)

            # Brief pause between requests to be polite
            if not read_cache(url):
                time.sleep(1)

        browser_instance.close()

    # Write summary
    summary_path = SPECS_OUT / "fujifilm-specs.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        for r in results:
            special_str = ", ".join(r.get("special", [])) or "none"
            f.write(
                f"{r['model']}|{r.get('elements', '?')}|"
                f"{r.get('groups', '?')}|{special_str}\n"
            )
    print(f"\nSummary written to {summary_path}")
    print(f"Processed {len(results)} lenses")


if __name__ == "__main__":
    main()
