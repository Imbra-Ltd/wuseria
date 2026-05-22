"""Fetch optical specs and images for Venus Laowa lenses.

Venus Laowa (venuslens.net) is behind Cloudflare Turnstile. This tool uses
SeleniumBase UC mode to bypass the challenge, then extracts spec table data
and downloads construction diagram and MTF chart images.

Usage:
    py tools/venus/fetch_specs.py                    # fetch all specs + images
    py tools/venus/fetch_specs.py --dry-run           # list lenses without fetching
    py tools/venus/fetch_specs.py --filter 10mm       # filter by model substring
    py tools/venus/fetch_specs.py --specs-only        # only extract specs text
    py tools/venus/fetch_specs.py --images-only       # only download images
"""

import argparse
import time

from common import (
    OPTICAL_SPECS_DIR,
    download_image,
    extract_image_urls,
    extract_specs,
    extract_venus_lenses,
    fetch_page_seleniumbase,
    model_to_slug,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Venus Laowa optical specs")
    parser.add_argument("--dry-run", action="store_true", help="List lenses without fetching")
    parser.add_argument("--filter", type=str, help="Filter by model substring (case-insensitive)")
    parser.add_argument("--specs-only", action="store_true", help="Only extract specs text")
    parser.add_argument("--images-only", action="store_true", help="Only download images")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    lenses = extract_venus_lenses()
    print(f"Found {len(lenses)} Venus Laowa lenses with official URLs")

    if args.filter:
        lenses = [l for l in lenses if args.filter.lower() in l["model"].lower()]
        print(f"  Filtered to {len(lenses)} matching '{args.filter}'")

    if args.dry_run:
        for lens in lenses:
            slug = model_to_slug(lens["model"])
            print(f"  {lens['model']} -> {slug}")
            print(f"    URL: {lens['url']}")
        return

    stats = {"specs": 0, "images": 0, "skipped": 0, "failed": 0}

    for i, lens in enumerate(lenses):
        model = lens["model"]
        slug = model_to_slug(model)
        url = lens["url"]
        specs_dir = OPTICAL_SPECS_DIR / slug

        print(f"\n[{i + 1}/{len(lenses)}] {model}")
        print(f"  URL: {url}")

        try:
            html = fetch_page_seleniumbase(url)
        except Exception as e:
            print(f"  FAILED to fetch page: {e}")
            stats["failed"] += 1
            continue

        # Check if we actually got page content
        if "_cf_chl" in html or "security verification" in html.lower():
            print("  SKIP: blocked by Cloudflare")
            stats["skipped"] += 1
            continue

        # Extract and display specs
        if not args.images_only:
            specs = extract_specs(html)
            if specs.get("elements"):
                special_str = ", ".join(specs.get("special", [])) or "none"
                coating_str = ", ".join(specs.get("coating", [])) or "none"
                print(f"  Optical: {specs['elements']} elements in {specs['groups']} groups")
                print(f"  Special: {special_str}")
                print(f"  Coating: {coating_str}")
                stats["specs"] += 1
            else:
                print("  No optical specs found in page")

        # Download images
        if not args.specs_only:
            image_urls = extract_image_urls(html)

            for j, constr_url in enumerate(image_urls["construction"]):
                ext = constr_url.rsplit(".", 1)[-1].split("?")[0].lower()
                if ext not in ("png", "jpg", "jpeg", "webp"):
                    ext = "png"
                suffix = f"-{j + 1}" if j > 0 else ""
                dest = specs_dir / f"{slug}-construction{suffix}.{ext}"
                if download_image(constr_url, dest):
                    print(f"  Downloaded: {dest.name}")
                    stats["images"] += 1
                else:
                    print(f"  FAILED: {dest.name}")
                    stats["failed"] += 1

            for j, mtf_url in enumerate(image_urls["mtf"]):
                ext = mtf_url.rsplit(".", 1)[-1].split("?")[0].lower()
                if ext not in ("png", "jpg", "jpeg", "webp"):
                    ext = "png"
                suffix = f"-{j + 1}" if j > 0 else ""
                dest = specs_dir / f"{slug}-mtf{suffix}.{ext}"
                if download_image(mtf_url, dest):
                    print(f"  Downloaded: {dest.name}")
                    stats["images"] += 1
                else:
                    print(f"  FAILED: {dest.name}")
                    stats["failed"] += 1

            if not image_urls["construction"] and not image_urls["mtf"]:
                print("  No optical images found")

        # Brief pause between pages to be polite
        if i < len(lenses) - 1:
            time.sleep(2)

    print(f"\n{'=' * 40}")
    print(f"Done: {stats['specs']} specs, {stats['images']} images, "
          f"{stats['skipped']} skipped, {stats['failed']} failed")


if __name__ == "__main__":
    main()
