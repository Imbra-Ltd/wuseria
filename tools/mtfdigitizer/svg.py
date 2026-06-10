"""MTF SVG emitter (#971, ADR-038 §5).

Renders an ``ExtractedChart`` (the pipeline's 11-point readings) into a
standalone SVG document, used as:

1. **Provenance** — committed alongside the source PNG in
   ``docs/optical-specs/<slug>/`` as a record of what the extractor
   read from the chart.
2. **Review-file right panel** — the "regenerated from readings" pane
   in the upcoming 3-panel review file, paired against the original
   raster and the overlay (ADR-038 §4).

Lens-page display is **not** this module's job — ``src/components/
static/MtfChart.astro`` already renders MTF SVGs at build time from the
same ``MtfData`` shape. This module produces a Python-side artifact
with the same visual conventions (plot box, line styles, palette) so the
review file's right panel previews what the lens page will look like,
without claiming byte-identity with the Astro component (their HTML
shapes differ — scoped class hashes, whitespace, attribute order — and
chasing byte-identity for a swap we may never want would be expensive).

The single source of truth is the readings. Both renderers consume them;
neither owns them.

Usage::

    cd tools
    py -m mtfdigitizer.svg              # emit all runnable reference charts
    py -m mtfdigitizer.svg --check      # verify outputs without writing

Output paths: ``docs/optical-specs/<slug>/<chart-stem>.svg`` — one SVG
per source PNG in the runnable reference set.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .aperture_passes import aperture_passes_for_view
from .pipeline import ExtractedChart, SampledReading, extract_chart
from .pipeline.dispatch import parse_field_name
from .pipeline.rendermatch import fields_in
from .pipeline.types import PlotBox
from .referenceset import REFERENCE_CHARTS
from .referenceset.charts import PlotBoxCoords, ReferenceChart


REPO_ROOT = Path(__file__).resolve().parents[2]


# --- visual conventions ---------------------------------------------
#
# Mirrors `src/components/static/MtfChart.astro`. Same viewBox, same
# padding ratios, same line semantics (solid S / dashed M / accent for
# 10 lp/mm, blue for 30 lp/mm). Palette is hard-coded here rather than
# pulled from CSS custom properties: this SVG is standalone, no theme
# context applies.

_VIEWBOX_W = 320
# The Astro component renders the legend as a sibling <div> below the
# SVG. The provenance SVG is standalone — no sibling DOM — so its
# legend has to live inside the viewBox. We extend the canvas by
# `_LEGEND_STRIP_H` past the Astro component's 200px height to give the
# legend its own row, keeping the data area visually identical.
_LEGEND_STRIP_H = 18
_VIEWBOX_H = 200 + _LEGEND_STRIP_H
_PAD_TOP = 12
_PAD_RIGHT = 16
_PAD_BOTTOM = 28 + _LEGEND_STRIP_H
_PAD_LEFT = 36

_PLOT_W = _VIEWBOX_W - _PAD_LEFT - _PAD_RIGHT
# The plot area sizes off the unextended 200px height so the gridlines
# and x-axis labels land at the same coordinates as MtfChart.astro.
_PLOT_H = 200 - _PAD_TOP - (_PAD_BOTTOM - _LEGEND_STRIP_H)

# Y-axis gridlines, 0.0 to 1.0 in 0.2 steps (6 lines).
_Y_TICKS: tuple[float, ...] = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)

# Palette. The Astro component uses `var(--color-accent)` (warm gold) +
# `#6b9bd2` (cool blue). The provenance SVG is rendered against a light
# review panel and needs to read on white paper too, so we pick concrete
# colors with sufficient contrast on both. The frequency-color map
# mirrors `src/components/static/MtfChart.astro` (ADR-042); unknown
# frequencies fall back to a muted neutral so a new brand never silently
# renders invisible.
_FREQUENCY_COLOR: dict[int, str] = {
    10: "#c89b3c",  # warm gold, matches site accent
    15: "#d4a14a",
    20: "#5fa86f",
    30: "#6b9bd2",  # cool blue
    40: "#5d7bb5",
    45: "#5d7bb5",
}
_COLOR_NEUTRAL = "#888888"
_COLOR_GRID = "#d8d8d8"
_COLOR_AXIS_TEXT = "#666666"


def _color_for_freq(freq: int) -> str:
    return _FREQUENCY_COLOR.get(freq, _COLOR_NEUTRAL)


def _x_pixel(position_mm: float, max_mm: float) -> float:
    """Map a position in mm to its x pixel inside the SVG viewBox."""
    if max_mm <= 0:
        raise ValueError(f"max_mm must be positive, got {max_mm}")
    return _PAD_LEFT + (position_mm / max_mm) * _PLOT_W


def _y_pixel(mtf: float) -> float:
    """Map an MTF value (0..1) to its y pixel inside the SVG viewBox."""
    return _PAD_TOP + (1.0 - mtf) * _PLOT_H


def _polyline_segments(
    readings: tuple[SampledReading, ...], field: str, max_mm: float
) -> list[str]:
    """Return one SVG ``points=`` string per continuous run of non-None values.

    A ``None`` at any position breaks the polyline — segments draw only
    between adjacent positions where both endpoints carry a value (the
    B2 contract; matches ``rasterize_readings`` in
    ``pipeline/rendermatch.py``). A single-point run is dropped: a
    polyline with one vertex is invisible and adds noise to the DOM.
    """
    segments: list[list[str]] = []
    current: list[str] = []
    for reading in readings:
        value = reading.samples.get(field)
        if value is None:
            if len(current) >= 2:
                segments.append(current)
            current = []
            continue
        x = _x_pixel(reading.position_mm, max_mm)
        y = _y_pixel(value)
        current.append(f"{x:.1f},{y:.1f}")
    if len(current) >= 2:
        segments.append(current)
    return [" ".join(s) for s in segments]


def _field_style(field: str) -> tuple[str, str]:
    """Return (stroke_color, dash_array_or_empty) for one synthetic field.

    Field name follows the `freq{N}{S|M}` convention (ADR-042). Solid
    stroke = sagittal, `4 2` dash = meridional. Color comes from the
    frequency table; unknown frequencies fall back to the neutral.
    """
    freq, sm = parse_field_name(field)
    color = _color_for_freq(freq)
    dash = "" if sm == "S" else "4 2"
    return color, dash


def _format_position_label(position_mm: float) -> str:
    """Center reads as 'C'; positive positions print as plain numbers."""
    if position_mm == 0:
        return "C"
    if position_mm == int(position_mm):
        return str(int(position_mm))
    return f"{position_mm:.1f}"


def render_svg(chart: ExtractedChart) -> str:
    """Render an ``ExtractedChart`` to a standalone SVG document.

    The SVG carries its own ``<style>`` block so it stands alone in a
    file viewer or a review-file composition — no external CSS, no theme
    context. The 11 sample points appear as polyline vertices and as
    dots, matching ``MtfChart.astro``'s convention.

    Visual choices:

    - Plot box (320x200, pad 12/16/28/36) mirrors the Astro component
      so a side-by-side review file reads as the same chart.
    - 10 lp/mm uses warm gold; 30 lp/mm uses cool blue. S is solid, M
      dashed. The chart's source PNG conventions are not mimicked — the
      provenance SVG always uses the digitizer's own palette so a
      maintainer scanning many review files reads the same color for
      "10S" regardless of the source brand.
    - ``None`` readings break the polyline at that vertex (B2 contract).
    """
    max_mm = chart.image_height_mm
    body: list[str] = []

    body.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {_VIEWBOX_W} {_VIEWBOX_H}" '
        f'role="img" aria-label="MTF chart, generated from readings">'
    )
    body.append(_render_style_block())
    body.extend(_render_grid())
    body.extend(_render_y_axis_labels())
    body.extend(_render_x_axis_labels(chart.readings))
    body.append(_render_x_axis_title())
    body.extend(_render_curves(chart.readings, max_mm))
    body.extend(_render_dots(chart.readings, max_mm))
    body.extend(_render_legend(chart.readings))
    body.append("</svg>")
    return "\n".join(body) + "\n"


def _render_style_block() -> str:
    # Per-frequency stroke colors are delivered via inline `style=`
    # attributes on each polyline/circle (set in `_render_curves` and
    # `_render_dots`) since the frequency set is per-chart after ADR-042
    # and not knowable at style-block render time. The class-level rules
    # below carry shared geometry (fill, dash, stroke-width) only.
    return (
        "<style>"
        f".grid-line {{ stroke: {_COLOR_GRID}; stroke-width: 0.5; }}"
        f".axis-label {{ font-size: 7px; fill: {_COLOR_AXIS_TEXT}; "
        f"font-family: ui-monospace, monospace; }}"
        ".axis-y { text-anchor: end; }"
        ".axis-x { text-anchor: middle; }"
        f".axis-title {{ font-size: 7px; fill: {_COLOR_AXIS_TEXT}; "
        f"text-anchor: middle; }}"
        ".curve { fill: none; stroke-width: 1.5; }"
        ".curve-m { stroke-dasharray: 4 2; }"
        ".dot { fill: white; stroke-width: 1; }"
        ".legend-text { font-size: 7px; fill: " + _COLOR_AXIS_TEXT
        + "; font-family: ui-monospace, monospace; }"
        "</style>"
    )


def _render_grid() -> list[str]:
    lines: list[str] = []
    x1 = _PAD_LEFT
    x2 = _VIEWBOX_W - _PAD_RIGHT
    for tick in _Y_TICKS:
        y = _y_pixel(tick)
        lines.append(
            f'<line class="grid-line" x1="{x1}" y1="{y:.1f}" '
            f'x2="{x2}" y2="{y:.1f}"/>'
        )
    return lines


def _render_y_axis_labels() -> list[str]:
    x = _PAD_LEFT - 4
    return [
        f'<text class="axis-label axis-y" x="{x}" y="{_y_pixel(t) + 3:.1f}">'
        f'{t:.1f}</text>'
        for t in _Y_TICKS
    ]


def _render_x_axis_labels(readings: tuple[SampledReading, ...]) -> list[str]:
    if not readings:
        return []
    max_mm = readings[-1].position_mm
    y = _VIEWBOX_H - _PAD_BOTTOM + 14
    return [
        f'<text class="axis-label axis-x" x="{_x_pixel(r.position_mm, max_mm):.1f}" '
        f'y="{y}">{_format_position_label(r.position_mm)}</text>'
        for r in readings
    ]


def _render_x_axis_title() -> str:
    x = _PAD_LEFT + _PLOT_W / 2
    # Sits at the same coordinate as MtfChart.astro (y=198) regardless
    # of the legend strip, so the data area is visually identical.
    y = 198
    return (
        f'<text class="axis-title" x="{x:.1f}" y="{y}">'
        f"Image height (mm)</text>"
    )


def _render_curves(
    readings: tuple[SampledReading, ...], max_mm: float
) -> list[str]:
    elements: list[str] = []
    for field in fields_in(readings):
        color, dash = _field_style(field)
        css_class = _curve_css_class(field)
        for points in _polyline_segments(readings, field, max_mm):
            extra = f' stroke-dasharray="{dash}"' if dash else ""
            elements.append(
                f'<polyline class="{css_class}" style="stroke:{color}" '
                f'points="{points}"{extra}/>'
            )
    return elements


def _curve_css_class(field: str) -> str:
    """`curve curve-{freq}` for S, `curve curve-{freq} curve-m` for M.

    The frequency suffix is a stable identifier even when CSS does not
    declare a per-frequency rule — color is delivered via inline style
    after ADR-042 made the frequency set unbounded.
    """
    freq, sm = parse_field_name(field)
    base = f"curve curve-{freq}"
    return f"{base} curve-m" if sm == "M" else base


def _render_dots(
    readings: tuple[SampledReading, ...], max_mm: float
) -> list[str]:
    elements: list[str] = []
    for field in fields_in(readings):
        freq, _sm = parse_field_name(field)
        color = _color_for_freq(freq)
        css_class = f"dot dot-{freq}"
        for reading in readings:
            value = reading.samples.get(field)
            if value is None:
                continue
            cx = _x_pixel(reading.position_mm, max_mm)
            cy = _y_pixel(value)
            elements.append(
                f'<circle class="{css_class}" style="stroke:{color}" '
                f'cx="{cx:.1f}" cy="{cy:.1f}" r="2"/>'
            )
    return elements


def _render_legend(readings: tuple[SampledReading, ...]) -> list[str]:
    # Legend lives in its own strip below the x-axis title (the Astro
    # component renders it as a sibling `<div>`; the provenance file is
    # standalone, so the legend has to live inside the viewBox without
    # crowding the data area). One pair per frequency the chart
    # publishes (ADR-042), sorted low → high.
    items: list[tuple[str, str, bool]] = []
    seen_freqs: set[int] = set()
    for field in fields_in(readings):
        freq, _sm = parse_field_name(field)
        seen_freqs.add(freq)
    for freq in sorted(seen_freqs):
        color = _color_for_freq(freq)
        items.append((f"{freq} lp/mm S", color, False))
        items.append((f"{freq} lp/mm M", color, True))

    elements: list[str] = []
    x = _PAD_LEFT
    y = _VIEWBOX_H - 6  # baseline near the bottom of the legend strip
    swatch_w = 12
    gap_swatch_text = 3
    item_gap = 56
    for i, (label, color, dashed) in enumerate(items):
        cx = x + i * item_gap
        dash_attr = ' stroke-dasharray="3 2"' if dashed else ""
        elements.append(
            f'<line x1="{cx}" y1="{y - 3}" x2="{cx + swatch_w}" y2="{y - 3}" '
            f'stroke="{color}" stroke-width="1.5"{dash_attr}/>'
        )
        elements.append(
            f'<text class="legend-text" x="{cx + swatch_w + gap_swatch_text}" '
            f'y="{y}">{label}</text>'
        )
    return elements


# --- CLI -------------------------------------------------------------


def _to_plotbox(coords: PlotBoxCoords) -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
    )


def _emit_chart(chart: ReferenceChart, *, check_only: bool) -> list[Path]:
    """Extract one reference chart and write its SVG(s). Returns the output paths.

    Multi-aperture charts (ADR-044) fan out into one SVG per aperture,
    suffixed `<stem>-<aperture>.svg` (matching the production extractor's
    naming). Single-aperture charts produce one SVG at `<stem>.svg`.
    """
    assert chart.plot_box is not None
    image_path = REPO_ROOT / chart.chart_path
    plot_box = _to_plotbox(chart.plot_box)
    passes = aperture_passes_for_view(chart, image_path)
    multi = len(passes) > 1
    out_paths: list[Path] = []
    for aperture, profile in passes:
        extracted = extract_chart(
            image_path, profile, plot_box,
            image_height_mm=chart.image_height_mm,
        )
        svg = render_svg(extracted)
        if multi:
            out_path = image_path.with_name(f"{image_path.stem}-{aperture}.svg")
        else:
            out_path = image_path.with_suffix(".svg")
        if not check_only:
            out_path.write_text(svg, encoding="utf-8")
        out_paths.append(out_path)
    return out_paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="Render to memory only, don't write files. Used in CI/tests.",
    )
    args = parser.parse_args()

    runnable = [c for c in REFERENCE_CHARTS if c.plot_box and c.ground_truth]
    print(f"Emitting SVG for {len(runnable)} of {len(REFERENCE_CHARTS)} reference charts.")
    if args.check:
        print("(--check: rendering only, no files written)")
    print()

    for chart in runnable:
        out_paths = _emit_chart(chart, check_only=args.check)
        action = "would write" if args.check else "wrote"
        for out_path in out_paths:
            relative = out_path.relative_to(REPO_ROOT)
            print(f"  {chart.slug:<40}  {action}  {relative}")


if __name__ == "__main__":
    main()
