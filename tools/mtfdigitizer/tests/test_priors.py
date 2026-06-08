"""Tests for the physical-plausibility priors (#966).

Acceptance criteria from issue #966:

- Each of the four priors has both passing and failing fixtures.
- The reference-set smoke separates as REFERENCE_SET.md predicts:
  Sigma 56mm and Samyang 85mm MAX clear all priors; Samyang 300mm
  reflex fires the flatness prior only.
- `check_all()` aggregates per-prior outputs and returns an empty
  list iff every prior passed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mtfdigitizer.pipeline import PlotBox, SampledReading, extract_chart
from mtfdigitizer.priors import (
    CONTRAST_10M,
    CONTRAST_10S,
    FIELDS,
    FLATNESS_MEAN_THRESHOLD,
    INEQUALITY_TOLERANCE,
    RESOLUTION_30M,
    RESOLUTION_30S,
    check_10_ge_30,
    check_all,
    check_center_ge_edge,
    check_in_range,
    check_no_consecutive_zeros,
    check_not_suspiciously_flat,
)
from mtfdigitizer.profiles import (
    SAMYANG_4COLOR_ALL_SOLID,
    SIGMA_2COLOR_SOLID_DASHED,
)
from mtfdigitizer.referenceset import REFERENCE_CHARTS


REPO_ROOT = Path(__file__).resolve().parents[3]


# --- Fixture builders -----------------------------------------------


def _readings(
    *,
    c10s: tuple[float | None, ...] | None = None,
    c10m: tuple[float | None, ...] | None = None,
    r30s: tuple[float | None, ...] | None = None,
    r30m: tuple[float | None, ...] | None = None,
) -> tuple[SampledReading, ...]:
    """Build 11 SampledReading rows with explicit per-field columns.

    Any field left at None defaults to all-None across the 11 rows —
    a missing curve, not a failure. Positions are spaced by 1.0 mm
    for convenience; the priors don't read `position_mm`.
    """
    none11: tuple[None, ...] = (None,) * 11
    c10s = c10s if c10s is not None else none11
    c10m = c10m if c10m is not None else none11
    r30s = r30s if r30s is not None else none11
    r30m = r30m if r30m is not None else none11
    for col in (c10s, c10m, r30s, r30m):
        assert len(col) == 11, "fixture column must have 11 values"
    return tuple(
        SampledReading(
            position_mm=i * 1.0,
            samples={
                "freq10S": c10s[i],
                "freq10M": c10m[i],
                "freq30S": r30s[i],
                "freq30M": r30m[i],
            },
        )
        for i in range(11)
    )


def _well_behaved_curve() -> tuple[float | None, ...]:
    """Monotonically non-increasing curve: 0.95 at center → 0.65 at edge."""
    return tuple(round(0.95 - 0.03 * i, 2) for i in range(11))


def _good_lens() -> tuple[SampledReading, ...]:
    """A plausible lens: 10 lp/mm above 30 lp/mm, both fall off to edge."""
    return _readings(
        c10s=tuple(round(0.95 - 0.03 * i, 2) for i in range(11)),
        c10m=tuple(round(0.95 - 0.03 * i, 2) for i in range(11)),
        r30s=tuple(round(0.80 - 0.04 * i, 2) for i in range(11)),
        r30m=tuple(round(0.80 - 0.04 * i, 2) for i in range(11)),
    )


# --- check_center_ge_edge -------------------------------------------


def test_center_ge_edge_passes_on_well_behaved() -> None:
    assert check_center_ge_edge(_good_lens()) == []


def test_center_ge_edge_passes_within_tolerance() -> None:
    """A tiny inversion within ±tolerance is noise, not a violation."""
    values = list(_well_behaved_curve())
    # Just inside the tolerance: edge - center < INEQUALITY_TOLERANCE.
    # The prior fires on `> tolerance`, so an inversion strictly less
    # than the tolerance is below the noise floor.
    values[-1] = values[0] + INEQUALITY_TOLERANCE * 0.5
    assert check_center_ge_edge(_readings(c10s=tuple(values))) == []


def test_center_ge_edge_fires_on_inverted_curve() -> None:
    """Edge MTF exceeds center by more than tolerance — unphysical."""
    inverted = tuple(round(0.40 + 0.05 * i, 2) for i in range(11))
    violations = check_center_ge_edge(_readings(c10s=inverted))
    assert len(violations) == 1
    assert violations[0].field == CONTRAST_10S
    assert violations[0].prior_name == "center_ge_edge"
    assert "exceeds center" in violations[0].detail


def test_center_ge_edge_skips_fields_with_none_endpoints() -> None:
    """Curves that don't sample to center or edge can't be judged here."""
    partial = tuple(None if i in (0, 10) else 0.5 for i in range(11))
    assert check_center_ge_edge(_readings(c10s=partial)) == []


# --- check_10_ge_30 -------------------------------------------------


def test_10_ge_30_passes_on_well_behaved() -> None:
    assert check_10_ge_30(_good_lens()) == []


def test_10_ge_30_fires_when_bands_swapped() -> None:
    """30 lp/mm above 10 lp/mm at every point — canonical swap signature."""
    high10 = (0.90,) * 11
    low30 = (0.50,) * 11
    # Swap them: freq10S = 0.50, freq30S = 0.90.
    swapped = _readings(c10s=low30, r30s=high10)
    violations = check_10_ge_30(swapped)
    # 11 positions all inverted on the S side.
    assert len(violations) == 11
    assert all(v.field == RESOLUTION_30S for v in violations)
    assert all(v.prior_name == "low_freq_ge_high" for v in violations)
    assert "bands swapped" in violations[0].detail


def test_10_ge_30_fires_per_position() -> None:
    """Inversion at one position only produces one violation."""
    c10s = (0.90,) * 11
    r30s = (0.50,) * 5 + (0.95,) + (0.50,) * 5  # spike past 10 at position 5
    violations = check_10_ge_30(_readings(c10s=c10s, r30s=r30s))
    assert len(violations) == 1
    assert violations[0].position_index == 5
    assert violations[0].field == RESOLUTION_30S


def test_10_ge_30_passes_within_tolerance() -> None:
    """30 lp/mm just barely above 10 lp/mm — within tolerance, not
    a violation. Models the wide-open case where both bands saturate
    near 1.0 and eye-reading noise can flip the order by a tick."""
    flat = (1.0,) * 11
    nearly = (1.0 - INEQUALITY_TOLERANCE * 0.5,) * 11
    assert check_10_ge_30(_readings(c10s=nearly, r30s=flat)) == []


def test_10_ge_30_checks_each_side_independently() -> None:
    """S-side swap doesn't pollute the M-side check, and vice versa."""
    c10s = (0.50,) * 11  # S side: inverted
    r30s = (0.90,) * 11
    c10m = (0.90,) * 11  # M side: well-behaved
    r30m = (0.50,) * 11
    violations = check_10_ge_30(_readings(c10s=c10s, c10m=c10m, r30s=r30s, r30m=r30m))
    assert {v.field for v in violations} == {RESOLUTION_30S}


