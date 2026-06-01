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

from .pipeline import ExtractedChart, PlotBox, extract_chart, score_chart
from .pipeline.rendermatch import DEFAULT_DILATION_RADIUS_PX
from .priors import check_all
from .family_profile import profile_for_chart
from .referenceset.charts import REFERENCE_CHARTS, PlotBoxCoords, ReferenceChart
from .review import write_review
from .triage import (
    IOU_THRESHOLD,
    PRECISION_THRESHOLD,
    ChartVerdict,
    triage,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def _to_plotbox(coords: PlotBoxCoords) -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
    )


def _run_pipeline(
    chart: ReferenceChart,
) -> tuple[ChartVerdict, ExtractedChart, Path, PlotBox]:
    """Run extract → score → priors → triage on one chart.

    Returns the verdict plus everything the runner needs to also write
    a 3-panel review file for LOW charts (#973): the extracted readings,
    the source path, and the plot box. Kept private so callers go
    through ``triage_chart()`` (verdict-only) or the runner.
    """
    assert chart.plot_box is not None
    profile = profile_for_chart(chart)
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
    verdict = triage(score, violations)
    return verdict, extracted, image_path, plot_box


def triage_chart(chart: ReferenceChart) -> ChartVerdict:
    """Run the full pipeline on one reference chart and return its verdict."""
    verdict, _, _, _ = _run_pipeline(chart)
    return verdict


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
    reviews_written: list[Path] = []
    for chart in runnable:
        verdict, extracted, image_path, plot_box = _run_pipeline(chart)
        verdicts.append(verdict)
        print(f"## {chart.slug} ({chart.style_family})")
        print(_format_verdict(verdict))
        if verdict.reasons:
            for reason in verdict.reasons:
                print(f"    - {reason.value}")
        if verdict.verdict == "LOW":
            # ADR-038 §"Workflow": review file emitted only for LOW
            # charts — HIGH charts auto-commit, the maintainer is never
            # asked to eyeball a chart the gate already verified.
            outputs = write_review(
                extracted,
                image_path,
                plot_box=plot_box,
                image_height_mm=chart.image_height_mm,
                svg_path=image_path.with_suffix(".svg"),
            )
            reviews_written.append(outputs.html_path)
            rel_html = outputs.html_path.relative_to(REPO_ROOT)
            print(f"    review: {rel_html}")
        print()

    high = sum(1 for v in verdicts if v.verdict == "HIGH")
    low = sum(1 for v in verdicts if v.verdict == "LOW")
    print("## Aggregate")
    print(f"  charts triaged:  {len(verdicts)}")
    print(f"  HIGH:            {high}")
    print(f"  LOW:             {low}")
    print(f"  reviews written: {len(reviews_written)}  (one per LOW chart)")
    print()
    print("  Expected separation per scoring.md + plausibility.md:")
    print("    sigma-56mm           LOW  (precision_below_threshold)")
    print("    samyang-85mm MAX     HIGH (both signals clear)")
    print("    samyang-300mm reflex LOW  (prior_failed_not_suspiciously_flat)")


if __name__ == "__main__":
    main()
