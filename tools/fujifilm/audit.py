"""Audit Fujifilm lens data completeness.

Checks which lenses have MTF charts, optical construction diagrams,
construction data in lenses.ts, and coating data.

Usage:
    py tools/fujifilm/audit.py                  # full audit
    py tools/fujifilm/audit.py --filter gf      # filter by model substring
    py tools/fujifilm/audit.py --missing        # show only lenses with missing data
"""

import argparse
import re

from common import (
    LENSES_TS,
    OPTICAL_SPECS_DIR,
    OPTICAL_CONSTRUCTION_DIR,
    MTF_CHARTS_DIR,
    extract_fujifilm_lenses,
    model_to_slug,
    has_construction_image,
    has_mtf_charts,
)


def check_lenses_ts_fields() -> dict[str, dict]:
    """Check which Fujifilm lenses have optical fields populated in lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    entries = content.split("  {")
    results = {}

    for entry in entries:
        brand_m = re.search(r'brand: "Fujifilm"', entry)
        if not brand_m:
            continue
        model_m = re.search(r'model: "([^"]+)"', entry)
        if not model_m:
            continue

        model = model_m.group(1)
        results[model] = {
            "has_elements": "opticalElements:" in entry,
            "has_groups": "opticalGroups:" in entry,
            "has_coating": "coating:" in entry,
            "has_ed": "edElements:" in entry,
            "has_aspherical": "asphericalElements:" in entry,
            "has_official_url": "officialUrl:" in entry,
        }

    return results


def check_files(slug: str) -> dict:
    """Check which files exist for a given lens slug."""
    optical_specs_dir = OPTICAL_SPECS_DIR / slug
    has_optical_specs = optical_specs_dir.is_dir()
    has_notes = (optical_specs_dir / "notes.md").exists() if has_optical_specs else False

    return {
        "has_construction_img": has_construction_image(slug),
        "has_mtf": has_mtf_charts(slug),
        "has_optical_specs_dir": has_optical_specs,
        "has_notes": has_notes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Fujifilm lens data completeness")
    parser.add_argument("--filter", type=str, help="Filter by model substring (case-insensitive)")
    parser.add_argument("--missing", action="store_true", help="Show only lenses with missing data")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Get all Fujifilm lenses from lenses.ts (including those without officialUrl)
    ts_fields = check_lenses_ts_fields()
    url_lenses = {l["model"]: l["url"] for l in extract_fujifilm_lenses()}

    all_models = sorted(ts_fields.keys())
    if args.filter:
        all_models = [m for m in all_models if args.filter.lower() in m.lower()]

    complete = 0
    incomplete = 0

    for model in all_models:
        slug = model_to_slug(model)
        fields = ts_fields[model]
        files = check_files(slug)

        issues = []

        if not fields["has_official_url"]:
            issues.append("no officialUrl")
        if not fields["has_elements"]:
            issues.append("no opticalElements")
        if not fields["has_groups"]:
            issues.append("no opticalGroups")
        if not fields["has_coating"]:
            issues.append("no coating")
        if not files["has_construction_img"]:
            issues.append("no construction image")
        if not files["has_mtf"]:
            issues.append("no MTF charts")
        if not files["has_optical_specs_dir"]:
            issues.append("no optical-specs dir")

        if issues:
            incomplete += 1
            print(f"  {model}: {', '.join(issues)}")
        elif not args.missing:
            complete += 1
            print(f"  {model}: OK")

    print(f"\n{complete} complete, {incomplete} incomplete out of {len(all_models)} lenses")


if __name__ == "__main__":
    main()
