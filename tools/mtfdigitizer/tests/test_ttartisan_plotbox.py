"""Tests for the TTartisan plot-box detector (`ttartisan_plotbox.py`).

`detect_ttartisan_plotbox()` classifies one chart as APS-C or GFX/full-
frame by counting two-digit x-axis tick labels, then returns the template
plot box and image height for that scheme. Until #950 the detector shipped
untested — it ran only inside `scripts/scaffold_ttartisan_tier2.py`, so a
regression in the label-width classifier could rot silently. This suite
promotes it into the gated tier.

What each assertion pins:

- `test_detect_reproduces_scheme_and_box` — for every TTartisan chart in
  the reference set the detector returns the recorded box and image
  height. The image height (14.0 mm APS-C vs 20.5 mm GFX) is the visible
  output of the scheme classifier, so this pins the fragile part: the
  two-digit-label count. The box constants and recorded values were
  eye-verified across the 19-chart survey before the detector was
  committed; the boxes themselves are template lookups, so exact equality
  here is a scheme-classification + template-constant regression guard.
- `test_reference_set_covers_both_schemes` — the reference set exercises
  both classifier branches (at least one APS-C and one GFX chart), so the
  suite above cannot pass while leaving one branch untested.
- `test_refuses_blank_image` — a frameless image yields zero tick-label
  clusters and raises rather than guessing (ADR-038 §4 B1 fail-loud).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from mtfdigitizer.referenceset import REFERENCE_CHARTS
from mtfdigitizer.ttartisan_plotbox import (
    TTartisanPlotBoxError,
    detect_ttartisan_plotbox,
)


REPO_ROOT = Path(__file__).resolve().parents[3]

# Image height (mm) each scheme must report — the observable output of the
# tick-label classifier.
_SCHEME_IMAGE_HEIGHT_MM = {"aps-c": 14.0, "gfx-or-ff": 20.5}


def _ttartisan_charts() -> list:
    return [
        c
        for c in REFERENCE_CHARTS
        if c.slug.startswith("ttartisan-") and c.plot_box is not None
    ]


def _coords(pb) -> tuple[int, int, int, int]:
    return (pb.x_left, pb.x_right, pb.y_top, pb.y_bottom)


@pytest.mark.parametrize(
    "chart",
    _ttartisan_charts(),
    ids=lambda c: c.slug,
)
def test_detect_reproduces_scheme_and_box(chart) -> None:
    """The detector reproduces the recorded box and image height.

    The image height is the observable output of the two-digit-label
    scheme classifier — this is the assertion that pins it.
    """
    path = REPO_ROOT / chart.chart_path
    if not path.exists():
        pytest.skip(f"chart image missing: {path}")

    result = detect_ttartisan_plotbox(path)

    assert result.plot_box == _coords(chart.plot_box), (
        f"detected box {result.plot_box}, recorded {_coords(chart.plot_box)}"
    )
    assert result.image_height_mm == pytest.approx(chart.image_height_mm), (
        f"detected image height {result.image_height_mm} mm "
        f"(scheme {result.scheme}), recorded {chart.image_height_mm} mm"
    )
    assert (
        _SCHEME_IMAGE_HEIGHT_MM[result.scheme]
        == pytest.approx(result.image_height_mm)
    ), f"scheme {result.scheme} disagrees with its own image height"


def test_reference_set_covers_both_schemes() -> None:
    """Both classifier branches (APS-C, GFX) appear in the reference set.

    Guards against the reproduce test passing while silently exercising
    only one branch of the two-digit-label classifier.
    """
    heights = {c.image_height_mm for c in _ttartisan_charts()}
    assert 14.0 in heights, "no APS-C (14.0 mm) TTartisan reference chart"
    assert 20.5 in heights, "no GFX (20.5 mm) TTartisan reference chart"


def test_refuses_blank_image(tmp_path) -> None:
    """A frameless white image has no tick labels — detection must raise."""
    blank = tmp_path / "blank.png"
    Image.fromarray(np.full((600, 800, 3), 255, dtype=np.uint8)).save(blank)
    with pytest.raises(TTartisanPlotBoxError, match="x-axis label clusters"):
        detect_ttartisan_plotbox(blank)
