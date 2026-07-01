"""Unit tests for `emit_ttartisan_tier2` (ADR-044 emit pipeline).

Targets the pure formatting helpers — string emission, lens-tuple
shape. The end-to-end extractor pipeline (extract_chart →
SampledReading) is exercised by the live runner; this module verifies
that the TS-literal output shape is correct.
"""

from __future__ import annotations

from mtfdigitizer.pipeline.types import SampledReading
from mtfdigitizer.scripts.emit_ttartisan_tier2 import (
    _format_chart_block,
    _format_reading,
    _format_value,
    _ttartisan_lenses,
)


def test_format_value_strips_trailing_zeros():
    assert _format_value(0.5) == "0.5"
    assert _format_value(0.95) == "0.95"
    assert _format_value(0.90) == "0.9"  # no trailing zero
    assert _format_value(0.0) == "0"
    assert _format_value(None) == "null"


def test_format_reading_emits_per_frequency_pairs():
    """One SampledReading → one TS object with `position` + `samples` of
    `{freq: { S, M }}` pairs, sorted by frequency."""
    reading = SampledReading(
        position_mm=5.6,
        samples={
            "freq10S": 0.95,
            "freq10M": 0.94,
            "freq30S": 0.80,
            "freq30M": None,
        },
    )
    out = _format_reading(reading)
    # Position appears as plain number, sample keys in frequency order.
    assert "position: 5.6," in out
    assert "10: { S: 0.95, M: 0.94 }" in out
    assert "30: { S: 0.8, M: null }" in out
    # Frequencies sorted (10 then 30 — not order of dict insertion)
    assert out.index("10:") < out.index("30:")


def test_format_chart_block_carries_aperture_and_readings():
    """A chart block carries the f-number (NOT the orchestrator label)
    and the readings array."""
    readings = (
        SampledReading(
            position_mm=0.0,
            samples={"freq10S": 0.9, "freq10M": 0.9, "freq30S": 0.5, "freq30M": 0.5},
        ),
    )
    out = _format_chart_block("f/1.2", readings, "HIGH", None)
    assert 'aperture: "f/1.2",' in out
    assert "readings: [" in out
    assert "position: 0," in out


def test_format_chart_block_emits_high_confidence():
    """HIGH passes carry `confidence: "HIGH"` and no `confidenceReason`."""
    readings = (
        SampledReading(
            position_mm=0.0,
            samples={"freq10S": 0.9},
        ),
    )
    out = _format_chart_block("f/1.2", readings, "HIGH", None)
    assert 'confidence: "HIGH",' in out
    assert "confidenceReason" not in out


def test_format_chart_block_emits_low_confidence_with_reason():
    """LOW passes carry `confidence: "LOW"` and the reason code."""
    readings = (
        SampledReading(
            position_mm=0.0,
            samples={"freq10S": 0.9},
        ),
    )
    out = _format_chart_block(
        "f/5.6", readings, "LOW", "prior_failed_center_ge_edge"
    )
    assert 'confidence: "LOW",' in out
    assert 'confidenceReason: "prior_failed_center_ge_edge",' in out


def test_format_chart_block_keeps_position_0_even_when_all_null():
    """The mtf-readings data-integrity test asserts position 0 is always
    present. Mirror the Fuji emit's null-row preservation."""
    readings = (
        SampledReading(
            position_mm=0.0,
            samples={"freq10S": None, "freq10M": None, "freq30S": None, "freq30M": None},
        ),
        SampledReading(
            position_mm=14.0,
            samples={"freq10S": 0.6, "freq10M": 0.6, "freq30S": 0.3, "freq30M": 0.3},
        ),
    )
    out = _format_chart_block("f/1.2", readings, "HIGH", None)
    assert "position: 0," in out  # kept despite all-null samples


def test_format_chart_block_drops_intermediate_all_null_rows():
    """A middle row where every sample is None drops out (the renderer
    doesn't need it — `position: 0` is the only forced-keep)."""
    readings = (
        SampledReading(
            position_mm=0.0,
            samples={"freq10S": 0.9, "freq30S": 0.5},
        ),
        SampledReading(
            position_mm=5.0,
            samples={"freq10S": None, "freq30S": None},  # drop
        ),
        SampledReading(
            position_mm=14.0,
            samples={"freq10S": 0.6, "freq30S": 0.3},
        ),
    )
    out = _format_chart_block("f/1.2", readings, "HIGH", None)
    assert "position: 0," in out
    assert "position: 14," in out
    assert "position: 5," not in out


def test_ttartisan_lenses_returns_19_entries():
    """The emit walker must find every TTartisan 4-color dual-aperture
    chart: 17 Tier 2 (auto-scaffolded) + 2 Tier 1 anchors (50/1.2 and
    7.5 fisheye, both maintained inline in `charts.py` per ADR-041) = 19.
    (#1090 unblocked the 2 100mm-macro twins that were temporarily
    skipped via an allowlist; the 7.5 fisheye was promoted from Tier 2
    to a second Tier 1 anchor in session 148.)"""
    lenses = _ttartisan_lenses()
    assert len(lenses) == 19
    for lens in lenses:
        assert lens.style_family == "ttartisan-4color-dual-aperture"
        assert len(lens.apertures) == 2  # max + stopped


def test_ttartisan_aperture_tuple_aligns_with_profile():
    """Every TTartisan ReferenceChart's `apertures` tuple must align
    positionally with the profile's `apertures_per_chart`. The emit
    script's _emit_one_lens zip-aligns them — if they ever drift, the
    f-number on the panel would mis-label the wrong aperture pass."""
    from mtfdigitizer.family_profile import profile_for_chart

    for lens in _ttartisan_lenses():
        profile = profile_for_chart(lens)
        assert profile.apertures_per_chart is not None
        assert len(profile.apertures_per_chart) == len(lens.apertures), lens.slug
        # First position is always max-aperture lens stop; second is stopped.
        assert profile.apertures_per_chart == ("max", "stopped"), profile.name


def test_format_reading_uses_compact_position_repr():
    """Position values are emitted with `:g` — no trailing zeros or
    decimal point for integers. The mtf-readings data-integrity tests
    expect this representation (e.g. `position: 0,` not
    `position: 0.0,`)."""
    integer_pos = SampledReading(position_mm=14.0, samples={"freq10S": 0.5})
    decimal_pos = SampledReading(position_mm=5.6, samples={"freq10S": 0.5})
    assert "position: 14," in _format_reading(integer_pos)
    assert "position: 5.6," in _format_reading(decimal_pos)
