"""Auto-detect plot box and image_height_mm for Fujifilm MTF charts.

Fuji publishes its MTF charts in many slightly-different templates (~19
distinct (width, height, alpha) tuples across the 199 chart files).
Hand-measuring each plot box is tedious; this module reads the visual
structure of one chart image and returns calibrated coordinates.

Pipeline:
    1. Composite RGBA over white (if needed).
    2. Find horizontal lines — dark axis baseline and light gridlines.
    3. The bottommost line is the x-axis (y_bottom); its dark-pixel
       span gives x_left / x_right of the plot box.
    4. Detect tick-label clusters below the axis. Use the cluster count
       to identify the labelling scheme:
         - 6 numeric clusters → "0/5/10/15/20/25 mm" (GF "25 mm" family)
         - 4 numeric clusters → "0/5/10/14.2 mm" (XF family)
         - 10 numeric clusters → "0/3/6/.../27 mm" (GF "27 mm" family)
    5. image_height_mm = (x_right - x_left) / px_per_mm, where
       px_per_mm is calibrated from the leftmost-to-rightmost
       numeric-tick span and the known label range.
    6. y_top is one gridline-spacing above the topmost light gridline
       (the MTF=1.0 line is unprinted in Fuji charts).

Limitations (the scheme detection by tick count is heuristic; verify
the result against the source PNG before committing it).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(frozen=True)
class FujiBoxResult:
    """Detected plot-box geometry + chart-axis calibration for one image."""

    plot_box: tuple[int, int, int, int]
    image_height_mm: float
    px_per_mm: float
    rightmost_tick_mm: float
    tick_count: int
    gridline_spacing_px: float
    has_alpha: bool
    notes: tuple[str, ...]


# Known Fuji axis-label patterns. Key = number of numeric tick label
# clusters (excluding the trailing "mm" cluster); value = (rightmost
# label in mm, scheme name).
_TICK_SCHEMES: dict[int, tuple[float, str]] = {
    4: (14.2, "XF 0/5/10/14.2"),
    6: (25.0, "GF 0/5/10/15/20/25"),
    10: (27.0, "GF 0/3/6/.../27"),
}


# Sensor half-diagonal in mm — the actual image height Fujifilm publishes
# MTF for. Used as the calibration anchor when label-cluster detection
# fails to find an unambiguous tick scheme (super-tele zooms truncate
# the rightmost label; GF 30mm-style 0/3/6/.../27 charts have so many
# ticks they merge under naive clustering). The mount (GF or XF) is
# read from the lens slug.
#
# GF: 44x33 mm sensor → half-diag √(22² + 16.5²) = 27.5 mm. Fujifilm
# draws the data area out to ~26.9 mm on the 282x212 template (the
# tick label "25" sits inside the plot box; the right gridline goes
# past it).
# XF: 23.5x15.6 mm sensor → half-diag √(11.75² + 7.8²) = 14.1 mm.
# Fujifilm labels the rightmost tick "14.2 mm" explicitly.
#
# These are TEMPLATE defaults. The detector still prefers the
# label-cluster reading when available — those tracker px-per-mm
# directly from the chart's own ticks. The mount default is the
# fallback when label detection is ambiguous.
_MOUNT_IMAGE_HEIGHT_MM: dict[str, float] = {
    "gf": 26.9,  # GF charts: gridline runs past "25" tick to ~26.9 mm
    "xf": 14.2,  # XF charts: rightmost tick labelled "14.2 mm"
    "mkx": 14.2,  # MK X cinema lenses share the XF mount/sensor
    "xc": 14.2,   # XC lenses share APS-C sensor
}


def _mount_from_slug(slug: str) -> str | None:
    """Pull the mount key (gf/xf/mkx/xc) from a lens slug.

    Fujifilm folders are named `fujifilm-<mount>-<rest>` — the second
    dash-separated token identifies the mount.
    """
    if not slug.startswith("fujifilm-"):
        return None
    parts = slug.split("-")
    if len(parts) < 2:
        return None
    mount = parts[1].lower()
    return mount if mount in _MOUNT_IMAGE_HEIGHT_MM else None


def _composite_alpha(img: np.ndarray) -> np.ndarray:
    """Composite a BGRA image over white; pass-through for BGR."""
    if img.ndim == 2:
        return img
    if img.shape[2] == 3:
        return img
    bgr = img[..., :3].astype(np.float32)
    a = (img[..., 3] / 255.0)[..., None]
    return (bgr * a + 255 * (1 - a)).astype(np.uint8)


def _horizontal_lines(
    gray: np.ndarray,
    *,
    dark_th: int = 100,
    mid_lo: int = 120,
    mid_hi: int = 220,
    frac: float = 0.3,
) -> tuple[list[int], list[int]]:
    """Return (dark_rows, light_rows) — y values whose horizontal-line
    density exceeds `frac` of the image width."""
    h, w = gray.shape
    dark = (gray < dark_th).sum(axis=1)
    light = ((gray > mid_lo) & (gray < mid_hi)).sum(axis=1)
    dark_rows = [y for y in range(h) if dark[y] > w * frac]
    light_rows = [y for y in range(h) if light[y] > w * frac]
    return dark_rows, light_rows


def _label_clusters(
    gray: np.ndarray,
    y_below: int,
    *,
    dark_th: int = 100,
    gap: int = 8,
    band_height: int = 25,
) -> list[float]:
    """Detect tick-label cluster centers in the band just below `y_below`."""
    h, w = gray.shape
    band = gray[y_below + 1 : min(y_below + 1 + band_height, h)]
    if band.size == 0:
        return []
    dark_any = (band < dark_th).any(axis=0)
    dark = np.where(dark_any)[0]
    if dark.size == 0:
        return []
    groups: list[list[int]] = []
    cur = [int(dark[0])]
    for x in dark[1:]:
        if int(x) - cur[-1] <= gap:
            cur.append(int(x))
        else:
            groups.append(cur)
            cur = [int(x)]
    groups.append(cur)
    return [(g[0] + g[-1]) / 2 for g in groups]


def _gridline_runs(rows: list[int]) -> list[int]:
    """Collapse runs of adjacent y values into a single representative y
    (the run's midpoint). Useful when an axis line is rendered 2-3 px
    thick and shows up as several adjacent dark rows."""
    if not rows:
        return []
    runs: list[list[int]] = [[rows[0]]]
    for y in rows[1:]:
        if y - runs[-1][-1] <= 2:
            runs[-1].append(y)
        else:
            runs.append([y])
    return [int(round((r[0] + r[-1]) / 2)) for r in runs]


def detect_fuji_plotbox(
    img_path: Path,
    *,
    image_height_mm_hint: float | None = None,
) -> FujiBoxResult | None:
    """Read one Fuji chart and return its plot-box geometry, or None on failure.

    The result encodes (x_left, x_right, y_top, y_bottom) plus
    `image_height_mm` calibrated from the detected x-axis tick labels.

    `image_height_mm_hint` overrides label-based calibration. Pass the
    mount default (26.9 for GF, 14.2 for XF) when the tick scheme is
    ambiguous — the detector uses the axis dark-pixel span and the
    hint to compute `px_per_mm`. If omitted, the mount is inferred
    from the slug (the parent folder name) when `img_path` matches the
    Fuji folder convention.
    """
    img = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    has_alpha = img.ndim == 3 and img.shape[2] == 4
    composed = _composite_alpha(img)
    gray = (
        cv2.cvtColor(composed, cv2.COLOR_BGR2GRAY)
        if composed.ndim == 3
        else composed
    )
    h, w = gray.shape
    notes: list[str] = []

    dark_rows, light_rows = _horizontal_lines(gray)
    horizontal = sorted(set(dark_rows + light_rows))
    if not horizontal:
        notes.append("no horizontal lines detected")
        return _none_with_notes(has_alpha, notes)

    # Bottom-most line is the x-axis baseline.
    y_bottom = horizontal[-1]
    row = gray[y_bottom]
    dark_cols = np.where(row < 100)[0]
    if dark_cols.size < w * 0.3:
        dark_cols = np.where((row > 120) & (row < 220))[0]
    if dark_cols.size == 0:
        notes.append(f"y_bottom={y_bottom} has no horizontal-line pixels")
        return _none_with_notes(has_alpha, notes)
    x_left, x_right = int(dark_cols.min()), int(dark_cols.max())

    # Tick labels below the bottom axis.
    label_centers = _label_clusters(gray, y_bottom)
    # Drop a trailing cluster that sits outside the axis span (typically
    # the "mm" label).
    numeric_ticks = [c for c in label_centers if c <= x_right + 5]
    if len(numeric_ticks) < 2:
        notes.append(
            f"fewer than 2 numeric tick clusters ({len(numeric_ticks)} found)"
        )
        return _none_with_notes(has_alpha, notes)

    # Pick a calibration anchor. The mount default is more reliable
    # than label-cluster detection across the Fuji template zoo
    # (tick centers from label clusters can drift up to several %
    # because text widths vary; the sensor half-diagonal is fixed
    # physics). Priority:
    #   1. Explicit `image_height_mm_hint` argument.
    #   2. Mount default (read from the parent folder slug).
    #   3. The label-cluster tick scheme as a last resort.
    mount = _mount_from_slug(img_path.parent.name)
    mount_default = (
        _MOUNT_IMAGE_HEIGHT_MM.get(mount) if mount is not None else None
    )

    image_height_mm: float
    px_per_mm: float
    rightmost_mm: float
    axis_span = x_right - x_left

    if image_height_mm_hint is not None:
        image_height_mm = image_height_mm_hint
        px_per_mm = axis_span / image_height_mm if image_height_mm > 0 else 0.0
        rightmost_mm = image_height_mm
        notes.append(f"calibrated from explicit hint = {image_height_mm} mm")
    elif mount_default is not None:
        image_height_mm = mount_default
        px_per_mm = axis_span / image_height_mm if image_height_mm > 0 else 0.0
        rightmost_mm = image_height_mm
        notes.append(
            f"calibrated from {mount} mount default = {mount_default} mm "
            f"({len(numeric_ticks)} ticks detected)"
        )
    else:
        scheme = _TICK_SCHEMES.get(len(numeric_ticks))
        if scheme is None:
            notes.append(
                f"unknown tick scheme ({len(numeric_ticks)} clusters) and "
                "no mount default; pass image_height_mm_hint"
            )
            return _none_with_notes(has_alpha, notes)
        rightmost_mm, _scheme_label = scheme
        tick_span = numeric_ticks[-1] - numeric_ticks[0]
        if tick_span <= 0:
            notes.append("tick span is zero — degenerate detection")
            return _none_with_notes(has_alpha, notes)
        px_per_mm = tick_span / rightmost_mm
        image_height_mm = round(axis_span / px_per_mm, 2)

    # y_top from the topmost light gridline + one spacing.
    upper_light = _gridline_runs(
        [y for y in light_rows if y < y_bottom - 10]
    )
    if not upper_light:
        notes.append("no upper light gridlines found; using axis-span fallback")
        gridline_spacing_px = max(1.0, (y_bottom - 4) / 5.0)
        y_top = max(0, int(round(y_bottom - 5 * gridline_spacing_px)))
    else:
        if len(upper_light) >= 2:
            spacings = [
                upper_light[i + 1] - upper_light[i]
                for i in range(len(upper_light) - 1)
            ]
            gridline_spacing_px = float(np.median(spacings))
        else:
            gridline_spacing_px = float(y_bottom - upper_light[0]) / 4.0
        y_top = max(0, int(round(upper_light[0] - gridline_spacing_px)))

    return FujiBoxResult(
        plot_box=(x_left, x_right, y_top, y_bottom),
        image_height_mm=image_height_mm,
        px_per_mm=round(px_per_mm, 3),
        rightmost_tick_mm=rightmost_mm,
        tick_count=len(numeric_ticks),
        gridline_spacing_px=round(gridline_spacing_px, 1),
        has_alpha=has_alpha,
        notes=tuple(notes),
    )


def _none_with_notes(has_alpha: bool, notes: list[str]) -> FujiBoxResult:
    """Return a sentinel "detection failed" result that surfaces the
    failure reason. Callers check `plot_box == (0, 0, 0, 0)` to detect."""
    return FujiBoxResult(
        plot_box=(0, 0, 0, 0),
        image_height_mm=0.0,
        px_per_mm=0.0,
        rightmost_tick_mm=0.0,
        tick_count=0,
        gridline_spacing_px=0.0,
        has_alpha=has_alpha,
        notes=tuple(notes),
    )


def _format_result(path: Path, res: FujiBoxResult) -> str:
    if res.plot_box == (0, 0, 0, 0):
        return f"FAIL  {path.name}  reasons: {'; '.join(res.notes)}"
    parts = [
        f"OK    {path.name}",
        f"  box={res.plot_box}",
        f"  ih={res.image_height_mm}mm",
        f"  px/mm={res.px_per_mm}",
        f"  ticks={res.tick_count}/{res.rightmost_tick_mm}mm",
        f"  spacing={res.gridline_spacing_px}px",
    ]
    if res.has_alpha:
        parts.append("  alpha")
    if res.notes:
        parts.append(f"  notes: {'; '.join(res.notes)}")
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="One or more chart PNG paths to detect.",
    )
    args = parser.parse_args(argv)
    rc = 0
    for p in args.paths:
        res = detect_fuji_plotbox(p)
        if res is None:
            print(f"FAIL  {p}: cannot read image", file=sys.stderr)
            rc = 1
            continue
        print(_format_result(p, res))
        if res.plot_box == (0, 0, 0, 0):
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
