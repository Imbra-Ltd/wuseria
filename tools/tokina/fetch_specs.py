"""Fetch optical specs, MTF charts, and construction diagrams from Tokina pages.

Extracts optical construction (elements, groups, special elements), coating
data, MTF chart images, and construction diagram images from official
Tokina product pages.

Usage:
    py tools/tokina/fetch_specs.py                    # fetch all (specs + images)
    py tools/tokina/fetch_specs.py --dry-run           # list lenses without fetching
    py tools/tokina/fetch_specs.py --filter 23mm       # filter by model substring
    py tools/tokina/fetch_specs.py --limit 2           # fetch first N only
    py tools/tokina/fetch_specs.py --no-cache          # bypass cache, re-fetch all pages
    py tools/tokina/fetch_specs.py --specs-only        # only extract specs text, no images
    py tools/tokina/fetch_specs.py --images-only       # only download images
"""

import argparse
import time

from common import (
    CACHE_DIR,
    OPTICAL_SPECS_DIR,
    download_image,
    extract_image_urls,
    extract_specs,
    extract_tokina_lenses,
    fetch_page,
    model_to_slug,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Tokina optical specs and images")
    parser.add_argument("--dry-run", action="store_true", help="List lenses without fetching")
    parser.add_argument("--filter", type=str, help="Filter by model substring (case-insensitive)")
    parser.add_argument("--limit", type=int, help="Fetch first N lenses only")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache, re-fetch all pages")
    parser.add_argument("--specs-only", action="store_true", help="Only extract specs text, no images")
    parser.add_argument("--images-only", action="store_true", help="Only download images")
    return parser.parse_args()


def format_ts_fields(specs: dict) -> str:
    """Format specs as TypeScript fields for lenses.ts."""
    lines = []
    if "elements" in specs:
        lines.append(f"    opticalElements: {specs['elements']},")
    if "groups" in specs:
        lines.append(f"    opticalGroups: {specs['groups']},")
    if specs.get("special"):
        items = ", ".join(f'"{s}"' for s in specs["special"])
        lines.append(f"    specialElements: [{items}],")
    if specs.get("coating"):
        items = ", ".join(f'"{c}"' for c in specs["coating"])
        lines.append(f"    coating: [{items}],")
    return "\n".join(lines)


def _detect_ext(url: str) -> str:
    """Detect file extension from URL."""
    if ".png" in url.lower():
        return ".png"
    return ".jpg"


def main() -> None:
    args = parse_args()

    if args.no_cache and CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.html"):
            f.unlink()
        print("Cache cleared")

    lenses = extract_tokina_lenses()
    print(f"Found {len(lenses)} Tokina lenses with official URLs")

    if args.filter:
        lenses = [l for l in lenses if args.filter.lower() in l["model"].lower()]
        print(f"  Filtered to {len(lenses)} matching '{args.filter}'")

    if args.limit:
        lenses = lenses[: args.limit]

    if args.dry_run:
        for lens in lenses:
            print(f"  {lens['model']}: {lens['url']}")
        return

    do_specs = not args.images_only
    do_images = not args.specs_only

    stats = {"specs": 0, "mtf": 0, "construction": 0, "failed": 0}

    for i, lens in enumerate(lenses):
        model = lens["model"]
        slug = model_to_slug(model)
        url = lens["url"]

        print(f"\n[{i + 1}/{len(lenses)}] {model}")

        try:
            html = fetch_page(url)

            if do_specs:
                specs = extract_specs(html)
                el = specs.get("elements", "?")
                gr = specs.get("groups", "?")
                sp = specs.get("special", [])
                co = specs.get("coating", [])

                print(f"  Specs: {el}e/{gr}g, special={sp}, coating={co}")

                estimated = [s for s in sp if s.startswith("~")]
                if estimated:
                    print(f"  WARN: estimated counts (verify manually): {estimated}")

                if el != "?":
                    print(format_ts_fields(specs))
                    stats["specs"] += 1
                else:
                    print("  WARN: could not extract elements/groups")
                    stats["failed"] += 1

            if do_images:
                img_urls = extract_image_urls(html)
                specs_dir = OPTICAL_SPECS_DIR / slug

                # Download construction diagram
                if img_urls["construction"]:
                    ext = _detect_ext(img_urls["construction"][0])
                    dest = specs_dir / f"{slug}-construction{ext}"
                    if download_image(img_urls["construction"][0], dest):
                        print(f"  Construction: {dest.name}")
                        stats["construction"] += 1
                    else:
                        print("  WARN: construction download failed")
                else:
                    print("  No construction diagram found on page")

                # Download MTF charts
                if img_urls["mtf"]:
                    for j, mtf_url in enumerate(img_urls["mtf"]):
                        ext = _detect_ext(mtf_url)
                        suffix = f"-mtf-{j + 1}" if len(img_urls["mtf"]) > 1 else "-mtf"
                        dest = specs_dir / f"{slug}{suffix}{ext}"
                        if download_image(mtf_url, dest):
                            print(f"  MTF: {dest.name}")
                            stats["mtf"] += 1
                        else:
                            print(f"  WARN: MTF download failed for {dest.name}")
                else:
                    print("  No MTF charts found on page")

            if i < len(lenses) - 1:
                time.sleep(1)

        except Exception as e:
            print(f"  ERROR: {e}")
            stats["failed"] += 1

    print(f"\n{'=' * 40}")
    print(f"Done: {stats['specs']} specs, {stats['mtf']} MTF charts, "
          f"{stats['construction']} construction diagrams, {stats['failed']} failed")


if __name__ == "__main__":
    main()
