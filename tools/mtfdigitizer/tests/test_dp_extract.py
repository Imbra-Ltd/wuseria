"""Tests for the DP shortest-path curve extractor."""

from __future__ import annotations

import numpy as np

from mtfdigitizer.pipeline.dp_extract import (
    CurvePoints,
    _trim_flatlined_tail,
    _viterbi_path,
    curves_to_field_skeletons,
    dilate_for_dp,
    extract_one_curve_dp,
    extract_two_curves_dp,
)
from mtfdigitizer.pipeline.types import PlotBox


def test_viterbi_finds_dark_path_through_uniform_emission() -> None:
    # 10x5 cost field: a dark row at y=2 cuts through brighter pixels.
    emission = np.ones((5, 10), dtype=np.float64)
    emission[2, :] = 0.0
    trace = _viterbi_path(emission, alpha=0.5, max_jump=2)
    assert list(trace) == [2] * 10


def test_viterbi_respects_smoothness_prior_over_one_bright_pixel() -> None:
    # The path should stay on the dark row even when one column on
    # that row is briefly bright — the alternative dark row is 3 rows
    # away and reaching it costs 2 * alpha * 3 = 60 (down then back up).
    emission = np.full((7, 5), 100.0, dtype=np.float64)
    emission[3, :] = 0.0  # cheap row
    emission[3, 2] = 5.0  # one spike on the cheap row
    emission[6, 2] = 0.0  # tempting one-column gap on another row
    trace = _viterbi_path(emission, alpha=10.0, max_jump=6)
    # Going to row 6 for one column then back to row 3 costs 2*10*3 = 60;
    # tolerating the 5-cost spike costs 5. DP must stay on row 3.
    assert list(trace) == [3] * 5


def test_extract_two_curves_returns_upper_then_lower_by_mean_y() -> None:
    # Synthetic mask: two horizontal stripes at y=10 (upper) and y=40.
    mask = np.zeros((60, 100), dtype=np.uint8)
    mask[10, :] = 1
    mask[40, :] = 1
    plot_box = PlotBox(x_left=0, x_right=99, y_top=0, y_bottom=59)
    upper, lower = extract_two_curves_dp(mask, plot_box)
    assert all(abs(y - 10) <= 1 for _, y in upper.points)
    assert all(abs(y - 40) <= 1 for _, y in lower.points)


def test_curves_to_field_skeletons_rasterises_columns_in_curve_points() -> None:
    # The DP dispatch's rasterisation is "draw the path at every column
    # the curve covers". With the #1215 right-edge trim, curves may end
    # before the right plot edge — those trimmed columns get no skeleton
    # pixel, so the sampler returns None there. Columns inside the curve
    # range still get exactly one pixel per column per curve.
    mask = np.zeros((40, 300), dtype=np.uint8)
    mask[10, 100:201] = 1
    mask[30, 100:201] = 1
    plot_box = PlotBox(x_left=0, x_right=299, y_top=0, y_bottom=39)
    upper, lower = extract_two_curves_dp(mask, plot_box)
    upper_sk, lower_sk = curves_to_field_skeletons(upper, lower, mask, plot_box)
    # Each curve marks one pixel per column it covers.
    upper_cols = sorted({x for x, _ in upper.points})
    lower_cols = sorted({x for x, _ in lower.points})
    assert all(upper_sk[:, x].sum() == 1 for x in upper_cols)
    assert all(lower_sk[:, x].sum() == 1 for x in lower_cols)
    # Curves must at least cover the columns where the original mask had ink.
    assert min(upper_cols) <= 100 and max(upper_cols) >= 200
    assert min(lower_cols) <= 100 and max(lower_cols) >= 200


def test_curves_to_field_skeletons_uses_mask_shape_for_output() -> None:
    mask = np.zeros((20, 50), dtype=np.uint8)
    mask[5, 10:41] = 1
    plot_box = PlotBox(x_left=0, x_right=49, y_top=0, y_bottom=19)
    upper, lower = extract_two_curves_dp(mask, plot_box)
    upper_sk, lower_sk = curves_to_field_skeletons(upper, lower, mask, plot_box)
    assert upper_sk.shape == mask.shape
    assert lower_sk.shape == mask.shape


