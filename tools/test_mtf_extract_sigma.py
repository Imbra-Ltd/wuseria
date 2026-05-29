"""Tests for the legacy Sigma MTF extractor (mtf-extract-sigma.py).

Superseded by mtf-extract-skeleton.py but kept; this guards the B4 fix from
the #726 audit: interpolate_missing must not manufacture a center astigmatism
gap. At the optical center S and M coincide, so missing M before the first
detected M (and on the trailing edge) is filled M = S, not a magic taper.

Hyphenated filename → load via importlib.
"""

import importlib.util
import os

_SPEC = importlib.util.spec_from_file_location(
    "mtf_extract_sigma",
    os.path.join(os.path.dirname(__file__), "mtf-extract-sigma.py"),
)
mes = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(mes)


def test_center_missing_m_equals_s_not_a_tapered_gap():
    # M undetected at center positions 0,1 (merged into S), first detected at 2.
    s = [0.99, 0.98, 0.96, 0.90]
    m = [None, None, 0.94, 0.85]
    out = mes.interpolate_missing(s, m)
    # Center fills must equal S exactly (coincident), NOT S minus a fraction of
    # the gap-at-first (the old 0.6+0.4*t taper would give ~0.93/0.93, not 0.99).
    assert out[0] == 0.99
    assert out[1] == 0.98
    assert out[2] == 0.94  # untouched detected value
    assert out[3] == 0.85


def test_after_crossing_center_still_m_equals_s():
    # First detected M is above S (post-crossing). Center still coincides.
    s = [0.95, 0.94, 0.90]
    m = [None, 0.97, 0.88]
    out = mes.interpolate_missing(s, m)
    assert out[0] == 0.95  # M = S at center regardless of crossing direction


def test_interior_gap_linear_interpolated():
    s = [0.99, 0.97, 0.95, 0.92]
    m = [0.99, None, 0.85, 0.80]  # gap at index 1 between detected 0.99 and 0.85
    out = mes.interpolate_missing(s, m)
    assert out[1] == round(0.99 + 0.5 * (0.85 - 0.99), 3)  # 0.92


def test_trailing_edge_gap_falls_back_to_s():
    # M detected through index 1, then missing at the edge → M = S there.
    s = [0.98, 0.95, 0.80, 0.60]
    m = [0.98, 0.90, None, None]
    out = mes.interpolate_missing(s, m)
    assert out[2] == 0.80
    assert out[3] == 0.60


def test_no_m_detected_returns_unchanged():
    s = [0.99, 0.98]
    m = [None, None]
    out = mes.interpolate_missing(s, m)
    assert out == [None, None]
