"""Per-lens digitization log writer.

For each lens (one or more reference charts of the same lens), emit
a markdown log under `docs/optical-specs/<lens-slug>/digitization-log.md`
with:

- The per-panel readings grid (frac, GT, EX, Δ per field)
- Per-field summary stats (paired, median |Δ|, p95 |Δ|)
- Center value summary (10 lp/mm and 30 lp/mm at frac 0.0)
- Edge value summary (frac 0.9 / 1.0)
- Sister-fallback counters per field
- Cross-chart shape metrics (peak position, half-falloff position)

Usage::

    cd tools
    py -m mtfdigitizer.log              # write logs for every Tokina lens
    py -m mtfdigitizer.log --all        # write logs for every lens with a chart
"""

from __future__ import annotations

import argparse
import re
import statistics
from pathlib import Path

from .family_profile import profile_for_chart
from .pipeline import PlotBox, extract_chart
from .pipeline.sampling import SAMPLE_FRACTIONS
from .pipeline.types import ExtractedChart
from .referenceset.charts import REFERENCE_CHARTS, PlotBoxCoords, ReferenceChart


REPO_ROOT = Path(__file__).resolve().parents[2]


# Strip "-at-Nmm" trailing panel marker so multi-panel lenses (Tokina 11-18)
# group under one lens slug.
_AT_FOCAL_RE = re.compile(r"-at-\d+mm$")


def _lens_slug_from_chart(chart_slug: str) -> str:
    """Map a chart slug to its parent lens slug.

    Single-panel charts return their own slug (no `-at-Nmm` suffix);
    multi-panel charts collapse to the shared lens slug.
    """
    return _AT_FOCAL_RE.sub("", chart_slug)


def _to_plotbox(coords: PlotBoxCoords) -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
    )


def _panel_focal_label(chart_slug: str) -> str | None:
    """If a chart slug has `-at-Nmm`, return `Nmm`; else None."""
    m = re.search(r"-at-(\d+mm)$", chart_slug)
    return m.group(1) if m else None


def _format_value(v: float | None) -> str:
    return f"{v:.2f}" if v is not None else "—"


def _format_delta(ex: float | None, gt: float | None) -> str:
    if ex is None or gt is None:
        return "—"
    return f"{abs(ex - gt):.3f}"


def _half_falloff_fraction(
    values: tuple[float | None, ...], peak: float | None
) -> float | None:
    """Fraction at which a curve first drops below peak/2 (the half-falloff).

    Walks left to right; returns the first frac where the value <= peak/2,
    or None when the curve never falls that low (or has no peak).
    """
    if peak is None or peak <= 0:
        return None
    threshold = peak / 2
    for frac, v in zip(SAMPLE_FRACTIONS, values):
        if v is not None and v <= threshold:
            return frac
    return None


def _peak_fraction(values: tuple[float | None, ...]) -> tuple[float, float] | None:
    """The (fraction, value) at which a curve peaks. None if all values are None."""
    paired = [(f, v) for f, v in zip(SAMPLE_FRACTIONS, values) if v is not None]
    if not paired:
        return None
    return max(paired, key=lambda fv: fv[1])


def _field_stats(extracted: ExtractedChart, field: str, ground_truth: tuple) -> dict:
    ex_values = tuple(getattr(r, field) for r in extracted.readings)
    deltas = [
        abs(ex - gt)
        for ex, gt in zip(ex_values, ground_truth)
        if ex is not None and gt is not None
    ]
    return {
        "paired": len(deltas),
        "median": statistics.median(deltas) if deltas else None,
        "p95": (
            statistics.quantiles(deltas, n=20)[-1]
            if len(deltas) >= 2
            else (deltas[0] if deltas else None)
        ),
        "fallback": extracted.sister_fallback_count.get(field, 0),
        "ex_values": ex_values,
    }


def _render_readings_grid(extracted: ExtractedChart, ground_truth: dict) -> list[str]:
    """One markdown table per (aperture, field) summary + one wide grid table."""
    lines: list[str] = []
    fields = ("contrast10S", "contrast10M", "resolution30S", "resolution30M")
    for aperture, gt_by_field in ground_truth.items():
        if len(ground_truth) > 1:
            lines.append(f"#### Aperture {aperture}")
            lines.append("")
        # Stats table
        lines.append(
            "| Field          | paired | med \\|Δ\\| | p95 \\|Δ\\| | sister-fill |"
        )
        lines.append(
            "| -------------- | ------ | --------- | --------- | ----------- |"
        )
        for f in fields:
            if f not in gt_by_field:
                continue
            stats = _field_stats(extracted, f, gt_by_field[f])
            med = f"{stats['median']:.3f}" if stats["median"] is not None else "—"
            p95 = f"{stats['p95']:.3f}" if stats["p95"] is not None else "—"
            lines.append(
                f"| {f:<14} | {stats['paired']:>2}/11  | {med:>9} | {p95:>9} | "
                f"{stats['fallback']:>2}/11       |"
            )
        lines.append("")

        # Wide grid: rows = sample fractions, columns = (GT, EX, Δ) per field
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
                ex = getattr(extracted.readings[i], f)
                row.extend(
                    [_format_value(gt), _format_value(ex), _format_delta(ex, gt)]
                )
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")
    return lines


