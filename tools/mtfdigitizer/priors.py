"""Physical-plausibility priors (#966, ADR-038 §"Confidence signal").

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

- `check_center_ge_edge`  — center MTF should not be lower than edge MTF
- `check_10_ge_30`         — 10 lp/mm should be >= 30 lp/mm on the same side
- `check_not_suspiciously_flat` — no real lens holds ~1.0 across the field
- `check_in_range`         — values stay in [0.0, 1.0]

`check_all()` runs all four and returns a flat list of violations. An empty
list means HIGH plausibility; any violation means LOW. The auto-commit gate
(separate task) combines this verdict with the render-match score.

The flatness thresholds (`FLATNESS_MEAN_THRESHOLD`, `FLATNESS_STDEV_THRESHOLD`)
are module constants tuned in `referenceset/plausibility.md`. The discipline
from session 101 applies: the thresholds move, not the extractor.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from .pipeline.types import SampledReading


# --- Field naming ----------------------------------------------------
# Mirrors `pipeline.rendermatch.CURVE_FIELDS` and the schema in
# `src/types/mtf.ts`. Duplicated here intentionally — `priors.py` doesn't
# import from `pipeline.rendermatch` so the two confidence signals stay
# independently testable.

CONTRAST_10S = "contrast10S"
CONTRAST_10M = "contrast10M"
RESOLUTION_30S = "resolution30S"
RESOLUTION_30M = "resolution30M"

FIELDS: tuple[str, ...] = (
    CONTRAST_10S,
    CONTRAST_10M,
    RESOLUTION_30S,
    RESOLUTION_30M,
)

# Pairs of (low-frequency field, high-frequency field) on the same S/M side.
# Physical law: at a given position, contrast at 10 lp/mm >= contrast at
# 30 lp/mm. Inversion typically means the two bands were swapped.
_FREQ_PAIRS: tuple[tuple[str, str], ...] = (
    (CONTRAST_10S, RESOLUTION_30S),
    (CONTRAST_10M, RESOLUTION_30M),
)


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


# --- Helpers ---------------------------------------------------------


def _values_for_field(
    readings: tuple[SampledReading, ...], field: str
) -> tuple[float | None, ...]:
    """Pull one column of values across the 11 readings."""
    return tuple(getattr(r, field) for r in readings)


def _defined(values: tuple[float | None, ...]) -> tuple[float, ...]:
    """Drop the Nones — what's left is the curve's actual sampled values."""
    return tuple(v for v in values if v is not None)


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
    for field in FIELDS:
        c = getattr(center, field)
        e = getattr(edge, field)
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


def check_10_ge_30(
    readings: tuple[SampledReading, ...],
) -> list[PriorViolation]:
    """10 lp/mm contrast >= 30 lp/mm contrast at every position, same side.

    Higher spatial frequencies cannot have higher MTF than lower ones
    at the same field point — the optical transfer function is
    monotonically non-increasing in frequency for a physical lens.
    Inversion is the canonical "bands were swapped" signature
    (the example ADR-038 calls out: '10<30 at edge -- bands swapped?').
    """
    violations: list[PriorViolation] = []
    for low_field, high_field in _FREQ_PAIRS:
        for i, r in enumerate(readings):
            lo = getattr(r, low_field)
            hi = getattr(r, high_field)
            if lo is None or hi is None:
                continue
            if hi - lo > INEQUALITY_TOLERANCE:
                violations.append(
                    PriorViolation(
                        prior_name="ten_ge_thirty",
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
    for field in FIELDS:
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
    for field in FIELDS:
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


# --- Aggregator ------------------------------------------------------


_ALL_PRIORS = (
    check_center_ge_edge,
    check_10_ge_30,
    check_not_suspiciously_flat,
    check_in_range,
)


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
