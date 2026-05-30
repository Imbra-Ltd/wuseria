"""Tests for the 3-panel review-file generator (#973).

Acceptance criteria from issue #973:

- Overlay polylines reflect the readings (geometry correctness).
- A `None` reading breaks the polyline (no segment across a gap — B2
  contract, matches `rasterize_readings` and the SVG emitter).
- Plot-box clamping: values rendered to a fixed plot box land inside it,
  out-of-range values clamp to the edges rather than overflow.
- HTML structure: 3 panels, each referencing its expected filename, no
  external assets, valid HTML.
- Integration: writing a review file for a real reference chart leaves
  the HTML + overlay PNG on disk and the HTML references both panel
  artifacts by their actual basenames.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pytest

from mtfdigitizer.pipeline import (
    PlotBox,
    SampledReading,
    extract_chart,
)
from mtfdigitizer.profiles import SIGMA_2COLOR_SOLID_DASHED
from mtfdigitizer.referenceset import REFERENCE_CHARTS
from mtfdigitizer.review import (
    ReviewPaths,
    _OVERLAY_COLOR_10,
    _OVERLAY_COLOR_30,
    render_overlay,
    render_review_html,
    write_review,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


# --- fixtures -------------------------------------------------------


def _readings(values_per_field: dict[str, tuple[float | None, ...]]) -> tuple[SampledReading, ...]:
    """11 SampledReading rows at uniform positions over 0-14mm."""
    positions = tuple(round(i * 1.4, 1) for i in range(11))
    blank: tuple[None, ...] = (None,) * 11
    c10s = values_per_field.get("contrast10S", blank)
    c10m = values_per_field.get("contrast10M", blank)
    r30s = values_per_field.get("resolution30S", blank)
    r30m = values_per_field.get("resolution30M", blank)
    return tuple(
        SampledReading(
            position_mm=positions[i],
            contrast10S=c10s[i],
            contrast10M=c10m[i],
            resolution30S=r30s[i],
            resolution30M=r30m[i],
        )
        for i in range(11)
    )


def _blank_image(h: int = 200, w: int = 300) -> np.ndarray:
    """Pure-white BGR canvas — visible overlay pixels stand out."""
    return np.full((h, w, 3), 255, dtype=np.uint8)


def _plot_box() -> PlotBox:
    return PlotBox(x_left=10, x_right=290, y_top=20, y_bottom=180)


# --- render_overlay --------------------------------------------------


def test_overlay_does_not_mutate_input() -> None:
    """The overlay is rendered onto a copy; the source image is untouched."""
    image = _blank_image()
    snapshot = image.copy()
    readings = _readings({"contrast10S": tuple(0.9 for _ in range(11))})
    render_overlay(image, readings, _plot_box(), image_height_mm=14.0)
    assert np.array_equal(image, snapshot), "render_overlay mutated its input"


def test_overlay_draws_10s_in_gold() -> None:
    """A populated 10S field paints gold pixels (#c89b3c in BGR)."""
    image = _blank_image()
    readings = _readings({"contrast10S": tuple(0.5 for _ in range(11))})
    out = render_overlay(image, readings, _plot_box(), image_height_mm=14.0)
    # OpenCV BGR matches against the constant. A flat 0.5 line at
    # plot-box mid-height (y=100) should have many gold pixels along
    # that row.
    target = np.array(_OVERLAY_COLOR_10, dtype=np.uint8)
    matches = np.all(out == target, axis=-1)
    assert matches.any(), "no gold (10 lp/mm) pixels in overlay"


def test_overlay_draws_30s_in_blue() -> None:
    """Populated 30S → blue pixels (#6b9bd2 in BGR)."""
    image = _blank_image()
    readings = _readings({"resolution30S": tuple(0.5 for _ in range(11))})
    out = render_overlay(image, readings, _plot_box(), image_height_mm=14.0)
    target = np.array(_OVERLAY_COLOR_30, dtype=np.uint8)
    matches = np.all(out == target, axis=-1)
    assert matches.any(), "no blue (30 lp/mm) pixels in overlay"


def test_overlay_all_none_paints_nothing() -> None:
    """No populated fields → no overlay pixels drawn."""
    image = _blank_image()
    out = render_overlay(image, _readings({}), _plot_box(), image_height_mm=14.0)
    assert np.array_equal(out, image)


def test_overlay_skips_segments_across_none() -> None:
    """A None reading breaks the polyline at that vertex.

    Setup: two short runs of values separated by a None. The overlay
    must draw two segments, not bridge across the gap. We measure this
    by checking that there are *no* gold pixels in the column band
    where the None sits.
    """
    values: tuple[float | None, ...] = (
        0.5, 0.5, 0.5, 0.5, None, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
    )
    image = _blank_image()
    plot_box = _plot_box()
    readings = _readings({"contrast10S": values})
    out = render_overlay(image, readings, plot_box, image_height_mm=14.0)

    # The None sits at index 4 (position 5.6mm, x ≈ 122). The last
    # painted vertex before the gap is index 3 (position 4.2mm, x = 94)
    # and the first painted vertex after is index 5 (position 7.0mm,
    # x = 150). The analytic gap is x ∈ (94, 150). We test the *interior*
    # of the gap (well inside both endpoints) — `cv2.line`'s endpoint
    # rounding can spill one pixel past the analytic endpoint, but the
    # middle of the gap must be empty if the polyline truly broke.
    target = np.array(_OVERLAY_COLOR_10, dtype=np.uint8)
    gap_interior = out[:, 105:140, :]
    matches_in_gap = np.all(gap_interior == target, axis=-1)
    assert not matches_in_gap.any(), "polyline bridged across a None"


def test_overlay_clamps_out_of_range_values() -> None:
    """Readings outside [0, 1] are clamped to the plot box edges.

    Defense in depth — the sampler clamps too, but a downstream caller
    handing us a stale or hand-crafted value shouldn't crash the
    overlay or paint outside the canvas.
    """
    image = _blank_image()
    plot_box = _plot_box()
    # Value above 1.0 → must clamp to y=y_top=20, not above.
    readings = _readings({"contrast10S": tuple(1.5 for _ in range(11))})
    out = render_overlay(image, readings, plot_box, image_height_mm=14.0)
    target = np.array(_OVERLAY_COLOR_10, dtype=np.uint8)
    # The line should be drawn at or near y=20 (the plot top), not
    # somewhere undefined. Look in a narrow band around plot top.
    band = out[18:25, :, :]
    matches = np.all(band == target, axis=-1)
    assert matches.any(), "clamped value did not draw at plot top"


def test_overlay_m_field_is_dashed_not_continuous() -> None:
    """M fields draw as broken segments, so a horizontal run shows gaps.

    A solid 10S over the full width paints a contiguous gold streak; a
    dashed 10M over the same width paints alternating gold + white
    along that row. The dashed row has fewer painted pixels.
    """
    plot_box = _plot_box()
    image_height_mm = 14.0
    solid_readings = _readings({"contrast10S": tuple(0.5 for _ in range(11))})
    dashed_readings = _readings({"contrast10M": tuple(0.5 for _ in range(11))})

    solid_out = render_overlay(_blank_image(), solid_readings, plot_box, image_height_mm)
    dashed_out = render_overlay(_blank_image(), dashed_readings, plot_box, image_height_mm)

    target = np.array(_OVERLAY_COLOR_10, dtype=np.uint8)
    solid_painted = int(np.all(solid_out == target, axis=-1).sum())
    dashed_painted = int(np.all(dashed_out == target, axis=-1).sum())

    # Dashed must paint strictly fewer pixels (the gaps eat ~40% under
    # the configured dash/gap ratio).
    assert dashed_painted < solid_painted
    assert dashed_painted > 0  # but it does paint something


# --- HTML composition ------------------------------------------------


def _parse_html(content: str) -> ET.Element:
    """Parse the HTML5 fragment using ET. We pass `html=True` semantics
    via lxml-like permissiveness: the template is hand-authored, so the
    fragment is well-formed XML if we strip the doctype line."""
    # ET cannot parse the leading <!doctype html> — strip it before parsing.
    stripped = re.sub(r"<!doctype[^>]*>\s*", "", content, count=1, flags=re.I)
    return ET.fromstring(stripped)


def test_review_html_has_three_panels() -> None:
    """One `.panel` per role: original, SVG, overlay."""
    html = render_review_html(
        title="test",
        paths=ReviewPaths(
            original_filename="orig.png",
            svg_filename="orig.svg",
            overlay_filename="orig-overlay.png",
        ),
    )
    root = _parse_html(html)
    panels = root.findall(".//div[@class='panel']") + root.findall(
        ".//div[@class='panel bottom']"
    )
    assert len(panels) == 3


def test_review_html_references_all_three_artifacts_by_name() -> None:
    """Each `<img src=>` points to the basename it was given — no path
    munging, no rewriting, so the HTML works opened off-disk."""
    html = render_review_html(
        title="test",
        paths=ReviewPaths(
            original_filename="my-chart.png",
            svg_filename="my-chart.svg",
            overlay_filename="my-chart-overlay.png",
        ),
    )
    root = _parse_html(html)
    srcs = {img.get("src") for img in root.findall(".//img")}
    assert srcs == {"my-chart.png", "my-chart.svg", "my-chart-overlay.png"}


def test_review_html_title_is_escaped() -> None:
    """A title containing HTML special characters must not break the
    document — the renderer escapes user content."""
    html = render_review_html(
        title="lens & <bad>",
        paths=ReviewPaths(
            original_filename="o.png",
            svg_filename="o.svg",
            overlay_filename="o-overlay.png",
        ),
    )
    # The literal "&" must appear as "&amp;" in the rendered HTML.
    assert "&amp;" in html
    assert "<bad>" not in html
    # Still parseable after escaping.
    root = _parse_html(html)
    assert root.tag in ("html", "{http://www.w3.org/1999/xhtml}html")


def test_review_html_has_no_javascript() -> None:
    """ADR-038: 'no editor UI'. The review file is a viewer, not an
    interactive editor — no `<script>` tags, ever."""
    html = render_review_html(
        title="test",
        paths=ReviewPaths(
            original_filename="o.png",
            svg_filename="o.svg",
            overlay_filename="o-overlay.png",
        ),
    )
    assert "<script" not in html.lower()


def test_review_html_has_no_external_assets() -> None:
    """No remote stylesheets, fonts, or images — the file works without
    a network connection."""
    html = render_review_html(
        title="test",
        paths=ReviewPaths(
            original_filename="o.png",
            svg_filename="o.svg",
            overlay_filename="o-overlay.png",
        ),
    )
    # No `https?://` in any href or src attribute.
    assert not re.search(r'(?:src|href)="https?://', html, flags=re.I)


# --- integration: write_review on a real reference chart ------------


def test_write_review_on_real_sigma_chart(tmp_path: Path) -> None:
    """Smoke: writing a review file for the Sigma reference chart leaves
    the HTML and overlay PNG on disk, and the HTML references both by
    their actual basenames."""
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
    svg_path = image_path.with_suffix(".svg")

    outputs = write_review(
        extracted,
        image_path,
        plot_box=plot_box,
        image_height_mm=chart_entry.image_height_mm,
        svg_path=svg_path,
        out_dir=tmp_path,
    )

    assert outputs.html_path.is_file()
    assert outputs.overlay_path.is_file()
    assert outputs.overlay_path.stat().st_size > 0

    html = outputs.html_path.read_text(encoding="utf-8")
    # The HTML must reference the source PNG basename and the overlay
    # basename. The SVG is referenced by `<stem>.svg`, the
    # ADR-038 / #971 convention for the provenance file.
    assert image_path.name in html
    assert outputs.overlay_path.name in html
    assert svg_path.name in html


def test_write_review_default_out_dir_is_image_folder(tmp_path: Path) -> None:
    """When `out_dir` is omitted, the review files land next to the
    source image — matching the ADR-038 convention for per-lens artifacts."""
    # Build a small synthetic chart in tmp so we don't touch the real
    # reference data.
    source_png = tmp_path / "fake-chart.png"
    blank = _blank_image(220, 320)
    import cv2  # local import keeps test_review.py top-level clean
    cv2.imwrite(str(source_png), blank)

    # An ExtractedChart with one populated field — enough to exercise
    # the overlay write.
    plot_box = PlotBox(x_left=20, x_right=300, y_top=20, y_bottom=200)
    readings = _readings({"contrast10S": tuple(0.5 for _ in range(11))})
    from mtfdigitizer.pipeline import ExtractedChart
    extracted = ExtractedChart(
        source_path=str(source_png),
        profile_name="test",
        plot_box=plot_box,
        image_height_mm=14.0,
        readings=readings,
    )

    outputs = write_review(
        extracted,
        source_png,
        plot_box=plot_box,
        image_height_mm=14.0,
        svg_path=source_png.with_suffix(".svg"),
    )
    assert outputs.html_path.parent == source_png.parent
    assert outputs.overlay_path.parent == source_png.parent
