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
Viterbi pass extracts the residual curve. The two paths are sorted by
verified mean-y; the smaller-mean-y path is the upper-MTF curve.

Each DP path IS one curve. The path's y at every column is that
curve's value — the smoothness prior already interpolates across dash
gaps and antialiasing holes. ``curves_to_field_skeletons`` rasterises
the path everywhere; no anchoring, no support-interval rebuild, no
per-column B2 gate. When two curves of the same hue converge to a
single ink stripe (e.g. 10S and 30S coincident in the middle of a
plot), both paths report the shared y and both readings are correct —
the optical reality is "both curves equal here," not "only one curve
exists here."

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

# Verified-median window for path-ordering. Each DP path's mean-y is
# computed over columns where the raw mask has ink within +/- these
# half-widths of the predicted point. The smaller-mean-y path is the
# upper-MTF curve.
_RAW_DX_HALF: int = 25
_RAW_DY_HALF: int = 6


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
    """Rasterize two DP paths into two skeleton masks (Option 2).

    The DP path is the answer at every column — the smoothness prior
    has already interpolated across dash gaps and antialiasing holes.
    This function just rasterizes each path's y at every column.

    No anchoring, no labelling, no support-interval reconstruction
    happens here. The B2 check ("is there real ink near this sample
    point?") runs at sampling time in `pipeline/sampling.py`, against
    each of the 11 fixed sample fractions only. That keeps the safety
    gate at the moment it matters and removes the per-column logic
    that kept producing edge-case mislabels.

    `raw_mask` is used only for its shape (the skeletons match the
    full image dimensions so downstream tools can look up positions
    in absolute coordinates).
    """
    del plot_box  # unused
    shape = raw_mask.shape
    h, w = shape
    upper_sk = np.zeros(shape, dtype=np.uint8)
    lower_sk = np.zeros(shape, dtype=np.uint8)
    for x, y in upper_curve.points:
        xi, yi = int(x), int(round(y))
        if 0 <= yi < h and 0 <= xi < w:
            upper_sk[yi, xi] = 1
    for x, y in lower_curve.points:
        xi, yi = int(x), int(round(y))
        if 0 <= yi < h and 0 <= xi < w:
            lower_sk[yi, xi] = 1
    return upper_sk, lower_sk


def dilate_for_dp(mask: np.ndarray) -> np.ndarray:
    """Return the dilated mask used as the DP emission source.

    Exposed so callers (dispatch, render-match) can re-use the same
    "is data near here" check the extractor used at sampling time.
    """
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (_DILATE_KERNEL_W, _DILATE_KERNEL_H)
    )
    return cv2.dilate(mask.astype(np.uint8), kernel)
