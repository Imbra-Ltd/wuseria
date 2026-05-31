"""Reference-set plausibility-priors runner (#966, ADR-038 §"Confidence signal").

Runs `extract_chart()` against every reference chart with both ground
truth and a plot box, then reports which physical-plausibility priors
fire — the second of the two confidence signals ADR-038 requires.

Sister runner to `calibrate.py` (offset distribution against ground truth)
and `scorer.py` (round-trip render-match IoU). This one is silent on both;
it asks only: do the extracted readings violate hard optical facts?

Usage::

    cd tools
    py -m mtfdigitizer.plausibility

Output: a per-chart table on stdout (passes/fails per prior) + an
aggregate summary. No file writes — findings live in
`referenceset/plausibility.md`, which the maintainer updates after a run.
"""

from __future__ import annotations

from pathlib import Path

from .family_profile import profile_for
from .pipeline import PlotBox, extract_chart
from .priors import PriorViolation, check_all
from .referenceset.charts import REFERENCE_CHARTS, PlotBoxCoords, ReferenceChart


REPO_ROOT = Path(__file__).resolve().parents[2]


def _to_plotbox(coords: PlotBoxCoords) -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
    )


def _check_one(chart: ReferenceChart) -> list[PriorViolation]:
    """Extract one reference chart and run all priors over the readings."""
    assert chart.plot_box is not None
    profile = profile_for(chart.style_family, chart.slug)
    image_path = REPO_ROOT / chart.chart_path
    plot_box = _to_plotbox(chart.plot_box)
    extracted = extract_chart(
        image_path, profile, plot_box, image_height_mm=chart.image_height_mm
    )
    return check_all(extracted.readings)


def _format_violation(v: PriorViolation) -> str:
    pos = f"pos {v.position_index:2d}" if v.position_index is not None else "whole "
    return f"  [{v.prior_name:<24}] {v.field:<14} {pos}  {v.detail}"


def main() -> None:
    runnable = [c for c in REFERENCE_CHARTS if c.plot_box and c.ground_truth]
    print(
        f"Checking plausibility priors on {len(runnable)} of {len(REFERENCE_CHARTS)} "
        f"reference charts."
    )
    print()

    total_violations = 0
    charts_with_violations = 0
    for chart in runnable:
        violations = _check_one(chart)
        print(f"## {chart.slug} ({chart.style_family})")
        if not violations:
            print("  PASS — no priors fired")
        else:
            charts_with_violations += 1
            total_violations += len(violations)
            # Group by prior name for readability.
            by_prior: dict[str, list[PriorViolation]] = {}
            for v in violations:
                by_prior.setdefault(v.prior_name, []).append(v)
            for prior_name in sorted(by_prior):
                hits = by_prior[prior_name]
                fields = sorted({v.field for v in hits})
                print(
                    f"  FAIL {prior_name:<24} ({len(hits)} hits on {', '.join(fields)})"
                )
                for v in hits:
                    print(_format_violation(v))
        print()

    print("## Aggregate")
    print(f"  charts checked:           {len(runnable)}")
    print(f"  charts with violations:   {charts_with_violations}")
    print(f"  total violations:         {total_violations}")
    print()
    print("  Expected separation per REFERENCE_SET.md:")
    print("    sigma-56mm           — all priors pass")
    print("    samyang-85mm MAX     — all priors pass")
    print("    samyang-300mm reflex — flatness prior fires")


if __name__ == "__main__":
    main()
