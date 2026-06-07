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
from mtfdigitizer.referenceset.charts import PlotBoxCoords, ReferenceChart


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

    with pytest.raises(KeyError, match="apertures_per_chart"):
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
