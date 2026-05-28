"""Fetch optical specs, MTF charts, and construction diagrams for Tokina.

Thin entry point: it wires the Tokina BrandExtractor to a pagefetch
NetworkFetcher via a brandkit BrandTool, then drives the shared pipeline.
All brand-specific parsing lives in extractor.py; all shared scaffolding
(slug, lenses.ts parsing, caching, image download, verification) lives in
brandkit.

Usage:
    py tools/tokina/fetch_specs.py                # fetch all (specs + images)
    py tools/tokina/fetch_specs.py --dry-run      # list lenses without fetching
    py tools/tokina/fetch_specs.py --filter 23mm  # filter by model substring
    py tools/tokina/fetch_specs.py --limit 2      # fetch first N only
    py tools/tokina/fetch_specs.py --specs-only   # only extract specs text
    py tools/tokina/fetch_specs.py --images-only  # only download images
    py tools/tokina/fetch_specs.py --verify       # cross-validate physical specs (#779)
"""

import argparse
import sys
import time
from pathlib import Path

# Make the sibling packages (pagefetch, brandkit) importable.
TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import BrandTool  # noqa: E402
from pagefetch import FileCache, NetworkFetcher  # noqa: E402

from extractor import TokinaExtractor  # noqa: E402

ROOT = TOOLS_DIR.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"
CACHE_DIR = ROOT / ".cache" / "fetch"


def build_tool() -> BrandTool:
    return BrandTool(
        extractor=TokinaExtractor(),
        source=NetworkFetcher(cache=FileCache(cache_dir=CACHE_DIR)),
        lenses_path=LENSES_TS,
        specs_root=OPTICAL_SPECS_DIR,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Tokina optical specs and images")
    parser.add_argument("--dry-run", action="store_true", help="List lenses without fetching")
    parser.add_argument("--filter", type=str, help="Filter by model substring (case-insensitive)")
    parser.add_argument("--limit", type=int, help="Fetch first N lenses only")
    parser.add_argument("--specs-only", action="store_true", help="Only extract specs text, no images")
    parser.add_argument("--images-only", action="store_true", help="Only download images")
    parser.add_argument("--verify", action="store_true", help="Cross-validate stored physical specs (#779)")
    return parser.parse_args()


def format_ts_fields(specs: dict) -> str:
    """Format extracted specs as TypeScript fields for lenses.ts."""
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


def run_verify(tool: BrandTool, lenses) -> None:
    """#779: report physical-spec mismatches and unreachable URLs."""
    clean = issues = 0
    for i, lens in enumerate(lenses):
        print(f"\n[{i + 1}/{len(lenses)}] {lens.model}")
        status = tool.validate_url(lens)
        if not status.ok:
            print(f"  URL: {status.detail} -> {lens.url}")
            issues += 1
            continue
        mismatches = tool.verify(lens)
        if mismatches:
            for m in mismatches:
                print(f"  MISMATCH {m}")
            issues += 1
        else:
            clean += 1
        if i < len(lenses) - 1:
            time.sleep(1)
    print(f"\n{'=' * 40}\nVerify: {clean} clean, {issues} with issues")


def run_fetch(tool: BrandTool, lenses, do_specs: bool, do_images: bool) -> None:
    stats = {"specs": 0, "mtf": 0, "construction": 0, "failed": 0}
    for i, lens in enumerate(lenses):
        print(f"\n[{i + 1}/{len(lenses)}] {lens.model}")
        try:
            if do_specs:
                specs = tool.fetch_optical(lens)
                el, gr = specs.get("elements", "?"), specs.get("groups", "?")
                sp, co = specs.get("special", []), specs.get("coating", [])
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
                urls = tool.fetch_image_urls(lens)
                written = tool.save_images(lens, urls)
                for path in written:
                    kind = "MTF" if "-mtf" in path.name else "Construction"
                    print(f"  {kind}: {path.name}")
                    stats["mtf" if "-mtf" in path.name else "construction"] += 1
                if not urls["construction"]:
                    print("  No construction diagram found on page")
                if not urls["mtf"]:
                    print("  No MTF charts found on page")

            if i < len(lenses) - 1:
                time.sleep(1)
        except Exception as e:
            print(f"  ERROR: {e}")
            stats["failed"] += 1

    print(f"\n{'=' * 40}")
    print(
        f"Done: {stats['specs']} specs, {stats['mtf']} MTF charts, "
        f"{stats['construction']} construction diagrams, {stats['failed']} failed"
    )


def main() -> None:
    args = parse_args()
    tool = build_tool()

    lenses = tool.resolve_lenses()
    print(f"Found {len(lenses)} Tokina lenses with official URLs")

    if args.filter:
        lenses = [l for l in lenses if args.filter.lower() in l.model.lower()]
        print(f"  Filtered to {len(lenses)} matching '{args.filter}'")
    if args.limit:
        lenses = lenses[: args.limit]

    if args.dry_run:
        for lens in lenses:
            print(f"  {lens.model}: {lens.url}")
        return

    if args.verify:
        run_verify(tool, lenses)
        return

    run_fetch(tool, lenses, do_specs=not args.images_only, do_images=not args.specs_only)


if __name__ == "__main__":
    main()
