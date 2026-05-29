"""Tests for the MTF curve-tracing tool (mtf-extract-skeleton.py).

The script has a hyphenated filename so it cannot be imported directly;
load it via importlib (the same pattern the script's own --compare path uses).

Covers the #726 audit correctness fixes:
- B1 — chart-family detection: unknown brands are refused, not defaulted to
  Samyang (the tool only knows Sigma red/blue and Samyang 4-color charts).
- B2 — interpolate_at returns None when the curve has no nearby data instead
  of fabricating a neighbor's reading.
- B3 — components_to_curve centroids same-curve pixels order-independently
  and keeps every pixel of the curve (no 5px cap, no pairwise running mean).
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


# ---------------------------------------------------------------------------
# B2 — interpolate_at must not fabricate values across large gaps
# ---------------------------------------------------------------------------

# y_top=0, y_bot=100 → MTF = 1 - y/100, so y=20 → 0.8, y=50 → 0.5.
_Y_TOP, _Y_BOT = 0, 100


def test_interpolate_exact_match_returns_point_value():
    curve = {100: 20.0}
    assert mtf.interpolate_at(curve, 102, _Y_TOP, _Y_BOT) == 0.8


def test_interpolate_between_close_points_is_linear():
    curve = {100: 20.0, 140: 60.0}  # gap 40px < MAX_INTERP_GAP_PX
    # midpoint x=120 → y=40 → MTF 0.6
    assert mtf.interpolate_at(curve, 120, _Y_TOP, _Y_BOT) == 0.6


def test_interpolate_returns_none_across_large_gap():
    # Points 300px apart bracket the target, but the curve has no real data
    # near it — must be reported missing, not interpolated across the void.
    curve = {100: 20.0, 400: 80.0}
    assert mtf.interpolate_at(curve, 250, _Y_TOP, _Y_BOT) is None


def test_interpolate_does_not_fall_back_to_distant_neighbor():
    # Old B2 bug: a point 20px away was returned as the value at target_x.
    # With only a left point far from target and no right bracket, expect None.
    curve = {100: 20.0}
    assert mtf.interpolate_at(curve, 118, _Y_TOP, _Y_BOT) is None


def test_interpolate_empty_curve_is_none():
    assert mtf.interpolate_at({}, 100, _Y_TOP, _Y_BOT) is None


# ---------------------------------------------------------------------------
# B3 — components_to_curve centroids same-curve pixels without dropping any
# ---------------------------------------------------------------------------
#
# split_solid_dashed_cc separates solid from dashed by component WIDTH, then
# pools each group into a curve. The function's contract is to centroid the
# pixels of one logical curve at each x — it must (a) not cap/pairwise-average
# in a way that drifts toward a midpoint, and (b) not silently drop pixels.


def test_solid_curve_centroids_line_thickness_per_column():
    # One solid line, 3px thick (a real skeleton column has a little height).
    # Each x must map to the centroid of its 3 pixels, not a drifting average.
    h, w = 120, 400
    skel = np.zeros((h, w), dtype=np.uint8)
    for x in range(20, 380):
        center = 60
        skel[center - 1: center + 2, x] = 255  # y = 59, 60, 61

    solid, dashed = mtf.split_solid_dashed_cc(skel, y_top=0, y_bot=h - 1, x_start=0)
    assert dashed is None  # single wide component → no dashed group
    for x in range(40, 360, 20):
        assert x in solid
        assert abs(solid[x] - 60.0) <= 0.01  # centroid of 59,60,61 == 60


def test_solid_curve_keeps_pixels_beyond_the_old_5px_window():
    # A steep column within ONE connected component spans more than the old
    # 5px window: a near-vertical segment puts y=40 and y=48 at the same x,
    # connected through the line itself. The old code's `< 5` cap dropped the
    # farther pixel; the fix counts every pixel of the curve at that column.
    h, w = 120, 400
    skel = np.zeros((h, w), dtype=np.uint8)
    for x in range(20, 200):
        skel[40, x] = 255          # flat segment at y=40
    for y in range(40, 49):
        skel[y, 200] = 255         # vertical riser at x=200 (one component)
    for x in range(200, 380):
        skel[48, x] = 255          # flat segment at y=48

    solid, _ = mtf.split_solid_dashed_cc(skel, y_top=0, y_bot=h - 1, x_start=0)
    # At x=200 the riser contributes y=40..48; centroid is 44. The far pixels
    # are counted, not discarded as under the old 5px cap.
    assert abs(solid[200] - 44.0) <= 0.01


def test_x_start_excludes_axis_region():
    h, w = 120, 400
    skel = np.zeros((h, w), dtype=np.uint8)
    for x in range(0, 380):
        skel[40, x] = 255
    solid, _ = mtf.split_solid_dashed_cc(skel, y_top=0, y_bot=h - 1, x_start=100)
    assert all(x >= 100 for x in solid)
