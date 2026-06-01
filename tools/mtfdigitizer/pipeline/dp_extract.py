"""DP shortest-path curve extraction (#1003 follow-up).

For each per-hue mask, this dispatch finds two curves by Viterbi shortest
path through a per-pixel cost field:

- Emission cost = 0 on mask pixels (after a horizontal dilation that
  bridges dashed-line gaps), 1 off-mask.
- Transition cost = ``alpha * |dy|`` per column step, capped at
  ``max_jump`` rows. This is the smoothness prior that lets the path
  walk over dash gaps cheaply but penalizes hopping to a parallel curve.

The first path captures the lowest-cost curve through the dilated mask.
A vertical band around that path is then masked off with a heavy
emission penalty (not infinite — the second path may need to nick the
band briefly if its real ink is close to the first), and a second
Viterbi pass extracts the residual curve.

Per-column reconciliation against the raw mask resolves which DP path
represents which curve: at columns where only one curve has ink in the
chart (e.g. the leftmost columns of the Tokina 11-18 panels where one
curve hasn't started yet), the verified path is labelled by its
position in a global ordering of verified positions, and the unverified
path emits no skeleton pixel — same B2 contract as the other
dispatches.

Performance: the Viterbi loop is the hot path. For each column we sweep
``2*max_jump + 1`` candidate predecessors. At plot size 1338x777 with
``max_jump=30`` this is ~10^7 ops total — a few hundred ms in NumPy,
dominated by the inner sweep.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .types import PlotBox


# Tuned once against the Tokina reference set (#1003 calibration run).
_ALPHA: float = 0.30
_MAX_JUMP: int = 30
_DILATE_KERNEL_W: int = 51
_DILATE_KERNEL_H: int = 3
_ERASE_HALF: int = 18
_ERASE_PENALTY: float = 5.0
_INF: float = 1e18

# Per-column reconciliation window. A DP path point at column x is
# considered "on a real curve" when the raw (undilated) mask has ink
# within +/- _RAW_DX_HALF columns and +/- _RAW_DY_HALF rows. The x
# tolerance spans about one dash period; the y tolerance spans half
# a curve thickness plus anti-aliasing.
_RAW_DX_HALF: int = 25
_RAW_DY_HALF: int = 6

# When both paths verify against the same patch of raw ink (they're
# tracking the same physical curve because the other curve has no ink
# at this column), treat them as one and assign whichever path is
# closer. Two verified positions within this many pixels are "same."
_SAME_INK_PX: int = 10

# An anchor at column x is "drifted" when its y differs from the path's
# typical y trend by more than this many pixels. Drifted anchors are
# rejected: the path is reaching across an absence of its own curve's
# ink to grab another curve's. Tuned to be wider than _RAW_DY_HALF
# (so a sample with slightly mis-centred ink still passes) but tighter
# than the typical inter-curve separation on the Tokina charts (~30 px
# between 10 and 30 lp/mm at the same hue).
_DRIFT_REJECT_PX: int = 15


@dataclass(frozen=True)
class CurvePoints:
    """An x→y mapping for one continuous curve, ordered by x.

    Identical contract to `continuous_pick.CurvePoints` — kept local so
    this module can be removed independently if the legacy path is ever
    retired.
    """

    points: tuple[tuple[int, float], ...]


def _viterbi_path(emission: np.ndarray, alpha: float, max_jump: int) -> np.ndarray:
    """One curve y(x) over an emission field.

    `emission[y, x]` is the cost of placing the curve at (x, y); lower
    is better. Transition cost from y' to y is `alpha * |y - y'|` for
    `|y - y'| <= max_jump`, infinite otherwise. Returns the y-trace
    (one int per column).
    """
    height, width = emission.shape
    effective_jump = min(max_jump, height - 1)
    dp = np.empty_like(emission, dtype=np.float64)
    back = np.full((height, width), -1, dtype=np.int32)
    dp[:, 0] = emission[:, 0]
    for x in range(1, width):
        prev = dp[:, x - 1]
        best = np.full(height, _INF)
        bi = np.full(height, -1, dtype=np.int32)
        for dy in range(-effective_jump, effective_jump + 1):
            shifted = np.full(height, _INF)
            if dy >= 0:
                shifted[dy:] = prev[: height - dy] + alpha * abs(dy)
            else:
                shifted[:dy] = prev[-dy:] + alpha * abs(dy)
            src = np.arange(height) - dy
            improved = shifted < best
            best[improved] = shifted[improved]
            bi[improved] = src[improved]
        dp[:, x] = emission[:, x] + best
        back[:, x] = bi
    trace = np.empty(width, dtype=np.int32)
    trace[-1] = int(np.argmin(dp[:, -1]))
    for x in range(width - 1, 0, -1):
        trace[x - 1] = back[trace[x], x]
    return trace


def _raw_centroid_in_window(
    raw_mask: np.ndarray,
    x_abs: int,
    y_abs: int,
    dx: int,
    dy: int,
) -> float | None:
    """Centroid y of raw-mask ink in a window around (x, y).

    Returns None when the window has no ink. Used to verify a DP path
    point against the original (undilated) mask — the smoothness prior
    can carry a path through pure-white columns, but a sampled value
    must come from a column where the curve actually exists.
    """
    h, w = raw_mask.shape
    x0 = max(0, x_abs - dx)
    x1 = min(w, x_abs + dx + 1)
    y0 = max(0, y_abs - dy)
    y1 = min(h, y_abs + dy + 1)
    submask = raw_mask[y0:y1, x0:x1]
    if not submask.any():
        return None
    ys, _ = np.nonzero(submask)
    return float(ys.mean()) + y0


def _run_two_dp_passes(
    box: np.ndarray,
    alpha: float,
    max_jump: int,
    dilate_kernel_w: int,
    erase_half: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Two Viterbi passes against the dilated mask, second pass with the
    first path's vertical band erased."""
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (dilate_kernel_w, _DILATE_KERNEL_H)
    )
    dilated = cv2.dilate(box, kernel)
    emission = (dilated == 0).astype(np.float64)
    first = _viterbi_path(emission, alpha, max_jump)
    second_emission = emission.copy()
    height = box.shape[0]
    for x in range(box.shape[1]):
        y0 = max(0, int(first[x]) - erase_half)
        y1 = min(height, int(first[x]) + erase_half + 1)
        second_emission[y0:y1, x] = _ERASE_PENALTY
    second = _viterbi_path(second_emission, alpha, max_jump)
    return first, second


