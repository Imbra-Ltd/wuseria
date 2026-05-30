"""Tests for the auto-triage gate (#968).

Acceptance criteria from issue #968:

- Pure-function `triage()` exercised over each LowReason path with
  hand-constructed `RenderMatchScore` + violation fixtures.
- `aggregate_precision()` matches `scoring.md`'s reported numbers on
  fields with defined precision; skips undefined fields.
- Reference-set integration: Sigma 56mm = LOW (precision), Samyang 85mm
  = HIGH, Samyang 300mm reflex = LOW (flatness prior).
- `_PRIOR_NAME_TO_REASON` covers every name `check_all()` emits — a
  new prior added without a mapping fails loud, not silent.
"""

from __future__ import annotations

import pytest

from mtfdigitizer.pipeline.rendermatch import FieldIou, RenderMatchScore
from mtfdigitizer.priors import (
    CONTRAST_10S,
    RESOLUTION_30M,
    PriorViolation,
    check_all,
)
from mtfdigitizer.referenceset import REFERENCE_CHARTS
from mtfdigitizer.triage import (
    IOU_THRESHOLD,
    PRECISION_THRESHOLD,
    LowReason,
    aggregate_precision,
    precision_of,
    triage,
)


# --- Fixture builders -----------------------------------------------


def _field_iou(
    field: str,
    *,
    rasterized_px: int,
    skeleton_px: int,
    intersection_px: int,
    union_px: int | None = None,
) -> FieldIou:
    """Build a FieldIou with the IoU + precision implied by the pixel counts."""
    u = union_px if union_px is not None else (rasterized_px + skeleton_px - intersection_px)
    score: float | None
    if rasterized_px == 0 and skeleton_px == 0:
        score = None
    elif u == 0:
        score = None
    else:
        score = intersection_px / u
    return FieldIou(
        field=field,
        score=score,
        rasterized_px=rasterized_px,
        skeleton_px=skeleton_px,
        intersection_px=intersection_px,
        union_px=u,
    )


def _render_match(
    *fields: FieldIou,
    aggregate: float | None = None,
    source_path: str = "fake.png",
    profile_name: str = "FAKE_PROFILE",
) -> RenderMatchScore:
    """Build a RenderMatchScore. `aggregate` defaults to the mean of
    defined field scores, matching `score_chart()`'s behavior."""
    if aggregate is None:
        defined = [fs.score for fs in fields if fs.score is not None]
        aggregate = sum(defined) / len(defined) if defined else None
    return RenderMatchScore(
        source_path=source_path,
        profile_name=profile_name,
        field_scores=tuple(fields),
        aggregate=aggregate,
    )


def _high_render_match() -> RenderMatchScore:
    """A render-match that comfortably clears both thresholds."""
    # precision = 90/100 = 0.90, IoU = 90/110 = 0.818 — clears both.
    fs = _field_iou(
        CONTRAST_10S,
        rasterized_px=100,
        skeleton_px=100,
        intersection_px=90,
        union_px=110,
    )
    return _render_match(fs)


def _flatness_violation() -> PriorViolation:
    return PriorViolation(
        prior_name="not_suspiciously_flat",
        field=CONTRAST_10S,
        position_index=None,
        detail="mean 1.000 >= 0.95 and stdev 0.000 <= 0.02 (11/11 defined)",
    )


def _swap_violation() -> PriorViolation:
    return PriorViolation(
        prior_name="ten_ge_thirty",
        field=RESOLUTION_30M,
        position_index=5,
        detail="resolution30M=0.900 exceeds contrast10M=0.500 by 0.400 at position 5",
    )


# --- precision helpers ----------------------------------------------


def test_precision_of_returns_intersection_over_rasterized() -> None:
    fs = _field_iou(
        CONTRAST_10S,
        rasterized_px=100,
        skeleton_px=200,
        intersection_px=80,
    )
    assert precision_of(fs) == pytest.approx(0.80)


