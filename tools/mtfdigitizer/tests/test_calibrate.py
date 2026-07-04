"""Tests for the calibration runner's dispatch shapes (ADR-043, ADR-044).

The calibrator handles three dispatch shapes:

- Standard single-aperture single-image (Sigma, Samyang, Tokina,
  7Artisans, Viltrox)
- Per-frequency single-aperture multi-image (Fujifilm; ADR-043)
- Multi-aperture single-image (TTartisan; ADR-044)

This module focuses on the multi-aperture path that landed with #1074
items 3+4 — the other two paths are exercised by the live
`calibrate.py` runner on the actual reference set.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mtfdigitizer import calibrate as calibrate_mod
from mtfdigitizer.pipeline.types import ExtractedChart, PlotBox, SampledReading
from mtfdigitizer.profiles.types import HueRange, MtfProfile
from mtfdigitizer.referenceset.charts import (
    REFERENCE_CHARTS,
    PlotBoxCoords,
    ReferenceChart,
)


@pytest.fixture
def multi_aperture_chart():
    """A minimal multi-aperture chart with two-aperture ground truth.

    Profile declares ``apertures_per_chart=("max", "stopped")``; ground
    truth carries one tuple per (aperture, field) at the 11 sample
    fractions. The plot_box and chart_path are real-looking but the
    extractor is monkeypatched so the chart raster is never read.
    """
    return ReferenceChart(
        slug="probe-ttartisan",
        chart_path="docs/optical-specs/probe-ttartisan/probe-ttartisan-mtf.png",
        style_family="ttartisan-4color-dual-aperture",
        apertures=("f/1.2", "f/5.6"),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="probe",
        plot_box=PlotBoxCoords(x_left=87, x_right=607, y_top=116, y_bottom=461),
        ground_truth={
            "max": {
                "freq10S": (0.9,) * 11,
                "freq30S": (0.5,) * 11,
            },
            "stopped": {
                "freq10S": (0.95,) * 11,
                "freq30S": (0.7,) * 11,
            },
        },
    )


@pytest.fixture
def probe_profile():
    return MtfProfile(
        name="probe-dual",
        hues=(
            HueRange(name="max-10-black", h_lo=0, h_hi=179, s_min=0, v_max=80),
            HueRange(name="max-30-grey", h_lo=0, h_hi=179, s_min=0, v_min=90, v_max=160),
            HueRange(name="stopped-10-red", h_lo=0, h_hi=5, s_min=80, v_min=80),
            HueRange(name="stopped-30-orange", h_lo=12, h_hi=22, s_min=80, v_min=80),
        ),
        style_axis="SPLIT_BY_DASH",
        hue_meaning="FREQUENCY",
        frequencies_lpmm=(10, 30),
        apertures_per_chart=("max", "stopped"),
    )


def _make_readings(value_by_field: dict[str, float]) -> tuple[SampledReading, ...]:
    """11 SampledReadings with the same value across every position."""
    from mtfdigitizer.pipeline.sampling import SAMPLE_FRACTIONS

    return tuple(
        SampledReading(
            position_mm=frac * 14.0,
            samples=dict(value_by_field),
        )
        for frac in SAMPLE_FRACTIONS
    )


def test_multi_aperture_dispatch_runs_one_pass_per_aperture(
    monkeypatch, multi_aperture_chart, probe_profile
):
    """`_calibrate_chart` for a multi-aperture chart calls the
    extractor once per declared aperture, each with a hue-filtered
    profile, and returns a dict keyed by aperture label."""
    calls: list[tuple[str, ...]] = []

    def fake_extract_chart(image_path, profile, plot_box, *, image_height_mm):
        # Tag the call by which hue names the filtered profile carries.
        calls.append(tuple(h.name for h in profile.hues))
        # Synthesize readings whose value matches the aperture so the
        # test can verify the right pass's readings go into the right
        # GT-vs-EX comparison.
        if any(h.name.startswith("max-") for h in profile.hues):
            readings = _make_readings({"freq10S": 0.9, "freq30S": 0.5})
        else:
            readings = _make_readings({"freq10S": 0.95, "freq30S": 0.7})
        return ExtractedChart(
            source_path=str(image_path),
            profile_name=profile.name,
            plot_box=plot_box,
            image_height_mm=image_height_mm,
            readings=readings,
        )

    monkeypatch.setattr(calibrate_mod, "extract_chart", fake_extract_chart)
    monkeypatch.setattr(
        calibrate_mod, "profile_for_chart", lambda chart: probe_profile
    )

    field_deltas, result = calibrate_mod._calibrate_chart(multi_aperture_chart)

    # Two passes: one per aperture, each with only its own hues.
    assert len(calls) == 2
    assert calls[0] == ("max-10-black", "max-30-grey")
    assert calls[1] == ("stopped-10-red", "stopped-30-orange")

    # Result is a per-aperture dict.
    assert isinstance(result, dict)
    assert set(result.keys()) == {"max", "stopped"}

    # GT-vs-EX paired correctly: max pass returned exactly GT values
    # (every Δ = 0), stopped pass also returned exactly GT values.
    by_key = {(fd.aperture, fd.field): fd for fd in field_deltas}
    assert by_key[("max", "freq10S")].deltas == (0.0,) * 11
    assert by_key[("max", "freq30S")].deltas == (0.0,) * 11
    assert by_key[("stopped", "freq10S")].deltas == (0.0,) * 11
    assert by_key[("stopped", "freq30S")].deltas == (0.0,) * 11


def test_multi_aperture_dispatch_rejects_unknown_gt_aperture(
    monkeypatch, multi_aperture_chart, probe_profile
):
    """A GT aperture key that the profile didn't declare is a fail-loud
    event — masks a missing extractor pass otherwise."""
    monkeypatch.setattr(
        calibrate_mod, "extract_chart",
        lambda *a, **kw: ExtractedChart(
            source_path="", profile_name="probe",
            plot_box=PlotBox(x_left=0, x_right=10, y_top=0, y_bottom=10),
            image_height_mm=14.0, readings=_make_readings({"freq10S": 0.9}),
        ),
    )
    monkeypatch.setattr(
        calibrate_mod, "profile_for_chart", lambda chart: probe_profile
    )

    # Inject a stray aperture key into ground truth — same shape as a
    # maintainer mis-typing the aperture label.
    chart_with_bad_gt = ReferenceChart(
        slug=multi_aperture_chart.slug,
        chart_path=multi_aperture_chart.chart_path,
        style_family=multi_aperture_chart.style_family,
        apertures=multi_aperture_chart.apertures,
        frequencies_lpmm=multi_aperture_chart.frequencies_lpmm,
        image_height_mm=multi_aperture_chart.image_height_mm,
        notes=multi_aperture_chart.notes,
        plot_box=multi_aperture_chart.plot_box,
        ground_truth={
            "max": multi_aperture_chart.ground_truth["max"],
            "MAX": multi_aperture_chart.ground_truth["max"],  # the typo
        },
    )

    with pytest.raises(KeyError, match="not in extracted passes"):
        calibrate_mod._calibrate_chart(chart_with_bad_gt)


def test_readings_for_aperture_handles_dict_and_single(multi_aperture_chart):
    """`_readings_for_aperture` returns the right readings tuple for
    either result shape."""
    single = ExtractedChart(
        source_path="x", profile_name="p",
        plot_box=PlotBox(x_left=0, x_right=10, y_top=0, y_bottom=10),
        image_height_mm=14.0, readings=_make_readings({"freq10S": 0.5}),
    )
    # Single-aperture: ignores aperture, returns the one readings tuple.
    assert calibrate_mod._readings_for_aperture(single, "any") is single.readings
    assert calibrate_mod._readings_for_aperture(single, "max") is single.readings

    # Multi-aperture: picks the matching aperture's readings.
    by_ap = {
        "max": ExtractedChart(
            source_path="x", profile_name="p",
            plot_box=PlotBox(x_left=0, x_right=10, y_top=0, y_bottom=10),
            image_height_mm=14.0, readings=_make_readings({"freq10S": 0.9}),
        ),
        "stopped": ExtractedChart(
            source_path="x", profile_name="p",
            plot_box=PlotBox(x_left=0, x_right=10, y_top=0, y_bottom=10),
            image_height_mm=14.0, readings=_make_readings({"freq10S": 0.95}),
        ),
    }
    assert calibrate_mod._readings_for_aperture(by_ap, "max") is by_ap["max"].readings
    assert calibrate_mod._readings_for_aperture(by_ap, "stopped") is by_ap["stopped"].readings


# ---------------------------------------------------------------------------
# Real-chart calibration gate -- Zeiss Touit 12mm f/2.8 (#1347)
#
# Promotes the 12mm press-kit panel (both apertures) from the print-only
# `calibrate.py` runner to a gated pytest tier, per quality-gates
# "promote a resistant case to a gated tier". The 12mm ground truth
# (both panels, all 11 positions) was maintainer-eye-read and applied in
# #1348, so it is a sound anchor to gate against. Unlike the dispatch
# tests above, these run the real extractor on the real chart raster.
#
# Two tests split the signal:
#   * `test_touit_12mm_stopped_panel_stays_calibrated` -- a hard
#     regression guard on the panels/fields that already extract well.
#     Spike attempt 1 (#1347, global gap-based band split) regressed
#     exactly these (stopped freq20S 0.005 -> 0.118; freq20M/freq40M
#     dropped to 0/11); this guard is what catches that class.
#   * `test_touit_12mm_max_panel_m_curves_recovered` -- xfail(strict)
#     on the broken max-panel cells (dashed M curves dropped, 20 lp/mm
#     mis-filed under freq40). The interior-anchoring fix flips this to
#     xpass; the strict marker then fails the run -- the signal to drop
#     the marker and keep the body as a hard assertion.
# ---------------------------------------------------------------------------

_TOUIT_12_SLUG = "zeiss-touit-12mm-f2-8"


@pytest.fixture(scope="module")
def touit_12mm_deltas() -> dict[tuple[str, str], calibrate_mod.FieldDelta]:
    """Run the real extractor on the 12mm reference chart (both panels).

    Returns a ``{(aperture, field): FieldDelta}`` lookup so the two gate
    tests can assert per-cell without re-running the real-raster
    extraction twice.
    """
    chart = next(c for c in REFERENCE_CHARTS if c.slug == _TOUIT_12_SLUG)
    field_deltas, _ = calibrate_mod._calibrate_chart(chart)
    return {(fd.aperture, fd.field): fd for fd in field_deltas}


def _cell(
    deltas: dict[tuple[str, str], calibrate_mod.FieldDelta],
    aperture: str,
    field: str,
) -> calibrate_mod.FieldDelta:
    fd = deltas.get((aperture, field))
    assert fd is not None, f"no FieldDelta for {aperture}/{field}"
    return fd


def test_touit_12mm_stopped_panel_stays_calibrated(touit_12mm_deltas) -> None:
    """Hard regression guard: the 12mm stopped panel and the max-panel
    freq10S extract within tolerance and MUST stay there.

    Pins: on the maintainer-verified 12mm GT (#1348), RIDGE_TRACKING
    keeps the stopped-panel S curves paired 11/11 at med |d| <= 0.02 and
    the sparse stopped M curves paired >= their S200 floor. Calibrated
    against the S200 baseline (stopped S med |d| 0.003-0.005). Spike
    attempt 1 (#1347) regressed freq20S to 0.118 and dropped
    freq20M/freq40M to 0/11 -- this guard catches that class.

    If a legitimate extractor improvement moves these, re-run
    `py -m mtfdigitizer.calibrate` and update the thresholds to the new
    floor; do not loosen them to paper over a regression.
    """
    d = touit_12mm_deltas

    # max panel: freq10S is the one max-panel curve that already reads
    # correctly (the f/2.8 corner crash inflates p95 but not the median).
    s10 = _cell(d, "max", "freq10S")
    assert s10.paired_count >= 9
    assert s10.median_abs_delta is not None and s10.median_abs_delta <= 0.02

    # stopped panel: all three S curves paired 11/11 at a low median.
    for field, min_paired, max_med in (
        ("freq10S", 9, 0.02),
        ("freq20S", 11, 0.02),
        ("freq40S", 11, 0.03),
    ):
        fd = _cell(d, "stopped", field)
        assert fd.paired_count >= min_paired, f"stopped/{field} paired {fd.paired_count}"
        assert (
            fd.median_abs_delta is not None and fd.median_abs_delta <= max_med
        ), f"stopped/{field} med |d| {fd.median_abs_delta}"

    # stopped panel: the sparse dashed M curves must still pair some
    # cells and read low where they do (attempt 1 dropped these to 0/11).
    for field, min_paired in (("freq10M", 3), ("freq20M", 4), ("freq40M", 8)):
        fd = _cell(d, "stopped", field)
        assert fd.paired_count >= min_paired, f"stopped/{field} paired {fd.paired_count}"
        assert (
            fd.median_abs_delta is not None and fd.median_abs_delta <= 0.03
        ), f"stopped/{field} med |d| {fd.median_abs_delta}"


@pytest.mark.xfail(
    strict=True,
    reason="#1347: interior-anchoring fix not yet built -- the 12mm max "
    "panel drops the dashed M curves (freq10M/freq20M 0/11) and files the "
    "20 lp/mm curve under freq40. When the fix lands this xpasses; drop "
    "the marker and keep the body as a hard assertion.",
)
def test_touit_12mm_max_panel_m_curves_recovered(touit_12mm_deltas) -> None:
    """Target gate: the 12mm max panel recovers its dashed M curves and
    assigns 20/40 lp/mm correctly.

    Pins the fixed state against the #1348 GT: freq20S paired >= 9 at
    med |d| <= 0.03 (today 2/11 at 0.151 -- the 20-curve is mis-filed
    under freq40), the dashed M curves detected (freq10M >= 6, freq20M
    >= 4; today both 0/11), and freq40S reading its own curve at med |d|
    <= 0.05 (today 0.157 -- it carries the 20-curve). See #1347 for the
    interior-anchoring approach and the rejected attempt 1.
    """
    d = touit_12mm_deltas

    s20 = _cell(d, "max", "freq20S")
    assert s20.paired_count >= 9
    assert s20.median_abs_delta is not None and s20.median_abs_delta <= 0.03

    assert _cell(d, "max", "freq10M").paired_count >= 6
    assert _cell(d, "max", "freq20M").paired_count >= 4

    s40 = _cell(d, "max", "freq40S")
    assert s40.paired_count >= 9
    assert s40.median_abs_delta is not None and s40.median_abs_delta <= 0.05
