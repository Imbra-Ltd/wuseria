"""Tests for the MTF curve-tracing tool (mtf-extract-skeleton.py).

The script has a hyphenated filename so it cannot be imported directly;
load it via importlib (the same pattern the script's own --compare path uses).

Focus: chart-family detection (B1 from the #726 audit). The tool only knows
how to trace Sigma (red/blue) and Samyang (4-color) charts. Any other brand
run through the wrong color masks produces silent garbage, so an unrecognized
chart MUST be classified 'unknown' and refused — never defaulted to Samyang.
"""

import importlib.util
import os

import numpy as np
from PIL import Image

_SPEC = importlib.util.spec_from_file_location(
    "mtf_extract_skeleton",
    os.path.join(os.path.dirname(__file__), "mtf-extract-skeleton.py"),
)
mtf = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(mtf)


def _white(w=600, h=900):
    """Blank white chart canvas."""
    return np.full((h, w, 3), 255, dtype=np.uint8)


def _paint(arr, color, count):
    """Paint `count` pixels of `color` into the top-left run of the image."""
    flat = arr.reshape(-1, 3)
    flat[:count] = color
    return arr


def _as_image(arr):
    return Image.fromarray(arr, mode="RGB")


def test_sigma_blue_curves_detected_as_sigma():
    arr = _paint(_white(), color=(20, 40, 220), count=400)  # strong blue
    assert mtf.detect_chart_type(_as_image(arr)) == "sigma"


def test_samyang_pink_curves_detected_as_samyang():
    arr = _paint(_white(), color=(225, 127, 152), count=300)  # samyang pink
    assert mtf.detect_chart_type(_as_image(arr)) == "samyang"


def test_unknown_brand_colors_are_not_defaulted_to_samyang():
    # Green curves — no brand the tool knows. Must be refused, not coerced.
    arr = _paint(_white(), color=(30, 200, 60), count=2000)
    assert mtf.detect_chart_type(_as_image(arr)) == "unknown"


def test_blank_chart_is_unknown():
    assert mtf.detect_chart_type(_as_image(_white())) == "unknown"


def test_detection_is_size_relative_not_absolute_count():
    # A tiny Sigma chart whose blue pixel COUNT is below the old absolute
    # threshold (100) must still be detected via the size-relative fraction.
    small = _paint(_white(w=60, h=60), color=(20, 40, 220), count=80)
    assert mtf.detect_chart_type(_as_image(small)) == "sigma"


def test_sigma_takes_precedence_when_both_signatures_present():
    # Sigma charts legitimately contain red; the blue signature is the
    # discriminator and is checked first.
    arr = _white()
    _paint(arr, color=(20, 40, 220), count=400)  # blue (sigma)
    flat = arr.reshape(-1, 3)
    flat[400:700] = (225, 127, 152)  # also some pink
    assert mtf.detect_chart_type(_as_image(arr)) == "sigma"