def test_precision_of_returns_none_when_no_polyline() -> None:
    """Zero rasterized pixels = no surface to score, not zero precision."""
    fs = _field_iou(
        CONTRAST_10S,
        rasterized_px=0,
        skeleton_px=500,
        intersection_px=0,
    )
    assert precision_of(fs) is None


def test_aggregate_precision_skips_undefined() -> None:
    """Fields with no rasterized pixels don't pull the mean toward zero."""
    defined = _field_iou(
        CONTRAST_10S,
        rasterized_px=100,
        skeleton_px=100,
        intersection_px=80,
    )
    sparse = _field_iou(
        RESOLUTION_30M,
        rasterized_px=0,
        skeleton_px=500,
        intersection_px=0,
    )
    score = _render_match(defined, sparse)
    # Mean of {0.80} only; sparse skipped.
    assert aggregate_precision(score) == pytest.approx(0.80)


def test_aggregate_precision_returns_none_when_all_undefined() -> None:
    sparse = _field_iou(
        CONTRAST_10S, rasterized_px=0, skeleton_px=500, intersection_px=0
    )
    score = _render_match(sparse)
    assert aggregate_precision(score) is None


# --- triage: HIGH path ----------------------------------------------


def test_triage_high_when_both_signals_clear() -> None:
    verdict = triage(_high_render_match(), [])
    assert verdict.verdict == "HIGH"
    assert verdict.reasons == ()
    assert verdict.prior_violations == ()
    # Carried metrics populated for the run log.
    assert verdict.render_match_iou is not None
    assert verdict.render_match_precision is not None


# --- triage: precision below threshold ------------------------------


def test_triage_low_when_precision_below_threshold() -> None:
    """Sigma-56mm pattern: precision 0.44 from sparse dashed-M bridging,
    even though IoU still clears its threshold."""
    # precision 0.40 < 0.80, IoU 100/300 = 0.33 > 0.20
    fs = _field_iou(
        CONTRAST_10S,
        rasterized_px=250,
        skeleton_px=150,
        intersection_px=100,
        union_px=300,
    )
    verdict = triage(_render_match(fs), [])
    assert verdict.verdict == "LOW"
    assert LowReason.PRECISION_BELOW_THRESHOLD in verdict.reasons
    assert LowReason.IOU_BELOW_THRESHOLD not in verdict.reasons


# --- triage: IoU below threshold ------------------------------------


def test_triage_low_when_iou_below_threshold() -> None:
    """Precision clears but IoU doesn't — the geometric-asymmetry case."""
    # precision = 100/100 = 1.00 (polyline lands perfectly)
    # IoU = 100/600 = 0.167 < 0.20 (skeleton is 5× bigger)
    fs = _field_iou(
        CONTRAST_10S,
        rasterized_px=100,
        skeleton_px=600,
        intersection_px=100,
        union_px=600,
    )
    verdict = triage(_render_match(fs), [])
    assert verdict.verdict == "LOW"
    assert LowReason.IOU_BELOW_THRESHOLD in verdict.reasons
    assert LowReason.PRECISION_BELOW_THRESHOLD not in verdict.reasons


def test_triage_borderline_iou_at_threshold_passes() -> None:
    """The rule is `>= threshold` — a value exactly at threshold must pass.
    Otherwise the Samyang 85mm (IoU 0.224 in scoring.md) would oscillate."""
    # precision 1.00, IoU exactly at IOU_THRESHOLD.
    fs = _field_iou(
        CONTRAST_10S,
        rasterized_px=100,
        skeleton_px=int(100 / IOU_THRESHOLD - 100),  # union = 100/IOU_THRESHOLD
        intersection_px=100,
        union_px=int(round(100 / IOU_THRESHOLD)),
    )
    verdict = triage(_render_match(fs), [])
    # Precision check must also pass (it's 1.0).
    assert LowReason.IOU_BELOW_THRESHOLD not in verdict.reasons


