"""Tests for emit.py: ExtractedChart → TypeScript object literal."""

from __future__ import annotations

from mtfdigitizer.emit import (
    _FIELDS,
    _format_entry,
    _format_reading,
    _format_value,
    _has_any_data,
)
from mtfdigitizer.pipeline.types import SampledReading


def _r(
    pos: float = 0.0,
    c10s: float | None = 0.9,
    c10m: float | None = 0.9,
    r30s: float | None = 0.7,
    r30m: float | None = 0.7,
) -> SampledReading:
    return SampledReading(
        position_mm=pos,
        contrast10S=c10s,
        contrast10M=c10m,
        resolution30S=r30s,
        resolution30M=r30m,
    )


# --- _format_value -------------------------------------------------------


def test_format_value_renders_two_decimals() -> None:
    assert _format_value(0.92) == "0.92"


def test_format_value_strips_floating_point_noise() -> None:
    assert _format_value(0.92000000001) == "0.92"


def test_format_value_renders_none_as_null() -> None:
    assert _format_value(None) == "null"


def test_format_value_renders_one_as_one_decimal_two_digits() -> None:
    # The lens-page table calls .toFixed(2) on the JS side; the emitted
    # TS literal should be a valid number, not "1" or "1.0" specifically.
    assert _format_value(1.0) == "1.00"


# --- _has_any_data -------------------------------------------------------


def test_has_any_data_true_when_one_field_present() -> None:
    r = _r(c10s=0.9, c10m=None, r30s=None, r30m=None)
    assert _has_any_data(r) is True


def test_has_any_data_false_when_all_fields_none() -> None:
    r = _r(c10s=None, c10m=None, r30s=None, r30m=None)
    assert _has_any_data(r) is False


# --- _format_reading -----------------------------------------------------


def test_format_reading_includes_all_four_fields() -> None:
    out = _format_reading(_r(pos=5.0, c10s=0.95, c10m=0.94, r30s=0.85, r30m=0.84))
    for field in _FIELDS:
        assert field in out


def test_format_reading_emits_null_for_none_fields() -> None:
    out = _format_reading(_r(c10m=None, r30m=None))
    assert "contrast10M: null," in out
    assert "resolution30M: null," in out
    assert "null: null" not in out  # only field values become null


def test_format_reading_position_renders_without_trailing_zero() -> None:
    out = _format_reading(_r(pos=14.0))
    assert "position: 14," in out


def test_format_reading_position_renders_float() -> None:
    out = _format_reading(_r(pos=1.4))
    assert "position: 1.4," in out


# --- _format_entry -------------------------------------------------------


def test_format_entry_wraps_a_lens_block() -> None:
    rows = (_r(pos=0), _r(pos=5.0))
    out = _format_entry(
        slug="test-lens",
        source="https://example.com/lens",
        aperture="f/2.8",
        paired=rows,
    )
    assert '"test-lens":' in out
    assert 'source: "https://example.com/lens",' in out
    assert 'mtfType: "measured",' in out
    assert 'aperture: "f/2.8",' in out
    # Both rows appear
    assert out.count("position:") == 2


def test_format_entry_empty_readings_block_is_valid_ts() -> None:
    out = _format_entry(
        slug="test-lens", source="https://x", aperture="f/2", paired=()
    )
    assert "readings: [\n\n        ]," in out
