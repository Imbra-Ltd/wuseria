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