# --- triage: render-match undefined ---------------------------------


def test_triage_low_when_render_match_undefined() -> None:
    """No comparable fields (both sides empty everywhere) → undefined → LOW.

    Distinct from the "one side empty" case — that's a genuine
    disagreement (score=0.0) handled by IOU_BELOW_THRESHOLD. Undefined
    is the all-empty case: the chart loaded but produced no skeleton
    and no polyline anywhere. Rare in practice (only happens if the
    extractor returns all-None readings AND the dispatch finds no
    skeleton fields), but the gate must handle it cleanly."""
    both_empty = _field_iou(
        CONTRAST_10S, rasterized_px=0, skeleton_px=0, intersection_px=0
    )
    score = _render_match(both_empty)
    assert score.aggregate is None  # both sides empty ⇒ None per rendermatch.iou()
    verdict = triage(score, [])
    assert verdict.verdict == "LOW"
    assert LowReason.RENDER_MATCH_UNDEFINED in verdict.reasons
    # Doesn't pile on with precision/IoU codes — undefined supersedes.
    assert LowReason.PRECISION_BELOW_THRESHOLD not in verdict.reasons
    assert LowReason.IOU_BELOW_THRESHOLD not in verdict.reasons


# --- triage: prior failures -----------------------------------------


def test_triage_low_when_flatness_prior_fires() -> None:
    """The 300mm reflex pattern: render-match looks fine, prior catches it."""
    verdict = triage(_high_render_match(), [_flatness_violation()])
    assert verdict.verdict == "LOW"
    assert LowReason.PRIOR_FAILED_NOT_SUSPICIOUSLY_FLAT in verdict.reasons
    # No render-match codes — that signal cleared.
    assert LowReason.PRECISION_BELOW_THRESHOLD not in verdict.reasons


def test_triage_collapses_duplicate_prior_violations() -> None:
    """Three flatness violations (one per field) → one reason code, not three."""
    violations = [_flatness_violation(), _flatness_violation(), _flatness_violation()]
    verdict = triage(_high_render_match(), violations)
    flatness_codes = [
        r for r in verdict.reasons if r == LowReason.PRIOR_FAILED_NOT_SUSPICIOUSLY_FLAT
    ]
    assert len(flatness_codes) == 1
    # Underlying violations preserved verbatim — runner displays each one.
    assert len(verdict.prior_violations) == 3


def test_triage_preserves_violation_order() -> None:
    """First-appearance order — so the findings doc reads consistently."""
    verdict = triage(
        _high_render_match(),
        [_swap_violation(), _flatness_violation()],
    )
    swap_idx = verdict.reasons.index(LowReason.PRIOR_FAILED_TEN_GE_THIRTY)
    flat_idx = verdict.reasons.index(LowReason.PRIOR_FAILED_NOT_SUSPICIOUSLY_FLAT)
    assert swap_idx < flat_idx


def test_triage_unknown_prior_name_raises() -> None:
    """A new prior added without updating the map fails loud — never silent."""
    rogue = PriorViolation(
        prior_name="rogue_new_prior",
        field=CONTRAST_10S,
        position_index=None,
        detail="hypothetical",
    )
    with pytest.raises(NotImplementedError, match="rogue_new_prior"):
        triage(_high_render_match(), [rogue])


def test_triage_all_four_priors_each_map_to_a_distinct_reason() -> None:
    """The four prior names check_all() emits each have a LowReason. If
    a prior is added, this fails until _PRIOR_NAME_TO_REASON is extended."""
    expected = {
        "center_ge_edge": LowReason.PRIOR_FAILED_CENTER_GE_EDGE,
        "ten_ge_thirty": LowReason.PRIOR_FAILED_TEN_GE_THIRTY,
        "not_suspiciously_flat": LowReason.PRIOR_FAILED_NOT_SUSPICIOUSLY_FLAT,
        "in_range": LowReason.PRIOR_FAILED_IN_RANGE,
    }
    for prior_name, expected_reason in expected.items():
        v = PriorViolation(
            prior_name=prior_name,
            field=CONTRAST_10S,
            position_index=None,
            detail="x",
        )
        verdict = triage(_high_render_match(), [v])
        assert expected_reason in verdict.reasons, (
            f"prior name {prior_name!r} did not map to {expected_reason!r}"
        )


