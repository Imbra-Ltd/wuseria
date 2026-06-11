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

from dataclasses import dataclass
from pathlib import Path

from .aperture_passes import aperture_passes_for_view
from .family_profile import profile_for_chart
from .pipeline import ExtractedChart, PlotBox, extract_chart, score_chart
from .pipeline.rendermatch import DEFAULT_DILATION_RADIUS_PX
from .priors import check_all
from .profiles.types import MtfProfile
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


@dataclass(frozen=True)
class PassResult:
    """One pipeline pass output (ADR-052).

    A multi-aperture chart produces N PassResults, one per declared
    aperture; single-aperture charts produce one. The verdict's
    `pass_key` matches `pass_key` here so a caller can route review
    files and aggregation by the same identifier.
    """

    verdict: ChartVerdict
    extracted: ExtractedChart
    image_path: Path
    plot_box: PlotBox
    pass_key: str | None


def _run_one_pass(
    image_path: Path,
    profile: MtfProfile,
    plot_box: PlotBox,
    image_height_mm: float,
    pass_key: str | None,
) -> PassResult:
    extracted = extract_chart(
        image_path, profile, plot_box, image_height_mm=image_height_mm
    )
    score = score_chart(
        image_path,
        profile,
        plot_box,
        image_height_mm=image_height_mm,
        readings=extracted.readings,
        dilation_radius_px=DEFAULT_DILATION_RADIUS_PX,
    )
    violations = check_all(extracted.readings)
    verdict = triage(score, violations, pass_key=pass_key)
    return PassResult(verdict, extracted, image_path, plot_box, pass_key)


def _run_pipeline(chart: ReferenceChart) -> list[PassResult]:
    """Run extract → score → priors → triage on every aperture pass.

    Single-aperture charts return a list of length 1 with
    `pass_result.pass_key is None`. ADR-044 multi-aperture charts return
    one PassResult per declared aperture, each with the orchestrator's
    aperture label as `pass_key`. ADR-052 records the per-aperture
    verdict-shape decision.

    Kept private so callers go through ``triage_chart()`` (single-aperture,
    verdict-only) or ``triage_chart_all_apertures()`` (multi-aperture).
    """
    assert chart.plot_box is not None
    image_path = REPO_ROOT / chart.chart_path
    plot_box = _to_plotbox(chart.plot_box)

    # `aperture_passes_for_view` returns [(aperture, profile)] for both
    # multi-aperture and default charts. We surface `pass_key` only for
    # true ADR-044 multi-aperture (the case the verdict shape exists
    # for); single-aperture and ADR-043 per-frequency charts keep
    # `pass_key=None` so existing single-aperture consumers stay
    # back-compatible. ADR-043 per-frequency labeling is a follow-up
    # (see ADR-052 §Consequences).
    base = profile_for_chart(chart)
    use_pass_key = base.apertures_per_chart is not None

    passes = aperture_passes_for_view(chart, image_path)
    results: list[PassResult] = []
    for aperture, profile in passes:
        pass_key = aperture if use_pass_key else None
        results.append(
            _run_one_pass(
                image_path,
                profile,
                plot_box,
                chart.image_height_mm,
                pass_key,
            )
        )
    return results


def triage_chart(chart: ReferenceChart) -> ChartVerdict:
    """Run the full pipeline on one single-aperture reference chart.

    Single-aperture wrapper that preserves the original verdict-only
    API for callers (e.g. test_triage's reference-set integration tests).
    Raises on multi-aperture charts — use
    ``triage_chart_all_apertures()`` for those.
    """
    results = _run_pipeline(chart)
    if len(results) != 1:
        raise ValueError(
            f"{chart.slug}: triage_chart() is single-aperture only; got "
            f"{len(results)} passes. Use triage_chart_all_apertures()."
        )
    return results[0].verdict


def triage_chart_all_apertures(chart: ReferenceChart) -> list[ChartVerdict]:
    """Run the full pipeline on a chart and return one verdict per pass (ADR-052)."""
    return [r.verdict for r in _run_pipeline(chart)]


def _format_metric(value: float | None) -> str:
    return f"{value:.3f}" if value is not None else "  -  "


def _format_verdict(v: ChartVerdict) -> str:
    iou = _format_metric(v.render_match_iou)
    prec = _format_metric(v.render_match_precision)
    pass_label = f" [{v.pass_key}]" if v.pass_key else ""
    return (
        f"  {v.verdict:<4}{pass_label}  IoU {iou}  precision {prec}  "
        f"priors {len(v.prior_violations):2d}"
    )


def main() -> None:
    # ADR-052: lifted the `c.ground_truth` filter so the auto-confidence
    # gate covers the full cohort, not just the calibration subset.
    # Multi-aperture charts (ADR-044) emit one verdict per aperture.
    runnable = [c for c in REFERENCE_CHARTS if c.plot_box]
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
        print(f"## {chart.slug} ({chart.style_family})")
        for result in _run_pipeline(chart):
            verdict = result.verdict
            verdicts.append(verdict)
            print(_format_verdict(verdict))
            if verdict.reasons:
                for reason in verdict.reasons:
                    print(f"    - {reason.value}")
            if verdict.verdict == "LOW":
                # ADR-038 §"Workflow": review file emitted only for LOW
                # passes — HIGH passes auto-commit. Per-aperture stems
                # (ADR-044, ADR-052) so multiple passes don't overwrite
                # each other's overlay PNG and HTML. The per-aperture
                # SVG emit (ADR-044 S135) writes one SVG per aperture
                # with the `-{aperture}` suffix on the chart stem; the
                # review HTML references it by basename so the suffix
                # must match.
                if verdict.pass_key:
                    stem_override = f"{result.image_path.stem}-{verdict.pass_key}"
                    svg_path = result.image_path.with_name(
                        f"{stem_override}.svg"
                    )
                else:
                    stem_override = None
                    svg_path = result.image_path.with_suffix(".svg")
                outputs = write_review(
                    result.extracted,
                    result.image_path,
                    plot_box=result.plot_box,
                    image_height_mm=chart.image_height_mm,
                    svg_path=svg_path,
                    stem_override=stem_override,
                )
                reviews_written.append(outputs.html_path)
                rel_html = outputs.html_path.relative_to(REPO_ROOT)
                print(f"    review: {rel_html}")
        print()

    high = sum(1 for v in verdicts if v.verdict == "HIGH")
    low = sum(1 for v in verdicts if v.verdict == "LOW")
    print("## Aggregate")
    print(f"  charts triaged:  {len(runnable)}")
    print(f"  verdicts (chart x pass): {len(verdicts)}")
    print(f"  HIGH:            {high}")
    print(f"  LOW:             {low}")
    print(f"  reviews written: {len(reviews_written)}  (one per LOW pass)")
    print()
    print("  Expected separation per scoring.md + plausibility.md:")
    print("    sigma-56mm           LOW  (precision_below_threshold)")
    print("    samyang-85mm MAX     HIGH (both signals clear)")
    print("    samyang-300mm reflex LOW  (prior_failed_not_suspiciously_flat)")


if __name__ == "__main__":
    main()
