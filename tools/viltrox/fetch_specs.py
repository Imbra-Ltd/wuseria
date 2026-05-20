"""Fetch optical specs from Viltrox Shopify product pages.

Extracts optical construction (elements, groups, special elements) and
coating data from the Shopify JSON API. Viltrox does NOT provide MTF
charts or construction diagrams on their website.

Usage:
    py tools/viltrox/fetch_specs.py                    # fetch all specs
    py tools/viltrox/fetch_specs.py --dry-run           # list lenses without fetching
    py tools/viltrox/fetch_specs.py --filter 13mm       # filter by model substring
    py tools/viltrox/fetch_specs.py --limit 5           # fetch first N only
    py tools/viltrox/fetch_specs.py --no-cache          # bypass cache, re-fetch all pages
"""

import argparse
import time

from common import (
    CACHE_DIR,
    extract_specs,
    extract_viltrox_lenses,
    fetch_product_json,
    model_to_slug,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Viltrox optical specs")
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
        for f in CACHE_DIR.glob("*.json"):
            f.unlink()
        print("Cache cleared")

    lenses = extract_viltrox_lenses()
    print(f"Found {len(lenses)} Viltrox lenses with official URLs")

    if args.filter:
        lenses = [l for l in lenses if args.filter.lower() in l["model"].lower()]
        print(f"  Filtered to {len(lenses)} matching '{args.filter}'")

    if args.limit:
        lenses = lenses[:args.limit]

    if args.dry_run:
        for lens in lenses:
            slug = model_to_slug(lens["model"])
            print(f"  {lens['model']}: {slug} -> {lens['url']}")
        return

    stats = {"specs": 0, "no_specs": 0, "failed": 0}

    for i, lens in enumerate(lenses):
        model = lens["model"]
        slug = model_to_slug(model)
        url = lens["url"]

        print(f"\n[{i + 1}/{len(lenses)}] {model}")

        try:
            data = fetch_product_json(url)
            specs = extract_specs(data)
            el = specs.get("elements", "?")
            gr = specs.get("groups", "?")
            sp = specs.get("special", [])
            co = specs.get("coating", [])

            print(f"  Specs: {el}e/{gr}g, special={sp}, coating={co}")

            if el != "?":
                print(format_ts_fields(specs))
                stats["specs"] += 1
            else:
                print(f"  No specs found in Shopify body_html (older pages lack detail)")
                stats["no_specs"] += 1

            if i < len(lenses) - 1:
                time.sleep(0.5)

        except Exception as e:
            print(f"  ERROR: {e}")
            stats["failed"] += 1

    print(f"\n{'=' * 40}")
    print(f"Done: {stats['specs']} with specs, {stats['no_specs']} without specs, "
          f"{stats['failed']} failed")
    print(f"\nNote: Viltrox does not provide MTF charts or construction diagrams.")
    print(f"Missing specs can be supplemented from LensTip, OpticalLimits, etc.")


if __name__ == "__main__":
    main()
