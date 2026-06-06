"""Tests for the Fujifilm plot-box auto-detector (`fuji_plotbox.py`).

Covers:
- The two Tier 1 anchors (GF 23mm, XF 23mm) get detected with values
  matching the hand-measured calibrations in `referenceset/charts.py`.
- A non-chart image (the XF 16-50 legend file) is rejected.
- Mount-default selection works for slugs starting with `fujifilm-gf-`,
  `fujifilm-xf-`, `fujifilm-mkx-`, `fujifilm-xc-`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mtfdigitizer.fuji_plotbox import (
    _MOUNT_IMAGE_HEIGHT_MM,
    _mount_from_slug,
    detect_fuji_plotbox,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


# --- Mount slug parsing ---------------------------------------------------


@pytest.mark.parametrize(
    "slug, expected_mount",
    [
        ("fujifilm-gf-23mm-f4-r-lm-wr", "gf"),
        ("fujifilm-xf-23mm-f1-4-r-lm-wr", "xf"),
        ("fujifilm-mkx-18-55mm-t2-9", "mkx"),
        ("fujifilm-xc-35mm-f2-0", "xc"),
        ("sigma-56mm-f1-4-dc-dn-c", None),
        ("fujifilm-", None),
        ("", None),
    ],
)
def test_mount_from_slug(slug, expected_mount):
    assert _mount_from_slug(slug) == expected_mount


def test_mount_defaults_are_sane():
    """GF/XF mount defaults match the sensor half-diagonals + Fuji's
    publication conventions."""
    assert _MOUNT_IMAGE_HEIGHT_MM["gf"] == 26.9
    assert _MOUNT_IMAGE_HEIGHT_MM["xf"] == 14.2


# --- Anchor detection ----------------------------------------------------


_GF_ANCHOR = REPO_ROOT / "docs/optical-specs/fujifilm-gf-23mm-f4-r-lm-wr/fujifilm-gf-23mm-f4-r-lm-wr-15lp.png"
_XF_ANCHOR = REPO_ROOT / "docs/optical-specs/fujifilm-xf-23mm-f1-4-r-lm-wr/fujifilm-xf-23mm-f1-4-r-lm-wr-15lp.png"
_LEGEND_FILE = REPO_ROOT / "docs/optical-specs/fujifilm-xf-16-50mm-f2-8-4-8-r-lm-wr/fujifilm-xf-16-50mm-f2-8-4-8-r-lm-wr-45lp.png"


@pytest.mark.skipif(not _GF_ANCHOR.exists(), reason="GF anchor chart missing")
def test_detect_gf_anchor_matches_hand_measurement():
    """The detector reproduces the hand-measured plot box for the GF
    anchor. Values are the calibrated truth in `referenceset/charts.py`."""
    res = detect_fuji_plotbox(_GF_ANCHOR)
    assert res is not None
    assert res.plot_box == (15, 249, 4, 184)
    assert res.image_height_mm == 26.9
    # px/mm computed from axis_span / image_height_mm — verify it lands
    # close to the hand-measured tick-mark calibration of 8.7 px/mm.
    assert 8.6 <= res.px_per_mm <= 8.8


@pytest.mark.skipif(not _XF_ANCHOR.exists(), reason="XF anchor chart missing")
def test_detect_xf_anchor_matches_hand_measurement():
    """The detector reproduces the hand-measured plot box for the XF
    anchor (RGBA template, smaller image height)."""
    res = detect_fuji_plotbox(_XF_ANCHOR)
    assert res is not None
    assert res.plot_box == (19, 319, 40, 245)
    assert res.image_height_mm == 14.2
    assert res.has_alpha is True
    # px/mm should be close to the hand-measured 21.13.
    assert 20.9 <= res.px_per_mm <= 21.3


@pytest.mark.skipif(not _LEGEND_FILE.exists(), reason="legend file missing")
def test_detect_rejects_legend_image():
    """The XF 16-50 'legend' file is the colour/style key, not a chart.
    The detector should reject it (no horizontal lines detected)."""
    res = detect_fuji_plotbox(_LEGEND_FILE)
    assert res is not None
    assert res.plot_box == (0, 0, 0, 0), (
        f"expected legend image to be rejected; got box={res.plot_box}"
    )


# --- Hint override -------------------------------------------------------


@pytest.mark.skipif(not _GF_ANCHOR.exists(), reason="GF anchor chart missing")
def test_explicit_image_height_hint_overrides_mount_default():
    """`image_height_mm_hint` takes precedence over the mount default —
    useful when a chart's image height is known to differ from the
    template's typical value."""
    res = detect_fuji_plotbox(_GF_ANCHOR, image_height_mm_hint=27.5)
    assert res is not None
    assert res.image_height_mm == 27.5