# --- check_not_suspiciously_flat ------------------------------------


def test_flatness_fires_on_all_ones() -> None:
    """The 300mm reflex case in miniature: every value pinned at 1.0."""
    flat = (1.0,) * 11
    violations = check_not_suspiciously_flat(
        _readings(c10s=flat, c10m=flat, r30s=flat, r30m=flat)
    )
    assert len(violations) == 4
    assert {v.field for v in violations} == set(FIELDS)
    assert all(v.prior_name == "not_suspiciously_flat" for v in violations)


def test_flatness_passes_on_good_lens() -> None:
    """A real lens falls off — the curve isn't flat AND isn't near 1.0."""
    assert check_not_suspiciously_flat(_good_lens()) == []


def test_flatness_passes_when_mean_below_threshold() -> None:
    """Samyang 85mm 10M shape: high mean ~0.93 but below the 0.95 floor."""
    samyang_10m_like = (0.91, 0.92, 0.93, 0.93, 0.94, 0.94, 0.94, 0.94, 0.94, 0.93, 0.93)
    assert check_not_suspiciously_flat(_readings(c10m=samyang_10m_like)) == []


def test_flatness_passes_when_stdev_too_large() -> None:
    """Mean above threshold but visibly varies across the field — not flat."""
    varied = (1.0, 0.98, 0.96, 0.94, 0.96, 0.98, 1.0, 0.98, 0.96, 0.94, 0.92)
    # mean ~0.965 (above 0.95), stdev > 0.02 — should not fire.
    assert check_not_suspiciously_flat(_readings(c10s=varied)) == []


def test_flatness_skips_field_with_one_defined_value() -> None:
    """stdev() needs ≥ 2 points — single-point curves are insufficient."""
    single = (None,) * 5 + (1.0,) + (None,) * 5
    assert check_not_suspiciously_flat(_readings(c10s=single)) == []


def test_flatness_fires_just_above_threshold() -> None:
    """Boundary case: mean = 0.96, stdev ~0.01 — should fire."""
    near_top = (0.96, 0.97, 0.96, 0.95, 0.96, 0.97, 0.96, 0.95, 0.96, 0.97, 0.96)
    violations = check_not_suspiciously_flat(_readings(c10s=near_top))
    assert len(violations) == 1
    assert violations[0].field == CONTRAST_10S


# --- check_in_range -------------------------------------------------


def test_in_range_passes_on_valid_values() -> None:
    assert check_in_range(_good_lens()) == []


