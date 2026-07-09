"""Tests for `mtfdigitizer.log` (Tier 1 calibration log writer).

Focused on the ADR-044 multi-aperture port (#1160): the writer must
not crash on TTartisan-style charts that pack two apertures per chart
via color encoding.
"""

from __future__ import annotations

from mtfdigitizer.log import (
    _check_logs,
    _extract_panel,
    _ordered_fields,
    _render_lens_log,
)
from mtfdigitizer.referenceset.charts import REFERENCE_CHARTS


def _find_chart(slug: str):
    for chart in REFERENCE_CHARTS:
        if chart.slug == slug:
            return chart
    raise AssertionError(f"reference chart {slug!r} not found")


def _log_for(slug: str) -> str:
    chart = _find_chart(slug)
    return _render_lens_log(chart.slug, [(chart, _extract_panel(chart))])


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


def test_ordered_fields_sorts_by_frequency_then_sagittal_first():
    """_ordered_fields (#1388) sorts by frequency ascending, S before M,
    independent of dict insertion order — so 7artisans (stored M,S) and
    multifreq charts both render in a stable, canonical order."""
    assert _ordered_fields({"freq10M": (), "freq10S": ()}) == ("freq10S", "freq10M")
    assert _ordered_fields(
        {"freq40M": (), "freq10S": (), "freq20S": (), "freq10M": (), "freq40S": (),
         "freq20M": ()}
    ) == ("freq10S", "freq10M", "freq20S", "freq20M", "freq40S", "freq40M")


def test_render_lens_log_emits_all_multifreq_bands():
    """Regression for #1388: the writer hardcoded (freq10/freq30), so a
    multifreq press-kit chart (Zeiss Touit, 10/20/40 lp/mm) rendered only
    freq10 plus a phantom freq30. Every real band must now appear and no
    freq30 may leak in."""
    log_text = _log_for("zeiss-touit-32mm-f1-8")
    for field in ("freq10S", "freq20S", "freq40S", "freq20M", "freq40M"):
        assert f"**{field}**" in log_text, field
    assert "freq30" not in log_text


def test_render_lens_log_emits_fujifilm_bands():
    """Regression for #1388: Fujifilm publishes MTF at 15 & 45 lp/mm.
    The hardcoded tuple omitted both and injected phantom freq30 rows."""
    log_text = _log_for("fujifilm-xf-23mm-f1-4-r-lm-wr")
    for field in ("freq15S", "freq15M", "freq45S", "freq45M"):
        assert f"**{field}**" in log_text, field
    assert "freq30" not in log_text


def test_render_lens_log_preserves_standard_sagittal_first_order():
    """A standard freq10/30 chart whose ground-truth dict stores keys in
    M,S order (7artisans) must still render S before M — this is what
    keeps every pre-#1388 log byte-identical after the switch away from
    the hardcoded tuple."""
    log_text = _log_for("7artisans-50mm-f1-2-mark-ii")
    assert log_text.index("**freq10S**") < log_text.index("**freq10M**")
    assert log_text.index("**freq30S**") < log_text.index("**freq30M**")
    assert "freq20" not in log_text and "freq40" not in log_text


def test_committed_digitization_logs_are_fresh():
    """Staleness gate wired into pytest (#1388). The writer's own
    `--check` was never in CI, so its `--check` passed on the truncated
    output and the multifreq bug shipped unnoticed. This asserts every
    committed digitization-log.md matches a fresh render, so a future
    pipeline change that is not regenerated fails CI."""
    runnable = [c for c in REFERENCE_CHARTS if c.plot_box and c.ground_truth]
    assert _check_logs(runnable) == 0
