"""Hue → binary mask (#935, ADR-038 §2).

Apply each declared HueRange to an HSV image, then OR together masks
that share a name (red wraps both ends of the hue circle in HSV).
"""

from __future__ import annotations

from collections import defaultdict

import cv2
import numpy as np

from ..profiles.types import HueRange, MtfProfile


def hue_mask(hsv: np.ndarray, hue: HueRange) -> np.ndarray:
    """Binary mask of pixels inside one HueRange's HSV box."""
    h, s, v = cv2.split(hsv)
    return (
        (h >= hue.h_lo)
        & (h <= hue.h_hi)
        & (s >= hue.s_min)
        & (s <= hue.s_max)
        & (v >= hue.v_min)
        & (v <= hue.v_max)
    )


def masks_by_curve_name(hsv: np.ndarray, profile: MtfProfile) -> dict[str, np.ndarray]:
    """Return one binary mask per curve name declared in the profile.

    Multiple HueRange entries with the same `name` are ORed — that's how
    wrap-around colors (e.g. red at both ends of the hue circle) collapse
    into one curve. The output is keyed by HueRange.name, exactly the
    identifier downstream stages use to tag readings.
    """
    masks: dict[str, np.ndarray] = {}
    for hue in profile.hues:
        m = hue_mask(hsv, hue)
        if hue.name in masks:
            masks[hue.name] = masks[hue.name] | m
        else:
            masks[hue.name] = m
    return masks


# Spike #1217 Option 4 — plot-box border cleanup
#
# On charts where the plot-box right border line falls INSIDE the data-edge
# plot box (e.g. af-35 has x_right=607 with the border drawn at col 603),
# the grey HSV mask catches the full vertical border as a high-density
# column. The DP then locks onto it and the sampler reads carry-forward
# state at frac=1.0. Real curves contribute at most a few px per column;
# a column that is more than 50% filled within the rightmost 10 px of the
# plot box is unambiguously chart decoration, not a curve.
#
# Charts where the border falls OUTSIDE the data-edge plot box (e.g.
# ttartisan-50 has x_right=607 with the border at col 609) are already
# clipped by the plot-box clip step — this function is a no-op on them.
_BORDER_WINDOW = 10
_BORDER_DENSITY_THRESHOLD = 0.5


def strip_plot_box_borders(
    masks: dict[str, np.ndarray],
    plot_box,
) -> dict[str, np.ndarray]:
    """Zero out plot-box border columns that fall inside the data-edge box.

    Operates on already-clipped masks (plot-box clip applied first). Each
    column within the rightmost ``_BORDER_WINDOW`` px of ``x_right`` is
    inspected: if its grey-px density exceeds
    ``_BORDER_DENSITY_THRESHOLD * plot_height``, it is zeroed.

    Returns a new dict; inputs are not mutated.
    """
    plot_height = plot_box.y_bottom - plot_box.y_top + 1
    threshold = _BORDER_DENSITY_THRESHOLD * plot_height
    border_col_start = plot_box.x_right - _BORDER_WINDOW + 1
    border_col_end = plot_box.x_right  # inclusive

    out: dict[str, np.ndarray] = {}
    for name, mask in masks.items():
        m = mask.copy()
        for x in range(border_col_start, border_col_end + 1):
            if x < 0 or x >= m.shape[1]:
                continue
            col_count = m[plot_box.y_top:plot_box.y_bottom + 1, x].sum()
            if col_count >= threshold:
                m[plot_box.y_top:plot_box.y_bottom + 1, x] = False
        out[name] = m
    return out
