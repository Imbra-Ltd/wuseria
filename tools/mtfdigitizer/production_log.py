"""Per-lens production digitization log writer (ADR-041 Tier 2).

Sister to `log.py` for the production tier: same file name
(`digitization-log.md`), same banner / `--check` semantics from
ADR-040, no EYE column. Where `log.py` compares the extractor against
maintainer eye-reads, this log records what the extractor produced
plus the two confidence signals the gate (`triage.py`) consumed to
accept it.

Emitted sections per panel:

- Chart metadata (path, style family, dispatch profile, plot box, image height)
- Sample grid (per-field tables + sparklines, EX-only)
- Center / edge summary
- Shape metrics (peak position, half-falloff position)
- Confidence signals (render-match precision + IoU, plausibility-prior outcomes)
- Gate verdict (HIGH/LOW + reasons)

The renderer is a pure function over `ExtractedChart` + `ChartVerdict`;
the runner (`extract.py`) is responsible for orchestrating the
extract → score → priors → triage pipeline and calling this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .pipeline.rendermatch import fields_in
from .pipeline.sampling import SAMPLE_FRACTIONS
from .pipeline.types import ExtractedChart
from .triage import (
    IOU_THRESHOLD,
    PRECISION_THRESHOLD,
    ChartVerdict,
)


REPO_ROOT = Path(__file__).resolve().parents[2]

_SPARK_CHARS: tuple[str, ...] = ("▁", "▂", "▃", "▄", "▅", "▆", "▇", "█")


@dataclass(frozen=True)
class ProductionPanel:
    """One panel's inputs to the production log renderer.

    Multi-panel lenses come from two shapes today: Fujifilm
    per-frequency rasters (one panel per .png file in the lens dir),
    and Samyang stacked-aperture panels (two panels in one .png file,
    one ChartView per panel — ADR-063). ``aperture`` distinguishes the
    panels in the rendered heading when more than one is present.
    """

    chart_slug: str
    chart_path: str
    style_family: str
    plot_box: tuple[int, int, int, int]  # x_left, x_right, y_top, y_bottom
    image_height_mm: float
    extracted: ExtractedChart
    verdict: ChartVerdict
    aperture: str = ""


def _spark(values: tuple[float | None, ...]) -> str:
    """Render a curve as a row of Unicode block characters."""
    out: list[str] = []
    n = len(_SPARK_CHARS)
    for v in values:
        if v is None:
            out.append("·")
        else:
            clamped = max(0.0, min(1.0, v))
            idx = min(n - 1, int(round(clamped * (n - 1))))
            out.append(_SPARK_CHARS[idx])
    return "".join(out)


def _format_value(v: float | None) -> str:
    return f"{v:.2f}" if v is not None else "—"


def _peak_fraction(
    values: tuple[float | None, ...],
) -> tuple[float, float] | None:
    paired = [(f, v) for f, v in zip(SAMPLE_FRACTIONS, values) if v is not None]
    if not paired:
        return None
    return max(paired, key=lambda fv: fv[1])


def _half_falloff_fraction(
    values: tuple[float | None, ...], peak: float | None
) -> float | None:
    if peak is None or peak <= 0:
        return None
    threshold = peak / 2
    for frac, v in zip(SAMPLE_FRACTIONS, values):
        if v is not None and v <= threshold:
            return frac
    return None


def _render_sample_grid(extracted: ExtractedChart) -> list[str]:
    """Per-field stats table, sparkline block, and per-field grids."""
    lines: list[str] = []
    fields = fields_in(extracted.readings)

    # Stats: paired count, sister-fill, optional center-anchor — no Δ
    # since no GT. The center-anchor column is added only when at
    # least one field used it (#1267), keeping clean logs visually
    # unchanged.
    show_anchor = any(
        extracted.center_anchor_count.get(f, 0) for f in fields
    )
    if show_anchor:
        lines.append(
            "| Field          | non-null | sister-fill | center-anchor |"
        )
        lines.append(
            "| -------------- | -------- | ----------- | ------------- |"
        )
    else:
        lines.append("| Field          | non-null | sister-fill |")
        lines.append("| -------------- | -------- | ----------- |")
    for f in fields:
        ex_values = tuple(r.samples.get(f) for r in extracted.readings)
        non_null = sum(1 for v in ex_values if v is not None)
        fallback = extracted.sister_fallback_count.get(f, 0)
        if show_anchor:
            anchor = extracted.center_anchor_count.get(f, 0)
            lines.append(
                f"| {f:<14} | {non_null:>2}/11    | {fallback:>2}/11       "
                f"| {anchor:>2}/11         |"
            )
        else:
            lines.append(
                f"| {f:<14} | {non_null:>2}/11    | {fallback:>2}/11       |"
            )
    lines.append("")

    # Sparklines.
    lines.append("```")
    for f in fields:
        ex_values = tuple(r.samples.get(f) for r in extracted.readings)
        endpoints = (
            f"{ex_values[0]:.2f}" if ex_values[0] is not None else " — ",
            f"{ex_values[-1]:.2f}" if ex_values[-1] is not None else " — ",
        )
        lines.append(
            f"  EX   {f:<14} {_spark(ex_values)}  "
            f"({endpoints[0]} → {endpoints[1]})"
        )
    lines.append("```")
    lines.append("")

    # Per-field tables: rows = sample fractions, columns = frac, EX.
    for f in fields:
        lines.append(f"**{f}**")
        lines.append("")
        lines.append("| frac | EX |")
        lines.append("| ---- | --- |")
        for i, frac in enumerate(SAMPLE_FRACTIONS):
            ex = extracted.readings[i].samples.get(f)
            lines.append(f"| {frac:.1f} | {_format_value(ex)} |")
        lines.append("")
    return lines


def _render_center_edge(extracted: ExtractedChart) -> list[str]:
    lines: list[str] = []
    lines.append("| Field          | center (0.0) | edge (0.9) | corner (1.0) |")
    lines.append("| -------------- | ------------ | ---------- | ------------ |")
    for f in fields_in(extracted.readings):
        v0 = extracted.readings[0].samples.get(f)
        v9 = extracted.readings[9].samples.get(f)
        v10 = extracted.readings[10].samples.get(f)
        lines.append(
            f"| {f:<14} | {_format_value(v0):>12} | "
            f"{_format_value(v9):>10} | {_format_value(v10):>12} |"
        )
    lines.append("")
    return lines


def _render_shape_metrics(extracted: ExtractedChart) -> list[str]:
    lines: list[str] = []
    lines.append("| Field          | peak frac | peak value | half-falloff frac |")
    lines.append("| -------------- | --------- | ---------- | ----------------- |")
    for f in fields_in(extracted.readings):
        ex_values = tuple(r.samples.get(f) for r in extracted.readings)
        peak = _peak_fraction(ex_values)
        half = _half_falloff_fraction(ex_values, peak[1] if peak else None)
        peak_frac = f"{peak[0]:.1f}" if peak else "—"
        peak_val = f"{peak[1]:.2f}" if peak else "—"
        half_str = f"{half:.1f}" if half is not None else "—"
        lines.append(
            f"| {f:<14} | {peak_frac:>9} | {peak_val:>10} | "
            f"{half_str:>17} |"
        )
    lines.append("")
    return lines


def _render_confidence_signals(verdict: ChartVerdict) -> list[str]:
    lines: list[str] = []
    precision = verdict.render_match_precision
    iou = verdict.render_match_iou
    p_str = f"{precision:.3f}" if precision is not None else "—"
    i_str = f"{iou:.3f}" if iou is not None else "—"
    lines.append("#### Render-match")
    lines.append("")
    lines.append("| metric    | value | threshold | pass |")
    lines.append("| --------- | ----- | --------- | ---- |")
    p_pass = (
        "yes" if precision is not None and precision >= PRECISION_THRESHOLD else "no"
    )
    i_pass = "yes" if iou is not None and iou >= IOU_THRESHOLD else "no"
    lines.append(f"| precision | {p_str:>5} | {PRECISION_THRESHOLD:>9.2f} | {p_pass:>4} |")
    lines.append(f"| IoU       | {i_str:>5} | {IOU_THRESHOLD:>9.2f} | {i_pass:>4} |")
    lines.append("")

    lines.append("#### Plausibility priors")
    lines.append("")
    if not verdict.prior_violations:
        lines.append("All four priors held (`center_ge_edge`, `low_freq_ge_high`, "
                     "`not_suspiciously_flat`, `in_range`).")
    else:
        lines.append("| prior | field | position | detail |")
        lines.append("| ----- | ----- | -------- | ------ |")
        for v in verdict.prior_violations:
            pos = str(v.position_index) if v.position_index is not None else "—"
            lines.append(
                f"| `{v.prior_name}` | `{v.field}` | {pos} | {v.detail} |"
            )
    lines.append("")
    return lines


def _render_verdict(verdict: ChartVerdict) -> list[str]:
    lines: list[str] = []
    lines.append(f"**Gate verdict:** `{verdict.verdict}`")
    lines.append("")
    if verdict.reasons:
        lines.append("**Reasons:**")
        for r in verdict.reasons:
            lines.append(f"- `{r.value}`")
        lines.append("")
    else:
        lines.append("No reasons — both confidence signals cleared.")
        lines.append("")
    return lines


def render_production_log(lens_slug: str, panels: list[ProductionPanel]) -> str:
    """Build the full production digitization-log.md content for one lens."""
    lines: list[str] = []
    lines.append(
        "<!-- Generated by `py -m mtfdigitizer.extract`. Edit the source data "
        "(referenceset/charts.py, the chart PNG) or the renderer, "
        "not this file. Run `py -m mtfdigitizer.extract --check` to verify "
        "the committed file is up to date. -->"
    )
    lines.append("")
    lines.append(f"# Digitization log: {lens_slug}")
    lines.append("")
    lines.append(
        "Production-tier log per ADR-041. No per-lens ground truth; "
        "acceptance comes from the two confidence signals "
        "(render-match + plausibility priors) plus a maintainer overlay "
        "glance."
    )
    lines.append("")
    any_center_anchor = any(
        any(p.extracted.center_anchor_count.get(f, 0) for f in p.extracted.center_anchor_count)
        for p in panels
    )

    lines.append("**Legend.**")
    lines.append("")
    lines.append("- **EX** — what the extractor computed for the sample point.")
    lines.append("- **sister-fill** — count of samples filled from the sister curve.")
    if any_center_anchor:
        lines.append(
            "- **center-anchor** — count of cells anchored to MTF=1.0 at "
            "frac=0.0 by the B4 physics rule (S=M=1.0 at the optical axis); "
            "fires only when sister fallback could not fill (#1267)."
        )
    lines.append("- **·** in a sparkline — extractor returned None at that point.")
    lines.append("")
    lines.append(
        "See `tools/mtfdigitizer/README.md` for the dispatch algorithm and "
        "[ADR-041](../../decisions/041-production-digitization-no-per-lens-gt.md) "
        "for the production-tier acceptance rationale."
    )
    lines.append("")

    for panel in panels:
        if len(panels) > 1 and panel.aperture:
            lines.append(f"## Panel — {panel.aperture}")
        else:
            lines.append("## Panel")
        lines.append("")
        lines.append(f"- **Chart:** `{panel.chart_path}`")
        lines.append(f"- **Style family:** `{panel.style_family}`")
        lines.append(f"- **Dispatch profile:** `{panel.extracted.profile_name}`")
        x_l, x_r, y_t, y_b = panel.plot_box
        lines.append(
            f"- **Plot box (pixels):** x=[{x_l}, {x_r}], y=[{y_t}, {y_b}]"
        )
        lines.append(f"- **Image height:** {panel.image_height_mm} mm")
        lines.append("")

        lines.append("### Sample grid")
        lines.append("")
        lines.extend(_render_sample_grid(panel.extracted))

        lines.append("### Center / edge summary")
        lines.append("")
        lines.extend(_render_center_edge(panel.extracted))

        lines.append("### Shape metrics")
        lines.append("")
        lines.extend(_render_shape_metrics(panel.extracted))

        lines.append("### Confidence signals")
        lines.append("")
        lines.extend(_render_confidence_signals(panel.verdict))

        lines.append("### Gate")
        lines.append("")
        lines.extend(_render_verdict(panel.verdict))

    return "\n".join(lines)
