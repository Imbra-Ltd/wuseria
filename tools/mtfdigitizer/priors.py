"""Physical-plausibility priors (#966, ADR-038 §"Confidence signal",
generalized for ADR-042's arbitrary-frequency schema).

Render-match (`rendermatch.py`, #963) is one of the two confidence signals
ADR-038 requires. It catches calibration and merge errors but has two
documented blind spots:

1. **legend/label semantics** — bands swapped while curves trace correctly,
   pixel-identical to the original
2. **flat-axis translation** — horizontal shift on curves that carry no
   horizontal structure (the Samyang 300mm reflex case)

This module is the other signal. Four pure-function priors run over the
`SampledReading` tuple `extract_chart()` returns and report violations of
hard optical facts no real lens can break:

- `check_center_ge_edge`     — center MTF should not be lower than edge MTF
- `check_low_freq_ge_high`   — at the same field point, lower spatial
                                frequencies should have MTF >= higher
                                frequencies on the same S/M axis
- `check_not_suspiciously_flat` — no real lens holds ~1.0 across the field
- `check_in_range`           — values stay in [0.0, 1.0]

`check_all()` runs all four and returns a flat list of violations. An empty
list means HIGH plausibility; any violation means LOW. The auto-commit gate
(`triage.py`) combines this verdict with the render-match score.

The flatness thresholds (`FLATNESS_MEAN_THRESHOLD`, `FLATNESS_STDEV_THRESHOLD`)
are module constants tuned in `referenceset/plausibility.md`. The discipline
from session 101 applies: the thresholds move, not the extractor.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass

from .pipeline.types import SampledReading


# --- Field naming ----------------------------------------------------
# Field names follow the `freq{N}{S|M}` synthetic convention emitted by
# `pipeline.dispatch.curve_field()` (ADR-042). The priors discover the
# field set per-reading rather than hardcoding it — Sigma/Samyang/etc.
# carry {freq10S, freq10M, freq30S, freq30M}, Fuji GF primes carry
# {freq15S, freq15M, freq20S, freq20M, freq40S, freq40M}, etc.

_FIELD_NAME = re.compile(r"^freq(?P<freq>\d+)(?P<sm>[SM])$")


# Backwards-compat constants for callers and tests that referenced the
# legacy `contrast10S/M`, `resolution30S/M` field names — they now point
# to the synthetic `freq10S/M`, `freq30S/M` names emitted by the
# pipeline after ADR-042. New callers should NOT reference these; the
# priors discover the field set per-reading.
CONTRAST_10S = "freq10S"
CONTRAST_10M = "freq10M"
RESOLUTION_30S = "freq30S"
RESOLUTION_30M = "freq30M"

FIELDS: tuple[str, ...] = (
    CONTRAST_10S,
    CONTRAST_10M,
    RESOLUTION_30S,
    RESOLUTION_30M,
)


def _parse_field(field: str) -> tuple[int, str] | None:
    """Parse `freq{N}{S|M}` into (frequency_lpmm, 'S' | 'M').

    Returns `None` for names that don't follow the convention — callers
    skip those fields rather than raising. The legacy
    `contrast10S`/`resolution30S` names predate ADR-042 and never appear
    in pipeline output any more, so a non-match indicates a bug in a
    caller, not data the priors should validate.
    """
    m = _FIELD_NAME.match(field)
    if m is None:
        return None
    return int(m.group("freq")), m.group("sm")


def _fields_present(readings: tuple[SampledReading, ...]) -> tuple[str, ...]:
    """Union of field names across all readings, in insertion order.

    Reading rows are allowed to omit fields the chart did not publish at
    that position, so the per-reading field sets can differ — though
    ADR-042's within-chart invariant says they should not.
    """
    seen: list[str] = []
    for r in readings:
        for field in r.samples:
            if field not in seen:
                seen.append(field)
    return tuple(seen)


def _values_for_field(
    readings: tuple[SampledReading, ...], field: str
) -> tuple[float | None, ...]:
    """Pull one column of values across the 11 readings."""
    return tuple(r.samples.get(field) for r in readings)


def _defined(values: tuple[float | None, ...]) -> tuple[float, ...]:
    """Drop the Nones — what's left is the curve's actual sampled values."""
    return tuple(v for v in values if v is not None)


def _frequency_pairs_by_side(
    readings: tuple[SampledReading, ...],
) -> tuple[tuple[str, str], ...]:
    """All (lower_freq_field, higher_freq_field) pairs on the same S|M side.

    For a chart with frequencies {10, 30} this returns
    `(("freq10S", "freq30S"), ("freq10M", "freq30M"))`. For a chart with
    frequencies {15, 20, 40} this returns
    `(("freq15S", "freq20S"), ("freq15S", "freq40S"), ("freq20S", "freq40S"),
      ("freq15M", "freq20M"), ("freq15M", "freq40M"), ("freq20M", "freq40M"))`.

    The pairwise enumeration scales as `O(N^2)` in frequency count,
    which is fine for the published chart range (Fuji's max is 3
    frequencies per chart → 3 pairs × 2 sides = 6 comparisons).
    """
    by_side: dict[str, list[tuple[int, str]]] = {"S": [], "M": []}
    for field in _fields_present(readings):
        parsed = _parse_field(field)
        if parsed is None:
            continue
        freq, sm = parsed
        by_side[sm].append((freq, field))
    out: list[tuple[str, str]] = []
    for sm in ("S", "M"):
        freqs = sorted(by_side[sm], key=lambda fp: fp[0])
        for i in range(len(freqs)):
            for j in range(i + 1, len(freqs)):
                out.append((freqs[i][1], freqs[j][1]))
    return tuple(out)


# --- Tuning knobs ----------------------------------------------------
# Documented in `referenceset/plausibility.md`. Picked so the Samyang
# 300mm reflex (all 1.0, stdev ~0.001) fires the flatness prior cleanly
# while genuinely near-flat real curves do not: the Samyang 85mm 10M
# (mean ~0.93) is saved by the mean gate, and the Sigma 56mm 10M
# (mean ~0.967, stdev ~0.016 — a sharp lens barely tapering at 10 lp/mm)
# is saved by the stdev gate. The stdev bound tightened 0.02 → 0.01 when
# the (SPLIT_BY_DASH, GEODESIC_DP) dispatch gave Sigma a complete 10M
# curve: a dead-flat placeholder sits at stdev ~0.001, a real near-flat
# curve at ~0.016, so 0.01 separates them with margin. Tightening can
# only remove firings, never add them — no previously-clean chart regresses.

FLATNESS_MEAN_THRESHOLD: float = 0.95
FLATNESS_STDEV_THRESHOLD: float = 0.01

# Per-position tolerance for the inequality priors. Eye-reading is
# ~+/-0.02 (one half-gridline tick — same precision the reference set
# carries), so any inequality the priors flag must exceed that noise
# floor to count. Equal-to-tolerance values are allowed (e.g. 10S and
# 30S can legitimately co-incide at MTF=1.0 wide-open).
INEQUALITY_TOLERANCE: float = 0.02

# In-range bounds. The extractor's `sampling.py` derives values from
# pixel positions inside the plot box and is geometrically clamped, so
# in practice this prior is a defensive check — but cheap to run and
# meaningful if a caller hand-constructs `SampledReading` rows.
MTF_MIN: float = 0.0
MTF_MAX: float = 1.0


# --- Types -----------------------------------------------------------


@dataclass(frozen=True)
class PriorViolation:
    """One physical-plausibility violation.

    `position_index` is the index into the 11 SAMPLE_FRACTIONS where
    the violation occurred, or `None` for whole-curve violations
    (flatness).
    """

    prior_name: str
    field: str
    position_index: int | None
    detail: str


# --- Priors ----------------------------------------------------------


def check_center_ge_edge(
    readings: tuple[SampledReading, ...],
) -> list[PriorViolation]:
    """Center MTF >= edge MTF per field.

    A lens's optical performance falls off from the center outward;
    edge MTF that exceeds center MTF is unphysical and almost always
    means the curve was traced upside-down or the plot box was
    inverted. Compares position 0 to position 10 (the two extremes).
    """
    violations: list[PriorViolation] = []
    if not readings:
        return violations
    center, edge = readings[0], readings[-1]
    for field in _fields_present(readings):
        c = center.samples.get(field)
        e = edge.samples.get(field)
        if c is None or e is None:
            continue
        if e - c > INEQUALITY_TOLERANCE:
            violations.append(
                PriorViolation(
                    prior_name="center_ge_edge",
                    field=field,
                    position_index=None,
                    detail=(
                        f"edge MTF {e:.3f} exceeds center MTF {c:.3f} "
                        f"by {e - c:.3f} (tolerance {INEQUALITY_TOLERANCE})"
                    ),
                )
            )
    return violations


def check_low_freq_ge_high(
    readings: tuple[SampledReading, ...],
) -> list[PriorViolation]:
    """Lower-frequency MTF >= higher-frequency MTF at every position, same side.

    Higher spatial frequencies cannot have higher MTF than lower ones
    at the same field point — the optical transfer function is
    monotonically non-increasing in frequency for a physical lens.
    Inversion is the canonical "bands were swapped" signature
    (the example ADR-038 calls out: '10<30 at edge -- bands swapped?').

    Generalizes the legacy 10≥30 check (`check_10_ge_30`) to any pair
    of declared frequencies on the same S|M axis: for Fuji prime
    {15, 20, 40} the rule fires when 20S > 15S, 40S > 15S, 40S > 20S,
    or any of the analogous M comparisons.
    """
    violations: list[PriorViolation] = []
    for low_field, high_field in _frequency_pairs_by_side(readings):
        for i, r in enumerate(readings):
            lo = r.samples.get(low_field)
            hi = r.samples.get(high_field)
            if lo is None or hi is None:
                continue
            if hi - lo > INEQUALITY_TOLERANCE:
                violations.append(
                    PriorViolation(
                        prior_name="low_freq_ge_high",
                        field=high_field,
                        position_index=i,
                        detail=(
                            f"{high_field}={hi:.3f} exceeds {low_field}={lo:.3f} "
                            f"by {hi - lo:.3f} at position {i} "
                            f"(tolerance {INEQUALITY_TOLERANCE}) — bands swapped?"
                        ),
                    )
                )
    return violations


def check_not_suspiciously_flat(
    readings: tuple[SampledReading, ...],
) -> list[PriorViolation]:
    """No field holds near-perfect MTF across the whole image height.

    A real lens cannot maintain MTF ~1.0 from center to edge — that's
    the signature of an idealized/placeholder chart (the Samyang 300mm
    reflex case) or, more dangerously, of an extractor that mis-traced
    a chart and inadvertently produced a flat line at 1.0. Per-field:
    mean >= FLATNESS_MEAN_THRESHOLD AND stdev <= FLATNESS_STDEV_THRESHOLD
    triggers the prior.

    Requires at least 2 defined values per field to compute stdev;
    fields with fewer defined values are skipped (treated as
    'insufficient evidence', not a violation).
    """
    violations: list[PriorViolation] = []
    for field in _fields_present(readings):
        defined = _defined(_values_for_field(readings, field))
        if len(defined) < 2:
            continue
        mean = statistics.mean(defined)
        stdev = statistics.stdev(defined)
        if mean >= FLATNESS_MEAN_THRESHOLD and stdev <= FLATNESS_STDEV_THRESHOLD:
            violations.append(
                PriorViolation(
                    prior_name="not_suspiciously_flat",
                    field=field,
                    position_index=None,
                    detail=(
                        f"mean {mean:.3f} >= {FLATNESS_MEAN_THRESHOLD} "
                        f"and stdev {stdev:.3f} <= {FLATNESS_STDEV_THRESHOLD} "
                        f"({len(defined)}/11 defined) — idealized/placeholder?"
                    ),
                )
            )
    return violations


def check_in_range(
    readings: tuple[SampledReading, ...],
) -> list[PriorViolation]:
    """Every defined MTF value lies in [0.0, 1.0].

    The extractor clamps geometrically (pixel positions inside the plot
    box can't escape the y-axis), but a hand-constructed reading or a
    future post-processing step could escape the range. Cheap defensive
    check that doubles as documentation of the schema contract.
    """
    violations: list[PriorViolation] = []
    for field in _fields_present(readings):
        for i, v in enumerate(_values_for_field(readings, field)):
            if v is None:
                continue
            if v < MTF_MIN or v > MTF_MAX:
                violations.append(
                    PriorViolation(
                        prior_name="in_range",
                        field=field,
                        position_index=i,
                        detail=(
                            f"value {v:.3f} at position {i} outside "
                            f"[{MTF_MIN}, {MTF_MAX}]"
                        ),
                    )
                )
    return violations


def check_no_consecutive_zeros(
    readings: tuple[SampledReading, ...],
) -> list[PriorViolation]:
    """Flag 3+ consecutive 0.00 readings on a single field.

    Regression guard for #1090. The TTartisan 100mm-macro extraction
    leaked freq30S = 0.00 across 7 consecutive positions because the
    plot-box bottom border (MTF=0) was being mis-tracked as the
    grey S30 curve. A real lens curve cannot legitimately bottom out
    at exactly 0.00 for 3+ consecutive positions — even the worst
    corner of the worst lens has small but non-zero contrast.

    A real "missing reading" returns `None`, not `0.00`. A literal
    0.00 chain almost always indicates: (a) the extractor latched
    onto the plot-frame X-axis, (b) the dispatch mis-assigned a
    chrome track to a curve slot, or (c) the y_pixel_to_mtf clamp
    fired repeatedly. All three are extractor bugs, not data.
    """
    violations: list[PriorViolation] = []
    for field in _fields_present(readings):
        values = _values_for_field(readings, field)
        i = 0
        n = len(values)
        while i < n:
            if values[i] != 0.0:
                i += 1
                continue
            # Found start of a 0.00 run; consume the whole chain.
            run_start = i
            while i < n and values[i] == 0.0:
                i += 1
            run_length = i - run_start
            if run_length >= 3:
                violations.append(
                    PriorViolation(
                        prior_name="no_consecutive_zeros",
                        field=field,
                        position_index=run_start,
                        detail=(
                            f"{run_length} consecutive 0.00 readings on "
                            f"{field} starting at position {run_start}; "
                            f"suggests extractor latched onto chart "
                            f"chrome rather than the curve"
                        ),
                    )
                )
    return violations


# --- Aggregator ------------------------------------------------------


_ALL_PRIORS = (
    check_center_ge_edge,
    check_low_freq_ge_high,
    check_not_suspiciously_flat,
    check_in_range,
    check_no_consecutive_zeros,
)

# Backwards-compat alias for the legacy function name. The new name
# (`check_low_freq_ge_high`) generalizes the rule beyond 10 vs 30.
check_10_ge_30 = check_low_freq_ge_high


def check_all(
    readings: tuple[SampledReading, ...],
) -> list[PriorViolation]:
    """Run all four priors and return the flat list of violations.

    An empty list means HIGH plausibility. Any violation means LOW.
    The verdict is binary by design — these are physical facts, not
    statistical signals; either the data violates them or it doesn't.
    """
    out: list[PriorViolation] = []
    for prior in _ALL_PRIORS:
        out.extend(prior(readings))
    return out
