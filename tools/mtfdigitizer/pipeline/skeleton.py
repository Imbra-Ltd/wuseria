"""Mask → 1px skeleton (#935, ADR-038 §2).

Morphological close with a horizontally-biased kernel bridges dashed
lines into continuous strokes, then Zhang-Suen skeletonization reduces
them to 1-pixel-wide centerlines. Both are kept from the legacy tool —
ADR-038 §2 explicitly retains skeletonization.
"""

from __future__ import annotations

import cv2
import numpy as np
from skimage.morphology import skeletonize


# Horizontal kernel width — large enough to bridge typical dash gaps in
# Sigma/Samyang charts, small enough not to merge adjacent S/M curves
# that genuinely run parallel. Picked from the legacy tool's value;
# revisit if dash-bridging proves too aggressive or too weak on new
# chart styles in #935+ work.
_CLOSE_KERNEL_WIDTH = 7
_CLOSE_KERNEL_HEIGHT = 1


def close_and_skeletonize(
    mask: np.ndarray, close_kernel_width: int | None = None
) -> np.ndarray:
    """Bridge dashes with a horizontal morphological close, then skeletonize.

    Input: binary mask (any truthy dtype).
    Output: uint8 mask, 1 where the skeleton sits, 0 elsewhere.

    `close_kernel_width` overrides the default kernel width for profiles
    whose chart family has wider dash gaps (e.g. Fujifilm permfreq).
    None uses the module default.
    """
    width = (
        close_kernel_width
        if close_kernel_width is not None
        else _CLOSE_KERNEL_WIDTH
    )
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (width, _CLOSE_KERNEL_HEIGHT)
    )
    closed = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
    skeleton = skeletonize(closed.astype(bool))
    return skeleton.astype(np.uint8)
