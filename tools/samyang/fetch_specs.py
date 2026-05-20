"""Fetch optical specs from Samyang product pages.

Extracts optical construction (elements, groups, special elements) and
coating data from official Samyang product pages.

Usage:
    py tools/samyang/fetch_specs.py                    # fetch all
    py tools/samyang/fetch_specs.py --dry-run           # list lenses without fetching
    py tools/samyang/fetch_specs.py --filter 12mm       # filter by model substring
    py tools/samyang/fetch_specs.py --limit 5           # fetch first N only
    py tools/samyang/fetch_specs.py --no-cache          # bypass cache, re-fetch all pages
"""

import argparse
import sys
import time

from common import (
    extract_samyang_lenses,
    model_to_slug,
    fetch_page,
    extract_specs,
    CACHE_DIR,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Samyang optical specs")
    parser.add_argument("--dry-run", action="store_true", help="List lenses without fetching")
    parser.add_argument("--filter", type=str, help="Filter by model substring (case-insensitive)")
    parser.add_argument("--limit", type=int, help="Fetch first N lenses only")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache, re-fetch all pages")
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


def main() -> None:
    args = parse_args()

    if args.no_cache and CACHE_DIR.exists():
        # Clear Samyang-related cache entries
        for f in CACHE_DIR.glob("*.html"):
            f.unlink()
        print("Cache cleared")

    lenses = extract_samyang_lenses()
    print(f"Found {len(lenses)} Samyang lenses with official URLs")

    if args.filter:
        lenses = [l for l in lenses if args.filter.lower() in l["model"].lower()]
        print(f"  Filtered to {len(lenses)} matching '{args.filter}'")

    if args.limit:
        lenses = lenses[:args.limit]

    if args.dry_run:
        for lens in lenses:
            print(f"  {lens['model']}: {lens['url']}")
        return

    success = 0
    failed = 0

    for i, lens in enumerate(lenses):
        model = lens["model"]
        url = lens["url"]

        print(f"\n[{i + 1}/{len(lenses)}] {model}")
        print(f"  URL: {url}")

        try:
            html = fetch_page(url)
            specs = extract_specs(html)

            el = specs.get("elements", "?")
            gr = specs.get("groups", "?")
            sp = specs.get("special", [])
            co = specs.get("coating", [])

            print(f"  Elements: {el}, Groups: {gr}")
            print(f"  Special: {sp}")
            print(f"  Coating: {co}")

            if el != "?":
                print(f"  TypeScript:")
                print(format_ts_fields(specs))
                success += 1
            else:
                print(f"  WARN: could not extract elements/groups")
                failed += 1

            # Be polite to the server
            if i < len(lenses) - 1:
                time.sleep(1)

        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    print(f"\n{'=' * 40}")
    print(f"Done: {success} extracted, {failed} failed")


if __name__ == "__main__":
    main()
