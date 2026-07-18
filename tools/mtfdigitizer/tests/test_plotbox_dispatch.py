"""Tests for the unified plot-box dispatch (`plotbox_detect.py`, ADR-084).

The four brand detectors each own their own precision regression
(`test_plotbox_detect.py`, `test_samyang_plotbox.py`,
`test_ttartisan_plotbox.py`, `test_fuji_plotbox.py`). This suite does not
re-test detector accuracy; it pins the *routing* layer:

- `test_detected_families_route_to_their_detector` — each family with a
  detector routes to it and returns a ``source="detected"`` box that
  matches the committed reference box, confirming the dispatch table maps
  the style family to the right detector and normalizes its result.
- `test_samyang_dispatch_carries_secondary_box` — the two-panel family
  surfaces its stopped panel through `secondary_box`.
- `test_no_detector_families_fall_back` — a family with no detector but a
  hand-measured box falls back loudly (``source="fallback"``, reason in
  `notes`), never silently drops it.
- `test_missing_box_and_no_detector_raises` — the out-of-band
  fail-loud shape (no detector, no box) raises rather than guessing.
- `test_detector_failure_falls_back_*` — when a detector raises, the
  dispatch falls back to the hand-measured box, or raises when there is
  none. Uses a monkeypatched detector so the failure is deterministic
  and image-independent.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mtfdigitizer import plotbox_detect
from mtfdigitizer.plotbox_detect import (
    PlotBoxUnavailable,
    detect_plot_box,
    has_detector,
)
from mtfdigitizer.referenceset import REFERENCE_CHARTS
from mtfdigitizer.referenceset.charts import PlotBoxCoords, ReferenceChart


REPO_ROOT = Path(__file__).resolve().parents[3]
TOLERANCE_PX = 2

# style_family -> the `detector` label the dispatch must report.
# `idealized-flat` shares the Samyang 4-color template (see
# `plotbox_detect._DETECTOR_BY_STYLE`).
_EXPECTED_DETECTOR = {
    "mainstream-2color-solid-dashed": "sigma",
    "mainstream-4color-all-solid": "samyang",
    "idealized-flat": "samyang",
    "ttartisan-4color-dual-aperture": "ttartisan",
    "fujifilm-permfreq": "fuji",
}


def _coords(pb: PlotBoxCoords) -> tuple[int, int, int, int]:
    return (pb.x_left, pb.x_right, pb.y_top, pb.y_bottom)


def _box(pb) -> tuple[int, int, int, int]:
    return (pb.x_left, pb.x_right, pb.y_top, pb.y_bottom)


def _first_chart_per_detected_family() -> list:
    """One representative chart per family that has a detector."""
    seen: dict[str, ReferenceChart] = {}
    for chart in REFERENCE_CHARTS:
        if (
            chart.style_family in _EXPECTED_DETECTOR
            and chart.plot_box is not None
            and chart.style_family not in seen
        ):
            seen[chart.style_family] = chart
    return list(seen.values())


def _charts_without_detector() -> list:
    return [
        c
        for c in REFERENCE_CHARTS
        if not has_detector(c.style_family) and c.plot_box is not None
    ]


@pytest.mark.parametrize(
    "chart",
    _first_chart_per_detected_family(),
    ids=lambda c: c.style_family,
)
def test_detected_families_route_to_their_detector(chart) -> None:
    """A family with a detector routes to it and matches its committed box.

    Pins the dispatch table (right style_family -> right detector) and the
    result normalization, not detector precision — hence a 2px tolerance,
    the same the Sigma detector's own suite allows for hand-measured
    anchors.
    """
    if not (REPO_ROOT / chart.chart_path).exists():
        pytest.skip(f"chart image missing: {chart.chart_path}")

    result = detect_plot_box(chart)

    assert result.source == "detected"
    assert result.detector == _EXPECTED_DETECTOR[chart.style_family]

    detected = _box(result.plot_box)
    committed = _coords(chart.plot_box)
    for got, want, corner in zip(detected, committed, "x_left x_right y_top y_bottom".split()):
        assert abs(got - want) <= TOLERANCE_PX, (
            f"{chart.slug} {corner}: dispatch box {detected} vs committed "
            f"{committed} exceeds {TOLERANCE_PX}px"
        )


def test_samyang_dispatch_carries_secondary_box() -> None:
    """The Samyang two-panel family surfaces its stopped panel."""
    samyang = next(
        (
            c
            for c in REFERENCE_CHARTS
            if c.style_family == "mainstream-4color-all-solid"
            and c.plot_box is not None
        ),
        None,
    )
    assert samyang is not None, "no Samyang reference chart with a plot box"
    if not (REPO_ROOT / samyang.chart_path).exists():
        pytest.skip(f"chart image missing: {samyang.chart_path}")

    result = detect_plot_box(samyang)

    assert result.secondary_box is not None, (
        "Samyang dispatch must carry the stopped panel as secondary_box"
    )
    stopped_views = [
        v for v in samyang.additional_views if v.aperture == "stopped"
    ]
    assert stopped_views, f"{samyang.slug} has no stopped panel view"
    assert _box(result.secondary_box) == _coords(stopped_views[0].plot_box)


@pytest.mark.parametrize(
    "chart",
    _charts_without_detector(),
    ids=lambda c: c.slug,
)
def test_no_detector_families_fall_back(chart) -> None:
    """A family with no detector falls back to its hand-measured box.

    The fallback is loud: `source` marks it and `notes` records why, so a
    box that came from the hand-measured record is never mistaken for a
    detected one.
    """
    result = detect_plot_box(chart)

    assert result.source == "fallback"
    assert result.detector == "hand-measured"
    assert _box(result.plot_box) == _coords(chart.plot_box)
    assert result.notes, "fallback must record the reason in notes"
    assert "no detector" in result.notes[0]


def test_missing_box_and_no_detector_raises() -> None:
    """The out-of-band fail-loud shape has no detector and no box."""
    orphan = next(
        (
            c
            for c in REFERENCE_CHARTS
            if not has_detector(c.style_family) and c.plot_box is None
        ),
        None,
    )
    assert orphan is not None, (
        "expected at least one reference chart with no detector and no box "
        "(the deliberate fail-loud anchor)"
    )
    with pytest.raises(PlotBoxUnavailable, match="cannot supply a plot box"):
        detect_plot_box(orphan)


def _synthetic_chart(plot_box: PlotBoxCoords | None) -> ReferenceChart:
    """A minimal chart in a detector-backed family for failure tests."""
    return ReferenceChart(
        slug="synthetic-dispatch-test",
        chart_path="does/not/exist.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=(),
        frequencies_lpmm=(),
        image_height_mm=0.0,
        notes="synthetic",
        plot_box=plot_box,
    )


def _raise_value_error(_chart) -> plotbox_detect.DetectedPlotBox:
    raise ValueError("simulated detector failure")


def test_detector_failure_falls_back_to_hand_measured(monkeypatch) -> None:
    """When a detector raises, the dispatch uses the hand-measured box."""
    monkeypatch.setitem(
        plotbox_detect._DETECTOR_BY_STYLE,
        "mainstream-2color-solid-dashed",
        _raise_value_error,
    )
    chart = _synthetic_chart(PlotBoxCoords(10, 20, 30, 40))

    result = detect_plot_box(chart)

    assert result.source == "fallback"
    assert result.detector == "hand-measured"
    assert _box(result.plot_box) == (10, 20, 30, 40)
    assert "simulated detector failure" in result.notes[0]


def test_detector_failure_without_hand_box_raises(monkeypatch) -> None:
    """A detector failure with no hand-measured box fails loud."""
    monkeypatch.setitem(
        plotbox_detect._DETECTOR_BY_STYLE,
        "mainstream-2color-solid-dashed",
        _raise_value_error,
    )
    chart = _synthetic_chart(None)

    with pytest.raises(PlotBoxUnavailable, match="without guessing"):
        detect_plot_box(chart)
