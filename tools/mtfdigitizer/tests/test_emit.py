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


# --- _apply_suppression (ADR-079) ----------------------------------------


def test_apply_suppression_nulls_declared_fields_only() -> None:
    from mtfdigitizer.emit import _apply_suppression

    readings = (_r(pos=0.0), _r(pos=1.4))
    log: list[tuple[str, str]] = []
    # zeiss-touit-32mm stopped panel suppresses freq40S/freq40M; the
    # synthetic reading carries freq10/freq30 keys, so only a matching
    # key would be nulled. Use the 50mm max entry (freq10M) against a
    # reading that has freq10M populated.
    out = _apply_suppression(
        "zeiss-touit-50mm-f2-8-macro", "max", readings, log
    )
    for row in out:
        assert row.samples["freq10M"] is None, "suppressed field must be null"
        assert row.samples["freq10S"] == 0.9, "sibling field must survive"
        assert row.samples["freq30S"] == 0.7, "unrelated field must survive"
    assert ("max", "freq10M") in log
    assert ("max", "freq20M") in log


def test_apply_suppression_noop_without_entry() -> None:
    from mtfdigitizer.emit import _apply_suppression

    readings = (_r(pos=0.0),)
    log: list[tuple[str, str]] = []
    out = _apply_suppression("sigma-56mm-f1-4-dc-dn-c", "max", readings, log)
    assert out is readings, "no entry -> readings returned unchanged"
    assert log == []


def test_apply_suppression_keyed_by_panel_role() -> None:
    from mtfdigitizer.emit import _apply_suppression

    readings = (_r(pos=0.0),)
    log: list[tuple[str, str]] = []
    # The 32mm entry suppresses only the STOPPED panel — the max panel
    # of the same slug must pass through untouched.
    out = _apply_suppression("zeiss-touit-32mm-f1-8", "max", readings, log)
    assert out is readings
    assert log == []


# --- suppression / aperture tables reference real charts ------------------


def test_suppressed_fields_entries_match_reference_set() -> None:
    """Every skip-list entry must name a real chart, a declared panel
    role, and fields the chart's frequency tuple actually publishes —
    a renamed slug or role would otherwise turn the suppression into a
    silent no-op and ship the GT-refuted curve (ADR-079)."""
    from mtfdigitizer.emit import _SUPPRESSED_FIELDS
    from mtfdigitizer.pipeline.dispatch import parse_field_name
    from mtfdigitizer.referenceset.charts import REFERENCE_CHARTS

    charts = {c.slug: c for c in REFERENCE_CHARTS}
    for (slug, role), fields in _SUPPRESSED_FIELDS.items():
        chart = charts.get(slug)
        assert chart is not None, f"unknown slug in _SUPPRESSED_FIELDS: {slug}"
        assert role in chart.apertures, (
            f"{slug}: role {role!r} not in declared apertures "
            f"{chart.apertures}"
        )
        for field in fields:
            freq, _sm = parse_field_name(field)
            assert freq in chart.frequencies_lpmm, (
                f"{slug}: suppressed field {field} names frequency {freq} "
                f"the chart does not publish {chart.frequencies_lpmm}"
            )


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