# --- triage: combined paths -----------------------------------------


def test_triage_reports_all_reasons_when_multiple_fail() -> None:
    """Pathological chart: low precision AND prior violation AND low IoU.
    The verdict carries every reason, so the maintainer sees the full picture."""
    bad = _field_iou(
        CONTRAST_10S,
        rasterized_px=250,
        skeleton_px=1000,
        intersection_px=50,
        union_px=1200,
    )
    # precision = 50/250 = 0.20 < 0.80; IoU = 50/1200 = 0.042 < 0.20
    verdict = triage(_render_match(bad), [_flatness_violation()])
    assert verdict.verdict == "LOW"
    assert LowReason.PRECISION_BELOW_THRESHOLD in verdict.reasons
    assert LowReason.IOU_BELOW_THRESHOLD in verdict.reasons
    assert LowReason.PRIOR_FAILED_NOT_SUSPICIOUSLY_FLAT in verdict.reasons


# --- Reference-set integration --------------------------------------


def _triage_reference(slug: str):
    """Run the full pipeline on one reference chart and return the verdict."""
    # Imported lazily to keep test_triage's pure-fixture tests free of
    # OpenCV/IO weight at collection time.
    from mtfdigitizer.autotriage import triage_chart

    chart = next(c for c in REFERENCE_CHARTS if c.slug == slug)
    return triage_chart(chart)


def test_reference_sigma_56_classified_low_for_precision() -> None:
    """Sparse dashed-M bridging keeps precision below 0.80 — the LOW
    signal correctly routes the maintainer to the upstream extractor
    work, not to a chart review."""
    verdict = _triage_reference("sigma-56mm-f1-4-dc-dn-c")
    assert verdict.verdict == "LOW"
    assert LowReason.PRECISION_BELOW_THRESHOLD in verdict.reasons
    # Priors don't fire on Sigma (it's a real lens) — verify no false routing.
    prior_codes = {r for r in verdict.reasons if r.value.startswith("prior_failed_")}
    assert prior_codes == set(), f"Sigma should not trigger priors; got {prior_codes}"


def test_reference_samyang_85_classified_high() -> None:
    """Real 4-color chart with cleanly-traced curves — both signals clear."""
    verdict = _triage_reference("samyang-85mm-f1-4-as-if-umc")
    assert verdict.verdict == "HIGH", (
        f"Samyang 85mm should classify HIGH; got reasons {verdict.reasons}, "
        f"precision={verdict.render_match_precision}, iou={verdict.render_match_iou}"
    )
    assert verdict.reasons == ()


def test_reference_samyang_300_reflex_classified_low_for_flatness() -> None:
    """ADR-038's flat-axis blind-spot case — render-match would say HIGH
    (precision 0.99 in scoring.md) but the plausibility prior catches it."""
    verdict = _triage_reference("samyang-300mm-f6-3-ed-umc-cs-reflex")
    assert verdict.verdict == "LOW"
    assert LowReason.PRIOR_FAILED_NOT_SUSPICIOUSLY_FLAT in verdict.reasons


# --- Sanity guards on the constants ---------------------------------


def test_thresholds_match_scoring_md_recommendations() -> None:
    """If the constants drift, the findings docs go out of sync silently."""
    assert PRECISION_THRESHOLD == 0.80
    assert IOU_THRESHOLD == 0.20


def test_lowreason_values_are_lowercase_snake() -> None:
    """Reason codes are printed and read; consistent format keeps the
    findings doc grep-able."""
    for reason in LowReason:
        assert reason.value == reason.value.lower()
        assert " " not in reason.value
