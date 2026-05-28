"""Audit Tokina lens data completeness.

Checks which Tokina lenses have optical construction and coating data
populated in lenses.ts, plus MTF chart and construction diagram images in
docs/optical-specs/. Uses brandkit for slug generation and image checks.

Usage:
    py tools/tokina/audit.py                  # full audit
    py tools/tokina/audit.py --filter 23mm    # filter by model substring
    py tools/tokina/audit.py --missing        # show only lenses with missing data
"""

import argparse
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import has_construction_image, has_mtf_chart, model_to_slug  # noqa: E402

ROOT = TOOLS_DIR.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"

_FIELDS = {
    "has_official_url": ("officialUrl:", "no officialUrl"),
    "has_elements": ("opticalElements:", "no opticalElements"),
    "has_groups": ("opticalGroups:", "no opticalGroups"),
    "has_special": ("specialElements:", "no specialElements"),
    "has_coating": ("coating:", "no coating"),
}


def check_lenses_ts_fields() -> dict[str, dict]:
    """Which Tokina lenses have each optical field present in lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    blocks = re.split(r"(?=\{\s*\n\s*brand:)", content)
    results = {}
    for block in blocks:
        if 'brand: "Tokina"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        if model_m:
            results[model_m.group(1)] = {
                key: marker in block for key, (marker, _) in _FIELDS.items()
            }
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Tokina lens data completeness")
    parser.add_argument("--filter", type=str, help="Filter by model substring (case-insensitive)")
    parser.add_argument("--missing", action="store_true", help="Show only lenses with missing data")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ts_fields = check_lenses_ts_fields()
    models = sorted(ts_fields)
    if args.filter:
        models = [m for m in models if args.filter.lower() in m.lower()]

    complete = incomplete = 0
    for model in models:
        slug = model_to_slug("tokina", model)
        issues = [
            label for key, (_, label) in _FIELDS.items() if not ts_fields[model][key]
        ]
        if not has_mtf_chart(OPTICAL_SPECS_DIR, slug):
            issues.append("no MTF chart")
        if not has_construction_image(OPTICAL_SPECS_DIR, slug):
            issues.append("no construction image")

        if issues:
            incomplete += 1
            print(f"  {model}: {', '.join(issues)}")
        elif not args.missing:
            complete += 1
            print(f"  {model}: OK")

    print(f"\n{complete} complete, {incomplete} incomplete out of {len(models)} lenses")


if __name__ == "__main__":
    main()
