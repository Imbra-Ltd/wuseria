"""Fetch optical specs from Mitakon (Zhongyi Optics) zyoptics.net pages.

Uses SeleniumBase UC mode because zyoptics.net blocks urllib and Playwright
with 403 responses. Extracts optical construction (elements, groups, special
elements) and coating data from WooCommerce product pages.

Note: zyoptics.net does not publish MTF charts or construction diagrams.

Usage:
    py tools/mitakon/fetch_specs.py                    # fetch all
    py tools/mitakon/fetch_specs.py --dry-run           # list lenses without fetching
    py tools/mitakon/fetch_specs.py --filter 35mm       # filter by model substring
    py tools/mitakon/fetch_specs.py --limit 2           # fetch first N only
    py tools/mitakon/fetch_specs.py --no-cache          # bypass cache, re-fetch all pages
"""

import argparse
import sys
import io
import time

# Force UTF-8 stdout (zyoptics.net has Unicode characters like prime symbols)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from common import (
    CACHE_DIR,
    browser_session,
    extract_mitakon_lenses,
    extract_specs,
    fetch_page,
    model_to_slug,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Mitakon optical specs")
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
        for f in CACHE_DIR.glob("mitakon-*.html"):
            f.unlink()
        for f in CACHE_DIR.glob("mitakon-*.txt"):
            f.unlink()
        print("Cache cleared")

    lenses = extract_mitakon_lenses()
    print(f"Found {len(lenses)} Mitakon lenses with official URLs")

    if args.filter:
        lenses = [l for l in lenses if args.filter.lower() in l["model"].lower()]
        print(f"  Filtered to {len(lenses)} matching '{args.filter}'")

    if args.limit:
        lenses = lenses[: args.limit]

    if args.dry_run:
        for lens in lenses:
            slug = model_to_slug(lens["model"])
            print(f"  {lens['model']} [{lens['mount']}] ({slug}): {lens['url']}")
        return

    stats = {"specs": 0, "failed": 0}

    with browser_session() as sb:
        for i, lens in enumerate(lenses):
            model = lens["model"]
            mount = lens["mount"]
            slug = model_to_slug(model)
            url = lens["url"]

            print(f"\n[{i + 1}/{len(lenses)}] {model} [{mount}]")
            print(f"  URL: {url}")

            try:
                _text, html = fetch_page(sb, url)
                specs = extract_specs(html)

                el = specs.get("elements", "?")
                gr = specs.get("groups", "?")
                sp = specs.get("special", [])
                co = specs.get("coating", [])

                print(f"  Specs: {el}e/{gr}g, special={sp}, coating={co}")

                if el != "?":
                    print(format_ts_fields(specs))
                    stats["specs"] += 1
                else:
                    print("  WARN: could not extract elements/groups")
                    stats["failed"] += 1

            except Exception as e:
                print(f"  ERROR: {e}")
                stats["failed"] += 1

            if i < len(lenses) - 1:
                time.sleep(2)

    print(f"\n{'=' * 40}")
    print(f"Done: {stats['specs']} specs extracted, {stats['failed']} failed")


if __name__ == "__main__":
    main()
