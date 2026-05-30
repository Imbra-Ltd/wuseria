"""Reference-set render-match IoU runner (#963, ADR-038 §4).

Runs `extract_chart()` then `score_chart()` against every reference
chart with both ground truth and a plot box, and reports the per-field
IoU + a one-sided polyline-on-skeleton precision against the dilated
skeleton — the round-trip confidence signal.

Sister runner to `calibrate.py`: that one reports the offset distribution
against ground truth (the |d| half of REFERENCE_SET.md §"What
'calibration against the set' actually means"); this one reports the
render-match IoU half.

Usage::

    cd tools
    py -m mtfdigitizer.scorer

Output: a per-chart table on stdout + an aggregate summary. No file
writes — findings live in `referenceset/scoring.md`, which the
maintainer updates after a run.
"""

from __future__ import annotations

import statistics
from pathlib import Path

from .pipeline import PlotBox, extract_chart, score_chart
from .pipeline.rendermatch import (
    CURVE_FIELDS,
    DEFAULT_DILATION_RADIUS_PX,
    FieldIou,
    RenderMatchScore,
)
from .profiles import SAMYANG_4COLOR_ALL_SOLID, SIGMA_2COLOR_SOLID_DASHED
from .profiles.types import MtfProfile
from .referenceset.charts import REFERENCE_CHARTS, PlotBoxCoords, ReferenceChart
from .triage import precision_of


REPO_ROOT = Path(__file__).resolve().parents[2]


# Style family → declared profile. Same table as `calibrate.py` — kept
# in sync by hand for now (two entries; not worth a shared module yet).
_PROFILE_BY_STYLE: dict[str, MtfProfile] = {
    "mainstream-2color-solid-dashed": SIGMA_2COLOR_SOLID_DASHED,
    "mainstream-4color-all-solid": SAMYANG_4COLOR_ALL_SOLID,
    "idealized-flat": SAMYANG_4COLOR_ALL_SOLID,  # same 4-color template
}


def _to_plotbox(coords: PlotBoxCoords) -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
    )


def _score_one(chart: ReferenceChart) -> RenderMatchScore:
    """Run extract → score on one reference chart.

    Caller filters runnable charts (plot_box + ground_truth present);
    the ground_truth itself isn't consumed here — render-match doesn't
    compare to eye-read values, only to the chart's own skeleton.
    """
    assert chart.plot_box is not None
    profile = _PROFILE_BY_STYLE.get(chart.style_family)
    if profile is None:
        raise ValueError(
            f"{chart.slug}: no declared profile for style_family={chart.style_family!r}"
        )
    image_path = REPO_ROOT / chart.chart_path
    plot_box = _to_plotbox(chart.plot_box)
    extracted = extract_chart(
        image_path, profile, plot_box, image_height_mm=chart.image_height_mm
    )
    return score_chart(
        image_path,
        profile,
        plot_box,
        image_height_mm=chart.image_height_mm,
        readings=extracted.readings,
        dilation_radius_px=DEFAULT_DILATION_RADIUS_PX,
    )


def _format_field_row(fs: FieldIou) -> str:
    iou_s = f"{fs.score:.3f}" if fs.score is not None else "  -  "
    prec = precision_of(fs)
    prec_s = f"{prec:.3f}" if prec is not None else "  -  "
    return (
        f"  {fs.field:<14}  IoU {iou_s}  precision {prec_s}  "
        f"raster {fs.rasterized_px:6d}  skel {fs.skeleton_px:6d}  "
        f"inter {fs.intersection_px:6d}"
    )


def main() -> None:
    runnable = [c for c in REFERENCE_CHARTS if c.plot_box and c.ground_truth]
    print(
        f"Render-match scoring {len(runnable)} of {len(REFERENCE_CHARTS)} reference charts."
    )
    print(f"Dilation radius: {DEFAULT_DILATION_RADIUS_PX} px (symmetric).")
    print()

    aggregates: list[float] = []
    precisions: list[float] = []
    for chart in runnable:
        result = _score_one(chart)
        print(f"## {chart.slug} ({chart.style_family})")
        for fs in result.field_scores:
            print(_format_field_row(fs))
        if result.aggregate is not None:
            aggregates.append(result.aggregate)
            print(f"  aggregate IoU:                {result.aggregate:.3f}")
        else:
            print("  aggregate IoU:                  -")
        # Mean polyline-on-skeleton precision across defined fields.
        precs = [precision_of(fs) for fs in result.field_scores]
        defined = [p for p in precs if p is not None]
        if defined:
            mean_prec = statistics.mean(defined)
            precisions.append(mean_prec)
            print(f"  aggregate precision:          {mean_prec:.3f}  "
                  f"(polyline pixels landing on dilated skeleton)")
        print()

    if not aggregates:
        print("No defined comparisons — nothing to summarize.")
        return

    print("## Aggregate (all runnable charts)")
    print(f"  charts scored:                {len(aggregates)}")
    print(f"  mean IoU:                     {statistics.mean(aggregates):.3f}")
    print(f"  median IoU:                   {statistics.median(aggregates):.3f}")
    if precisions:
        mean_prec = statistics.mean(precisions)
        print(f"  mean precision (polyline-on-skel): {mean_prec:.3f}")
    print()
    print("  Proposed REFERENCE_SET.md threshold: IoU >= 0.75 (starting value).")
    above = sum(1 for a in aggregates if a >= 0.75)
    print(f"  Charts clearing IoU 0.75:     {above}/{len(aggregates)}")


if __name__ == "__main__":
    main()
