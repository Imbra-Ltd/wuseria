"""11-point sampling + B2-safe interpolation (#935, ADR-038 §3).

Every digitized curve is read at 0/10/20/.../100% of plot width — 11
fixed points, uniform across all brands and chart sizes. The grid is
mapped to real image-height-mm via the per-chart `image_height_mm`.

`interpolate_at` returns `None` when no skeleton pixels exist within
a small bracketing window of the target column — preserving the B2
fix from PR #931 (the legacy tool used to fabricate values up to 20px
from the target; this returns None instead).
"""

from __future__ import annotations

import numpy as np

from .plotbox import (
    image_height_mm_to_x_pixel,
    x_pixel_to_image_height_mm,
    y_pixel_to_mtf,
)
from .types import PlotBox


# Fractions of plot width at which to sample. ADR-038 §3 specifies
# 11 fixed points at 0, 0.1, 0.2, ..., 1.0.
SAMPLE_FRACTIONS: tuple[float, ...] = tuple(round(i * 0.1, 1) for i in range(11))


# Half-width of the column window scanned around each target x_pixel
# when reading a skeleton's y-value. Wide enough to bridge thin
# antialiased gaps, narrow enough to refuse genuinely-missing data.
# B2 contract: empty window → None, never extrapolate.
_BRACKET_HALF_WIDTH = 3

# Asymmetric edge-bracket extension (#1163-followup).
#
# TTartisan chart templates render curves with up to ~8 px of slack
# between the printed plot axis and where the curves actually start —
# e.g. the AF 27mm chart's curves begin at x=92 px when the plot box
# left edge is x=87, so the corner sample at fraction=0.0 (target_x=87)
# with the standard ±3 window looks in [84, 90] and finds nothing
# (curve only starts at x=92). The same effect occurs at the right edge.
# Across the 19-chart TTartisan cohort, observed left/right slacks range
# from 0 to 8 px.
#
# When `target_x` is at or near a plot-box edge, the bracket extends
# INWARD by `_EDGE_BRACKET_INWARD` px to bridge the slack. The opposite
# direction stays at `_BRACKET_HALF_WIDTH` so we never reach past the
# plot edge into chrome (axis labels, ticks). Triggers only when
# `target_x` is within `_BRACKET_HALF_WIDTH` of the plot edge — the
# 2 corner positions in practice.
#
# Sized at 5 (not the observed maximum 8) because on charts with sharp
# corner crashes (AF 35mm at f/1.8: solid black S10 drops from 0.95 to
# 0.37 in the last ~1mm), reaching past 5 px into the crash region picks
# up a value far from the actual corner position, dropping render-match
# precision. The 5-px window covers the majority of observed slack
# without distorting curves with extreme corner dynamics. Lenses with
# 6–8 px slack lose corner recovery; the standard B2 fail-safe still
# applies (None when no pixel found within the window).
_EDGE_BRACKET_INWARD = 5

# Half-width of the tight column window used to snap a DP-rasterised
# sample to the raw-mask centroid. When the raw mask has ink within
# this window of the sample target, the centroid of that ink is more
# faithful to the chart artist's stroke than the dilated DP path's
# centerline (which sits ~half a stroke width below the true line
# because of dilation + antialiasing). When the raw mask is empty,
# we fall back to the skeleton's own y — preserving DP continuity
# across dash gaps.
_RAW_SNAP_HALF_WIDTH = 5

# Half-width of the y window in which raw-mask ink near the
# skeleton's predicted y counts as "this curve's ink." A bit wider
# than half a typical stroke thickness so the snap finds the line
# even when the DP path is biased away from its true centerline.
_RAW_SNAP_DY_HALF = 8


def sample_skeleton_at_fraction(
    skeleton: np.ndarray,
    fraction: float,
    plot_box: PlotBox,
    raw_mask: np.ndarray | None = None,
) -> float | None:
    """Sample a skeleton at one fraction of plot width.

    Returns the MTF value (0..1) at that point, or `None` when no
    skeleton pixel exists within `_BRACKET_HALF_WIDTH` columns of the
    target — B2 fail-safe.

    When ``raw_mask`` is supplied (DP dispatch), the sample is snapped
    to the raw-mask ink centroid within a tight window around the
    skeleton's predicted y. This restores the pixel-accuracy that
    raw-mask anchoring gave on solid strokes, without losing the DP
    smoothness prior's interpolation across dash gaps (the snap is a
    no-op when no raw ink is present).
    """
    if not 0.0 <= fraction <= 1.0:
        raise ValueError(f"fraction out of range: {fraction}")

    target_x = int(round(plot_box.x_left + fraction * plot_box.width))
    # Asymmetric edge bracket: when target_x is near the plot edge, the
    # curve may start a few px inside; extend the search inward while
    # keeping the opposite side tight (never reach past the plot edge
    # into chrome). At mid-field both sides use _BRACKET_HALF_WIDTH.
    inward_lo = (
        _EDGE_BRACKET_INWARD
        if target_x > plot_box.x_right - _BRACKET_HALF_WIDTH
        else _BRACKET_HALF_WIDTH
    )
    inward_hi = (
        _EDGE_BRACKET_INWARD
        if target_x < plot_box.x_left + _BRACKET_HALF_WIDTH
        else _BRACKET_HALF_WIDTH
    )
    x_lo = max(plot_box.x_left, target_x - inward_lo)
    x_hi = min(plot_box.x_right, target_x + inward_hi)

    window = skeleton[plot_box.y_top : plot_box.y_bottom + 1, x_lo : x_hi + 1]
    ys_in_window = np.where(window.any(axis=1))[0]
    if ys_in_window.size == 0:
        return None
    skel_y_abs = float(np.median(ys_in_window)) + plot_box.y_top

    if raw_mask is not None:
        snap_y = _snap_to_raw_centroid(
            raw_mask, target_x, int(round(skel_y_abs)), plot_box
        )
        if snap_y is not None:
            return y_pixel_to_mtf(snap_y, plot_box)

    return y_pixel_to_mtf(skel_y_abs, plot_box)


def _snap_to_raw_centroid(
    raw_mask: np.ndarray, target_x: int, skel_y: int, plot_box: PlotBox
) -> float | None:
    """Centroid y of raw-mask ink in a tight window around (target_x, skel_y).

    Returns None when the window has no ink, so the caller can fall
    back to the skeleton's own y. The window is intentionally small
    (a few columns, a few rows): wide enough to find the real stroke
    around an anti-aliased DP centerline, narrow enough that we won't
    snap to a different curve's ink.
    """
    h, w = raw_mask.shape
    x0 = max(plot_box.x_left, target_x - _RAW_SNAP_HALF_WIDTH)
    x1 = min(plot_box.x_right, target_x + _RAW_SNAP_HALF_WIDTH)
    y0 = max(plot_box.y_top, skel_y - _RAW_SNAP_DY_HALF)
    y1 = min(plot_box.y_bottom, skel_y + _RAW_SNAP_DY_HALF)
    if x1 < x0 or y1 < y0:
        return None
    sub = raw_mask[y0 : y1 + 1, x0 : x1 + 1]
    if not sub.any():
        return None
    ys, _ = np.nonzero(sub)
    return float(ys.mean()) + y0


def sample_positions_mm(
    plot_box: PlotBox, image_height_mm: float
) -> tuple[float, ...]:
    """The 11 image-height-mm positions corresponding to the sample fractions."""
    return tuple(round(f * image_height_mm, 4) for f in SAMPLE_FRACTIONS)