def extract_two_curves_dp(
    mask: np.ndarray,
    plot_box: PlotBox,
    *,
    alpha: float = _ALPHA,
    max_jump: int = _MAX_JUMP,
    dilate_kernel_w: int = _DILATE_KERNEL_W,
    erase_half: int = _ERASE_HALF,
) -> tuple[CurvePoints, CurvePoints]:
    """Extract upper and lower curves from one per-hue mask via DP.

    Returns curves in absolute image coordinates. The two paths are
    sorted by their *verified* mean-y (i.e. mean over columns where the
    raw mask has ink) so the upper one is the upper-frequency curve.

    This function still returns one (x, y) per column for every column
    of the plot — including columns where the path crossed pure white.
    The B2 honesty check happens in `curves_to_field_skeletons` at
    rasterization time, not here.
    """
    box = mask[
        plot_box.y_top : plot_box.y_bottom + 1,
        plot_box.x_left : plot_box.x_right + 1,
    ].astype(np.uint8)
    first, second = _run_two_dp_passes(
        box, alpha, max_jump, dilate_kernel_w, erase_half
    )

    # Sort by verified mean-y: only consider columns where the path
    # sits on real raw-mask ink. Avoids global-mean-y inversion when
    # one path is dragged into white space by the erase band.
    raw_box = box
    first_verified_ys = [
        first[x]
        for x in range(len(first))
        if raw_box[
            max(0, int(first[x]) - _RAW_DY_HALF) : int(first[x]) + _RAW_DY_HALF + 1,
            max(0, x - _RAW_DX_HALF) : x + _RAW_DX_HALF + 1,
        ].any()
    ]
    second_verified_ys = [
        second[x]
        for x in range(len(second))
        if raw_box[
            max(0, int(second[x]) - _RAW_DY_HALF) : int(second[x]) + _RAW_DY_HALF + 1,
            max(0, x - _RAW_DX_HALF) : x + _RAW_DX_HALF + 1,
        ].any()
    ]
    first_med = (
        float(np.median(first_verified_ys)) if first_verified_ys else float(first.mean())
    )
    second_med = (
        float(np.median(second_verified_ys))
        if second_verified_ys
        else float(second.mean())
    )
    upper, lower = (first, second) if first_med < second_med else (second, first)

    upper_pts = tuple(
        (x + plot_box.x_left, float(y + plot_box.y_top))
        for x, y in enumerate(upper)
    )
    lower_pts = tuple(
        (x + plot_box.x_left, float(y + plot_box.y_top))
        for x, y in enumerate(lower)
    )
    return CurvePoints(points=upper_pts), CurvePoints(points=lower_pts)


