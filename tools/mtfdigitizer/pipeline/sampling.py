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


def sample_skeleton_at_fraction(
    skeleton: np.ndarray,
    fraction: float,
    plot_box: PlotBox,
) -> float | None:
    """Sample a skeleton at one fraction of plot width.

    Returns the MTF value (0..1) at that point, or `None` when no
    skeleton pixel exists within `_BRACKET_HALF_WIDTH` columns of the
    target — B2 fail-safe.
    """
    if not 0.0 <= fraction <= 1.0:
        raise ValueError(f"fraction out of range: {fraction}")

    target_x = int(round(plot_box.x_left + fraction * plot_box.width))
    x_lo = max(plot_box.x_left, target_x - _BRACKET_HALF_WIDTH)
    x_hi = min(plot_box.x_right, target_x + _BRACKET_HALF_WIDTH)

    window = skeleton[plot_box.y_top : plot_box.y_bottom + 1, x_lo : x_hi + 1]
    ys_in_window = np.where(window.any(axis=1))[0]
    if ys_in_window.size == 0:
        return None
    median_y = float(np.median(ys_in_window)) + plot_box.y_top
    return y_pixel_to_mtf(median_y, plot_box)


def sample_positions_mm(
    plot_box: PlotBox, image_height_mm: float
) -> tuple[float, ...]:
    """The 11 image-height-mm positions corresponding to the sample fractions."""
    return tuple(round(f * image_height_mm, 4) for f in SAMPLE_FRACTIONS)
