"""Tests for `mtfdigitizer.log` (Tier 1 calibration log writer).

Focused on the ADR-044 multi-aperture port (#1160): the writer must
not crash on TTartisan-style charts that pack two apertures per chart
via color encoding.
"""

from __future__ import annotations

from mtfdigitizer.log import _extract_panel, _render_lens_log
from mtfdigitizer.referenceset.charts import REFERENCE_CHARTS


def _find_chart(slug: str):
    for chart in REFERENCE_CHARTS:
        if chart.slug == slug:
            return chart
    raise AssertionError(f"reference chart {slug!r} not found")


def test_extract_panel_handles_multi_aperture_ttartisan():
    """Pre-ADR-044, _extract_panel called extract_chart with the full
    multi-aperture profile and crashed with KeyError on the stopped
    hues. Post-port, it returns one ExtractedChart per aperture."""
    chart = _find_chart("ttartisan-7-5mm-f2-0-fisheye")
    extracted_by_ap = _extract_panel(chart)
    assert set(extracted_by_ap.keys()) == {"max", "stopped"}
    for aperture, extracted in extracted_by_ap.items():
        # Each pass produces 11 sample readings (one per fraction).
        assert len(extracted.readings) == 11, aperture


def test_extract_panel_handles_single_aperture_chart():
    """Non-TTartisan reference charts have one aperture; the dict
    should have exactly one entry keyed by the chart's aperture label."""
    chart = _find_chart("sigma-56mm-f1-4-dc-dn-c")
    extracted_by_ap = _extract_panel(chart)
    assert len(extracted_by_ap) == 1
    (aperture,) = extracted_by_ap.keys()
    assert aperture == chart.apertures[0]
    assert len(extracted_by_ap[aperture].readings) == 11


def test_render_lens_log_emits_per_aperture_sections_for_ttartisan():
    """For multi-aperture charts the rendered log must include per-
    aperture sections (`#### Aperture max` / `#### Aperture stopped`)
    with per-aperture EX values - no single aperture's readings should
    leak into the other's stats."""
    chart = _find_chart("ttartisan-7-5mm-f2-0-fisheye")
    extracted_by_ap = _extract_panel(chart)
    log_text = _render_lens_log(chart.slug, [(chart, extracted_by_ap)])
    assert "#### Aperture max" in log_text
    assert "#### Aperture stopped" in log_text
    # Both apertures' grids must report 11/11 paired on at least one
    # field — would fail with the pre-port behaviour where the second
    # pass's readings did not exist.
    assert log_text.count("| freq10S        | 11/11") >= 2
