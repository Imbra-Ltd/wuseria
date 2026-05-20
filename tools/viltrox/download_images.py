"""Download MTF chart and construction diagram images from Viltrox product pages.

Viltrox embeds gallery images in their Shopify theme (not in the product
JSON API). This script scrapes the full HTML for ALL CDN image URLs,
downloads them to a cache directory, and lets the user identify which
ones contain MTF/construction data.

After identification, images must be converted to PNG before saving to
docs/optical-specs/ (project convention: all optical spec images are PNG).

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


def extract_theme_images(html: str) -> list[str]:
    """Extract ALL theme gallery images from page HTML.

    Shopify stores embed images in theme templates that don't appear in
    the product JSON API. Image naming is inconsistent across product
    generations:
    - Numbered UUIDs: cdn/shop/files/16_{uuid}.jpg
    - Descriptive: cdn/shop/files/27mm-f1.2-mb-25.jpg
    - Prefixed: cdn/shop/files/AF_9mm_F2.8_Air_XF-img5.jpg

    Extracts ALL cdn/shop/files/ images, filters out known non-product
    images (icons, badges, banners).
    """
    # Match all CDN image files — broad pattern
    pattern = re.compile(
        r'(?:https?://)?(?:viltrox\.com|cdn\.shopify\.com/s/files/1/0104/0380/7298)'
        r'/(?:cdn/shop/)?files/([^"\'?\s]+\.(?:jpg|png))'
    )
    raw_matches = set(pattern.findall(html))

    # Filter out non-product images (site chrome, badges, banners)
    skip_keywords = [
        "Free_Shipping", "Quality_guarantee", "Satisfied_or_refunded",
        "Secure_payments", "icon", "logo", "banner", "badge",
    ]

    # Deduplicate size variants — keep only the original (largest).
    # Shopify generates _768x and _1024x variants from the original.
    # E.g. img5.jpg, img5_768x.jpg, img5_1024x.jpg -> keep img5.jpg
    size_variant = re.compile(r'_\d+x\.(jpg|png)$')
    filtered = []
    for filename in sorted(raw_matches):
        if any(kw.lower() in filename.lower() for kw in skip_keywords):
            continue
        if size_variant.search(filename):
            continue
        filtered.append(f"https://viltrox.com/cdn/shop/files/{filename}")

    return filtered


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
            images = extract_theme_images(html)
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
