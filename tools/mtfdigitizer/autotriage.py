"""Reference-set auto-triage runner (#968, ADR-038 §"Confidence signal").

Runs the full confidence pipeline against every reference chart with both
ground truth and a plot box: `extract_chart` → `score_chart` → `check_all`
→ `triage`. Reports the binary verdict + reason codes per chart.

Sister runner to `calibrate.py`, `scorer.py`, `plausibility.py`. Where
those each report on one signal, this one reports on the *gate* — the
single decision the auto-commit + 3-panel review workflow consumes.

Usage::

    cd tools
    py -m mtfdigitizer.autotriage

Output: a per-chart verdict line + an aggregate summary. No file writes —
findings live in `referenceset/triage.md`, which the maintainer updates
after a run.
"""

from __future__ import annotations

from pathlib import Path

from .pipeline import PlotBox, extract_chart, score_chart
from .pipeline.rendermatch import DEFAULT_DILATION_RADIUS_PX
from .priors import check_all
from .profiles import SAMYANG_4COLOR_ALL_SOLID, SIGMA_2COLOR_SOLID_DASHED
from .profiles.types import MtfProfile
from .referenceset.charts import REFERENCE_CHARTS, PlotBoxCoords, ReferenceChart
from .triage import (
    IOU_THRESHOLD,
    PRECISION_THRESHOLD,
    ChartVerdict,
    triage,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


# Style family → declared profile. Same table as `calibrate.py`,
# `scorer.py`, `plausibility.py`. Kept in sync by hand for now (three
# entries; not worth a shared module yet — when a fourth lands, extract).
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


def triage_chart(chart: ReferenceChart) -> ChartVerdict:
    """Run the full pipeline on one reference chart and return its verdict."""
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
    score = score_chart(
        image_path,
        profile,
        plot_box,
        image_height_mm=chart.image_height_mm,
        readings=extracted.readings,
        dilation_radius_px=DEFAULT_DILATION_RADIUS_PX,
    )
    violations = check_all(extracted.readings)
    return triage(score, violations)


def _format_metric(value: float | None) -> str:
    return f"{value:.3f}" if value is not None else "  -  "


def _format_verdict(v: ChartVerdict) -> str:
    iou = _format_metric(v.render_match_iou)
    prec = _format_metric(v.render_match_precision)
    return (
        f"  {v.verdict:<4}  IoU {iou}  precision {prec}  "
        f"priors {len(v.prior_violations):2d}"
    )


def main() -> None:
    runnable = [c for c in REFERENCE_CHARTS if c.plot_box and c.ground_truth]
    print(
        f"Auto-triaging {len(runnable)} of {len(REFERENCE_CHARTS)} reference charts."
    )
    print(
        f"Thresholds: precision >= {PRECISION_THRESHOLD}, "
        f"IoU >= {IOU_THRESHOLD}, priors must all pass."
    )
    print()

    verdicts: list[ChartVerdict] = []
    for chart in runnable:
        verdict = triage_chart(chart)
        verdicts.append(verdict)
        print(f"## {chart.slug} ({chart.style_family})")
        print(_format_verdict(verdict))
        if verdict.reasons:
            for reason in verdict.reasons:
                print(f"    - {reason.value}")
        print()

    high = sum(1 for v in verdicts if v.verdict == "HIGH")
    low = sum(1 for v in verdicts if v.verdict == "LOW")
    print("## Aggregate")
    print(f"  charts triaged:  {len(verdicts)}")
    print(f"  HIGH:            {high}")
    print(f"  LOW:             {low}")
    print()
    print("  Expected separation per scoring.md + plausibility.md:")
    print("    sigma-56mm           LOW  (precision_below_threshold)")
    print("    samyang-85mm MAX     HIGH (both signals clear)")
    print("    samyang-300mm reflex LOW  (prior_failed_not_suspiciously_flat)")


if __name__ == "__main__":
    main()
