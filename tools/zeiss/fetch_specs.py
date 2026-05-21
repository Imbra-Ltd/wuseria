"""Fetch PDF datasheets for Carl Zeiss Touit lenses.

Carl Zeiss Touit lenses are discontinued and their product pages return 404.
The officialUrl fields point to PDF datasheets on zeiss.com that contain
optical construction diagrams, MTF charts, and full specifications.

This tool downloads the PDF datasheets to docs/optical-specs/{slug}/.
MTF charts and construction diagrams must be extracted manually from the PDFs
(e.g. screenshot or PDF image extraction tool).

Usage:
    py tools/zeiss/fetch_specs.py                    # download all datasheets
    py tools/zeiss/fetch_specs.py --dry-run           # list lenses without downloading
    py tools/zeiss/fetch_specs.py --filter 12mm       # filter by model substring
"""

import argparse
import time

from common import (
    OPTICAL_SPECS_DIR,
    download_pdf,
    extract_zeiss_lenses,
    model_to_slug,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Carl Zeiss Touit PDF datasheets")
    parser.add_argument("--dry-run", action="store_true", help="List lenses without downloading")
    parser.add_argument("--filter", type=str, help="Filter by model substring (case-insensitive)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    lenses = extract_zeiss_lenses()
    print(f"Found {len(lenses)} Carl Zeiss lenses with official URLs")

    if args.filter:
        lenses = [l for l in lenses if args.filter.lower() in l["model"].lower()]
        print(f"  Filtered to {len(lenses)} matching '{args.filter}'")

    if args.dry_run:
        for lens in lenses:
            print(f"  {lens['model']}: {lens['url']}")
        return

    stats = {"downloaded": 0, "skipped": 0, "failed": 0}

    for i, lens in enumerate(lenses):
        model = lens["model"]
        slug = model_to_slug(model)
        url = lens["url"]
        specs_dir = OPTICAL_SPECS_DIR / slug

        print(f"\n[{i + 1}/{len(lenses)}] {model}")

        dest = specs_dir / f"{slug}-datasheet.pdf"
        if dest.exists():
            print(f"  Already exists: {dest.name}")
            stats["skipped"] += 1
        elif download_pdf(url, dest):
            print(f"  Downloaded: {dest.name}")
            stats["downloaded"] += 1
        else:
            print(f"  FAILED: could not download datasheet")
            stats["failed"] += 1

        print(f"  NOTE: Extract MTF charts and construction diagrams manually from the PDF")
        print(f"        Save as: {slug}-mtf.png, {slug}-construction.png")

        if i < len(lenses) - 1:
            time.sleep(1)

    print(f"\n{'=' * 40}")
    print(f"Done: {stats['downloaded']} downloaded, {stats['skipped']} skipped, {stats['failed']} failed")


if __name__ == "__main__":
    main()
