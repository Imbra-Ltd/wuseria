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
    py -m mtfdigitizer.calibrate --write-readings

The default invocation prints a per-chart Δ table on stdout and an
aggregate summary. ``--write-readings`` additionally writes one
markdown file per chart under ``referenceset/readings/<slug>.md`` with
the full GT-vs-extracted-vs-Δ grid. Diff those files after an
algorithm change to see exactly what moved.
"""

from __future__ import annotations

import argparse
import statistics
from dataclasses import dataclass
from pathlib import Path

from .family_profile import profile_for_chart
from .pipeline import PlotBox, SampledReading, extract_chart
from .pipeline.sampling import SAMPLE_FRACTIONS
from .referenceset.charts import REFERENCE_CHARTS, PlotBoxCoords, ReferenceChart


REPO_ROOT = Path(__file__).resolve().parents[2]


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
    return reading.samples.get(field)


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


def _calibrate_chart(chart: ReferenceChart):
    """Run extract_chart on one reference chart and return per-field stats.

    The chart must carry both `plot_box` and `ground_truth`; the caller
    filters runnable charts.

    Returns ``(field_deltas, extracted)`` so callers can both summarize
    the Δ distribution and write the per-chart readings log.
    """
    assert chart.plot_box is not None
    assert chart.ground_truth is not None
    profile = profile_for_chart(chart)

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
    return out, result


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


READINGS_DIR = REPO_ROOT / "tools" / "mtfdigitizer" / "referenceset" / "readings"


def _write_readings_log(chart: ReferenceChart, result, field_deltas: list[FieldDelta]) -> Path:
    """Write a markdown grid of GT vs extracted vs Δ for one chart.

    The file lives at ``referenceset/readings/<slug>.md`` and is meant
    to be diffed across algorithm changes — every row is a single
    sample fraction, every column is a curve/field, and the Δ column
    shows the per-position error against the eye-read ground truth.
    """
    READINGS_DIR.mkdir(parents=True, exist_ok=True)
    path = READINGS_DIR / f"{chart.slug}.md"
    fields = ("freq10S", "freq10M", "freq30S", "freq30M")
    lines: list[str] = []
    lines.append(f"# {chart.slug}")
    lines.append("")
    lines.append(f"- **Style family:** `{chart.style_family}`")
    lines.append(f"- **Chart path:** `{chart.chart_path}`")
    lines.append(
        f"- **Plot box:** x=[{chart.plot_box.x_left}, {chart.plot_box.x_right}], "
        f"y=[{chart.plot_box.y_top}, {chart.plot_box.y_bottom}]"
    )
    lines.append(f"- **Image height:** {chart.image_height_mm} mm")
    lines.append("")

    # Per-aperture grids. In practice charts carry one aperture today,
    # but the format generalises.
    for aperture, gt_by_field in chart.ground_truth.items():
        lines.append(f"## Aperture {aperture}")
        lines.append("")
        # Per-field stats table
        lines.append("| Field          | paired | med \\|Δ\\| | p95 \\|Δ\\| |")
        lines.append("| -------------- | ------ | --------- | --------- |")
        for fd in field_deltas:
            if fd.aperture != aperture:
                continue
            med = (
                f"{fd.median_abs_delta:.3f}"
                if fd.median_abs_delta is not None
                else "—"
            )
            p95 = (
                f"{fd.p95_abs_delta:.3f}"
                if fd.p95_abs_delta is not None
                else "—"
            )
            lines.append(
                f"| {fd.field:<14} | {fd.paired_count:>2}/11  | {med:>9} | {p95:>9} |"
            )
        lines.append("")

        # Grid: rows = sample fractions, columns = (GT, EX, Δ) per field
        header_parts = ["frac"]
        for f in fields:
            header_parts.extend([f"{f} GT", f"{f} EX", f"{f} Δ"])
        lines.append("| " + " | ".join(header_parts) + " |")
        lines.append("| " + " | ".join(["---"] * len(header_parts)) + " |")
        for i, frac in enumerate(SAMPLE_FRACTIONS):
            row = [f"{frac:.1f}"]
            for f in fields:
                gt_vals = gt_by_field.get(f, (None,) * 11)
                gt = gt_vals[i] if i < len(gt_vals) else None
                ex = _extracted_value(result.readings[i], f)
                if gt is not None and ex is not None:
                    delta = f"{abs(ex - gt):.3f}"
                else:
                    delta = "—"
                row.extend([
                    f"{gt:.2f}" if gt is not None else "—",
                    f"{ex:.2f}" if ex is not None else "—",
                    delta,
                ])
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--write-readings",
        action="store_true",
        help="Additionally write per-chart markdown grids to "
        "referenceset/readings/<slug>.md",
    )
    args = parser.parse_args()

    runnable = [
        c for c in REFERENCE_CHARTS if c.plot_box and c.ground_truth
    ]
    print(f"Calibrating {len(runnable)} of {len(REFERENCE_CHARTS)} reference charts.")
    print(f"Sample fractions: {SAMPLE_FRACTIONS}")
    if args.write_readings:
        print(f"Writing per-chart readings to {READINGS_DIR.relative_to(REPO_ROOT)}/")
    print()

    all_deltas: list[float] = []
    for chart in runnable:
        print(f"## {chart.slug} ({chart.style_family})")
        field_deltas, result = _calibrate_chart(chart)
        for fd in field_deltas:
            print(_format_field_row(fd))
            all_deltas.extend(fd.deltas)
        if args.write_readings:
            _write_readings_log(chart, result, field_deltas)
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