def _render_center_edge_summary(
    extracted: ExtractedChart, ground_truth: dict
) -> list[str]:
    """One block per aperture showing center (frac 0.0) and edge (frac 0.9, 1.0) values."""
    lines: list[str] = []
    fields = ("contrast10S", "contrast10M", "resolution30S", "resolution30M")
    for aperture in ground_truth:
        if len(ground_truth) > 1:
            lines.append(f"#### Aperture {aperture}")
            lines.append("")
        lines.append("| Field          | center (0.0) | edge (0.9) | corner (1.0) |")
        lines.append("| -------------- | ------------ | ---------- | ------------ |")
        for f in fields:
            v0 = getattr(extracted.readings[0], f)
            v9 = getattr(extracted.readings[9], f)
            v10 = getattr(extracted.readings[10], f)
            lines.append(
                f"| {f:<14} | {_format_value(v0):>12} | {_format_value(v9):>10} | "
                f"{_format_value(v10):>12} |"
            )
        lines.append("")
    return lines


def _render_shape_metrics(
    extracted: ExtractedChart, ground_truth: dict
) -> list[str]:
    """Per-field peak position and half-falloff position."""
    lines: list[str] = []
    fields = ("contrast10S", "contrast10M", "resolution30S", "resolution30M")
    for aperture in ground_truth:
        if len(ground_truth) > 1:
            lines.append(f"#### Aperture {aperture}")
            lines.append("")
        lines.append("| Field          | peak frac | peak value | half-falloff frac |")
        lines.append("| -------------- | --------- | ---------- | ----------------- |")
        for f in fields:
            ex_values = tuple(getattr(r, f) for r in extracted.readings)
            peak = _peak_fraction(ex_values)
            half = _half_falloff_fraction(ex_values, peak[1] if peak else None)
            peak_frac = f"{peak[0]:.1f}" if peak else "—"
            peak_val = f"{peak[1]:.2f}" if peak else "—"
            half_str = f"{half:.1f}" if half is not None else "—"
            lines.append(
                f"| {f:<14} | {peak_frac:>9} | {peak_val:>10} | {half_str:>17} |"
            )
        lines.append("")
    return lines


def _render_lens_log(
    lens_slug: str, panels: list[tuple[ReferenceChart, ExtractedChart]]
) -> str:
    """Build the full digitization-log.md content for one lens."""
    lines: list[str] = []
    lines.append(f"# Digitization log: {lens_slug}")
    lines.append("")
    if len(panels) > 1:
        lines.append(
            f"This lens has {len(panels)} reference panels (different focal lengths "
            "of the same zoom). One section per panel."
        )
    else:
        lines.append("This lens has one reference panel.")
    lines.append("")
    lines.append(
        "See `tools/mtfdigitizer/README.md` for the dispatch algorithm "
        "(per-hue Viterbi shortest path + raw-centroid snap + sister "
        "fallback + center symmetry)."
    )
    lines.append("")

    for chart, extracted in panels:
        focal = _panel_focal_label(chart.slug)
        if focal:
            lines.append(f"## Panel at {focal}")
        else:
            lines.append("## Panel")
        lines.append("")
        lines.append(f"- **Chart:** `{chart.chart_path}`")
        lines.append(f"- **Style family:** `{chart.style_family}`")
        lines.append(f"- **Dispatch profile:** `{extracted.profile_name}`")
        lines.append(
            f"- **Plot box (pixels):** x=[{chart.plot_box.x_left}, "
            f"{chart.plot_box.x_right}], y=[{chart.plot_box.y_top}, "
            f"{chart.plot_box.y_bottom}]"
        )
        lines.append(f"- **Image height:** {chart.image_height_mm} mm")
        lines.append("")

        lines.append("### Sample grid (GT vs extracted)")
        lines.append("")
        lines.extend(_render_readings_grid(extracted, chart.ground_truth))

        lines.append("### Center / edge summary")
        lines.append("")
        lines.extend(_render_center_edge_summary(extracted, chart.ground_truth))

        lines.append("### Shape metrics")
        lines.append("")
        lines.extend(_render_shape_metrics(extracted, chart.ground_truth))

    return "\n".join(lines)


def _extract_panel(chart: ReferenceChart) -> ExtractedChart:
    profile = profile_for_chart(chart)
    image_path = REPO_ROOT / chart.chart_path
    plot_box = _to_plotbox(chart.plot_box)
    return extract_chart(
        image_path, profile, plot_box, image_height_mm=chart.image_height_mm
    )


def _group_by_lens(
    charts: list[ReferenceChart],
) -> dict[str, list[ReferenceChart]]:
    out: dict[str, list[ReferenceChart]] = {}
    for chart in charts:
        slug = _lens_slug_from_chart(chart.slug)
        out.setdefault(slug, []).append(chart)
    return out


def write_logs(
    charts: list[ReferenceChart], target_dir: Path | None = None
) -> list[Path]:
    """Extract each chart and write one digitization-log.md per lens.

    Returns the list of written paths.
    """
    groups = _group_by_lens(charts)
    written: list[Path] = []
    for lens_slug, lens_charts in groups.items():
        panels = [(c, _extract_panel(c)) for c in lens_charts]
        out_dir = (
            target_dir / lens_slug
            if target_dir
            else REPO_ROOT / "docs" / "optical-specs" / lens_slug
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "digitization-log.md"
        path.write_text(_render_lens_log(lens_slug, panels), encoding="utf-8")
        written.append(path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--all",
        action="store_true",
        help="Write logs for every lens with a runnable chart "
        "(default: Tokina only).",
    )
    args = parser.parse_args()

    runnable = [c for c in REFERENCE_CHARTS if c.plot_box and c.ground_truth]
    if not args.all:
        runnable = [c for c in runnable if c.slug.startswith("tokina-")]

    if not runnable:
        print("No matching reference charts.")
        return

    print(
        f"Writing digitization logs for {len(_group_by_lens(runnable))} "
        f"lens(es) from {len(runnable)} chart(s)..."
    )
    written = write_logs(runnable)
    for path in written:
        rel = path.relative_to(REPO_ROOT)
        print(f"  wrote {rel}")


if __name__ == "__main__":
    main()
