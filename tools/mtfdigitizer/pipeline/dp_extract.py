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
mean-y so the upper one is the upper-frequency curve in the per-hue
convention.

B2 is preserved at sampling time: a path point is reported only when
the dilated mask has any ink within a small window — DP paths through
all-white columns still produce a y-coordinate, but the sampler refuses
to emit it.

Performance: the Viterbi loop is the hot path. For each column we sweep
``2*max_jump + 1`` candidate predecessors with a `np.roll` per offset.
At plot size 1338x777 with ``max_jump=30`` this is ~10^7 ops total — a
few hundred ms in NumPy, dominated by the inner sweep.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .types import PlotBox


# Tuned once against the Tokina reference set (#1003 calibration run).
# These defaults move with `extract_two_curves_dp`; per-chart overrides
# can be added via kwargs if a future profile needs them.
_ALPHA: float = 0.30
_MAX_JUMP: int = 30
_DILATE_KERNEL_W: int = 51
_DILATE_KERNEL_H: int = 3
_ERASE_HALF: int = 18
_ERASE_PENALTY: float = 5.0
_INF: float = 1e18


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
    dp = np.empty_like(emission, dtype=np.float64)
    back = np.full((height, width), -1, dtype=np.int32)
    dp[:, 0] = emission[:, 0]
    for x in range(1, width):
        prev = dp[:, x - 1]
        best = np.full(height, _INF)
        bi = np.full(height, -1, dtype=np.int32)
        for dy in range(-max_jump, max_jump + 1):
            # candidate[y] = prev[y - dy] + alpha * |dy|, valid where
            # 0 <= y - dy < height.
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

    Operates on the plot-box crop of the mask: returns curves in absolute
    image coordinates so the caller can rasterize without re-translating.
    """
    box = mask[
        plot_box.y_top : plot_box.y_bottom + 1,
        plot_box.x_left : plot_box.x_right + 1,
    ].astype(np.uint8)
    height, width = box.shape
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (dilate_kernel_w, _DILATE_KERNEL_H)
    )
    dilated = cv2.dilate(box, kernel)
    emission = (dilated == 0).astype(np.float64)

    first = _viterbi_path(emission, alpha, max_jump)
    second_emission = emission.copy()
    for x in range(width):
        y0 = max(0, int(first[x]) - erase_half)
        y1 = min(height, int(first[x]) + erase_half + 1)
        second_emission[y0:y1, x] = _ERASE_PENALTY
    second = _viterbi_path(second_emission, alpha, max_jump)

    upper, lower = (first, second) if first.mean() < second.mean() else (second, first)
    upper_pts = tuple(
        (x + plot_box.x_left, float(y + plot_box.y_top))
        for x, y in enumerate(upper)
    )
    lower_pts = tuple(
        (x + plot_box.x_left, float(y + plot_box.y_top))
        for x, y in enumerate(lower)
    )
    return CurvePoints(points=upper_pts), CurvePoints(points=lower_pts)


# Sampling-time honesty window for B2. A DP path always emits a y per
# column — but if the dilated mask has no ink within this window of
# the predicted point, the sampler should treat it as missing data.
_B2_DX_HALF: int = 5
_B2_DY_HALF: int = 10


def curve_to_skeleton_b2(
    curve: CurvePoints,
    dilated_mask: np.ndarray,
    shape: tuple[int, int],
) -> np.ndarray:
    """Rasterize a CurvePoints into a 1-px skeleton mask, honoring B2.

    Emits a skeleton pixel at (x, y) only when the dilated mask has any
    ink within a small window of (x, y). DP-extrapolated columns (where
    the path crosses pure white) produce no skeleton pixel, so the
    11-point sampler returns None there — same B2 contract as the
    other dispatches.
    """
    sk = np.zeros(shape, dtype=np.uint8)
    h, w = dilated_mask.shape
    for x, y in curve.points:
        xi = int(x)
        yi = int(round(y))
        x0 = max(0, xi - _B2_DX_HALF)
        x1 = min(w, xi + _B2_DX_HALF + 1)
        y0 = max(0, yi - _B2_DY_HALF)
        y1 = min(h, yi + _B2_DY_HALF + 1)
        if dilated_mask[y0:y1, x0:x1].any():
            sk[yi, xi] = 1
    return sk


def dilate_for_dp(mask: np.ndarray) -> np.ndarray:
    """Return the dilated mask used as the DP emission source.

    Exposed so callers (dispatch, render-match) can re-use the same
    "is data near here" check the extractor used at sampling time.
    """
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (_DILATE_KERNEL_W, _DILATE_KERNEL_H)
    )
    return cv2.dilate(mask.astype(np.uint8), kernel)
