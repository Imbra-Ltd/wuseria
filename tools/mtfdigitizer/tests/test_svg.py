"""Tests for the MTF SVG emitter (#971).

Acceptance criteria from issue #971:

- Polyline `points=` reflects the readings (shape correctness).
- A `None` reading breaks the polyline (no segment across a gap — B2
  contract, matches `rasterize_readings` in `pipeline/rendermatch.py`).
- All four committed fields (10S/10M/30S/30M) render as separate
  polylines with the right styles (10 solid + dashed, 30 solid + dashed).
- Plot bounds reflect `image_height_mm`: the last sample point lands at
  the right edge of the plot area, the first at the left.
- The output is a self-contained SVG document (no external CSS, parseable
  as XML) so a file viewer can render it standalone.
- Integration: a real `ExtractedChart` from the runnable reference set
  emits an SVG with non-empty polylines for at least one field.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from mtfdigitizer.pipeline import (
    ExtractedChart,
    PlotBox,
    SampledReading,
    extract_chart,
)
from mtfdigitizer.profiles import SIGMA_2COLOR_SOLID_DASHED
from mtfdigitizer.referenceset import REFERENCE_CHARTS
from mtfdigitizer.svg import (
    _PAD_LEFT,
    _PAD_RIGHT,
    _VIEWBOX_H,
    _VIEWBOX_W,
    _polyline_segments,
    render_svg,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


# --- fixtures -------------------------------------------------------


def _readings(values_per_field: dict[str, tuple[float | None, ...]]) -> tuple[SampledReading, ...]:
    """Build 11 SampledReading rows at uniform 0..14mm positions.

    Defaults each field to None when not supplied — exercises the
    independent-field rendering path.
    """
    positions = tuple(round(i * 1.4, 1) for i in range(11))
    blank: tuple[None, ...] = (None,) * 11
    c10s = values_per_field.get("freq10S", blank)
    c10m = values_per_field.get("freq10M", blank)
    r30s = values_per_field.get("freq30S", blank)
    r30m = values_per_field.get("freq30M", blank)
    return tuple(
        SampledReading(
            position_mm=positions[i],
            samples={
                "freq10S": c10s[i],
                "freq10M": c10m[i],
                "freq30S": r30s[i],
                "freq30M": r30m[i],
            },
        )
        for i in range(11)
    )


def _chart(readings: tuple[SampledReading, ...]) -> ExtractedChart:
    return ExtractedChart(
        source_path="test://chart.png",
        profile_name="test",
        plot_box=PlotBox(x_left=0, x_right=100, y_top=0, y_bottom=100),
        image_height_mm=14.0,
        readings=readings,
    )


# --- _polyline_segments ---------------------------------------------


def test_polyline_continuous_run_is_one_segment() -> None:
    """All 11 values present → one segment with 11 vertices."""
    readings = _readings({"freq10S": tuple(0.9 - i * 0.05 for i in range(11))})
    segments = _polyline_segments(readings, "freq10S", max_mm=14.0)
    assert len(segments) == 1
    # 11 vertices → 11 "x,y" pairs separated by spaces.
    assert len(segments[0].split(" ")) == 11


def test_polyline_none_breaks_into_two_segments() -> None:
    """A single None in the middle splits the polyline into two runs."""
    values: tuple[float | None, ...] = (
        0.95, 0.95, 0.95, 0.95, None, 0.80, 0.78, 0.75, 0.72, 0.70, 0.65,
    )
    readings = _readings({"freq10S": values})
    segments = _polyline_segments(readings, "freq10S", max_mm=14.0)
    assert len(segments) == 2
    # 4 vertices before the gap, 6 after.
    assert len(segments[0].split(" ")) == 4
    assert len(segments[1].split(" ")) == 6


def test_polyline_drops_single_point_runs() -> None:
    """Isolated values surrounded by None produce no segment.

    A 1-vertex polyline is invisible; emitting one would clutter the
    DOM with elements that render nothing.
    """
    values: tuple[float | None, ...] = (
        0.9, None, 0.8, None, None, None, None, None, None, None, None,
    )
    readings = _readings({"freq10S": values})
    segments = _polyline_segments(readings, "freq10S", max_mm=14.0)
    assert segments == []


def test_polyline_all_none_produces_no_segments() -> None:
    """All-None field → no rendered polyline."""
    readings = _readings({})  # everything blank
    segments = _polyline_segments(readings, "freq10S", max_mm=14.0)
    assert segments == []


def test_polyline_first_vertex_at_left_edge() -> None:
    """Reading at position_mm=0.0 → x coordinate at _PAD_LEFT."""
    readings = _readings({"freq10S": (0.9,) + (None,) * 10})
    # Append another value at position 14 to satisfy the 2-vertex rule.
    rebuilt = (
        SampledReading(
            position_mm=0.0,
            samples={"freq10S": 0.9, "freq10M": None, "freq30S": None, "freq30M": None},
        ),
        SampledReading(
            position_mm=14.0,
            samples={"freq10S": 0.5, "freq10M": None, "freq30S": None, "freq30M": None},
        ),
    ) + tuple(
        SampledReading(
            position_mm=float(i),
            samples={"freq10S": None, "freq10M": None, "freq30S": None, "freq30M": None},
        )
        for i in range(2, 11)
    )
    segments = _polyline_segments(rebuilt[:2], "freq10S", max_mm=14.0)
    first_xy = segments[0].split(" ")[0]
    x_str = first_xy.split(",")[0]
    assert float(x_str) == pytest.approx(_PAD_LEFT)


def test_polyline_last_vertex_at_right_edge() -> None:
    """Reading at position_mm == image_height_mm → x at viewBox right minus pad."""
    last_x_expected = _VIEWBOX_W - _PAD_RIGHT
    readings = (
        SampledReading(
            position_mm=0.0,
            samples={"freq10S": 0.9, "freq10M": None, "freq30S": None, "freq30M": None},
        ),
        SampledReading(
            position_mm=14.0,
            samples={"freq10S": 0.5, "freq10M": None, "freq30S": None, "freq30M": None},
        ),
    )
    segments = _polyline_segments(readings, "freq10S", max_mm=14.0)
    last_xy = segments[0].split(" ")[-1]
    x_str = last_xy.split(",")[0]
    assert float(x_str) == pytest.approx(last_x_expected)


# --- render_svg whole-document ---------------------------------------


def test_render_svg_is_parseable_xml() -> None:
    """A standalone SVG must parse cleanly as XML — no broken tags."""
    readings = _readings(
        {"freq10S": tuple(0.9 for _ in range(11))}
    )
    svg = render_svg(_chart(readings))
    # ET.fromstring raises on malformed XML.
    root = ET.fromstring(svg)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"


def test_render_svg_viewbox_matches_constants() -> None:
    """Standalone provenance SVG extends the Astro 320x200 canvas by a
    legend strip below the plot — the legend lives in-document, not in
    a sibling `<div>`."""
    readings = _readings({"freq10S": tuple(0.9 for _ in range(11))})
    svg = render_svg(_chart(readings))
    root = ET.fromstring(svg)
    assert root.get("viewBox") == f"0 0 {_VIEWBOX_W} {_VIEWBOX_H}"
    # Width unchanged; height grew by the legend strip.
    assert _VIEWBOX_W == 320
    assert _VIEWBOX_H > 200


def test_render_svg_renders_all_four_fields_as_separate_polylines() -> None:
    """Each of the 4 committed fields produces its own polyline element."""
    values = tuple(0.9 - i * 0.05 for i in range(11))
    readings = _readings({
        "freq10S": values,
        "freq10M": values,
        "freq30S": values,
        "freq30M": values,
    })
    svg = render_svg(_chart(readings))
    root = ET.fromstring(svg)
    polylines = root.findall("{http://www.w3.org/2000/svg}polyline")
    assert len(polylines) == 4


def test_render_svg_skipped_field_emits_no_polyline() -> None:
    """A field with all-None readings produces zero polylines for that field."""
    readings = _readings({"freq10S": tuple(0.9 for _ in range(11))})
    svg = render_svg(_chart(readings))
    root = ET.fromstring(svg)
    polylines = root.findall("{http://www.w3.org/2000/svg}polyline")
    # Only freq10S is populated → exactly one polyline.
    assert len(polylines) == 1


def test_render_svg_solid_vs_dashed_styling() -> None:
    """S curves are solid (no stroke-dasharray); M curves are dashed."""
    values = tuple(0.9 - i * 0.05 for i in range(11))
    readings = _readings({
        "freq10S": values,
        "freq10M": values,
        "freq30S": values,
        "freq30M": values,
    })
    svg = render_svg(_chart(readings))
    root = ET.fromstring(svg)
    polylines = root.findall("{http://www.w3.org/2000/svg}polyline")
    classes = {p.get("class"): p.get("stroke-dasharray") for p in polylines}
    # Each S class has no inline dasharray, each M does.
    s_classes = [c for c in classes if c and "curve-m" not in c]
    m_classes = [c for c in classes if c and "curve-m" in c]
    assert all(classes[c] is None for c in s_classes)
    assert all(classes[c] == "4 2" for c in m_classes)


def test_render_svg_none_in_middle_produces_two_polylines() -> None:
    """One field with a gap → two polylines for that field."""
    values: tuple[float | None, ...] = (
        0.95, 0.95, 0.95, 0.95, None, 0.80, 0.78, 0.75, 0.72, 0.70, 0.65,
    )
    readings = _readings({"freq10S": values})
    svg = render_svg(_chart(readings))
    root = ET.fromstring(svg)
    polylines = root.findall("{http://www.w3.org/2000/svg}polyline")
    assert len(polylines) == 2


def test_render_svg_dots_match_non_none_readings() -> None:
    """One circle per non-None reading per populated field."""
    values: tuple[float | None, ...] = (
        0.9, 0.9, None, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9,
    )
    readings = _readings({"freq10S": values})
    svg = render_svg(_chart(readings))
    root = ET.fromstring(svg)
    circles = root.findall("{http://www.w3.org/2000/svg}circle")
    # 10 non-None values in one field → 10 circles.
    assert len(circles) == 10


def test_render_svg_axis_title_present() -> None:
    """The x-axis title 'Image height (mm)' appears once."""
    readings = _readings({"freq10S": tuple(0.9 for _ in range(11))})
    svg = render_svg(_chart(readings))
    assert svg.count("Image height (mm)") == 1


def test_render_svg_center_label_uses_C() -> None:
    """Position 0.0 prints as 'C' (matches MtfChart.astro)."""
    readings = _readings({"freq10S": tuple(0.9 for _ in range(11))})
    svg = render_svg(_chart(readings))
    # The 'C' label appears as an axis-x text element.
    assert re.search(r'<text class="axis-label axis-x"[^>]*>C</text>', svg)


# --- integration on a real reference chart --------------------------


def test_render_svg_on_real_sigma_chart_has_content() -> None:
    """Smoke: a real extracted chart renders an SVG with populated polylines."""
    chart_entry = next(
        c for c in REFERENCE_CHARTS if c.slug == "sigma-56mm-f1-4-dc-dn-c"
    )
    assert chart_entry.plot_box is not None
    image_path = REPO_ROOT / chart_entry.chart_path
    plot_box = PlotBox(
        x_left=chart_entry.plot_box.x_left,
        x_right=chart_entry.plot_box.x_right,
        y_top=chart_entry.plot_box.y_top,
        y_bottom=chart_entry.plot_box.y_bottom,
    )
    extracted = extract_chart(
        image_path,
        SIGMA_2COLOR_SOLID_DASHED,
        plot_box,
        image_height_mm=chart_entry.image_height_mm,
    )
    svg = render_svg(extracted)
    root = ET.fromstring(svg)
    polylines = root.findall("{http://www.w3.org/2000/svg}polyline")
    # The Sigma extractor produces dense freq10S / freq30S
    # readings and sparse 10M / 30M (gaps from the B2 contract). The
    # honest floor is "at least one polyline" — adjusting upward would
    # smuggle in extractor-coverage assumptions that the SVG emitter
    # has no business holding. The polyline counts per field are the
    # extractor's domain (calibration.md / scoring.md), not the
    # emitter's.
    assert len(polylines) >= 1
    # No polyline is empty.
    for p in polylines:
        points = p.get("points") or ""
        assert points.strip(), "polyline points= must not be empty"
