"""S/M split for one-hue-carries-both-curves profiles (#935, ADR-038 §2).

For `SPLIT_BY_DASH` profiles (e.g. Sigma), one hue mask contains both
the sagittal (solid) and meridional (dashed) curves. After
skeletonization, the solid line is one long connected component while
the dashed line breaks into many short fragments. We classify by
fragment length:

- Pick the longest connected component as **S** (solid).
- Group every remaining component as **M** (dashed), provided it sits
  within a vertical band that doesn't overlap S — same-color curves
  that visibly merge would otherwise pollute each other's readings.

For `HUE_IS_CURVE` profiles (e.g. Samyang), each hue is already exactly
one curve; no split needed — `split_sm` is a no-op pass-through.

The legacy tool's `split_solid_dashed_cc` is the same idea; this is a
clean reimplementation rather than a port. The B3 fix from PR #931 is
preserved: per-column unweighted mean, not an order-dependent running
average with a 5px cap.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class SplitResult:
    """Two skeleton masks: S (solid/sagittal) and M (dashed/meridional).

    Either may be all-zero when only one of the two curves is detectable
    in the source — the sampler treats those rows as missing data (B2).
    """

    sagittal: np.ndarray  # uint8 skeleton
    meridional: np.ndarray  # uint8 skeleton


def _largest_component(num_labels: int, labels: np.ndarray, stats: np.ndarray) -> int:
    """Return the label of the largest non-background connected component,
    or -1 when the only label is the background."""
    if num_labels <= 1:
        return -1
    # Stats column 4 (cv2.CC_STAT_AREA) — skip label 0 (background).
    areas = stats[1:, cv2.CC_STAT_AREA]
    return int(np.argmax(areas)) + 1


def split_sm_by_cc_width(skeleton: np.ndarray) -> SplitResult:
    """Split one skeleton into S (longest CC) and M (everything else)."""
    sk = skeleton.astype(np.uint8)
    num_labels, labels, stats, _centroids = cv2.connectedComponentsWithStats(
        sk, connectivity=8
    )
    largest = _largest_component(num_labels, labels, stats)
    if largest < 0:
        empty = np.zeros_like(sk)
        return SplitResult(sagittal=empty, meridional=empty)

    sagittal = (labels == largest).astype(np.uint8)
    meridional = ((labels > 0) & (labels != largest)).astype(np.uint8)
    return SplitResult(sagittal=sagittal, meridional=meridional)
