"""Plot-box geometry (#935, ADR-038 §2 'axis and grid detection').

The pipeline needs to know which rectangle of the image is the plot
area, because:

- y-pixel → MTF value mapping uses `y_top` (MTF=1) and `y_bottom` (MTF=0)
- x-pixel → image-height-mm mapping uses `x_left` (mm=0) and `x_right` (mm=max)

Detection across chart styles is genuinely hard (multi-panel stacks,
solid vs dashed axes, dark vs white backgrounds, transparency). For the
two profiles #935 ships with — Sigma and Samyang — call sites supply
the box directly (measured against the reference set). Auto-detection
arrives later as a separate task.

The `bbox_to_mtf_value` and `bbox_to_image_height_mm` helpers convert
between pixel coordinates and chart-space values given a `PlotBox`.
"""

from __future__ import annotations

from .types import PlotBox


def y_pixel_to_mtf(y_pixel: float, plot_box: PlotBox) -> float:
    """Convert a y pixel coordinate to MTF value (0..1).

    The plot's y-axis runs from MTF=1 at `y_top` to MTF=0 at `y_bottom`.
    Image y increases downward, so the conversion inverts.

    Out-of-box values are returned as-clipped to [0, 1] — the caller
    decides whether to treat a clamped value as missing data (the
    extractor does, via the sampling stage's gap detection).
    """
    if plot_box.height == 0:
        raise ValueError(f"degenerate plot box height: {plot_box}")
    mtf = (plot_box.y_bottom - y_pixel) / plot_box.height
    return max(0.0, min(1.0, mtf))


def x_pixel_to_image_height_mm(
    x_pixel: float, plot_box: PlotBox, image_height_mm: float
) -> float:
    """Convert an x pixel coordinate to image-height in mm.

    The plot's x-axis runs from 0mm at `x_left` to `image_height_mm`
    at `x_right`.
    """
    if plot_box.width == 0:
        raise ValueError(f"degenerate plot box width: {plot_box}")
    return (x_pixel - plot_box.x_left) / plot_box.width * image_height_mm


def image_height_mm_to_x_pixel(
    mm: float, plot_box: PlotBox, image_height_mm: float
) -> float:
    """Inverse of x_pixel_to_image_height_mm."""
    if image_height_mm == 0:
        raise ValueError("image_height_mm cannot be zero")
    return plot_box.x_left + (mm / image_height_mm) * plot_box.width
