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
        samples={
            "freq10S": c10s,
            "freq10M": c10m,
            "freq30S": r30s,
            "freq30M": r30m,
        },
    )


# --- _format_value -------------------------------------------------------


def test_format_value_renders_two_decimals() -> None:
    assert _format_value(0.92) == "0.92"


def test_format_value_strips_floating_point_noise() -> None:
    assert _format_value(0.92000000001) == "0.92"


def test_format_value_renders_none_as_null() -> None:
    assert _format_value(None) == "null"


def test_format_value_strips_trailing_zeros() -> None:
    # unicorn/no-zero-fractions rejects `0.90` and `1.00` literals; emit
    # must produce the canonical form prettier+eslint will accept.
    assert _format_value(0.9) == "0.9"
    assert _format_value(1.0) == "1"


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
    # ADR-042: per-frequency record. Each frequency emits its own
    # `S` / `M` pair under `samples`.
    assert "samples: {" in out
    assert "10: { S: 0.95, M: 0.94 }" in out
    assert "30: { S: 0.85, M: 0.84 }" in out


def test_format_reading_emits_null_for_none_fields() -> None:
    out = _format_reading(_r(c10m=None, r30m=None))
    # ADR-042: nulls flow through into the samples-record shape.
    assert "M: null" in out
    assert "null: null" not in out  # only field values become null


def test_format_reading_position_renders_without_trailing_zero() -> None:
    out = _format_reading(_r(pos=14.0))
    assert "position: 14," in out


def test_format_reading_position_renders_float() -> None:
    out = _format_reading(_r(pos=1.4))
    assert "position: 1.4," in out


# --- _format_chart focal length ------------------------------------------


def test_format_chart_omits_focal_length_when_none() -> None:
    from mtfdigitizer.emit import _format_chart

    out = _format_chart("f/1.4", (_r(pos=0),), focal_length=None)
    assert "focalLength" not in out


def test_format_chart_renders_focal_length_when_set() -> None:
    from mtfdigitizer.emit import _format_chart

    out = _format_chart("f/2.8", (_r(pos=0),), focal_length=10)
    assert "focalLength: 10," in out


# --- _format_entry -------------------------------------------------------


def test_format_entry_wraps_a_lens_block() -> None:
    rows = (_r(pos=0), _r(pos=5.0))
    out = _format_entry(
        slug="test-lens",
        mtf_type="measured",
        panels=(("f/2.8", None, rows, "HIGH", None),),
    )
    assert '"test-lens":' in out
    # `source` field was removed in #1342; the lens page reads
    # `officialUrl` from lenses.ts at render time instead.
    assert "source:" not in out
    assert 'mtfType: "measured",' in out
    assert 'aperture: "f/2.8",' in out
    assert 'confidence: "HIGH",' in out
    # Both rows appear
    assert out.count("position:") == 2


def test_format_entry_emits_computed_mtf_type_when_requested() -> None:
    out = _format_entry(
        slug="sigma-lens",
        mtf_type="computed",
        panels=(("f/1.4", None, (_r(pos=0),), "HIGH", None),),
    )
    assert 'mtfType: "computed",' in out
    assert 'mtfType: "measured",' not in out


def test_format_entry_empty_readings_block_is_valid_ts() -> None:
    out = _format_entry(
        slug="test-lens",
        mtf_type="measured",
        panels=(("f/2", None, (), "HIGH", None),),
    )
    assert "readings: [\n\n        ]," in out


def test_format_entry_emits_two_panels_for_zoom() -> None:
    """ADR-033: a zoom emits one chart entry per published focal length."""
    out = _format_entry(
        slug="sigma-10-18mm-f2-8-dc-dn-c",
        mtf_type="computed",
        panels=(
            ("f/2.8", 10, (_r(pos=0), _r(pos=14.0)), "HIGH", None),
            ("f/2.8", 18, (_r(pos=0), _r(pos=14.0)), "HIGH", None),
        ),
    )
    # One charts: [...] array, two chart objects inside
    assert out.count("aperture:") == 2
    assert "focalLength: 10," in out
    assert "focalLength: 18," in out


def test_format_entry_prime_emits_no_focal_length_line() -> None:
    """Primes have focal_length=None — emitted TS must not include the key."""
    out = _format_entry(
        slug="sigma-56mm-f1-4-dc-dn-c",
        mtf_type="computed",
        panels=(("f/1.4", None, (_r(pos=0),), "HIGH", None),),
    )
    assert "focalLength" not in out


def test_format_entry_emits_low_confidence_with_reason() -> None:
    """ADR-053 + #1134: LOW pass carries confidence + confidenceReason."""
    out = _format_entry(
        slug="ttartisan-50mm-f1-2",
        mtf_type="computed",
        panels=(
            ("f/5.6", None, (_r(pos=0),), "LOW", "prior_failed_center_ge_edge"),
        ),
    )
    assert 'confidence: "LOW",' in out
    assert 'confidenceReason: "prior_failed_center_ge_edge",' in out


