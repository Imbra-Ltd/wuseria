"""Plot-box detector for the Samyang two-panel MTF chart family.

Samyang publishes one PNG per lens that stacks two MTF panels vertically:
the MAX-aperture panel on top, the F8 panel below. Each panel renders the
same 4 curves (10S, 10M, 30S, 30M) at its own f-stop. ADR-063 captures the
per-view aperture override that lets one ``ReferenceChart`` declare both
panels via primary ``chart.plot_box`` + an additional view with
``aperture="F8"``.

This module's job is to find both plot boxes for every Samyang chart in
``docs/optical-specs/samyang-*/<slug>-mtf.png``. The probe handles the
three canvas widths Samyang ships (462, 490, 498 px) and the AF-series
charts (different x_right, slightly shifted F8 panel y-range) without
per-slug overrides.

Strategy:

- Find each panel's bottom axis (MTF=0.0 gridline) — a horizontal row
  where at least 60% of the canvas width is non-white. Search bands
  cover 458..470 (MAX bottom) and 980..1000 (F8 bottom).
- Read x_left and x_right off the MAX-panel bottom row.
- Find each panel's top by probing the chart's left vertical axis line
  (column x_left) for its topmost dark row in y-bands 40..50 (MAX top)
  and 570..585 (F8 top). The vertical axis runs from y_top (outer
  rectangle top) down to y_bottom — this directly yields the convention
  used by the S171 Tier 1 anchors: ``y_top=43, y_bottom=463`` for the
  MAX panel of the 85mm chart, and ``y_top=575, y_bottom=995`` for its
  F8 panel.

The detector raises ``SamyangPlotBoxError`` when any of the four
required signals is missing — the failure mode is loud and names which
search failed, so a maintainer can inspect the chart.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


_NON_WHITE_THRESHOLD = 250
_BOTTOM_AXIS_ROW_DARK_FRACTION = 0.6

_MAX_BOTTOM_BAND = (458, 470)
_F8_BOTTOM_BAND = (980, 1000)
_MAX_TOP_BAND = (40, 50)
_F8_TOP_BAND = (570, 585)


@dataclass(frozen=True)
class SamyangBoxes:
    """Detected plot-box coordinates for both Samyang panels.

    Coordinates use the same convention as the S171 Tier 1 anchors:
    ``y_top`` is the outer plot-rectangle top edge (where the chart's
    left vertical axis line starts), ``y_bottom`` is the MTF=0.0
    gridline row. All coordinates are pixel positions in the source PNG.
    """

    max_box: tuple[int, int, int, int]  # (x_left, x_right, y_top, y_bottom)
    f8_box: tuple[int, int, int, int]
    image_size: tuple[int, int]  # (width, height) of the source PNG


class SamyangPlotBoxError(RuntimeError):
    """Raised when a Samyang chart's plot box cannot be detected."""


def _find_bottom_axis(
    row_dark_count: np.ndarray, y_lo: int, y_hi: int, threshold: int
) -> int | None:
    """Last row in [y_lo, y_hi] above threshold.

    The MTF=0.0 gridline renders as 2-3 stacked pixel rows; taking the
    last row matches the Tier 1 anchor convention (S171 eye-read picked
    the lowest gridline pixel, e.g. y_bottom=463 for 85mm MAX).
    """
    last = None
    for y in range(y_lo, y_hi + 1):
        if row_dark_count[y] >= threshold:
            last = y
    return last


def _find_axis_top(
    non_white: np.ndarray, x_left: int, y_lo: int, y_hi: int
) -> int | None:
    """Topmost row in [y_lo, y_hi] where column x_left is non-white."""
    column = non_white[y_lo : y_hi + 1, x_left]
    hits = np.where(column)[0]
    if len(hits) == 0:
        return None
    return int(hits[0] + y_lo)


def detect_samyang_plotbox(chart_path: Path) -> SamyangBoxes:
    """Detect the MAX and F8 plot boxes for one Samyang chart image.

    Raises ``SamyangPlotBoxError`` if any required signal is missing.
    """
    with Image.open(chart_path) as raw:
        image = np.array(raw.convert("L"))
    height, width = image.shape
    non_white = image < _NON_WHITE_THRESHOLD
    row_dark_count = non_white.sum(axis=1)
    bottom_threshold = int(width * _BOTTOM_AXIS_ROW_DARK_FRACTION)

    max_bot = _find_bottom_axis(
        row_dark_count, *_MAX_BOTTOM_BAND, bottom_threshold
    )
    f8_bot = _find_bottom_axis(
        row_dark_count, *_F8_BOTTOM_BAND, bottom_threshold
    )
    if max_bot is None or f8_bot is None:
        raise SamyangPlotBoxError(
            f"{chart_path}: bottom axis missing — "
            f"max_bot={max_bot}, f8_bot={f8_bot} at threshold "
            f"{_NON_WHITE_THRESHOLD}, dark-fraction "
            f"{_BOTTOM_AXIS_ROW_DARK_FRACTION:.0%}"
        )

    nonzero = np.where(non_white[max_bot])[0]
    if len(nonzero) == 0:
        raise SamyangPlotBoxError(
            f"{chart_path}: MAX-bottom axis row y={max_bot} has no "
            f"dark pixels"
        )
    x_left = int(nonzero[0])
    x_right = int(nonzero[-1])

    max_top = _find_axis_top(non_white, x_left, *_MAX_TOP_BAND)
    f8_top = _find_axis_top(non_white, x_left, *_F8_TOP_BAND)
    if max_top is None or f8_top is None:
        raise SamyangPlotBoxError(
            f"{chart_path}: top axis missing — "
            f"max_top={max_top}, f8_top={f8_top} on column x={x_left}"
        )

    max_box = (x_left, x_right, max_top, max_bot)
    f8_box = (x_left, x_right, f8_top, f8_bot)
    return SamyangBoxes(
        max_box=max_box,
        f8_box=f8_box,
        image_size=(width, height),
    )
