"""Auto-detect plot-box geometry and image-height scheme for TTartisan
MTF charts.

TTartisan publishes every MTF chart in the same 800x600 RGB template
across the 19 surveyed lenses. The plot box is uniform per scheme; the
**scheme** itself varies by lens-mount coverage:

- **APS-C / X-mount lenses** label the x-axis ``0 / 3 / 7 / 10 / 13``
  (image height ~14 mm). Two of the five tick labels are two-digit.
- **GFX or full-frame lenses** label the x-axis ``0 / 5 / 10 / 15 / 20``
  (image height ~20.5 mm). Three of the five tick labels are two-digit.

The detector classifies the chart by counting two-digit tick-label
clusters; the plot box and image_height_mm are then hand-verified
template constants per scheme.

Stopped-aperture detection by pixel-OCR was attempted (S125 / this PR)
and abandoned — text width across ``F8`` / ``F11`` / ``F5.6`` overlaps
too much for a robust width-threshold classifier on the 800x600
template. The scaffolder ships an explicit per-lens stopped-aperture
table eye-read from each chart's legend; that is the single source of
truth and fails loud if a lens slug is missing.

Verified by eye on all 19 TTartisan charts in ``docs/optical-specs/
ttartisan-*`` before this module was committed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .loader import load_chart_gray


@dataclass(frozen=True)
class TTartisanBoxResult:
    """Detected plot-box geometry and chart-scheme classification."""

    plot_box: tuple[int, int, int, int]  # (x_left, x_right, y_top, y_bottom)
    image_height_mm: float
    scheme: str  # "aps-c" or "gfx-or-ff"
    notes: tuple[str, ...]


# Verified-by-eye plot-box convention for the 800x600 TTartisan
# template. The pixel auto-detection drifts ±2 px across the 19-chart
# survey; the hand-verified constants below ship with the scaffolder
# so the production extractor sees identical bounds across the cohort.
#
# Bounds are the **data edges**, one pixel inside the printed axis
# lines (left axis at x=85-86, top axis at y=115, bottom axis at y=462
# on the anchor chart). The axis pixels themselves are pure black and
# would be admitted by the max-aperture profile's black hue range,
# triggering ~78 false-curve pixels per gridline band (#1074 §1). The
# inset bounds exclude the axes from every per-hue mask uniformly.
#
# Anchor measurement: ttartisan-50mm-f1-2-mtf.png (S125 / this PR).
# Cross-checked against ttartisan-100mm-f2-8-macro-2x-gfx-mtf.png.
_APS_C_PLOT_BOX: tuple[int, int, int, int] = (87, 607, 116, 461)
_GFX_PLOT_BOX: tuple[int, int, int, int] = (93, 609, 117, 459)
_APS_C_IMAGE_HEIGHT_MM = 14.0
_GFX_IMAGE_HEIGHT_MM = 20.5


def _label_cluster_widths(gray: np.ndarray, y_bottom: int, x_max: int) -> list[int]:
    """Return the pixel width of each x-axis tick label cluster.

    Two-digit labels render ~10-13 px wide; single-digit ~5-7 px.
    """
    band = (gray[y_bottom + 6 : y_bottom + 30, :x_max] < 100).sum(axis=0)
    threshold = 3
    gap_limit = 8
    widths: list[int] = []
    in_cluster = False
    start = 0
    gap = 0
    for x in range(len(band)):
        if band[x] >= threshold:
            if not in_cluster:
                start = x
                in_cluster = True
            gap = 0
        elif in_cluster:
            gap += 1
            if gap > gap_limit:
                widths.append((x - gap) - start + 1)
                in_cluster = False
                gap = 0
    if in_cluster:
        widths.append((len(band) - 1) - start + 1)
    return widths


def _detect_scheme(widths: list[int]) -> str:
    """Classify the chart as APS-C (2 two-digit labels) or GFX (3)."""
    if len(widths) != 5:
        raise ValueError(
            f"expected 5 x-axis label clusters, found {len(widths)}; "
            f"chart does not match the known TTartisan template"
        )
    two_digit = sum(1 for w in widths if w >= 10)
    if two_digit == 2:
        return "aps-c"
    if two_digit == 3:
        return "gfx-or-ff"
    raise ValueError(
        f"could not classify chart: {two_digit} two-digit labels in {widths}"
    )


# Heuristic legend region: kept for future pixel-OCR work — not
# currently used; stopped apertures are read from the per-lens table
# in the scaffolder instead.
_LEGEND_X = slice(618, 798)
_LEGEND_Y = slice(100, 380)


def _read_stopped_aperture_pixel_ocr_unused(img_rgb: np.ndarray) -> str:
    """Read the stopped aperture f-number from the first red legend row.

    Returns one of ``f/5.6``, ``f/8``, ``f/11`` — the only stopped
    apertures present across the 19-chart TTartisan survey. Detection:
        1. Mask all red pixels in the legend region.
        2. Find the topmost row band containing red pixels (the "S10_F..."
           swatch). The swatch sits at roughly x ≈ 630-665 in legend coords.
        3. Crop the text region to the right of the swatch in that row.
        4. Classify the text by dark-pixel width — text widths for the
           three known stopped apertures are:
               "F8"   →  ~12-14 px
               "F11"  →  ~16-20 px
               "F5.6" →  ~24-28 px
    """
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    legend_hsv = hsv[_LEGEND_Y, _LEGEND_X]
    legend_gray = gray[_LEGEND_Y, _LEGEND_X]
    H = legend_hsv[:, :, 0]
    S = legend_hsv[:, :, 1]
    V = legend_hsv[:, :, 2]
    red_mask = (((H <= 5) | (H >= 175)) & (S >= 80) & (V >= 80) & (V <= 220))
    rows_with_red = np.where(red_mask.any(axis=1))[0]
    if len(rows_with_red) == 0:
        raise ValueError(
            "no red pixels found in legend region — chart layout may differ "
            "from the 19-lens TTartisan template"
        )
    # The first red rows belong to text antialiasing of color words —
    # the actual swatch line is a dense horizontal red run. Locate the
    # topmost row with >= 8 red pixels (swatch lines span ~30+ px).
    swatch_rows = np.where(red_mask.sum(axis=1) >= 8)[0]
    if len(swatch_rows) == 0:
        # Fallback to topmost any-red row.
        swatch_rows = rows_with_red
    first_swatch_y = int(swatch_rows[0])
    swatch_band = slice(first_swatch_y, min(first_swatch_y + 5, red_mask.shape[0]))
    red_cols = np.where(red_mask[swatch_band].any(axis=0))[0]
    swatch_right = int(red_cols.max())

    # Cap text region at the legend box's right inner border. Find the
    # rightmost dense vertical line (>100 dark pixels across the legend
    # column) — that's the box frame; text must lie left of it.
    col_dark_count = (legend_gray < 100).sum(axis=0)
    frame_cols = np.where(col_dark_count > 100)[0]
    text_region_right = (
        int(frame_cols.max()) - 3
        if len(frame_cols) > 0
        else legend_gray.shape[1] - 5
    )

    # Read text in the swatch's y-band — text height is ~10 px above
    # the swatch line center.
    text_y_band = slice(
        max(0, first_swatch_y - 9),
        min(first_swatch_y + 3, legend_gray.shape[0]),
    )
    text_region_left = swatch_right + 4
    if text_region_left >= text_region_right:
        raise ValueError("legend text region is empty between swatch and frame")
    text_strip = legend_gray[text_y_band, text_region_left:text_region_right]
    dark_cols = np.where((text_strip < 100).any(axis=0))[0]
    if len(dark_cols) == 0:
        raise ValueError("no text found right of red legend swatch")
    # The legend prefixes the f-number with "S10_F" / "T10_F". The "F"
    # is the last letter before the digits; the gap between the prefix
    # underscore and "F" is small (~2 px), but the gap between the "F"
    # and the previous text-block run is the largest gap < text_width.
    # Locate the last big gap to drop the prefix.
    gaps = np.diff(dark_cols)
    big_gap_indices = np.where(gaps > 3)[0]
    if len(big_gap_indices) == 0:
        f_number_cols = dark_cols
    else:
        last_split = int(big_gap_indices[-1])
        f_number_cols = dark_cols[last_split + 1 :]
    if len(f_number_cols) == 0:
        raise ValueError("f-number digit region is empty")
    width_px = int(f_number_cols.max() - f_number_cols.min() + 1)
    # Width thresholds verified on the 19-chart TTartisan survey:
    #   "F8"   →  ~ 8-11 px  (one digit, narrow)
    #   "F11"  →  ~12-15 px  (two narrow digits)
    #   "F5.6" →  ~16-22 px  (digit + period + digit)
    if width_px >= 16:
        return "f/5.6"
    if width_px >= 12:
        return "f/11"
    return "f/8"


def detect_ttartisan_plotbox(image_path: Path) -> TTartisanBoxResult:
    """Detect plot box, image height, stopped aperture for one chart."""
    gray = load_chart_gray(image_path)

    # Detect the plot-area scheme by counting x-axis label widths.
    # The bottom axis is near y=462 in the 800x600 template.
    widths = _label_cluster_widths(gray, y_bottom=462, x_max=615)
    scheme = _detect_scheme(widths)

    if scheme == "aps-c":
        plot_box = _APS_C_PLOT_BOX
        image_height_mm = _APS_C_IMAGE_HEIGHT_MM
    else:
        plot_box = _GFX_PLOT_BOX
        image_height_mm = _GFX_IMAGE_HEIGHT_MM

    notes = (
        f"scheme={scheme}; plot box and image_height_mm are template "
        f"constants for the 800x600 TTartisan chart family.",
    )
    return TTartisanBoxResult(
        plot_box=plot_box,
        image_height_mm=image_height_mm,
        scheme=scheme,
        notes=notes,
    )
