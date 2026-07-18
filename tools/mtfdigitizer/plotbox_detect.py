"""Unified plot-box detection dispatch (ADR-084; extends ADR-064).

The digitizer ships one plot-box detector per chart family that warrants
auto-detection:

    style_family                     detector
    ------------------------------   ------------------------------------
    mainstream-2color-solid-dashed   pipeline.plotbox.detect_sigma_plot_box
    mainstream-4color-all-solid      samyang_plotbox.detect_samyang_plotbox
    ttartisan-4color-dual-aperture   ttartisan_plotbox.detect_ttartisan_plotbox
    fujifilm-permfreq                fuji_plotbox.detect_fuji_plotbox

ADR-064 formalized how each detector is *named*; it deliberately left
them per-brand, with divergent signatures (a BGR array for Sigma vs a
path for the rest), return types (a bare `PlotBox` vs a `<Brand>BoxResult`),
and failure modes (`ValueError` vs a `<Brand>PlotBoxError` vs a
None / sentinel result). Every caller that wanted a box therefore had to
know which brand it was holding and adapt by hand — the per-brand
scaffolders each hard-code their own detector.

This module adds the missing routing layer: `detect_plot_box(chart)`
keys on `chart.style_family`, calls the right detector, and normalizes
the primary box into a `DetectedPlotBox`. When no detector covers the
family (Tokina, Viltrox, Zeiss, 7Artisans today) or detection fails, it
falls back to the chart's hand-measured `plot_box`. When neither a
detector nor a hand-measured box can supply one, it raises
`PlotBoxUnavailable` rather than guess (ADR-081 §4, ADR-038 §4 B1: a
silent wrong box is visible in the rendered table and forfeits the
reproduction's credibility).

The dispatch is read-only over the reference set — it does not rewrite
any committed box, so routing a caller through it changes zero output.
The four detectors keep their ADR-064 surfaces untouched; this is a thin
adapter on top, not a rewrite.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from .fuji_plotbox import detect_fuji_plotbox
from .loader import load_chart_bgr
from .pipeline import PlotBox
from .pipeline.plotbox import detect_sigma_plot_box
from .samyang_plotbox import SamyangPlotBoxError, detect_samyang_plotbox
from .ttartisan_plotbox import TTartisanPlotBoxError, detect_ttartisan_plotbox

if TYPE_CHECKING:
    from .referenceset.charts import PlotBoxCoords, ReferenceChart


REPO_ROOT = Path(__file__).resolve().parents[2]


class PlotBoxUnavailable(RuntimeError):
    """No detector covers the chart's family and it carries no hand-
    measured box, so the dispatch cannot supply a plot box without
    guessing."""


class _DetectorFailed(RuntimeError):
    """Internal: normalizes a detector's non-exception failure (Fuji's
    None / sentinel result) into a raised error, so the dispatch handles
    every detector's failure through one code path."""


# Detection failures worth catching and turning into a hand-measured
# fallback. Sigma raises bare `ValueError` (#950, predates ADR-064);
# Samyang / TTartisan raise their ADR-064 `<Brand>PlotBoxError`; Fuji
# returns None / a sentinel box, normalized to `_DetectorFailed` in its
# adapter below.
_DETECTION_ERRORS = (
    ValueError,
    SamyangPlotBoxError,
    TTartisanPlotBoxError,
    _DetectorFailed,
)


@dataclass(frozen=True)
class DetectedPlotBox:
    """A plot box resolved for one chart, plus how it was obtained.

    `plot_box` is always the primary plot rectangle. `source` is
    ``"detected"`` when a family detector produced it and ``"fallback"``
    when the detector was absent or failed and the chart's hand-measured
    box was used instead. `detector` names the family key that ran
    (``"sigma"``, ``"samyang"``, ...) or ``"hand-measured"`` on fallback.

    `secondary_box` carries a second panel when the family packs one into
    the same PNG (Samyang's stopped-aperture panel); it is None for
    single-panel families. `image_height_mm` is filled by detectors that
    calibrate it from the chart (TTartisan, Fuji) and None otherwise.
    `notes` records the fallback reason, so a silent-looking fallback
    stays traceable.
    """

    plot_box: PlotBox
    source: str
    detector: str
    secondary_box: PlotBox | None = None
    image_height_mm: float | None = None
    notes: tuple[str, ...] = ()


def _coords_to_box(coords: "PlotBoxCoords") -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
    )


def _tuple_to_box(coords: tuple[int, int, int, int]) -> PlotBox:
    x_left, x_right, y_top, y_bottom = coords
    return PlotBox(
        x_left=x_left, x_right=x_right, y_top=y_top, y_bottom=y_bottom
    )


