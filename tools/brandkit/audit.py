"""Shared data-completeness audit for brand spec tools.

Every brand's audit.py asked the same questions: which lenses for this
brand have opticalElements / opticalGroups / specialElements / coating /
officialUrl present in lenses.ts, and do MTF + construction images exist in
the specs folder. That logic lives here once; a brand's audit.py just
builds its BrandTool and calls audit().
"""

import argparse
import re

from .tool import BrandTool

# lenses.ts field markers checked for presence, with the label printed when
# the field is missing.
_FIELD_MARKERS = (
    ("officialUrl:", "no officialUrl"),
    ("opticalElements:", "no opticalElements"),
    ("opticalGroups:", "no opticalGroups"),
    ("specialElements:", "no specialElements"),
    ("coating:", "no coating"),
)


def _field_presence(lenses_path, brand: str) -> dict[str, dict[str, bool]]:
    """For each lens of the brand, which field markers are present."""
    content = lenses_path.read_text(encoding="utf-8")
    blocks = re.split(r"(?=\{\s*\n\s*brand:)", content)
    results: dict[str, dict[str, bool]] = {}
    for block in blocks:
        if f'brand: "{brand}"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        if model_m:
            results[model_m.group(1)] = {
                marker: marker in block for marker, _ in _FIELD_MARKERS
            }
    return results


def _parse_args(brand: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"Audit {brand} lens data completeness")
    parser.add_argument("--filter", type=str, help="Filter by model substring (case-insensitive)")
    parser.add_argument("--missing", action="store_true", help="Show only lenses with missing data")
    return parser.parse_args()


def audit(tool: BrandTool, extra_checks=None) -> None:
    """Parse argv and print a completeness report for the brand.

    extra_checks, if given, is called as extra_checks(tool, model) -> list[str]
    and its returned issue labels are appended — lets a brand add checks the
    shared report doesn't know about (e.g. Zeiss's PDF datasheet)."""
    brand = tool.config.name
    args = _parse_args(brand)

    presence = _field_presence(tool.lenses_path, brand)
    models = sorted(presence)
    if args.filter:
        models = [m for m in models if args.filter.lower() in m.lower()]

    complete = incomplete = 0
    for model in models:
        issues = [
            label for marker, label in _FIELD_MARKERS if not presence[model][marker]
        ]
        slug = tool.slug_for(model)
        # Image checks only apply to brands that publish diagrams.
        if tool.config.has_diagrams:
            if not tool.has_mtf_for_slug(slug):
                issues.append("no MTF chart")
            if not tool.has_construction_for_slug(slug):
                issues.append("no construction image")
        if extra_checks:
            issues.extend(extra_checks(tool, model))

        if issues:
            incomplete += 1
            print(f"  {model}: {', '.join(issues)}")
        elif not args.missing:
            complete += 1
            print(f"  {model}: OK")

    print(f"\n{complete} complete, {incomplete} incomplete out of {len(models)} lenses")
