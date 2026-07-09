"""Tests for the Samyang two-panel plot-box detector (`samyang_plotbox.py`).

`detect_samyang_plotbox()` finds both stacked panels (max on top, stopped
below) for one Samyang chart and returns their boxes plus the fail-loud
`SamyangPlotBoxError`. Until #950 the detector shipped untested — it was
exercised only by `scripts/scaffold_samyang_tier2.py` in production, so a
regression could rot silently. This suite promotes it into the gated tier.

What each assertion pins:

- `test_detect_reproduces_recorded_box` — the detector reproduces every
  recorded box in the reference set on both panels. For the two eye-read
  anchors (`_EYE_READ_ANCHORS`, the S171 Tier 1 boxes measured by hand)
  this is a correctness check against independent ground truth. For the
  Tier 2 charts the recorded boxes were themselves written by this
  detector via the scaffolder, so the match is a consistency guard —
  it catches detector drift or a hand-edited Tier 2 box, not an
  independent correctness claim. Exact equality is intended: a
  legitimate detector change re-runs the scaffolder, which rewrites the
  recorded boxes, so drift should fail loud here.
- `test_eye_read_anchors_present` — guards that the correctness anchors
  are still in the reference set, so the suite above cannot silently
  degrade into a pure consistency check if an anchor is removed.
- `test_refuses_blank_image` — a frameless image raises rather than
  guessing (ADR-038 §4 B1 fail-loud).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from mtfdigitizer.referenceset import REFERENCE_CHARTS
from mtfdigitizer.samyang_plotbox import (
    SamyangPlotBoxError,
    detect_samyang_plotbox,
)


REPO_ROOT = Path(__file__).resolve().parents[3]

# The two Samyang Tier 1 anchors whose boxes are independent, hand
# eye-read ground truth (S171). Every other Samyang box in the reference
# set was written by the detector itself via the Tier 2 scaffolder.
_EYE_READ_ANCHORS = frozenset(
    {
        "samyang-85mm-f1-4-as-if-umc",
        "samyang-300mm-f6-3-ed-umc-cs-reflex",
    }
)


def _samyang_charts() -> list:
    return [
        c
        for c in REFERENCE_CHARTS
        if c.slug.startswith("samyang-") and c.plot_box is not None
    ]


def _coords(pb) -> tuple[int, int, int, int]:
    return (pb.x_left, pb.x_right, pb.y_top, pb.y_bottom)


def _stopped_box(chart) -> tuple[int, int, int, int] | None:
    stopped = [v for v in chart.additional_views if v.aperture == "stopped"]
    return _coords(stopped[0].plot_box) if stopped else None


@pytest.mark.parametrize(
    "chart",
    _samyang_charts(),
    ids=lambda c: c.slug,
)
def test_detect_reproduces_recorded_box(chart) -> None:
    """The detector reproduces both recorded panel boxes exactly.

    Correctness for the eye-read anchors; consistency guard for the
    scaffolded Tier 2 charts (see module docstring).
    """
    path = REPO_ROOT / chart.chart_path
    if not path.exists():
        pytest.skip(f"chart image missing: {path}")

    result = detect_samyang_plotbox(path)

    assert result.plot_box == _coords(chart.plot_box), (
        f"max panel: detected {result.plot_box}, recorded "
        f"{_coords(chart.plot_box)}"
    )
    recorded_stopped = _stopped_box(chart)
    assert recorded_stopped is not None, (
        f"{chart.slug} has no stopped panel view — the Samyang template "
        "always stacks a second panel"
    )
    assert result.stopped_box == recorded_stopped, (
        f"stopped panel: detected {result.stopped_box}, recorded "
        f"{recorded_stopped}"
    )


def test_eye_read_anchors_present() -> None:
    """The independent eye-read anchors stay in the reference set.

    Without this guard, removing an anchor would quietly turn the
    reproduce test into a pure detector-vs-scaffolder consistency check
    with no correctness ground truth left.
    """
    slugs = {c.slug for c in _samyang_charts()}
    missing = _EYE_READ_ANCHORS - slugs
    assert not missing, f"eye-read anchors missing from reference: {missing}"


def test_refuses_blank_image(tmp_path) -> None:
    """A frameless white image has no panel axes — detection must raise."""
    blank = tmp_path / "blank.png"
    Image.fromarray(np.full((1200, 462, 3), 255, dtype=np.uint8)).save(blank)
    with pytest.raises(SamyangPlotBoxError, match="bottom axis missing"):
        detect_samyang_plotbox(blank)
