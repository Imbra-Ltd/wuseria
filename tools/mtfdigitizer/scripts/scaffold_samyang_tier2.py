"""Scaffold Tier 2 ReferenceChart entries for every Samyang lens that
has an MTF chart image.

Walks ``docs/optical-specs/samyang-*`` folders, detects both panel plot
boxes via ``samyang_plotbox.detect_samyang_plotbox``, and writes
``_samyang_tier2_charts.py`` declaring one ``ReferenceChart`` per lens
with:

- ``style_family="mainstream-4color-all-solid"`` (the registered family;
  the actual hue profile is ``SAMYANG_4COLOR_ALL_SOLID``)
- primary view's ``plot_box`` = MAX panel (top, typically y 43..463)
- ``additional_views=(ChartView(plot_box=<F8 panel>, aperture="F8"),)``
  per ADR-063 — the per-view aperture override that lets one chart
  publish two panels at different f-stops
- ``apertures=("MAX", "F8")`` — literal panel labels matching the
  Tier 1 anchors (85mm, 300mm reflex). The lens's wide-open f-number
  lives in the slug; no eye-read aperture table needed.
- ``frequencies_lpmm=(10, 30)``
- ``ground_truth=None`` (Tier 2 per ADR-041)

Per-slug ``image_height_mm`` comes from a small table here — the
chart's x-axis extent in mm cannot be read from the PNG alone without
OCR. The default split is APS-C 14.2 mm vs full-frame 21.6 mm; fisheye
lenses override to APS-C since Samyang's 8mm/12mm fisheyes are mirror-
mount/MFT-mount lenses despite no ``-cs`` slug suffix.

Usage::

    cd tools
    py -m mtfdigitizer.scripts.scaffold_samyang_tier2          # preview
    py -m mtfdigitizer.scripts.scaffold_samyang_tier2 --write  # commit
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from mtfdigitizer.samyang_plotbox import (
    SamyangBoxes,
    detect_samyang_plotbox,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
OPTICAL_SPECS_DIR = REPO_ROOT / "docs" / "optical-specs"


# Per-lens image-height (mm) — the chart x-axis extent. Cannot be read
# from the PNG without OCR; eye-read once per lens from the chart's
# x-axis tick labels.
#
# - Full-frame Samyang charts top out at 21.6 mm (the FF image-height).
# - APS-C charts top out at 14.0..14.2 mm (the APS-C image-height).
# - Samyang's 8mm and 12mm rectangular-fisheye charts are also APS-C
#   despite no ``-cs`` slug suffix.
#
# A slug not in this table fails the scaffolder loud at generation time.
_IMAGE_HEIGHT_MM_BY_SLUG: dict[str, float] = {
    "samyang-100mm-f2-8-ed-umc-macro": 21.6,
    "samyang-10mm-f2-8-ed-as-ncs-cs": 14.2,
    "samyang-12mm-f2-0-ncs-cs": 14.2,
    "samyang-12mm-f2-8-ed-as-ncs-fish-eye": 14.2,
    "samyang-135mm-f2-0-ed-umc": 21.6,
    "samyang-14mm-f2-8-ed-as-if-umc": 21.6,
    "samyang-16mm-f2-0-ed-as-umc-cs": 14.2,
    "samyang-20mm-f1-8-ed-as-umc": 21.6,
    "samyang-21mm-f1-4-ed-as-umc-cs": 14.2,
    "samyang-35mm-f1-2-ed-as-umc-cs": 14.2,
    "samyang-35mm-f1-4-as-umc": 21.6,
    "samyang-50mm-f1-2-as-umc-cs": 14.2,
    "samyang-50mm-f1-4-as-umc": 21.6,
    "samyang-8mm-f2-8-ed-as-if-umc-fisheye": 14.2,
    "samyang-8mm-f3-5-aspherical-if-mc-fish-eye": 14.2,
    "samyang-af-12mm-f2-0": 14.2,
    "samyang-af-75mm-f1-8": 14.2,
    "samyang-tiltshift-24mm-f3-5-ed-as-umc": 21.6,
}


# Tier 1 anchors live in ``charts.py`` proper with maintainer-read
# ground truth; the scaffolder never emits a duplicate entry for them
# (the ``test_no_duplicate_slugs`` assertion would fail).
_TIER1_SKIP_SLUGS: frozenset[str] = frozenset({
    "samyang-85mm-f1-4-as-if-umc",
    "samyang-300mm-f6-3-ed-umc-cs-reflex",
})


@dataclass(frozen=True)
class _ChartFile:
    """One detected chart image's metadata."""

    slug: str
    path: Path  # relative to repo root
    image_height_mm: float
    boxes: SamyangBoxes


