"""Skeleton + continuous-pick curve extraction (ports the legacy approach).

This module mirrors the per-curve extraction approach used by the retired
`tools/mtf-extract-skeleton.py`: dilate the per-color mask, skeletonize,
split connected components by mean-y to isolate the upper-frequency curve
from the lower-frequency curve, then walk each CC column-by-column picking
the branch closest to the previous y (`pick_continuous_curve` from #931).

Used by the Tokina wide-zoom dispatch where per-column ridge tracking
(`ridge.py`) fragmented the curves at coincidence regions and produced
sparse coverage. The continuous-pick approach is robust to:

- Dashed-line fragments: a thin dilation merges adjacent dashes into one CC.
- Curve coincidence: when two curves overlap, the merged ridge gets
  attributed to whichever curve's CC contains it; downstream sibling-fill
  (in `sampling.py`) propagates the value to the other curve at coincident
  positions.
- Edge fall-off: the continuous-pick walk extends as far as the skeleton
  goes, regardless of which fragment it came from.

The output format matches every other dispatch: `{field_name: skeleton mask}`
that the existing 11-point sampler reads.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from skimage.morphology import skeletonize

from .types import PlotBox


# y-distance below which skeleton pixels at the same x belong to one curve
# branch. Larger values merge two genuinely separate curves; smaller ones
# split a single anti-aliased curve into two branches. Sized to the legacy
# tool's value (3 px).
_BRANCH_GAP_PX: int = 3


# Horizontal close kernel width — bridges dash gaps within a single curve
# along the curve direction. Sized large enough to span the largest dash
# gap on the Tokina wide-zoom blue curve (~25-30 px) while staying narrow
# enough not to merge anti-aliased halos of adjacent curves.
_HCLOSE_KERNEL_WIDTH: int = 41
_HCLOSE_KERNEL_HEIGHT: int = 1


@dataclass(frozen=True)
class CurvePoints:
    """An x→y mapping for one continuous curve, ordered by x."""

    points: tuple[tuple[int, float], ...]


def _horizontal_close(mask: np.ndarray) -> np.ndarray:
    """Wide horizontal close to bridge dash gaps within one curve.

    A solid red curve already forms one CC; a dashed blue curve needs
    its fragments bridged into one CC so the mean-y CC ranking can
    separate "upper-curve component" from "lower-curve component."
    The kernel is horizontal only (1px tall) to bridge along the curve
    direction without thickening it vertically — preserves the y-gap
    between the two curves of one color.
    """
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (_HCLOSE_KERNEL_WIDTH, _HCLOSE_KERNEL_HEIGHT)
    )
    return cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)


def _skeleton_to_branches(
    skeleton: np.ndarray, plot_box: PlotBox
) -> dict[int, list[float]]:
    """Per-column branch centroids — `skeleton_to_curve` from the legacy code.

    At each x column in the plot, find skeleton pixels and cluster them
    into branches separated by gaps > _BRANCH_GAP_PX in y. Each branch
    yields one centroid (mean y). Output is x → [centroid_y, ...]; columns
    with no skeleton are omitted.
    """
    out: dict[int, list[float]] = {}
    for x in range(plot_box.x_left, plot_box.x_right + 1):
        ys = np.where(skeleton[plot_box.y_top : plot_box.y_bottom + 1, x])[0]
        if len(ys) == 0:
            continue
        ys_abs = ys + plot_box.y_top
        branches: list[list[int]] = []
        current = [int(ys_abs[0])]
        for y in ys_abs[1:]:
            if int(y) - current[-1] <= _BRANCH_GAP_PX:
                current.append(int(y))
            else:
                branches.append(current)
                current = [int(y)]
        branches.append(current)
        out[x] = [sum(b) / len(b) for b in branches]
    return out


def _pick_continuous_curve(branches_by_x: dict[int, list[float]]) -> CurvePoints:
    """Greedy y-continuity pick — `pick_continuous_curve` from legacy.

    Walk x columns left-to-right. At each column with multiple branches,
    pick the one closest to the previous column's chosen y. At the first
    column, pick the topmost branch (lowest y in image coordinates =
    highest MTF). This resolves multi-branch ambiguity from dashed lines
    or noise without ever fabricating data — every output point is a real
    column centroid.
    """
    if not branches_by_x:
        return CurvePoints(points=())
    sorted_xs = sorted(branches_by_x.keys())
    points: list[tuple[int, float]] = []
    prev_y: float | None = None
    for x in sorted_xs:
        centroids = branches_by_x[x]
        if prev_y is None:
            chosen = min(centroids)  # topmost = highest MTF
        else:
            chosen = min(centroids, key=lambda c: abs(c - prev_y))
        points.append((x, chosen))
        prev_y = chosen
    return CurvePoints(points=tuple(points))


# Two CCs at the same hue whose mean_y are within this many pixels of
# each other are fragments of one curve (the horizontal close didn't
# bridge every dash gap, especially near steep slopes). Merging them
# before mean-y ranking ensures the upper-curve CC is the topmost
# curve overall, not the topmost fragment. Kept tight (12 px ≈ 1.5%
# of plot height) so the upper curve at OTF 0.95 and the lower curve
# at OTF 0.85 — Tokina wide-zoom near-center separation — stay
# distinct.
_CC_MEAN_Y_MERGE_PX: float = 12.0


def _strip_chrome_rows(
    skeleton: np.ndarray, plot_box: PlotBox, min_width_fraction: float = 0.85
) -> np.ndarray:
    """Zero rows with ≥ `min_width_fraction` horizontal coverage.

    Printed plot-frame borders and OTF gridlines span the full plot
    width as nearly-continuous lines. Without stripping them, the top
    border at y=plot_box.y_top becomes a high-area CC at mean_y near
    the top — outranking the actual upper curve.
    """
    cleaned = skeleton.copy().astype(np.uint8)
    width = plot_box.x_right - plot_box.x_left + 1
    min_count = int(min_width_fraction * width)
    for y in range(plot_box.y_top, plot_box.y_bottom + 1):
        row = cleaned[y, plot_box.x_left : plot_box.x_right + 1]
        if int(row.sum()) >= min_count:
            cleaned[y, plot_box.x_left : plot_box.x_right + 1] = 0
    return cleaned


def _component_masks_with_mean_y(
    skeleton: np.ndarray, min_area: int = 20
) -> list[tuple[np.ndarray, float]]:
    """Connected components above an area floor, with mean-y per component.

    Tighter min_area than ridge.py's because skeletonized whole-curve CCs
    here are large (hundreds of pixels); the floor rejects single-dash
    fragments and stray noise. CCs within `_CC_MEAN_Y_MERGE_PX` are
    merged (fragments of one curve that the horizontal close didn't
    fully bridge). Returns sorted by mean-y ascending (top first).
    """
    sk = skeleton.astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        sk, connectivity=8
    )
    raw: list[tuple[np.ndarray, float]] = []
    for label in range(1, num_labels):
        if int(stats[label, cv2.CC_STAT_AREA]) < min_area:
            continue
        component = (labels == label).astype(np.uint8)
        ys = np.nonzero(component)[0]
        if ys.size == 0:
            continue
        raw.append((component, float(ys.mean())))
    raw.sort(key=lambda c: c[1])
    # Merge CCs whose mean_y is within tolerance — they're fragments
    # of one curve.
    merged: list[tuple[np.ndarray, float]] = []
    for comp, mean_y in raw:
        if merged and abs(mean_y - merged[-1][1]) <= _CC_MEAN_Y_MERGE_PX:
            prev_comp, _ = merged[-1]
            fused = prev_comp | comp
            ys = np.nonzero(fused)[0]
            merged[-1] = (fused, float(ys.mean()))
        else:
            merged.append((comp, mean_y))
    return merged


def _curve_to_skeleton(curve: CurvePoints, shape: tuple[int, int]) -> np.ndarray:
    """Rasterize a CurvePoints into a 1-px skeleton mask."""
    sk = np.zeros(shape, dtype=np.uint8)
    for x, y in curve.points:
        sk[int(round(y)), x] = 1
    return sk


def extract_two_curves_per_hue(
    mask: np.ndarray, plot_box: PlotBox
) -> tuple[CurvePoints, CurvePoints]:
    """Extract upper and lower curve per hue mask via skeleton + continuous pick.

    1. Wide horizontal close to bridge dash gaps within one curve.
    2. Skeletonize to 1-px lines.
    3. Split into connected components; rank by mean-y.
    4. For each of the top two CCs (top = upper-frequency, bottom = lower-
       frequency), walk skeleton columns to get one branch per x, then
       greedy y-continuity-pick to a single x→y curve.

    Returns (upper_curve, lower_curve). Either may be empty when the mask
    has no qualifying CC at that band.
    """
    closed = _horizontal_close(mask)
    skel = skeletonize(closed.astype(bool)).astype(np.uint8)
    skel = _strip_chrome_rows(skel, plot_box)
    components = _component_masks_with_mean_y(skel)

    if not components:
        return CurvePoints(points=()), CurvePoints(points=())

    # Pick the two highest-area CCs (the actual whole-curve components,
    # not stray dash fragments at the top/bottom of the plot), then rank
    # those two by mean-y: top = upper-frequency, bottom = lower-frequency.
    # If only one survives, treat it as both coincident curves.
    by_area = sorted(components, key=lambda c: int(c[0].sum()), reverse=True)
    top_two = by_area[:2]
    top_two.sort(key=lambda c: c[1])  # by mean-y, ascending
    if len(top_two) == 1:
        upper_cc = top_two[0][0]
        lower_cc = upper_cc
    else:
        upper_cc = top_two[0][0]
        lower_cc = top_two[1][0]

    upper_branches = _skeleton_to_branches(upper_cc, plot_box)
    lower_branches = _skeleton_to_branches(lower_cc, plot_box)
    upper = _pick_continuous_curve(upper_branches)
    lower = _pick_continuous_curve(lower_branches)
    return upper, lower
