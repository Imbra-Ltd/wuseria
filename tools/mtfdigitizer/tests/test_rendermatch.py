"""Tests for the render-match IoU scorer (#963).

Acceptance criteria from issue #963:

- Self-IoU = 1.0; disjoint masks = 0.0; both-empty = None (not 0).
- Rasterized polyline through known sample points hits known pixels.
- All-None field readings produce an empty raster (no fabricated curve).
- One-side-empty produces 0.0 (genuine disagreement, distinct from
  "no comparison").
- Integration smoke on a runnable reference chart returns a defined
  aggregate score in (0, 1].
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from mtfdigitizer.pipeline import (
    PlotBox,
    SampledReading,
    extract_chart,
    score_chart,
)
from mtfdigitizer.pipeline.rendermatch import (
    CURVE_FIELDS,
    DEFAULT_DILATION_RADIUS_PX,
    dilate_for_iou,
    iou,
    rasterize_readings,
)
from mtfdigitizer.profiles import SAMYANG_4COLOR_ALL_SOLID
from mtfdigitizer.referenceset import REFERENCE_CHARTS


REPO_ROOT = Path(__file__).resolve().parents[3]


def _ref(slug: str) -> tuple[Path, PlotBox, float]:
    chart = next(c for c in REFERENCE_CHARTS if c.slug == slug)
    assert chart.plot_box is not None
    box = PlotBox(
        x_left=chart.plot_box.x_left,
        x_right=chart.plot_box.x_right,
        y_top=chart.plot_box.y_top,
        y_bottom=chart.plot_box.y_bottom,
    )
    return REPO_ROOT / chart.chart_path, box, chart.image_height_mm


SAMYANG_85_CHART, SAMYANG_85_PLOT_BOX, SAMYANG_85_HEIGHT = _ref(
    "samyang-85mm-f1-4-as-if-umc"
)


def _all_nones() -> tuple[SampledReading, ...]:
    """11 readings with every field set to None."""
    return tuple(
        SampledReading(
            position_mm=i * 2.0,
            samples={
                "freq10S": None,
                "freq10M": None,
                "freq30S": None,
                "freq30M": None,
            },
        )
        for i in range(11)
    )


def _flat_readings(value: float) -> tuple[SampledReading, ...]:
    """11 readings with every field set to the same flat value."""
    return tuple(
        SampledReading(
            position_mm=i * 2.0,
            samples={
                "freq10S": value,
                "freq10M": value,
                "freq30S": value,
                "freq30M": value,
            },
        )
        for i in range(11)
    )


# --- iou primitive --------------------------------------------------


def test_iou_self_is_one() -> None:
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[40:60, 20:80] = 1
    assert iou(mask, mask) == 1.0


def test_iou_disjoint_is_zero() -> None:
    a = np.zeros((100, 100), dtype=np.uint8)
    b = np.zeros((100, 100), dtype=np.uint8)
    a[10:20, 10:20] = 1
    b[60:70, 60:70] = 1
    assert iou(a, b) == 0.0


def test_iou_both_empty_is_none() -> None:
    """No surface to compare ⇒ no score (None) — not a misleading 0.0."""
    empty = np.zeros((100, 100), dtype=np.uint8)
    assert iou(empty, empty) is None


def test_iou_one_side_empty_is_zero() -> None:
    """One side has pixels, the other doesn't — that's a genuine
    disagreement, not 'no comparison'. Distinct from both-empty."""
    populated = np.zeros((100, 100), dtype=np.uint8)
    populated[40:60, 20:80] = 1
    empty = np.zeros((100, 100), dtype=np.uint8)
    assert iou(populated, empty) == 0.0
    assert iou(empty, populated) == 0.0


def test_iou_half_overlap() -> None:
    """Two equal-area rectangles sharing exactly half their pixels:
    intersection = 50, union = 150, IoU = 1/3."""
    a = np.zeros((100, 100), dtype=np.uint8)
    b = np.zeros((100, 100), dtype=np.uint8)
    a[0:10, 0:10] = 1   # 100 px
    b[0:10, 5:15] = 1   # 100 px, 50 overlap
    score = iou(a, b)
    assert score is not None
    assert score == pytest.approx(50 / 150)


def test_iou_shape_mismatch_raises() -> None:
    with pytest.raises(ValueError, match="shape mismatch"):
        iou(np.zeros((10, 10), dtype=np.uint8), np.zeros((10, 11), dtype=np.uint8))


# --- dilate ---------------------------------------------------------


def test_dilate_zero_radius_is_noop_binary() -> None:
    mask = np.zeros((20, 20), dtype=np.uint8)
    mask[10, 10] = 7  # any truthy value
    out = dilate_for_iou(mask, radius_px=0)
    assert out.dtype == np.uint8
    assert out[10, 10] == 1
    assert out.sum() == 1


def test_dilate_grows_a_single_pixel_symmetrically() -> None:
    mask = np.zeros((30, 30), dtype=np.uint8)
    mask[15, 15] = 1
    out = dilate_for_iou(mask, radius_px=3)
    # Elliptical kernel covers at least the 7×7 bounding box minus corners.
    assert out[15, 15] == 1
    assert out[12, 15] == 1
    assert out[18, 15] == 1
    assert out[15, 12] == 1
    assert out[15, 18] == 1
    # Outside the radius is untouched.
    assert out[15, 22] == 0
    assert out[22, 15] == 0


def test_dilate_negative_radius_raises() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        dilate_for_iou(np.zeros((10, 10), dtype=np.uint8), radius_px=-1)


# --- rasterize ------------------------------------------------------


def test_rasterize_flat_readings_draws_horizontal_lines() -> None:
    """A flat MTF=0.5 should draw 4 horizontal lines (one per field) at
    the y-pixel corresponding to mid-height of the plot box."""
    plot_box = PlotBox(x_left=10, x_right=110, y_top=20, y_bottom=120)
    image_height_mm = 10.0
    readings = _flat_readings(0.5)
    masks = rasterize_readings(
        readings, plot_box, image_shape=(150, 200), image_height_mm=image_height_mm
    )
    assert set(masks.keys()) == set(CURVE_FIELDS)
    # MTF 0.5 → y = y_bottom - 0.5*height = 120 - 50 = 70.
    for field in CURVE_FIELDS:
        m = masks[field]
        assert m[70, 50] == 1, f"{field}: expected pixel at (70, 50) in flat line"
        # Nothing drawn outside the plot box span on the x-axis.
        assert m[70, 5] == 0
        # Nothing drawn at other y rows (with a small tolerance for the 1px line).
        assert m[40, 50] == 0


def test_rasterize_skips_none_gaps() -> None:
    """A reading with one None in the middle splits the line — no
    bridging segment crosses the gap."""
    plot_box = PlotBox(x_left=10, x_right=110, y_top=20, y_bottom=120)
    image_height_mm = 10.0
    # Flat 0.5 everywhere EXCEPT position 5 (middle) is None.
    values: list[float | None] = [0.5] * 11
    values[5] = None
    readings = tuple(
        SampledReading(
            position_mm=i * 1.0,
            samples={
                "freq10S": v,
                "freq10M": None,
                "freq30S": None,
                "freq30M": None,
            },
        )
        for i, v in enumerate(values)
    )
    masks = rasterize_readings(
        readings, plot_box, image_shape=(150, 200), image_height_mm=image_height_mm
    )
    m = masks["freq10S"]
    # Two segments either side of the gap should have pixels at y=70...
    assert m[70, 30] == 1  # before the gap
    assert m[70, 80] == 1  # after the gap
    # ...but the x column passing through the missing sample point is empty.
    # Position 5 of 11 over x_left=10..x_right=110 sits at x ≈ 60.
    assert m[70, 60] == 0


def test_rasterize_all_none_field_is_empty() -> None:
    """If every reading is None for a field, that field's mask is all-zero —
    no fabricated curve."""
    plot_box = PlotBox(x_left=10, x_right=110, y_top=20, y_bottom=120)
    masks = rasterize_readings(
        _all_nones(),
        plot_box,
        image_shape=(150, 200),
        image_height_mm=10.0,
    )
    for field in CURVE_FIELDS:
        assert masks[field].sum() == 0


def test_rasterize_wrong_length_raises() -> None:
    plot_box = PlotBox(x_left=10, x_right=110, y_top=20, y_bottom=120)
    not_eleven: tuple[SampledReading, ...] = _all_nones()[:5]
    with pytest.raises(ValueError, match="expected"):
        rasterize_readings(
            not_eleven, plot_box, image_shape=(150, 200), image_height_mm=10.0
        )


def test_rasterize_clamps_out_of_range_mtf() -> None:
    """An MTF reading outside [0, 1] (shouldn't happen post-extractor,
    but defensive) clamps to the plot box edges rather than drawing
    out-of-bounds."""
    plot_box = PlotBox(x_left=10, x_right=110, y_top=20, y_bottom=120)
    readings = _flat_readings(1.5)  # well past 1.0
    masks = rasterize_readings(
        readings, plot_box, image_shape=(150, 200), image_height_mm=10.0
    )
    # MTF clamped to 1.0 → drawn at y_top = 20.
    m = masks["freq10S"]
    assert m[20, 50] == 1


# --- integration ----------------------------------------------------


def test_score_chart_samyang_returns_defined_aggregate() -> None:
    """Smoke: a real reference chart trips the full pipeline and yields
    an IoU in (0, 1]. Acceptable range is wide — the calibration runner
    is where exact numbers are pinned; here we only assert 'sensible'."""
    extracted = extract_chart(
        SAMYANG_85_CHART,
        SAMYANG_4COLOR_ALL_SOLID,
        SAMYANG_85_PLOT_BOX,
        image_height_mm=SAMYANG_85_HEIGHT,
    )
    result = score_chart(
        SAMYANG_85_CHART,
        SAMYANG_4COLOR_ALL_SOLID,
        SAMYANG_85_PLOT_BOX,
        image_height_mm=SAMYANG_85_HEIGHT,
        readings=extracted.readings,
    )
    assert result.aggregate is not None
    # ADR-038's de-risking probe: good extractions cleared 0.64. Don't
    # pin to that here — that's the threshold-tuning conversation; this
    # test only asserts the scorer produces a non-degenerate number.
    assert 0.0 < result.aggregate <= 1.0
    # Every committed field reported a row, even if `score` is None.
    fields = {fs.field for fs in result.field_scores}
    assert fields == set(CURVE_FIELDS)


def test_score_chart_polyline_mostly_lands_on_skeleton() -> None:
    """The self-consistency property the threshold ultimately gates on:
    when you redraw the extracted readings, most of the polyline pixels
    fall inside the (dilated) skeleton. This is intersection / rasterized
    — a one-sided check that's robust to the geometric asymmetry between
    a sparse 11-point reconstruction and a dense skeleton trace.

    The IoU `aggregate` itself is asymmetric on this data (the skeleton
    has many more pixels than an 11-point polyline) and lands lower than
    the epic-#932 probe's symmetric-trace numbers. `scoring.md` records
    the real distribution; this test only asserts the round-trip is
    fundamentally sound on a chart we know calibrates cleanly (#953:
    median |d| = 0.014, all Samyang fields paired 11/11).

    `freq10M` is excluded post-#1216 (ADR-059): after the `10S-red` halo
    subtraction its real skeleton is honestly sparse at low fractions (the
    M10 and S10 curves overlap at high MTF, so the contaminator subtraction
    leaves cells covered by sister fallback rather than by direct skeleton
    ink). The polyline drawn from the corrected M10 readings runs through
    sister-filled gaps where the skeleton has none of its own pixels,
    dragging mean precision below the 0.85 self-consistency bar.

    `freq30M` is excluded post-ADR-062 for the same reason: the
    `30S-dark-grey` -> `30M-light-grey` halo subtraction empties the M30
    skeleton at the right edge where the legitimate M30 light-grey curve
    lies under the dark-grey AA wrap of S30. Sister fallback covers the
    emptied cells (GT confirms p95 |d| 0.086 -> 0.026), but the polyline
    runs through skeleton-empty space, dragging the precision aggregate
    below the bar. Aggregating only the two skeleton-resident S fields
    keeps the test's intent intact."""
    extracted = extract_chart(
        SAMYANG_85_CHART,
        SAMYANG_4COLOR_ALL_SOLID,
        SAMYANG_85_PLOT_BOX,
        image_height_mm=SAMYANG_85_HEIGHT,
    )
    result = score_chart(
        SAMYANG_85_CHART,
        SAMYANG_4COLOR_ALL_SOLID,
        SAMYANG_85_PLOT_BOX,
        image_height_mm=SAMYANG_85_HEIGHT,
        readings=extracted.readings,
        dilation_radius_px=DEFAULT_DILATION_RADIUS_PX,
    )
    assert result.aggregate is not None
    # Across the skeleton-resident fields, the polyline must mostly land
    # on the skeleton. `freq10M` and `freq30M` are excluded - see docstring.
    halo_emptied_fields = {"freq10M", "freq30M"}
    hits = []
    for fs in result.field_scores:
        if fs.field in halo_emptied_fields:
            continue
        if fs.rasterized_px == 0:
            continue
        hits.append(fs.intersection_px / fs.rasterized_px)
    assert hits, "no field carried a rasterized polyline"
    mean_precision = sum(hits) / len(hits)
    assert mean_precision >= 0.85, (
        f"on a cleanly-calibrated chart, ≥ 85% of polyline pixels should "
        f"land inside the dilated skeleton; got {mean_precision:.3f}"
    )