def _gather_charts() -> list[_ChartFile]:
    """Find every Samyang MTF chart image and run the detector."""
    charts: list[_ChartFile] = []
    for lens_dir in sorted(OPTICAL_SPECS_DIR.iterdir()):
        if not lens_dir.is_dir():
            continue
        if not lens_dir.name.startswith("samyang-"):
            continue
        if lens_dir.name in _TIER1_SKIP_SLUGS:
            continue
        slug = lens_dir.name
        chart_path = lens_dir / f"{slug}-mtf.png"
        if not chart_path.exists():
            print(
                f"SKIP {slug}: no <slug>-mtf.png file",
                file=sys.stderr,
            )
            continue
        if slug not in _IMAGE_HEIGHT_MM_BY_SLUG:
            raise KeyError(
                f"{slug}: no entry in _IMAGE_HEIGHT_MM_BY_SLUG. Add the "
                f"lens's chart x-axis extent (mm) to the table at the top "
                f"of scaffold_samyang_tier2.py — eye-read from the "
                f"x-axis tick labels (typically 21.6 for full-frame, "
                f"14.2 for APS-C)."
            )
        boxes = detect_samyang_plotbox(chart_path)
        charts.append(
            _ChartFile(
                slug=slug,
                path=chart_path.relative_to(REPO_ROOT),
                image_height_mm=_IMAGE_HEIGHT_MM_BY_SLUG[slug],
                boxes=boxes,
            )
        )
    return charts


# --- Code emission --------------------------------------------------------


def _box_repr(box: tuple[int, int, int, int]) -> str:
    xl, xr, yt, yb = box
    return (
        f"PlotBoxCoords(x_left={xl}, x_right={xr}, "
        f"y_top={yt}, y_bottom={yb})"
    )


def _chart_path_literal(rel_path: Path) -> str:
    """Forward-slashed path literal for ``chart_path``."""
    return str(rel_path).replace("\\", "/")


def _format_lens_entry(c: _ChartFile) -> str:
    """Emit one ReferenceChart literal for one Samyang lens."""
    notes = (
        f"Tier 2 production entry (ADR-041, ADR-063). Samyang two-panel "
        f"chart: MAX panel on top, F8 panel below, both sharing the same "
        f"x-axis (image height {c.image_height_mm} mm). Plot boxes "
        f"auto-detected by `samyang_plotbox.detect_samyang_plotbox`; "
        f"per-view aperture override emits MAX + F8 artifacts per pass."
    )
    chart_lit = _chart_path_literal(c.path)
    return (
        "    ReferenceChart(\n"
        f'        slug="{c.slug}",\n'
        f'        chart_path="{chart_lit}",\n'
        '        style_family="mainstream-4color-all-solid",\n'
        '        apertures=("MAX", "F8"),\n'
        "        frequencies_lpmm=(10, 30),\n"
        f"        image_height_mm={c.image_height_mm},\n"
        f'        notes=(\n            "{notes}"\n        ),\n'
        f"        plot_box={_box_repr(c.boxes.max_box)},\n"
        "        ground_truth=None,\n"
        "        additional_views=(\n"
        "            ChartView(\n"
        f'                chart_path="{chart_lit}",\n'
        f"                plot_box={_box_repr(c.boxes.f8_box)},\n"
        '                aperture="F8",\n'
        "            ),\n"
        "        ),\n"
        "    ),"
    )


def emit_module(charts: list[_ChartFile]) -> str:
    """Render the full ``_samyang_tier2_charts.py`` module body."""
    body = "\n".join(_format_lens_entry(c) for c in charts)
    header = (
        '"""Tier 2 ReferenceChart entries for Samyang lenses '
        "(ADR-063).\n\n"
        "Generated by `tools/mtfdigitizer/scripts/scaffold_samyang_tier2.py`.\n"
        "Plot boxes for both panels (MAX, F8) auto-detected by\n"
        "`samyang_plotbox.detect_samyang_plotbox`. Per-lens "
        "`image_height_mm`\n"
        "comes from the scaffolder's `_IMAGE_HEIGHT_MM_BY_SLUG` table.\n\n"
        "Do not hand-edit; re-run the scaffolder to update.\n\n"
        f"At time of generation: {len(charts)} lenses, "
        f"{len(charts)} chart images (one per lens, two panels each).\n"
        '"""\n\n'
        "from __future__ import annotations\n\n"
        "from .charts import ChartView, PlotBoxCoords, ReferenceChart\n\n\n"
        "SAMYANG_TIER2_CHARTS: tuple[ReferenceChart, ...] = (\n"
    )
    footer = "\n)\n"
    return header + body + footer


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the scaffolded module to "
        "tools/mtfdigitizer/referenceset/_samyang_tier2_charts.py. "
        "Without this flag, the output is printed to stdout for review.",
    )
    args = parser.parse_args(argv)

    charts = _gather_charts()
    if not charts:
        print("No Samyang Tier 2 lenses found.", file=sys.stderr)
        return 1

    module_source = emit_module(charts)
    target = (
        REPO_ROOT
        / "tools"
        / "mtfdigitizer"
        / "referenceset"
        / "_samyang_tier2_charts.py"
    )
    if args.write:
        target.write_text(module_source, encoding="utf-8", newline="\n")
        print(
            f"Wrote {target.relative_to(REPO_ROOT)} ({len(charts)} lenses).",
            file=sys.stderr,
        )
    else:
        print(module_source)
        print(
            f"\n# Preview only — pass --write to update "
            f"{target.relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
