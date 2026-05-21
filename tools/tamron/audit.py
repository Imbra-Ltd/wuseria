"""Audit Tamron lens data completeness.

Checks which Tamron lenses have optical construction and coating data
populated in lenses.ts, plus MTF chart and construction diagram images
in docs/optical-specs/.

Usage:
    py tools/tamron/audit.py                  # full audit
    py tools/tamron/audit.py --filter 11-20   # filter by model substring
    py tools/tamron/audit.py --missing        # show only lenses with missing data
"""

import argparse
import re

from common import (
    LENSES_TS,
    extract_tamron_lenses,
    has_construction_image,
    has_mtf_chart,
    model_to_slug,
)


def check_lenses_ts_fields() -> dict[str, dict]:
    """Check which Tamron lenses have optical fields populated in lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    blocks = re.split(r"(?=\{\s*\n\s*brand:)", content)
    results = {}

    for block in blocks:
        if 'brand: "Tamron"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        if not model_m:
            continue

        model = model_m.group(1)
        results[model] = {
            "has_elements": "opticalElements:" in block,
            "has_groups": "opticalGroups:" in block,
            "has_special": "specialElements:" in block,
            "has_coating": "coating:" in block,
            "has_official_url": "officialUrl:" in block,
        }

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Tamron lens data completeness")
    parser.add_argument("--filter", type=str, help="Filter by model substring (case-insensitive)")
    parser.add_argument("--missing", action="store_true", help="Show only lenses with missing data")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    ts_fields = check_lenses_ts_fields()
    all_models = sorted(ts_fields.keys())

    if args.filter:
        all_models = [m for m in all_models if args.filter.lower() in m.lower()]

    complete = 0
    incomplete = 0

    for model in all_models:
        slug = model_to_slug(model)
        fields = ts_fields[model]
        issues = []

        if not fields["has_official_url"]:
            issues.append("no officialUrl")
        if not fields["has_elements"]:
            issues.append("no opticalElements")
        if not fields["has_groups"]:
            issues.append("no opticalGroups")
        if not fields["has_special"]:
            issues.append("no specialElements")
        if not fields["has_coating"]:
            issues.append("no coating")
        if not has_mtf_chart(slug):
            issues.append("no MTF chart")
        if not has_construction_image(slug):
            issues.append("no construction image")

        if issues:
            incomplete += 1
            print(f"  {model}: {', '.join(issues)}")
        elif not args.missing:
            complete += 1
            print(f"  {model}: OK")

    print(f"\n{complete} complete, {incomplete} incomplete out of {len(all_models)} lenses")


if __name__ == "__main__":
    main()
