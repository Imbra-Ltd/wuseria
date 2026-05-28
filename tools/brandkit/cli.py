"""Shared command-line runner for brand spec tools.

Every brand's fetch_specs.py drives the same pipeline — parse the same
flags, list/filter lenses, then either fetch specs+images or verify
physical specs (#779). That orchestration lives here once; a brand's
fetch_specs.py only has to build its BrandTool and call run().

The brand name for log lines comes from the tool's BrandConfig, so the
runner needs no brand-specific parameters.
"""

import argparse
import time

from .tool import BrandTool


def _parse_args(brand: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"Fetch {brand} optical specs and images")
    parser.add_argument("--dry-run", action="store_true", help="List lenses without fetching")
    parser.add_argument("--filter", type=str, help="Filter by model substring (case-insensitive)")
    parser.add_argument("--limit", type=int, help="Fetch first N lenses only")
    parser.add_argument("--specs-only", action="store_true", help="Only extract specs text, no images")
    parser.add_argument("--images-only", action="store_true", help="Only download images")
    parser.add_argument("--verify", action="store_true", help="Cross-validate stored physical specs (#779)")
    return parser.parse_args()


def format_ts_fields(specs: dict) -> str:
    """Format extracted optical specs as TypeScript fields for lenses.ts."""
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


def _run_verify(tool: BrandTool, lenses) -> None:
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


def _run_fetch(tool: BrandTool, lenses, do_specs: bool, do_images: bool) -> None:
    stats = {"specs": 0, "mtf": 0, "construction": 0, "failed": 0}
    for i, lens in enumerate(lenses):
        print(f"\n[{i + 1}/{len(lenses)}] {lens.model}")
        try:
            if do_specs:
                specs = tool.fetch_optical(lens)
                el, gr = specs.get("elements", "?"), specs.get("groups", "?")
                print(
                    f"  Specs: {el}e/{gr}g, special={specs.get('special', [])}, "
                    f"coating={specs.get('coating', [])}"
                )
                estimated = [s for s in specs.get("special", []) if s.startswith("~")]
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
                for path in tool.save_images(lens, urls):
                    is_mtf = "-mtf" in path.name
                    print(f"  {'MTF' if is_mtf else 'Construction'}: {path.name}")
                    stats["mtf" if is_mtf else "construction"] += 1
                if not urls["construction"]:
                    print("  No construction diagram found on page")
                if not urls["mtf"]:
                    print("  No MTF chart found on page")

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


def run(tool: BrandTool) -> None:
    """Parse argv and drive the tool. A brand's fetch_specs.py calls this."""
    brand = tool.config.name
    args = _parse_args(brand)

    lenses = tool.resolve_lenses()
    print(f"Found {len(lenses)} {brand} lenses with official URLs")

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
        _run_verify(tool, lenses)
        return

    _run_fetch(tool, lenses, do_specs=not args.images_only, do_images=not args.specs_only)
