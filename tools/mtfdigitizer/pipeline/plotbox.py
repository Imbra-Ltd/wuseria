"""Plot-box geometry (#935, ADR-038 §2 'axis and grid detection').

The pipeline needs to know which rectangle of the image is the plot
area, because:

- y-pixel → MTF value mapping uses `y_top` (MTF=1) and `y_bottom` (MTF=0)
- x-pixel → image-height-mm mapping uses `x_left` (mm=0) and `x_right` (mm=max)

For most chart families a hand-measured box is recorded against the
reference set. `detect_sigma_plot_box()` (#950, Sigma family only)
automates that step for the `mainstream-2color-solid-dashed` template
shared by every Sigma DC DN C prime — see its docstring for the
detection rule and the Sigma-only scope. Other families still rely on
hand-measured boxes pending family-specific detectors.

The `bbox_to_mtf_value` and `bbox_to_image_height_mm` helpers convert
between pixel coordinates and chart-space values given a `PlotBox`.
"""

from __future__ import annotations

import numpy as np

from ..plotbox_primitives import cluster_consecutive
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


# --- Sigma family auto-detection (#950) -----------------------------------
#
# Detection rule (validated against all six Sigma DC DN C primes in the
# reference set — 12mm, 15mm, 16mm, 23mm, 30mm, 56mm — plus the five
# Sigma zooms scaffolded in #793):
#
# - The chart has a printed black axis frame on a white background. The
#   left frame column coincides with the 0 mm vertical dashed gridline;
#   the right frame is the printed plot frame.
# - Both frames produce the two columns with the highest total black
#   ink coverage in the image — order of magnitude denser than any
#   dashed gridline, axis label glyph, or curve line.
# - The top frame coincides with the OTF=1.0 horizontal gridline; the
#   bottom frame coincides with the OTF=0.0 horizontal gridline. Both
#   appear as the first and last rows whose horizontal black ink fraction
#   exceeds ~30% of image width.
#
# The data-edge convention (per `referenceset/charts.py` for the 56mm
# anchor) sits 1 px inside the left frame and 6 px inside the right
# frame — empirically the rightmost data column the curves ever paint.
# Those offsets are identical on every Sigma DC DN C chart measured.
#
# Historical note: the original rule used "longest contiguous vertical
# ink run" instead of "total ink fraction". That failed on the
# sigma-17-40mm-f1-8-dc-art wide-end chart, where the 30 lp/mm curves
# cross the right axis frame at four points on their way down to the
# bottom edge — the frame is still 82% inked total, but its longest
# unbroken segment is only 40% of image height. Total ink fraction
# captures the actual phenomenon (a printed line, with or without small
# gaps from curve crossings) rather than its visual coincidence. (#1036)

_SIGMA_INK_THRESHOLD: int = 100
_SIGMA_X_LEFT_OFFSET: int = -1
_SIGMA_X_RIGHT_OFFSET: int = -6
_SIGMA_MIN_AXIS_INK_FRACTION: float = 0.70
_SIGMA_MIN_GRIDLINE_INK_FRACTION: float = 0.30


def detect_sigma_plot_box(image_bgr: np.ndarray) -> PlotBox:
    """Detect the data-edge plot box on a Sigma MTF chart (#950).

    Only valid for the `mainstream-2color-solid-dashed` family used by
    the Sigma DC DN C primes and the Sigma zooms scaffolded in #793 —
    calling this on a different chart style (multi-panel, dark
    background, non-Sigma template) raises `ValueError` rather than
    guessing.

    Detection (see module-level note for the validated rule):

    1. Build a black-ink mask (every channel < threshold).
    2. Pick the columns whose total ink coverage is at least 70 % of
       image height — these are the printed left and right axis frames.
       Total coverage (not longest contiguous run) survives the case
       where the frame is interrupted by curves crossing it (#1036).
    3. Pick the first and last rows whose horizontal ink fraction
       exceeds 30 % of image width — these are the top (OTF=1.0) and
       bottom (OTF=0.0) gridlines.
    4. Apply the Sigma data-edge offsets (-1 px to x_left, -6 px to
       x_right) and return the box.

    Fail-loud per ADR-038 §4 B1: any missing signal raises rather than
    falls back to a guess.
    """
    if image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
        raise ValueError(
            f"expected BGR image with 3 channels, got shape {image_bgr.shape}"
        )

    height, width = image_bgr.shape[:2]
    ink = (image_bgr < _SIGMA_INK_THRESHOLD).all(axis=2)

    # --- Left and right axis frames -------------------------------------
    min_axis_ink = int(height * _SIGMA_MIN_AXIS_INK_FRACTION)
    column_ink_counts = ink.sum(axis=0)
    qualifying = np.where(column_ink_counts >= min_axis_ink)[0]
    if qualifying.size == 0:
        raise ValueError(
            "no column has total vertical ink coverage >= "
            f"{_SIGMA_MIN_AXIS_INK_FRACTION:.0%} of image height — chart "
            "does not look like a Sigma plot frame"
        )

    # Cluster adjacent columns (the printed frame is often 1-2 px wide
    # so adjacent x values share the same axis); take the leftmost
    # cluster and the rightmost cluster.
    clusters = cluster_consecutive(qualifying.tolist(), gap=3)
    if len(clusters) < 2:
        raise ValueError(
            f"expected at least two axis-frame columns; found {len(clusters)} "
            f"clusters of high-ink columns: {clusters}"
        )
    # Use the inside edge of each printed frame: the rightmost column of
    # the left cluster, the leftmost column of the right cluster. The
    # printed axis lines are 1-2 px wide; the inside edge is what the
    # data-edge convention measures against.
    left_frame = max(clusters[0])
    right_frame = min(clusters[-1])

    # --- Top and bottom horizontal gridlines ----------------------------
    min_gridline_ink = int(width * _SIGMA_MIN_GRIDLINE_INK_FRACTION)
    row_ink_counts = ink.sum(axis=1)
    qualifying_rows = np.where(row_ink_counts >= min_gridline_ink)[0]
    if qualifying_rows.size == 0:
        raise ValueError(
            "no row has horizontal ink coverage >= "
            f"{_SIGMA_MIN_GRIDLINE_INK_FRACTION:.0%} of image width — chart "
            "does not look like a Sigma plot frame"
        )
    row_clusters = cluster_consecutive(qualifying_rows.tolist(), gap=3)
    y_top = min(row_clusters[0])
    y_bottom = max(row_clusters[-1])

    box = PlotBox(
        x_left=left_frame + _SIGMA_X_LEFT_OFFSET,
        x_right=right_frame + _SIGMA_X_RIGHT_OFFSET,
        y_top=y_top,
        y_bottom=y_bottom,
    )
    if box.width <= 0 or box.height <= 0:
        raise ValueError(f"degenerate detected box: {box}")
    return box
