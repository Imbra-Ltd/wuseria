"""Tests for the DP shortest-path curve extractor."""

from __future__ import annotations

import numpy as np

from mtfdigitizer.pipeline.dp_extract import (
    CurvePoints,
    _viterbi_path,
    curves_to_field_skeletons,
    dilate_for_dp,
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


def test_curves_to_field_skeletons_emits_only_columns_with_real_ink() -> None:
    # Two horizontal stripes at y=10 and y=30, ink only in columns
    # 100..200 of a 300-wide plot — outside columns far enough from
    # the ink that the dilation kernel can't reach. DP runs across
    # the full width but the B2 rasterizer should only emit pixels
    # where the raw mask has real ink.
    mask = np.zeros((40, 300), dtype=np.uint8)
    mask[10, 100:201] = 1
    mask[30, 100:201] = 1
    plot_box = PlotBox(x_left=0, x_right=299, y_top=0, y_bottom=39)
    upper, lower = extract_two_curves_dp(mask, plot_box)
    upper_sk, lower_sk = curves_to_field_skeletons(upper, lower, mask, plot_box)
    # Columns inside [100, 200] should rasterize.
    assert upper_sk[:, 150].any()
    assert lower_sk[:, 150].any()
    # Columns well outside (beyond DX tolerance) should not.
    assert not upper_sk[:, 50].any()
    assert not lower_sk[:, 50].any()
    assert not upper_sk[:, 270].any()
    assert not lower_sk[:, 270].any()


def test_curves_to_field_skeletons_assigns_lone_ink_to_one_curve_only() -> None:
    # Only one stripe at y=5 exists; the second DP path will hit white.
    # The rasterizer should emit only ONE skeleton — the curve whose
    # anchored y matches the ink.
    mask = np.zeros((20, 50), dtype=np.uint8)
    mask[5, :] = 1
    plot_box = PlotBox(x_left=0, x_right=49, y_top=0, y_bottom=19)
    upper, lower = extract_two_curves_dp(mask, plot_box)
    upper_sk, lower_sk = curves_to_field_skeletons(upper, lower, mask, plot_box)
    # Exactly one of the two skeletons should be populated.
    assert (upper_sk.sum() > 0) != (lower_sk.sum() > 0)


def test_dilate_for_dp_bridges_dash_gaps_within_kernel_width() -> None:
    # Two single-pixel "dashes" 30 columns apart. The 51-wide kernel
    # should connect them.
    mask = np.zeros((10, 100), dtype=np.uint8)
    mask[5, 20] = 1
    mask[5, 50] = 1
    dilated = dilate_for_dp(mask)
    assert dilated[5, 35] == 1  # midway between the dashes


def test_curves_to_field_skeletons_interpolates_across_dash_gaps() -> None:
    # A dashed curve: ink at y=10 in columns 100..110, 130..140, 160..170,
    # plus a stripe at y=30 in columns 100..170 (the lower curve, solid).
    # The support interval for the upper curve is [100, 170]; the
    # rasterizer should produce a continuous skeleton across the
    # 110..130 and 140..160 gaps by interpolating between anchors.
    mask = np.zeros((40, 300), dtype=np.uint8)
    mask[10, 100:111] = 1
    mask[10, 130:141] = 1
    mask[10, 160:171] = 1
    mask[30, 100:171] = 1
    plot_box = PlotBox(x_left=0, x_right=299, y_top=0, y_bottom=39)
    upper, lower = extract_two_curves_dp(mask, plot_box)
    upper_sk, lower_sk = curves_to_field_skeletons(upper, lower, mask, plot_box)
    # Inside the support interval, every column should have an upper
    # skeleton pixel — including columns inside the dash gaps.
    for x in range(100, 171):
        assert upper_sk[:, x].any(), f"upper missing at x={x}"
    # Well outside the support interval (beyond the 51-wide dilation
    # kernel's reach from the leftmost / rightmost ink), no upper
    # skeleton pixel.
    assert not upper_sk[:, 50].any()
    assert not upper_sk[:, 220].any()
