"""Reference-set calibration runner (#953, ADR-038 §4).

Runs `extract_chart()` against every reference chart that has both
ground truth and a plot box, and reports the per-position offset (Δ)
distribution against the eye-read values.

This delivers the **offset distribution** half of the calibration
defined in `referenceset/REFERENCE_SET.md` §"What 'calibration against
the set' actually means". The other half — render-match IoU — needs the
confidence signal sub-task to land first; this runner is silent on it.

Usage::

    cd tools
    py -m mtfdigitizer.calibrate

Output: a per-chart Δ table on stdout + an aggregate summary at the end.
No file writes — the findings live in
`referenceset/calibration.md`, which the maintainer updates after a run.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from pathlib import Path

from .pipeline import PlotBox, SampledReading, extract_chart
from .pipeline.sampling import SAMPLE_FRACTIONS
from .profiles import (
    SAMYANG_4COLOR_ALL_SOLID,
    SEVENARTISANS_2COLOR_SAMECOLOR_DASHED,
    SIGMA_2COLOR_SOLID_DASHED,
    TOKINA_2COLOR_FREQUENCY,
    VILTROX_BW_DASHED_F12,
)
from .profiles.types import MtfProfile
from .referenceset.charts import REFERENCE_CHARTS, PlotBoxCoords, ReferenceChart


REPO_ROOT = Path(__file__).resolve().parents[2]


# Style family → declared profile. Five families wired today; the two
# absent ones (`soft-multicurve-promo`, `multifreq-press-kit`) are
# deliberately out-of-band fail-loud cases (the 7Artisans 35mm promo and
# Zeiss Touit press kit) and have no profile.
_PROFILE_BY_STYLE: dict[str, MtfProfile] = {
    "mainstream-2color-solid-dashed": SIGMA_2COLOR_SOLID_DASHED,
    "mainstream-4color-all-solid": SAMYANG_4COLOR_ALL_SOLID,
    "idealized-flat": SAMYANG_4COLOR_ALL_SOLID,  # same 4-color template
    "samecolor-dashed-sm": SEVENARTISANS_2COLOR_SAMECOLOR_DASHED,
    "2color-frequency": TOKINA_2COLOR_FREQUENCY,
    "bw-dashed-promo": VILTROX_BW_DASHED_F12,
}


@dataclass(frozen=True)
class FieldDelta:
    """One field's Δ stats across the 11 sample positions of one chart."""

    chart_slug: str
    aperture: str
    field: str
    deltas: tuple[float, ...]  # |extracted - gt| for positions where both exist
    gt_value_count: int  # positions where ground truth is not None
    extracted_none_count: int  # positions where extractor returned None
    paired_count: int  # positions where both sides had a value

    @property
    def median_abs_delta(self) -> float | None:
        return statistics.median(self.deltas) if self.deltas else None

    @property
    def p95_abs_delta(self) -> float | None:
        if not self.deltas:
            return None
        # statistics.quantiles needs ≥ 2 points; for fewer, return the max.
        if len(self.deltas) < 2:
            return self.deltas[0]
        return statistics.quantiles(self.deltas, n=20)[-1]  # 95th percentile


def _to_plotbox(coords: PlotBoxCoords) -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
    )


def _extracted_value(reading: SampledReading, field: str) -> float | None:
    return getattr(reading, field)


def _compare_field(
    chart: ReferenceChart,
    aperture: str,
    field: str,
    extracted: tuple[SampledReading, ...],
    ground_truth: tuple[float | None, ...],
) -> FieldDelta:
    deltas: list[float] = []
    gt_value_count = 0
    extracted_none_count = 0
    paired_count = 0
    for reading, gt in zip(extracted, ground_truth):
        ext = _extracted_value(reading, field)
        if gt is not None:
            gt_value_count += 1
        if ext is None:
            extracted_none_count += 1
        if gt is not None and ext is not None:
            deltas.append(abs(ext - gt))
            paired_count += 1
    return FieldDelta(
        chart_slug=chart.slug,
        aperture=aperture,
        field=field,
        deltas=tuple(deltas),
        gt_value_count=gt_value_count,
        extracted_none_count=extracted_none_count,
        paired_count=paired_count,
    )


def _calibrate_chart(chart: ReferenceChart) -> list[FieldDelta]:
    """Run extract_chart on one reference chart and return per-field stats.

    The chart must carry both `plot_box` and `ground_truth`; the caller
    filters runnable charts.
    """
    assert chart.plot_box is not None
    assert chart.ground_truth is not None
    profile = _PROFILE_BY_STYLE.get(chart.style_family)
    if profile is None:
        raise ValueError(
            f"{chart.slug}: no declared profile for style_family={chart.style_family!r}"
        )

    image_path = REPO_ROOT / chart.chart_path
    plot_box = _to_plotbox(chart.plot_box)
    result = extract_chart(
        image_path, profile, plot_box, image_height_mm=chart.image_height_mm
    )

    out: list[FieldDelta] = []
    # The ground truth dict may carry multiple apertures; the extractor
    # was given a single plot box (MAX panel today), so only compare the
    # apertures that match. In practice a single key today.
    for aperture, fields in chart.ground_truth.items():
        for field, gt_values in fields.items():
            out.append(_compare_field(chart, aperture, field, result.readings, gt_values))
    return out


def _format_field_row(delta: FieldDelta) -> str:
    med = delta.median_abs_delta
    p95 = delta.p95_abs_delta
    med_s = f"{med:.3f}" if med is not None else "  -  "
    p95_s = f"{p95:.3f}" if p95 is not None else "  -  "
    return (
        f"  {delta.field:<14}  med |d| {med_s}  p95 |d| {p95_s}  "
        f"paired {delta.paired_count:2d}/11  "
        f"ext-None {delta.extracted_none_count:2d}"
    )


def main() -> None:
    runnable = [
        c for c in REFERENCE_CHARTS if c.plot_box and c.ground_truth
    ]
    print(f"Calibrating {len(runnable)} of {len(REFERENCE_CHARTS)} reference charts.")
    print(f"Sample fractions: {SAMPLE_FRACTIONS}")
    print()

    all_deltas: list[float] = []
    for chart in runnable:
        print(f"## {chart.slug} ({chart.style_family})")
        field_deltas = _calibrate_chart(chart)
        for fd in field_deltas:
            print(_format_field_row(fd))
            all_deltas.extend(fd.deltas)
        print()

    if not all_deltas:
        print("No paired comparisons — nothing to summarize.")
        return

    median = statistics.median(all_deltas)
    p95 = (
        statistics.quantiles(all_deltas, n=20)[-1]
        if len(all_deltas) >= 2
        else all_deltas[0]
    )
    print("## Aggregate (all charts, all fields)")
    print(f"  paired comparisons:    {len(all_deltas)}")
    print(f"  median |d|:           {median:.4f}")
    print(f"  p95 |d|:              {p95:.4f}")
    print(f"  max |d|:              {max(all_deltas):.4f}")
    print()
    print("  Reference offset tolerance band proposed by REFERENCE_SET.md: +/-0.05.")
    in_band = sum(1 for d in all_deltas if d <= 0.05)
    print(f"  Comparisons within +/-0.05: {in_band}/{len(all_deltas)} "
          f"({100 * in_band / len(all_deltas):.1f}%)")


if __name__ == "__main__":
    main()