def test_trim_flatlined_tail_keeps_descending_trace_intact() -> None:
    # Monotone-descending trace with no flat run at the end: nothing to trim.
    # raw_box is irrelevant when the trace is not flat.
    trace = np.arange(50, dtype=np.int32)
    raw_box = np.zeros((100, 50), dtype=np.uint8)
    assert _trim_flatlined_tail(trace, raw_box) == 50


def test_trim_flatlined_tail_drops_long_flat_tail_when_no_raw_ink() -> None:
    # Trace descends 0->30 over 30 cols, then flat at y=30 for 25 cols.
    # Raw mask has ink only in the descending region, far from y=30.
    trace = np.concatenate([np.arange(0, 30), np.full(25, 30)]).astype(np.int32)
    raw_box = np.zeros((60, 55), dtype=np.uint8)
    for x in range(20):  # ink only in cols 0..19, well before the flat run
        raw_box[x, x] = 1
    new_len = _trim_flatlined_tail(trace, raw_box)
    # Flat run starts at the first col within ±1 of last_y=30, i.e. col 29.
    # 55 - 29 = 26 ≥ 12 → trim from col 29 onward.
    assert new_len == 29


def test_trim_flatlined_tail_keeps_flat_tail_when_raw_ink_present() -> None:
    # A genuinely flat curve with real ink at the flatline y: must NOT trim.
    trace = np.full(50, 30, dtype=np.int32)
    raw_box = np.zeros((60, 50), dtype=np.uint8)
    raw_box[30, :] = 1  # ink runs along y=30 the whole way
    assert _trim_flatlined_tail(trace, raw_box) == 50


def test_trim_flatlined_tail_short_flat_run_below_threshold_not_trimmed() -> None:
    # Flat run of only 5 columns at the end — below _FLATLINE_TRIM_MIN_COLS (12).
    trace = np.concatenate([np.arange(0, 45), np.full(5, 45)]).astype(np.int32)
    raw_box = np.zeros((60, 50), dtype=np.uint8)
    assert _trim_flatlined_tail(trace, raw_box) == 50


def test_extract_two_curves_dp_trims_flatlined_right_edge_tail() -> None:
    # Mask: an upper line that runs flat at y=20 through col 150 then
    # disappears completely (no ink) past col 200 — well past the 51-wide
    # dilation reach. Plus a lower line at y=200 with full-width ink. The
    # DP will hold the upper at y=20 across the right half where there
    # is no ink; the trim should drop those columns.
    mask = np.zeros((300, 400), dtype=np.uint8)
    mask[20, :150] = 1  # upper: y=20 across cols 0..149
    mask[200, :] = 1    # lower: y=200 full width
    plot_box = PlotBox(x_left=0, x_right=399, y_top=0, y_bottom=299)
    upper, lower = extract_two_curves_dp(mask, plot_box)
    # Lower curve has ink everywhere → kept full length.
    assert len(lower.points) == 400
    # Upper trimmed where ink ran out + dilation kernel half-width slack (~25).
    assert len(upper.points) < 400
    assert len(upper.points) >= 150


def test_extract_one_curve_dp_does_not_trim() -> None:
    # extract_one_curve_dp serves the dashed-meridional dispatch where
    # legitimate dash gaps would be mis-read as flatlines (#1215). It
    # must keep the trim disabled — even when DP holds a constant y
    # across an empty stretch, the full-width trace is returned.
    mask = np.zeros((200, 400), dtype=np.uint8)
    mask[40, :150] = 1
    plot_box = PlotBox(x_left=0, x_right=399, y_top=0, y_bottom=199)
    curve = extract_one_curve_dp(mask, plot_box)
    assert len(curve.points) == 400


def test_dilate_for_dp_bridges_dash_gaps_within_kernel_width() -> None:
    # Two single-pixel "dashes" 30 columns apart. The 51-wide kernel
    # should connect them.
    mask = np.zeros((10, 100), dtype=np.uint8)
    mask[5, 20] = 1
    mask[5, 50] = 1
    dilated = dilate_for_dp(mask)
    assert dilated[5, 35] == 1  # midway between the dashes