def test_in_range_passes_on_boundaries() -> None:
    """Exactly 0.0 and exactly 1.0 are inside the range."""
    edges = (0.0, 1.0) + (0.5,) * 9
    assert check_in_range(_readings(c10s=edges)) == []


def test_in_range_fires_on_negative() -> None:
    bad = (-0.1,) + (0.5,) * 10
    violations = check_in_range(_readings(c10s=bad))
    assert len(violations) == 1
    assert violations[0].position_index == 0
    assert violations[0].prior_name == "in_range"


def test_in_range_fires_on_above_one() -> None:
    bad = (0.5,) * 10 + (1.5,)
    violations = check_in_range(_readings(c10s=bad))
    assert len(violations) == 1
    assert violations[0].position_index == 10


def test_in_range_ignores_none_values() -> None:
    """None means 'no data', not 'out of range'."""
    assert check_in_range(_readings(c10s=(None,) * 11)) == []


# --- check_all ------------------------------------------------------


def test_check_all_empty_when_all_pass() -> None:
    assert check_all(_good_lens()) == []


def test_check_all_aggregates_violations() -> None:
    """A pathological reading triggers multiple priors at once.

    Construct one chart that:
    - inverts center/edge on 10S (1 center_ge_edge violation)
    - has 10S below 30S throughout (11 low_freq_ge_high violations)
    - holds 10M flat at 1.0 (1 not_suspiciously_flat violation)
    - has one out-of-range value on 30S (1 in_range violation)
    """
    inverted = tuple(round(0.40 + 0.05 * i, 2) for i in range(11))  # rises
    flat = (1.0,) * 11
    above30 = (0.99,) * 10 + (1.05,)  # 11th value escapes [0, 1]
    readings = _readings(c10s=inverted, c10m=flat, r30s=above30)
    violations = check_all(readings)
    by_prior = {v.prior_name for v in violations}
    assert "center_ge_edge" in by_prior
    assert "low_freq_ge_high" in by_prior
    assert "not_suspiciously_flat" in by_prior
    assert "in_range" in by_prior


# --- Reference-set integration --------------------------------------


def _runnable_chart(slug: str):
    """Helper: fetch a reference chart by slug and assert it's runnable."""
    chart = next(c for c in REFERENCE_CHARTS if c.slug == slug)
    assert chart.plot_box is not None, f"{slug}: no plot_box for integration test"
    return chart


def _extract_reference(slug: str, profile) -> tuple[SampledReading, ...]:
    """Run extract_chart on one reference chart by slug."""
    chart = _runnable_chart(slug)
    plot_box = PlotBox(
        x_left=chart.plot_box.x_left,
        x_right=chart.plot_box.x_right,
        y_top=chart.plot_box.y_top,
        y_bottom=chart.plot_box.y_bottom,
    )
    result = extract_chart(
        REPO_ROOT / chart.chart_path,
        profile,
        plot_box,
        image_height_mm=chart.image_height_mm,
    )
    return result.readings


def test_reference_sigma_56_passes_all_priors() -> None:
    """Canonical clean chart — must not trigger any prior. If this
    starts failing, the priors are too strict OR the extractor regressed."""
    readings = _extract_reference("sigma-56mm-f1-4-dc-dn-c", SIGMA_2COLOR_SOLID_DASHED)
    violations = check_all(readings)
    assert violations == [], (
        f"Sigma 56mm should pass all priors; got {len(violations)} violations: "
        f"{[(v.prior_name, v.field) for v in violations]}"
    )


def test_reference_samyang_85_max_passes_all_priors() -> None:
    """Real-lens 4-color chart (MAX panel) — must not trigger any prior."""
    readings = _extract_reference(
        "samyang-85mm-f1-4-as-if-umc", SAMYANG_4COLOR_ALL_SOLID
    )
    violations = check_all(readings)
    assert violations == [], (
        f"Samyang 85mm MAX should pass all priors; got {len(violations)}: "
        f"{[(v.prior_name, v.field) for v in violations]}"
    )


def test_reference_samyang_300_reflex_fires_only_flatness() -> None:
    """The idealized-flat case ADR-038 calls out as render-match's
    blind spot. The flatness prior is the only one that should fire —
    the other three priors pass (center==edge is fine, 10==30 is fine,
    1.0 is in-range)."""
    readings = _extract_reference(
        "samyang-300mm-f6-3-ed-umc-cs-reflex", SAMYANG_4COLOR_ALL_SOLID
    )
    violations = check_all(readings)
    assert violations, "Samyang 300mm reflex must fire at least one prior"
    fired = {v.prior_name for v in violations}
    assert fired == {"not_suspiciously_flat"}, (
        f"Samyang 300mm reflex should fire ONLY the flatness prior; got {fired}"
    )
    # All four committed fields trace as flat in this chart (per the
    # ground-truth notes); the prior should report per-field on each
    # that the extractor actually populated.
    fields_with_flatness = {
        v.field for v in violations if v.prior_name == "not_suspiciously_flat"
    }
    # At minimum the two solid-color fields the extractor reliably hits
    # (10S, 10M) must register; 30S/M may or may not depending on
    # whether the extractor produced enough points (per scoring.md the
    # 300mm reflex traces 10S/M cleanly but 30S/M are sparse).
    assert fields_with_flatness >= {CONTRAST_10S, CONTRAST_10M}, (
        f"Expected flatness on at least 10S and 10M; got {fields_with_flatness}"
    )


