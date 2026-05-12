"""Fetch MTF chart images from the official Samyang product pages.

Usage:
    py scripts/fetch-samyang-mtf.py                     # fetch all to docs/mtf-charts/
    py scripts/fetch-samyang-mtf.py --seq 351           # fetch one by seq
    py scripts/fetch-samyang-mtf.py --dry-run           # list URLs without downloading
    py scripts/fetch-samyang-mtf.py --temp              # fetch to temp dir (for testing)

Each product page at lksamyang.com has a <li class="mtf-chart"> containing
an <img src="/upload/editor/{id}"> with the MTF chart image.

Images are saved to docs/mtf-charts/ as samyang-{slug}.png.
"""

import sys
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.lksamyang.com/en/product/product-view.php?seq="
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "mtf-charts"

# Map: seq -> output filename (without extension)
# Sourced from existing MTF chart .md files and the scoring log
LENSES = {
    "351": "samyang-12mm-f2",
    "311": "samyang-85mm-f1-4",
    "297": "samyang-14mm-f2-8",
    "345": "samyang-10mm-f2-8",
    "301": "samyang-35mm-f1-4",
    "303": "samyang-16mm-f2",
    "309": "samyang-21mm-f1-4",
    "305": "samyang-50mm-f1-4",
    "299": "samyang-135mm-f2-ed-umc",
    "349": "samyang-12mm-f2-8",
    "343": "samyang-100mm-f2-8-macro",
    "313": "samyang-300mm-f6-3-ed-umc-cs",
    "477": "samyang-35mm-f1-2",
    "475": "samyang-50mm-f1-2",
    "347": "samyang-20mm-f1-8",
}


def fetch_mtf_image(
    seq: str, slug: str, output_dir: Path, dry_run: bool = False
) -> bool:
    """Fetch a single MTF chart image. Returns True if saved."""
    url = f"{BASE_URL}{seq}"
    out_path = output_dir / f"{slug}.png"

    if out_path.exists() and not dry_run:
        print(f"  SKIP {slug} (already exists)")
        return False

    if dry_run:
        exists = "exists" if out_path.exists() else "missing"
        print(f"  {slug} -> seq={seq} ({exists})")
        return False

    print(f"  Fetching {slug} (seq={seq})...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        mtf_el = page.query_selector("li.mtf-chart img")
        if not mtf_el:
            print(f"  WARN: no MTF chart found on {url}")
            browser.close()
            return False

        img_src = mtf_el.get_attribute("src")
        if not img_src:
            print(f"  WARN: MTF img has no src on {url}")
            browser.close()
            return False

        if img_src.startswith("/"):
            img_url = f"https://www.lksamyang.com{img_src}"
        else:
            img_url = img_src

        browser.close()

    print(f"  Downloading {img_url}...")
    req = urllib.request.Request(
        img_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Referer": url,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(data)
    print(f"  SAVED {out_path.name} ({len(data)} bytes)")
    return True


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    use_temp = "--temp" in sys.argv
    seq_filter = None

    if "--seq" in sys.argv:
        idx = sys.argv.index("--seq")
        if idx + 1 < len(sys.argv):
            seq_filter = sys.argv[idx + 1]

    if use_temp:
        output_dir = Path(__file__).resolve().parent.parent / "temp"
        output_dir.mkdir(exist_ok=True)
        print(f"Output: {output_dir}\n")
    else:
        output_dir = OUTPUT_DIR

    targets = LENSES
    if seq_filter:
        if seq_filter not in LENSES:
            print(f"Unknown seq: {seq_filter}")
            print(f"Known: {', '.join(LENSES.keys())}")
            sys.exit(1)
        targets = {seq_filter: LENSES[seq_filter]}

    mode = "DRY RUN" if dry_run else "FETCH"
    print(f"[{mode}] {len(targets)} Samyang MTF charts\n")

    saved = 0
    for seq, slug in targets.items():
        if fetch_mtf_image(seq, slug, output_dir, dry_run):
            saved += 1

    print(f"\nDone. {saved} new images saved.")


if __name__ == "__main__":
    main()
