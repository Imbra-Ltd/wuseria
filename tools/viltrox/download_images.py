"""Download MTF chart and construction diagram images from Viltrox product pages.

Viltrox embeds numbered gallery images in their Shopify theme (not in the
product JSON API). This script scrapes the full HTML for CDN image URLs
with the pattern cdn/shop/files/{N}_{hash}.jpg, downloads them to a temp
directory, and lets the user identify which ones contain MTF/construction data.

Usage:
    py tools/viltrox/download_images.py                    # download all
    py tools/viltrox/download_images.py --filter 13mm      # filter by model
    py tools/viltrox/download_images.py --dry-run           # list URLs only
"""

import argparse
import re
import time
import urllib.request
from pathlib import Path

from common import (
    OPTICAL_SPECS_DIR,
    USER_AGENT,
    extract_viltrox_lenses,
    model_to_slug,
)

DOWNLOAD_DIR = Path(__file__).resolve().parent.parent.parent / ".cache" / "viltrox-images"


def fetch_page_html(url: str, timeout: int = 30) -> str:
    """Fetch raw HTML from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_numbered_images(html: str) -> list[str]:
    """Extract numbered theme gallery images from page HTML.

    Pattern: cdn/shop/files/{N}_{uuid-hash}.jpg
    These are Shopify theme images embedded in the page template,
    NOT product API images.
    """
    pattern = re.compile(r'cdn/shop/files/(\d+_[a-f0-9-]+\.(?:jpg|png))')
    matches = sorted(set(pattern.findall(html)), key=lambda x: int(x.split("_")[0]))
    return [f"https://viltrox.com/cdn/shop/files/{m}" for m in matches]


def download_image(url: str, dest: Path, min_size: int = 5000) -> bool:
    """Download an image. Returns True on success."""
    if dest.exists() and dest.stat().st_size > min_size:
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if len(data) < min_size:
                return False
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"    WARN: download failed: {e}")
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Viltrox theme gallery images")
    parser.add_argument("--filter", type=str, help="Filter by model substring")
    parser.add_argument("--dry-run", action="store_true", help="List URLs only")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    lenses = extract_viltrox_lenses()
    print(f"Found {len(lenses)} Viltrox lenses")

    if args.filter:
        lenses = [l for l in lenses if args.filter.lower() in l["model"].lower()]
        print(f"  Filtered to {len(lenses)} matching '{args.filter}'")

    stats = {"pages": 0, "images": 0}

    for i, lens in enumerate(lenses):
        model = lens["model"]
        slug = model_to_slug(model)
        url = lens["url"]

        print(f"\n[{i + 1}/{len(lenses)}] {model}")
        print(f"  URL: {url}")

        try:
            html = fetch_page_html(url)
            images = extract_numbered_images(html)
            stats["pages"] += 1

            if not images:
                print(f"  No numbered theme images found")
                continue

            print(f"  Found {len(images)} theme images")

            if args.dry_run:
                for img_url in images:
                    print(f"    {img_url}")
                continue

            # Download to cache dir organized by slug
            lens_dir = DOWNLOAD_DIR / slug
            for img_url in images:
                filename = img_url.split("/")[-1].split("?")[0]
                dest = lens_dir / filename
                if download_image(img_url, dest):
                    print(f"    Downloaded: {filename} ({dest.stat().st_size // 1024}KB)")
                    stats["images"] += 1

            if i < len(lenses) - 1:
                time.sleep(1)

        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n{'=' * 40}")
    print(f"Done: {stats['pages']} pages scraped, {stats['images']} images downloaded")
    if not args.dry_run:
        print(f"Images saved to: {DOWNLOAD_DIR}")
        print(f"\nNext: visually inspect images to identify MTF charts and construction diagrams")


if __name__ == "__main__":
    main()
