"""Tests for `detect_sigma_plot_box()` (#950).

Detection rule is validated against every Sigma DC DN C reference chart
that carries a hand-measured `plot_box`. Each detected box must match
the hand-measured box within `TOLERANCE_PX` on all four corners.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from mtfdigitizer.loader import load_chart_bgr
from mtfdigitizer.pipeline.plotbox import detect_sigma_plot_box
from mtfdigitizer.referenceset import REFERENCE_CHARTS


REPO_ROOT = Path(__file__).resolve().parents[3]
TOLERANCE_PX = 2


def _known_sigma_charts() -> list:
    return [
        c for c in REFERENCE_CHARTS
        if c.style_family == "mainstream-2color-solid-dashed"
        and c.plot_box is not None
    ]


@pytest.mark.parametrize(
    "chart",
    _known_sigma_charts(),
    ids=lambda c: c.slug,
)
def test_detect_matches_known_box(chart) -> None:
    path = REPO_ROOT / chart.chart_path
    if not path.exists():
        pytest.skip(f"chart image missing: {path}")
    image = load_chart_bgr(path)

    detected = detect_sigma_plot_box(image)
    known = chart.plot_box

    assert abs(detected.x_left - known.x_left) <= TOLERANCE_PX, (
        f"x_left off by {detected.x_left - known.x_left} px"
    )
    assert abs(detected.x_right - known.x_right) <= TOLERANCE_PX, (
        f"x_right off by {detected.x_right - known.x_right} px"
    )
    assert abs(detected.y_top - known.y_top) <= TOLERANCE_PX, (
        f"y_top off by {detected.y_top - known.y_top} px"
    )
    assert abs(detected.y_bottom - known.y_bottom) <= TOLERANCE_PX, (
        f"y_bottom off by {detected.y_bottom - known.y_bottom} px"
    )


def test_refuses_image_without_frame() -> None:
    """A pure-white image has no axis frame — detection must raise."""
    blank = np.full((1000, 1500, 3), 255, dtype=np.uint8)
    with pytest.raises(ValueError, match="solid vertical run"):
        detect_sigma_plot_box(blank)


def test_refuses_non_bgr_input() -> None:
    grayscale = np.zeros((100, 100), dtype=np.uint8)
    with pytest.raises(ValueError, match="3 channels"):
        detect_sigma_plot_box(grayscale)
