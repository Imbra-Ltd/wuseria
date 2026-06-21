"""Image loader shared across the mtfdigitizer package.

OpenCV's `imread` drops the alpha channel by default, which is fine for
JPG charts but wrong for the many PNG charts published with a transparent
background — those load as pre-multiplied black-on-transparent, breaking
any background-aware logic (plot-box detection, white-background priors).

This loader composites RGBA charts onto a white background, then returns
BGR. The output is what every downstream stage of the digitizer expects.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def load_chart_bgr(image_path: str | Path) -> np.ndarray:
    """Load an MTF chart as BGR, compositing alpha onto white.

    Returns a (H, W, 3) uint8 array. Raises FileNotFoundError if the
    path doesn't exist, ValueError if the file can't be decoded.
    """
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"image not found: {path}")
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError(f"could not decode image: {path}")
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.shape[2] == 3:
        return image
    if image.shape[2] == 4:
        bgr = image[:, :, :3].astype(np.float32)
        alpha = image[:, :, 3:4].astype(np.float32) / 255.0
        white = np.full_like(bgr, 255.0)
        composited = bgr * alpha + white * (1.0 - alpha)
        return composited.astype(np.uint8)
    raise ValueError(f"unsupported channel count {image.shape[2]} in {path}")


def load_chart_hsv(image_path: str | Path) -> np.ndarray:
    """Load an MTF chart as HSV (after alpha composite)."""
    return cv2.cvtColor(load_chart_bgr(image_path), cv2.COLOR_BGR2HSV)


def load_chart_gray(image_path: str | Path) -> np.ndarray:
    """Load an MTF chart as a single-channel grayscale array.

    Composites alpha onto white via load_chart_bgr first so transparent
    PNG backgrounds become white (not black) under conversion.
    """
    return cv2.cvtColor(load_chart_bgr(image_path), cv2.COLOR_BGR2GRAY)
