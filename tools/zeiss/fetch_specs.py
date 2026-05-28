"""Fetch PDF datasheets for Carl Zeiss Touit lenses.

Carl Zeiss Touit lenses are discontinued and their product pages 404. The
officialUrl fields point to PDF datasheets on zeiss.com with optical
construction diagrams, MTF charts, and specs. This tool downloads those PDFs
to docs/optical-specs/{slug}/; charts must be extracted from the PDF manually.

Unlike other brands this is a PDF download, not spec scraping, so it builds a
brandkit BrandTool (for lens resolution + the shared save_pdf path) but keeps
its own small main rather than using the generic spec/verify CLI runner.

Usage:
    py tools/zeiss/fetch_specs.py                # download all datasheets
    py tools/zeiss/fetch_specs.py --dry-run      # list lenses without downloading
    py tools/zeiss/fetch_specs.py --filter 12mm  # filter by model substring
"""

import argparse
import sys
import time
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import BrandTool  # noqa: E402
from pagefetch import FileCache, NetworkFetcher  # noqa: E402
from zeiss.extractor import ZeissExtractor  # noqa: E402

ROOT = TOOLS_DIR.parent


def build_tool() -> BrandTool:
    return BrandTool(
        extractor=ZeissExtractor(),
        source=NetworkFetcher(cache=FileCache(cache_dir=ROOT / ".cache" / "fetch")),
        lenses_path=ROOT / "src" / "data" / "lenses.ts",
        specs_root=ROOT / "docs" / "optical-specs",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Carl Zeiss Touit PDF datasheets")
    parser.add_argument("--dry-run", action="store_true", help="List lenses without downloading")
    parser.add_argument("--filter", type=str, help="Filter by model substring (case-insensitive)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tool = build_tool()

    lenses = tool.resolve_lenses()
    print(f"Found {len(lenses)} Carl Zeiss lenses with official URLs")
    if args.filter:
        lenses = [l for l in lenses if args.filter.lower() in l.model.lower()]
        print(f"  Filtered to {len(lenses)} matching '{args.filter}'")

    if args.dry_run:
        for lens in lenses:
            print(f"  {lens.model}: {lens.url}")
        return

    stats = {"downloaded": 0, "skipped": 0, "failed": 0}
    for i, lens in enumerate(lenses):
        slug = tool.slug_for(lens.model)
        print(f"\n[{i + 1}/{len(lenses)}] {lens.model}")
        if tool.has_datasheet(lens):
            print(f"  Already exists: {slug}-datasheet.pdf")
            stats["skipped"] += 1
        elif tool.save_pdf(lens):
            print(f"  Downloaded: {slug}-datasheet.pdf")
            stats["downloaded"] += 1
        else:
            print("  FAILED: could not download datasheet")
            stats["failed"] += 1
        print("  NOTE: extract MTF + construction diagrams manually from the PDF")
        print(f"        save as: {slug}-mtf.png, {slug}-construction.png")
        if i < len(lenses) - 1:
            time.sleep(1)

    print(f"\n{'=' * 40}")
    print(f"Done: {stats['downloaded']} downloaded, {stats['skipped']} skipped, {stats['failed']} failed")


if __name__ == "__main__":
    main()