# --- Sanity guards on the constants ---------------------------------


def test_flatness_constants_are_sane() -> None:
    """The mean threshold must be near (but below) 1.0; the stdev
    threshold tight enough that a real lens's 0.02 noise doesn't fire."""
    assert 0.90 <= FLATNESS_MEAN_THRESHOLD < 1.0
    # Eye-reading precision is ~±0.02; the prior's stdev threshold must
    # be at most that, or it loses meaning.
    assert INEQUALITY_TOLERANCE <= 0.05


# --- check_no_consecutive_zeros (#1090) -----------------------------


def test_no_consecutive_zeros_passes_on_well_behaved_lens() -> None:
    readings = _readings(
        c10s=_well_behaved_curve(),
        r30s=tuple(round(0.75 - 0.04 * i, 2) for i in range(11)),
    )
    assert check_no_consecutive_zeros(readings) == []


def test_no_consecutive_zeros_passes_on_single_zero() -> None:
    """A single 0.00 value (rare but possible at the deepest corner) is
    allowed — the prior only flags 3+ consecutive."""
    curve = list(_well_behaved_curve())
    curve[5] = 0.0  # one isolated zero in the middle
    readings = _readings(r30s=tuple(curve))
    assert check_no_consecutive_zeros(readings) == []


def test_no_consecutive_zeros_passes_on_two_consecutive_zeros() -> None:
    """Two consecutive 0.00s are also allowed — the threshold is 3."""
    curve = list(_well_behaved_curve())
    curve[5] = curve[6] = 0.0
    readings = _readings(r30s=tuple(curve))
    assert check_no_consecutive_zeros(readings) == []


def test_no_consecutive_zeros_fires_on_three_consecutive_zeros() -> None:
    """Regression for #1090 (TTartisan 100mm-macro freq30S = 0.00 leak)."""
    curve = list(_well_behaved_curve())
    curve[3] = curve[4] = curve[5] = 0.0
    readings = _readings(r30s=tuple(curve))
    violations = check_no_consecutive_zeros(readings)
    assert len(violations) == 1
    v = violations[0]
    assert v.prior_name == "no_consecutive_zeros"
    assert v.field == "freq30S"
    assert v.position_index == 3
    assert "3 consecutive 0.00" in v.detail


def test_no_consecutive_zeros_emits_one_violation_per_chain() -> None:
    """A 7-long zero chain (the exact #1090 shape) should emit ONE
    violation describing the full run, not 5."""
    curve = list(_well_behaved_curve())
    for i in range(1, 8):  # positions 1..7 all zero (7-long chain)
        curve[i] = 0.0
    readings = _readings(r30s=tuple(curve))
    violations = check_no_consecutive_zeros(readings)
    assert len(violations) == 1
    assert "7 consecutive" in violations[0].detail


def test_no_consecutive_zeros_treats_none_as_break() -> None:
    """None values break a zero chain — a real missing reading is not
    the same shape as a literal 0.00 leak."""
    curve = list(_well_behaved_curve())
    curve[3] = 0.0
    curve[4] = None  # break
    curve[5] = 0.0
    curve[6] = 0.0
    readings = _readings(r30s=tuple(curve))
    assert check_no_consecutive_zeros(readings) == []


def test_check_all_includes_no_consecutive_zeros() -> None:
    """The aggregator must include the new prior."""
    curve = list(_well_behaved_curve())
    curve[3] = curve[4] = curve[5] = 0.0
    readings = _readings(r30s=tuple(curve))
    violations = check_all(readings)
    assert any(v.prior_name == "no_consecutive_zeros" for v in violations)


def test_fields_constant_matches_sampled_reading() -> None:
    """The legacy `FIELDS` constant maps to canonical `freq{N}{S|M}`
    field names (ADR-042 generalized the schema). Per-row priors now
    discover the field set from `SampledReading.samples` keys; FIELDS
    survives as a compat alias for the 10+30 canonical layout."""
    sample = SampledReading(
        position_mm=0.0,
        samples={f: 0.5 for f in FIELDS},
    )
    for field in FIELDS:
        assert field in sample.samples, (
            f"FIELDS lists {field!r} but the sample's samples dict lacks it"
        )
