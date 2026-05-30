"""Auto-triage gate: combine the two confidence signals into one verdict
(#968, ADR-038 §"Confidence signal").

Render-match (`pipeline.rendermatch`, #963) catches calibration and merge
errors. Plausibility priors (`priors.py`, #966) catch render-match's two
documented blind spots (legend swaps, flat-axis translation). Both ship
as independently-testable modules — this one is the predicate that turns
their outputs into the binary HIGH/LOW decision the auto-commit + 3-panel
review workflow needs.

Rule:

    HIGH iff:
      render_match.precision        >= PRECISION_THRESHOLD (0.80)
      AND render_match.aggregate    >= IOU_THRESHOLD       (0.20)
      AND plausibility.check_all()  == []
    LOW otherwise

A LOW verdict carries a tuple of `LowReason` codes so the run log says
*why*, not just *that*, a chart was flagged. The maintainer routes their
attention by reason: `PRIOR_FAILED_*` means investigate the chart;
`PRECISION_BELOW_THRESHOLD` on a known-sparse-dashed chart means an
upstream extractor fix is the right move, not a chart review.

Thresholds are deliberately strict — Sigma 56mm scores precision 0.44
today (sparse dashed-M bridging, calibration.md finding 6) and therefore
classifies LOW even though calibration and priors both say it's fine.
That's correct behaviour for a conservative gate: the LOW signal points
the maintainer at the *real* upstream problem (dashed bridging), not at
a false-confidence auto-commit.

The discipline from session 101 holds: thresholds move (here, in this
module's constants + the findings doc), not the extractor.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal

from .pipeline.rendermatch import FieldIou, RenderMatchScore
from .priors import PriorViolation


# --- Tuning knobs ----------------------------------------------------
# Promoted from `scoring.md` finding 2's tentative recommendation after
# one documented reference-set run. Pinned in `referenceset/triage.md`.

PRECISION_THRESHOLD: float = 0.80
IOU_THRESHOLD: float = 0.20


# --- Reason codes ----------------------------------------------------


class LowReason(str, Enum):
    """Why a chart was flagged LOW.

    One enum value per failure mode the triage rule can detect. The
    run log groups by reason — `PRIOR_FAILED_*` codes route to chart
    review, `*_BELOW_THRESHOLD` codes route to extractor work.

    String-valued so the runner can print them cleanly and the findings
    doc can copy-paste them.
    """

    PRECISION_BELOW_THRESHOLD = "precision_below_threshold"
    IOU_BELOW_THRESHOLD = "iou_below_threshold"
    RENDER_MATCH_UNDEFINED = "render_match_undefined"
    PRIOR_FAILED_CENTER_GE_EDGE = "prior_failed_center_ge_edge"
    PRIOR_FAILED_TEN_GE_THIRTY = "prior_failed_ten_ge_thirty"
    PRIOR_FAILED_NOT_SUSPICIOUSLY_FLAT = "prior_failed_not_suspiciously_flat"
    PRIOR_FAILED_IN_RANGE = "prior_failed_in_range"


# Map `PriorViolation.prior_name` → `LowReason`. One row per prior the
# `check_all()` aggregator can emit. Keyed by the string the prior
# itself stamps onto the violation — keeps the two modules in sync via
# a single point of translation.
_PRIOR_NAME_TO_REASON: dict[str, LowReason] = {
    "center_ge_edge": LowReason.PRIOR_FAILED_CENTER_GE_EDGE,
    "ten_ge_thirty": LowReason.PRIOR_FAILED_TEN_GE_THIRTY,
    "not_suspiciously_flat": LowReason.PRIOR_FAILED_NOT_SUSPICIOUSLY_FLAT,
    "in_range": LowReason.PRIOR_FAILED_IN_RANGE,
}


# --- Verdict ---------------------------------------------------------


@dataclass(frozen=True)
class ChartVerdict:
    """The auto-triage decision for one chart.

    `verdict` is binary by design. `reasons` is empty iff `verdict ==
    "HIGH"` (a HIGH chart has nothing to flag); a LOW chart has at
    least one reason. The numeric inputs (precision, IoU, violations)
    are carried so the run log + findings doc can be generated from
    `ChartVerdict` alone without re-running the signals.
    """

    source_path: str
    profile_name: str
    verdict: Literal["HIGH", "LOW"]
    reasons: tuple[LowReason, ...]
    render_match_iou: float | None
    render_match_precision: float | None
    prior_violations: tuple[PriorViolation, ...]


# --- precision -------------------------------------------------------


def precision_of(field_score: FieldIou) -> float | None:
    """`intersection / rasterized` for one field — what fraction of the
    redrawn polyline lands inside the dilated skeleton.

    Robust to the sparse-polyline vs dense-skeleton geometric asymmetry
    that depresses pure IoU on this data (scoring.md finding 1). Returns
    `None` when no polyline pixels were drawn — no surface to score.

    Centralized here so `scorer.py` and `triage.py` use the same
    definition. (The metric originally lived inlined in `scorer.py` as
    `_polyline_precision`; moved here as part of #968.)
    """
    if field_score.rasterized_px == 0:
        return None
    return field_score.intersection_px / field_score.rasterized_px


def aggregate_precision(score: RenderMatchScore) -> float | None:
    """Mean precision across fields where the metric is defined.

    Mirrors `RenderMatchScore.aggregate`'s "mean of defined scores"
    treatment — fields with no rasterized polyline are skipped, not
    treated as zero. Returns `None` when no field produced a defined
    precision (the all-empty case).
    """
    defined: list[float] = []
    for fs in score.field_scores:
        p = precision_of(fs)
        if p is not None:
            defined.append(p)
    if not defined:
        return None
    return sum(defined) / len(defined)


# --- the gate --------------------------------------------------------


def triage(
    score: RenderMatchScore,
    prior_violations: list[PriorViolation],
) -> ChartVerdict:
    """Combine the two confidence signals into a single verdict.

    Pure function — no I/O, no extractor calls, no chart loading. Takes
    the outputs of the two signal modules and applies the rule. The
    runner (`autotriage.py`) is responsible for producing those inputs.
    """
    precision = aggregate_precision(score)
    iou = score.aggregate

    reasons: list[LowReason] = []

    # Render-match side.
    if precision is None or iou is None:
        reasons.append(LowReason.RENDER_MATCH_UNDEFINED)
    else:
        if precision < PRECISION_THRESHOLD:
            reasons.append(LowReason.PRECISION_BELOW_THRESHOLD)
        if iou < IOU_THRESHOLD:
            reasons.append(LowReason.IOU_BELOW_THRESHOLD)

    # Plausibility side. Translate each unique prior-name into its
    # reason code, preserving the order of first appearance so the
    # findings doc reads the same way every run.
    seen: set[LowReason] = set()
    for v in prior_violations:
        reason = _PRIOR_NAME_TO_REASON.get(v.prior_name)
        if reason is None:
            # New prior added without updating the map — fail loud rather
            # than silently swallow. Mirrors `dispatch.py`'s discipline
            # for out-of-band combinations (B1).
            raise NotImplementedError(
                f"triage: no LowReason mapped for prior name {v.prior_name!r}. "
                f"Add an entry to _PRIOR_NAME_TO_REASON."
            )
        if reason not in seen:
            seen.add(reason)
            reasons.append(reason)

    verdict: Literal["HIGH", "LOW"] = "HIGH" if not reasons else "LOW"
    return ChartVerdict(
        source_path=score.source_path,
        profile_name=score.profile_name,
        verdict=verdict,
        reasons=tuple(reasons),
        render_match_iou=iou,
        render_match_precision=precision,
        prior_violations=tuple(prior_violations),
    )