# --- _suppress_gt_refuted_cells (ADR-079 Tier 1 GT gate) ------------------


def test_gt_gate_nulls_cells_beyond_tolerance() -> None:
    from mtfdigitizer.emit import _suppress_gt_refuted_cells

    readings = (_r(pos=0.0, c10s=0.90, c10m=0.90), _r(pos=1.4, c10s=0.72, c10m=0.90))
    gt = {
        "freq10S": (0.90, 0.90),  # row 1 EX 0.72 misses GT 0.90 by 0.18
        "freq10M": (0.90, 0.90),
        "freq30S": (0.70, 0.70),  # EX 0.70 within tolerance
        "freq30M": (0.70, 0.70),
    }
    log: list[tuple[str, str, float]] = []
    out = _suppress_gt_refuted_cells("max", readings, gt, log)
    assert out[0].samples["freq10S"] == 0.90, "in-band cell must survive"
    assert out[1].samples["freq10S"] is None, "out-of-band cell must be null"
    assert out[1].samples["freq10M"] == 0.90, "sibling in-band cell survives"
    assert log == [("max", "freq10S", 1.4)]


def test_gt_gate_skips_gt_none_and_ex_none_cells() -> None:
    from mtfdigitizer.emit import _suppress_gt_refuted_cells

    readings = (_r(pos=0.0, c10s=0.20, c10m=None),)
    gt = {
        "freq10S": (None,),  # unreadable GT cell: EX ships unverified
        "freq10M": (0.90,),  # EX None stays None, no log entry
        "freq30S": (0.70,),
        "freq30M": (0.70,),
    }
    log: list[tuple[str, str, float]] = []
    out = _suppress_gt_refuted_cells("max", readings, gt, log)
    assert out[0].samples["freq10S"] == 0.20, "GT-None cell passes through"
    assert out[0].samples["freq10M"] is None
    assert log == []


def test_gt_gate_exact_tolerance_boundary_ships() -> None:
    from mtfdigitizer.emit import _suppress_gt_refuted_cells

    # |EX - GT| == 0.05 is IN band (calibration scores <= 0.05 as
    # in-band); only strictly-greater misses are nulled.
    readings = (_r(pos=0.0, c10s=0.85),)
    gt = {"freq10S": (0.90,), "freq10M": (0.90,), "freq30S": (0.70,), "freq30M": (0.70,)}
    log: list[tuple[str, str, float]] = []
    out = _suppress_gt_refuted_cells("max", readings, gt, log)
    assert out[0].samples["freq10S"] == 0.85
    assert log == []


def test_gt_gate_fails_loud_on_row_mismatch() -> None:
    import pytest

    from mtfdigitizer.emit import _suppress_gt_refuted_cells

    readings = (_r(pos=0.0),)
    gt = {"freq10S": (0.9, 0.9), "freq10M": (0.9, 0.9)}
    with pytest.raises(ValueError, match="row mismatch"):
        _suppress_gt_refuted_cells("max", readings, gt, [])


def test_gt_gate_ignores_fields_absent_from_gt() -> None:
    from mtfdigitizer.emit import _suppress_gt_refuted_cells

    # A field the GT does not carry (e.g. a chart publishing more
    # frequencies than were eye-read) ships unverified rather than
    # being nulled or crashing.
    readings = (_r(pos=0.0, c10s=0.90),)
    gt = {"freq10S": (0.90,)}
    log: list[tuple[str, str, float]] = []
    out = _suppress_gt_refuted_cells("max", readings, gt, log)
    assert out[0].samples["freq30S"] == 0.7
    assert log == []


# --- suppression / aperture tables reference real charts ------------------


def test_default_apertures_entries_match_reference_set() -> None:
    """Every display-aperture entry must name a real chart and carry
    one f-number string per view, primary first (ADR-079)."""
    import re

    from mtfdigitizer.emit import _DEFAULT_APERTURES
    from mtfdigitizer.referenceset.charts import REFERENCE_CHARTS

    charts = {c.slug: c for c in REFERENCE_CHARTS}
    for slug, apertures in _DEFAULT_APERTURES.items():
        chart = charts.get(slug)
        assert chart is not None, f"unknown slug in _DEFAULT_APERTURES: {slug}"
        assert len(apertures) == len(chart.views), (
            f"{slug}: {len(apertures)} apertures for {len(chart.views)} views"
        )
        for aperture in apertures:
            assert re.match(r"^f/\d", aperture), (
                f"{slug}: {aperture!r} is not an f-number string — the site "
                f"schema requires an f/N prefix (mtf-readings.test.ts)"
            )