def _chart_image(chart: "ReferenceChart") -> Path:
    return REPO_ROOT / chart.chart_path


def _detect_sigma(chart: "ReferenceChart") -> DetectedPlotBox:
    image = load_chart_bgr(_chart_image(chart))
    box = detect_sigma_plot_box(image)
    return DetectedPlotBox(plot_box=box, source="detected", detector="sigma")


def _detect_samyang(chart: "ReferenceChart") -> DetectedPlotBox:
    result = detect_samyang_plotbox(_chart_image(chart))
    return DetectedPlotBox(
        plot_box=_tuple_to_box(result.plot_box),
        source="detected",
        detector="samyang",
        secondary_box=_tuple_to_box(result.stopped_box),
    )


def _detect_ttartisan(chart: "ReferenceChart") -> DetectedPlotBox:
    result = detect_ttartisan_plotbox(_chart_image(chart))
    return DetectedPlotBox(
        plot_box=_tuple_to_box(result.plot_box),
        source="detected",
        detector="ttartisan",
        image_height_mm=result.image_height_mm,
    )


def _detect_fuji(chart: "ReferenceChart") -> DetectedPlotBox:
    # Fuji signals failure by returning None (unreadable image) or a
    # (0, 0, 0, 0) sentinel box with the reason in `notes`, rather than
    # raising. Normalize both to `_DetectorFailed` so the dispatch's
    # single except clause handles it like every other detector.
    result = detect_fuji_plotbox(_chart_image(chart))
    if result is None:
        raise _DetectorFailed("image could not be read")
    if result.plot_box == (0, 0, 0, 0):
        raise _DetectorFailed("; ".join(result.notes) or "detection failed")
    return DetectedPlotBox(
        plot_box=_tuple_to_box(result.plot_box),
        source="detected",
        detector="fuji",
        image_height_mm=result.image_height_mm,
    )


# Single source of truth for style_family -> detector, mirroring
# `family_profile.PROFILE_BY_STYLE`. A family absent here has no detector
# yet; `detect_plot_box` falls back to its hand-measured box. Only
# validated detectors are listed — an unproven mapping would let a
# wrong-but-non-raising box silently override the hand-measured one,
# exactly the failure ADR-081 §4 forbids.
_DETECTOR_BY_STYLE: dict[
    str, Callable[["ReferenceChart"], DetectedPlotBox]
] = {
    "mainstream-2color-solid-dashed": _detect_sigma,
    "mainstream-4color-all-solid": _detect_samyang,
    # `idealized-flat` is the Samyang 4-color template under a distinct
    # family name (the flat ~1.0 reflex chart); `family_profile` already
    # maps it to the Samyang profile, and the Samyang detector reproduces
    # its committed box exactly. Route it to the same detector so a
    # shared-template chart still gets detection (ADR-081 §5).
    "idealized-flat": _detect_samyang,
    "ttartisan-4color-dual-aperture": _detect_ttartisan,
    "fujifilm-permfreq": _detect_fuji,
}


def has_detector(style_family: str) -> bool:
    """Whether a plot-box detector covers `style_family`."""
    return style_family in _DETECTOR_BY_STYLE


def _fallback(chart: "ReferenceChart", reason: str) -> DetectedPlotBox:
    if chart.plot_box is None:
        raise PlotBoxUnavailable(
            f"{chart.slug}: {reason}, and the chart carries no hand-"
            f"measured plot_box — cannot supply a plot box without guessing"
        )
    return DetectedPlotBox(
        plot_box=_coords_to_box(chart.plot_box),
        source="fallback",
        detector="hand-measured",
        notes=(reason,),
    )


def detect_plot_box(chart: "ReferenceChart") -> DetectedPlotBox:
    """Resolve the plot box for one reference chart.

    Routes on `chart.style_family` to the family's detector and returns a
    ``source="detected"`` box on success. When no detector covers the
    family, or detection fails, falls back to the chart's hand-measured
    `plot_box` (``source="fallback"``, with the reason in `notes`).
    Raises `PlotBoxUnavailable` when neither is available — never returns
    a silently guessed box (ADR-081 §4).
    """
    detector = _DETECTOR_BY_STYLE.get(chart.style_family)
    if detector is None:
        return _fallback(
            chart, f"no detector for style_family={chart.style_family!r}"
        )
    try:
        return detector(chart)
    except _DETECTION_ERRORS as exc:
        return _fallback(chart, f"{type(exc).__name__}: {exc}")