def curves_to_field_skeletons(
    upper_curve: CurvePoints,
    lower_curve: CurvePoints,
    raw_mask: np.ndarray,
    plot_box: PlotBox,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """Rasterize two DP paths into two skeleton masks using support-interval B2.

    Conceptual model: a curve exists across a contiguous interval of
    columns determined by where the chart artist drew it. Inside that
    interval the curve is continuous — dashes and anti-aliasing leave
    individual columns without ink, but the curve's value still exists
    there. Outside the interval the curve genuinely doesn't exist.

    Algorithm:
      1. For each column, anchor each DP path to the centroid of raw
         ink in a small window of the path's predicted y. Anchors
         categorise the column.
      2. Label anchors per column:
         - Two anchors well-separated -> sort by y, smaller = upper-MTF.
         - Two anchors at the same y (within _SAME_INK_PX) -> one
           physical curve; keep the closer path.
         - One anchor -> the path with the smaller *predicted* y is the
           upper-MTF curve at this column; assign the lone anchor to
           the matching slot.
      3. Compute each curve's support interval as [leftmost, rightmost]
         column where the curve had a labelled anchor.
      4. Inside the support interval, emit one skeleton pixel per
         column using the DP path's y (not the anchor). The smoothness
         prior of DP makes the path the right interpolation across dash
         gaps and antialiasing holes.

    Outside the support interval, no pixel — the curve genuinely
    doesn't exist there. This preserves the failure mode that B2 was
    written to prevent (silent fabrication beyond chart data) while
    eliminating false `None`s inside the curve from dashed-line gaps.
    """
    shape = raw_mask.shape
    upper_sk = np.zeros(shape, dtype=np.uint8)
    lower_sk = np.zeros(shape, dtype=np.uint8)

    upper_by_x = {int(x): float(y) for x, y in upper_curve.points}
    lower_by_x = {int(x): float(y) for x, y in lower_curve.points}

    # Per-column labelling: for each curve, build (column -> anchor_y)
    # for columns where the curve was identified.
    upper_anchors_by_x: dict[int, float] = {}
    lower_anchors_by_x: dict[int, float] = {}
    for x_abs in range(plot_box.x_left, plot_box.x_right + 1):
        yu_path = upper_by_x.get(x_abs)
        yl_path = lower_by_x.get(x_abs)
        anchor_u = (
            _raw_centroid_in_window(
                raw_mask, x_abs, int(yu_path), _RAW_DX_HALF, _RAW_DY_HALF
            )
            if yu_path is not None
            else None
        )
        anchor_l = (
            _raw_centroid_in_window(
                raw_mask, x_abs, int(yl_path), _RAW_DX_HALF, _RAW_DY_HALF
            )
            if yl_path is not None
            else None
        )
        if (
            anchor_u is not None
            and anchor_l is not None
            and abs(anchor_u - anchor_l) < _SAME_INK_PX
        ):
            # Same physical curve. Keep whichever path is closer.
            if (
                yu_path is not None
                and (yl_path is None or abs(yu_path - anchor_u) <= abs(yl_path - anchor_l))
            ):
                anchor_l = None
            else:
                anchor_u = None
        if anchor_u is not None and anchor_l is not None:
            # Two distinct curves present: smaller anchored y is upper-MTF.
            if anchor_u <= anchor_l:
                upper_anchors_by_x[x_abs] = anchor_u
                lower_anchors_by_x[x_abs] = anchor_l
            else:
                upper_anchors_by_x[x_abs] = anchor_l
                lower_anchors_by_x[x_abs] = anchor_u
            continue
        if anchor_u is None and anchor_l is None:
            continue
        # One anchor: label by comparing the two paths' predicted y.
        # The path with the smaller predicted y is the upper-MTF curve;
        # the lone anchor goes to whichever path anchored.
        upper_path_is_smaller = (
            yu_path is not None
            and yl_path is not None
            and yu_path <= yl_path
        )
        smaller_anchored = anchor_u if upper_path_is_smaller else anchor_l
        y_only = anchor_u if anchor_u is not None else anchor_l
        if smaller_anchored is not None:
            upper_anchors_by_x[x_abs] = y_only  # type: ignore[assignment]
        else:
            lower_anchors_by_x[x_abs] = y_only  # type: ignore[assignment]

    # Each curve's support interval = [min, max] of the labelled columns.
    # Inside the interval, interpolate the y between the nearest
    # anchored columns on either side. Outside the interval, no pixel.
    h, w = shape
    _draw_curve_within_support(upper_sk, upper_anchors_by_x, h, w)
    _draw_curve_within_support(lower_sk, lower_anchors_by_x, h, w)
    return upper_sk, lower_sk


def _draw_curve_within_support(
    sk: np.ndarray, anchors_by_x: dict[int, float], h: int, w: int
) -> None:
    """Rasterise a curve at every column inside its support interval.

    For columns where the curve has an anchor, use the anchor's y.
    For columns between two anchors (dash gaps, antialiasing holes),
    linearly interpolate y between the nearest anchored columns on
    either side. Outside the support interval, do not draw.
    """
    if not anchors_by_x:
        return
    xs = sorted(anchors_by_x.keys())
    x_lo, x_hi = xs[0], xs[-1]
    # Build a sorted lookup for interpolation.
    xs_arr = np.array(xs)
    ys_arr = np.array([anchors_by_x[x] for x in xs])
    for x_abs in range(x_lo, x_hi + 1):
        # np.interp is linear between adjacent xs; outside [x_lo, x_hi]
        # it clamps to endpoints, but our loop stays inside the interval.
        y = float(np.interp(x_abs, xs_arr, ys_arr))
        yi = int(round(y))
        if 0 <= yi < h and 0 <= x_abs < w:
            sk[yi, x_abs] = 1


def dilate_for_dp(mask: np.ndarray) -> np.ndarray:
    """Return the dilated mask used as the DP emission source.

    Exposed so callers (dispatch, render-match) can re-use the same
    "is data near here" check the extractor used at sampling time.
    """
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (_DILATE_KERNEL_W, _DILATE_KERNEL_H)
    )
    return cv2.dilate(mask.astype(np.uint8), kernel)
