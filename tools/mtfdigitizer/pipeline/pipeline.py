"""Top-level pipeline orchestrator (#935, ADR-038 §2-3).

Reads chart → dispatches per profile dialect → samples each curve at the
11 fixed points. The "which curve becomes which committed field" logic
lives in `dispatch.field_skeletons()` so the render-match scorer reuses
the same answer the extractor computes (#963).

Post-extraction the pipeline applies two physics-grounded corrections:

- **Sister fallback.** When a curve has no real ink near a sample
  fraction (the dispatch's skeleton is empty in the bracket window),
  the reading falls back to the sister curve's value — i.e. 10M takes
  10S's value when 10M has no ink, and vice versa; same for 30S/30M.
  Lossy but defensible: at the optical axis sister curves are equal
  (B4), and where one curve drops off near the field edge the other
  often tracks closely. Better than letting the DP path drift onto a
  parallel curve's ink and reporting a misleading value.

- **Center symmetry.** At fraction 0.0 (the optical axis), sagittal
  and meridional MTF are equal by physics (B4). Whatever value each
  frequency reports at center is averaged so S and M match exactly,
  removing any anti-aliasing or pixel-noise asymmetry.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import numpy as np

from ..loader import load_chart_bgr
from ..profiles.types import MtfProfile
from .dispatch import (
    _apply_declared_halo_pairs,
    _apply_small_below_top_cc_filter,
    _hue_clip,
    curve_field,
    field_skeletons,
    parse_curve_identity_name,
    unique_named_hues,
)
from .masks import masks_by_curve_name, strip_plot_box_borders
from .skeleton import close_and_skeletonize
from .split import split_sm_by_cc_width
from .sampling import (
    SAMPLE_FRACTIONS,
    sample_positions_mm,
    sample_skeleton_at_fraction,
)
from .types import ExtractedChart, PlotBox, SampledReading

if TYPE_CHECKING:
    from ..diagnostic import DiagnosticSink, FileDiagnosticSink


SAMPLE_POINTS: tuple[float, ...] = SAMPLE_FRACTIONS  # re-export


# Half-width of the column window in which raw ink is required for a
# sample to count as "really there" (i.e. not eligible for sister
# fallback). About half a dash period — small enough that a normal
# dashed curve still passes (dashes are ~10 px wide; even mid-gap
# columns find ink within ~10 px), but big enough to fire when the
# curve is genuinely absent (Tokina 11-18 left edge where 10M
# starts ~25 px right of the plot box). Earlier values of 30 were
# overshooting: single dashes were not enough to trigger fallback,
# but their ~0.01 anti-aliasing biases were inheriting from the
# sister and broadcasting across the curve.
_INK_PRESENCE_HALF_WIDTH: int = 10


# Horizontal kernel width used to bridge a dashed curve's gaps when
# building its sister-fallback presence mask under the
# (SPLIT_BY_DASH, GEODESIC_DP) dispatch. Wide enough (~0.5 mm at Sigma
# plot scale) that a curve whose last dash falls just short of the plot
# edge still reads "present" at the field-edge sample — so the DP path's
# extrapolated value is kept instead of being overwritten by the
# diverging solid (sister) curve. Vertical extent stays 3 px so the mask
# does not pull the raw-centroid snap off the true stroke.
_DASH_PRESENCE_BRIDGE_W: int = 121


def _sister_of(field: str) -> str | None:
    """Sister field of `field` — same frequency, opposite S/M axis.

    `freq10S` ↔ `freq10M`, `freq30S` ↔ `freq30M`, etc. Returns `None`
    when the field name does not follow the synthetic convention (a
    defensive guard; the dispatch is the only producer of these names
    and always emits them in form `freq{N}{S|M}`).
    """
    if not field.startswith("freq"):
        return None
    if field.endswith("S"):
        return field[:-1] + "M"
    if field.endswith("M"):
        return field[:-1] + "S"
    return None


def _sample_curve(
    skeleton, plot_box: PlotBox, raw_mask=None
) -> tuple[float | None, ...]:
    """11-point sample of one skeleton, returns one MTF value per fraction.

    When ``raw_mask`` is supplied, each sample is snapped to the raw
    ink centroid in a tight window around the skeleton's predicted y —
    restores pixel-accuracy on solid strokes without losing DP
    interpolation across dash gaps.
    """
    return tuple(
        sample_skeleton_at_fraction(skeleton, f, plot_box, raw_mask=raw_mask)
        for f in SAMPLE_FRACTIONS
    )


def _ink_presence_per_field(
    skeletons: dict[str, np.ndarray], plot_box: PlotBox
) -> dict[str, tuple[bool, ...]]:
    """For each field, return whether real ink exists in a wide window
    of each sample fraction.

    True means the skeleton has at least one pixel within
    ``_INK_PRESENCE_HALF_WIDTH`` columns of the sample target —
    proxy for "this curve really exists at this fraction." False
    means the sample is a candidate for sister fallback.
    """
    out: dict[str, tuple[bool, ...]] = {}
    for field, skel in skeletons.items():
        presence: list[bool] = []
        for f in SAMPLE_FRACTIONS:
            target_x = int(round(plot_box.x_left + f * plot_box.width))
            x_lo = max(plot_box.x_left, target_x - _INK_PRESENCE_HALF_WIDTH)
            x_hi = min(plot_box.x_right, target_x + _INK_PRESENCE_HALF_WIDTH)
            window = skel[plot_box.y_top : plot_box.y_bottom + 1, x_lo : x_hi + 1]
            presence.append(bool(window.any()))
        out[field] = tuple(presence)
    return out


def _replace_sister_fills_with_intra_interp(
    samples: dict[str, tuple[float | None, ...]],
    sister_filled: dict[str, tuple[bool, ...]],
) -> tuple[dict[str, tuple[float | None, ...]], dict[str, int]]:
    """Replace sister-filled cells with intra-curve interp where possible.

    Sister fallback assumes S and M track each other when one has a gap
    — true near the optical axis (B4), often true near the field edge,
    but false at mid-field where S and M can legitimately diverge by
    0.2+ MTF (Samyang 85mm stopped 30S flat at 0.97 while 30M sweeps
    0.95->0.55, see #1254). Continuity within a single optical curve is
    a stronger prior than S~=M off-axis.

    Runs AFTER sister fallback so we know exactly which cells it filled.
    Identifies each maximal run of consecutive sister-filled cells; if
    both bracketing samples (the indices immediately before and after
    the run) are present AND were NOT themselves sister-filled, linearly
    interpolates across the run between those two endpoints.

    Conservatism — does NOT interpolate when:
    - the run touches index 0 or the last index (no two-sided bracket)
    - either bracketing sample is None (sister fallback could not fill
      because both curves lacked data)
    - either bracketing sample is itself sister-filled (the bracket value
      is not from the field's own curve; interpolating would propagate
      sister-fill error across an even wider span)

    Runs that fail any of these conditions keep their sister-fill values
    — sister fallback's S~=M approximation is the best signal we have
    when the field's own curve provides no anchor.

    Returns ``(samples, intra_fill_count_by_field)``.
    """
    out: dict[str, tuple[float | None, ...]] = {}
    intra_count: dict[str, int] = {}
    for field, values in samples.items():
        fills = sister_filled.get(field, (False,) * len(values))
        fixed: list[float | None] = list(values)
        count = 0
        n = len(values)
        i = 0
        while i < n:
            if not fills[i]:
                i += 1
                continue
            run_start = i
            while i < n and fills[i]:
                i += 1
            run_end = i - 1  # inclusive
            left = run_start - 1
            right = run_end + 1
            if left < 0 or right >= n:
                continue
            if fills[left] or fills[right]:
                continue
            left_v = values[left]
            right_v = values[right]
            if left_v is None or right_v is None:
                continue
            span = right - left  # 2 for single-cell, 3 for two-cell, ...
            for j in range(run_start, run_end + 1):
                t = (j - left) / span
                fixed[j] = left_v + t * (right_v - left_v)
                count += 1
        out[field] = tuple(fixed)
        intra_count[field] = count
    return out, intra_count


def _apply_sister_fallback(
    samples: dict[str, tuple[float | None, ...]],
    presence: dict[str, tuple[bool, ...]],
    *,
    presence_is_authoritative: bool = False,
) -> tuple[dict[str, tuple[float | None, ...]], dict[str, int]]:
    """Replace samples where ink is absent with the sister curve's value.

    Two trigger conditions, in priority order:

    1. The field's raw ink is absent in the wide presence window AND the
       sister's ink is present — the historical trigger. Copies the
       sister's value, counts as a fallback.
    2. The field's own sample is `None` (sampler bracket found no
       skeleton pixel) AND the sister has a non-None value AND the
       per-field presence window saw ink near this fraction — the
       "sampler-None" trigger. Catches the curve-start case (first
       dash falls just outside the sampler bracket) and the both-
       curves-overlap case (one hue's mask dominates the other in
       pixel-blended regions). The presence gate (#1215) keeps the
       trigger off when our trim has explicitly said the curve does
       NOT extend here.

    ``presence_is_authoritative`` (#1215): set True when the presence
    mask is derived from a trim-aware skeleton (HUE_IS_CURVE/GEODESIC_DP,
    where the right-edge flatline trim has already verified curve
    extent). In that mode, `field_presence[i] is False` is the trim's
    verdict that the curve does not extend here, and BOTH triggers are
    suppressed at that index — None stays None rather than being
    overwritten by a diverging sister value (Tokina 56 freq30M
    frac=1.0). Default False preserves historical behaviour for
    profiles whose presence mask is a coarse per-hue raw signal.

    Returns ``(samples, fallback_count_by_field, sister_filled_by_field)``.
    The counter records how many of a field's 11 samples were filled
    from the sister curve via either trigger; samples that stayed
    `None` because both curves lacked data do not count as fallbacks.
    The per-cell boolean tuple flags which cells came from the sister
    (vs. the field's own sampler) so a downstream pass can intervene
    on the diverging-curve case (#1254).
    """
    out: dict[str, tuple[float | None, ...]] = {}
    fallback_count: dict[str, int] = {}
    sister_filled: dict[str, tuple[bool, ...]] = {}
    for field, values in samples.items():
        sister = _sister_of(field)
        sister_values = samples.get(sister, (None,) * len(SAMPLE_FRACTIONS)) if sister else (None,) * len(SAMPLE_FRACTIONS)
        field_presence = presence.get(field, (False,) * len(SAMPLE_FRACTIONS))
        sister_presence = presence.get(sister, (False,) * len(SAMPLE_FRACTIONS)) if sister else (False,) * len(SAMPLE_FRACTIONS)
        fixed: list[float | None] = []
        filled_flags: list[bool] = []
        count = 0
        for i, v in enumerate(values):
            if v is None and sister_values[i] is not None and field_presence[i]:
                # Sampler-None trigger (see docstring).
                fixed.append(sister_values[i])
                filled_flags.append(True)
                count += 1
            elif field_presence[i]:
                fixed.append(v)
                filled_flags.append(False)
            elif sister_presence[i] and not presence_is_authoritative:
                # Sister has real ink here; trust it over our drifted value.
                # Suppressed when presence is authoritative — the trim's
                # field_presence=False verdict overrides sister-has-ink.
                fixed.append(sister_values[i])
                filled_flags.append(True)
                count += 1
            else:
                # Neither curve has ink — keep whatever the DP path
                # interpolated (or None if the curve was missing entirely).
                fixed.append(v)
                filled_flags.append(False)
        out[field] = tuple(fixed)
        fallback_count[field] = count
        sister_filled[field] = tuple(filled_flags)
    return out, fallback_count, sister_filled


_CENTER_AXIS_MTF = 1.0

# When the lower-frequency curve sits at MTF >= this threshold, a
# sister-filled higher-frequency cell at the same frac is assumed to
# be coincident with the lower curve (the chart artist merged two
# near-1.0 strokes into one visible line) and inherits the lower
# curve's value. Picked at 0.90 to cover the case where the lower
# curve has begun a mild dip but the higher-freq curve, masked by
# coincidence, cannot plausibly have already crashed to its sister's
# value (typical sister-fill error in this regime is 0.4+ MTF, i.e.
# a clearly wrong reading we'd rather replace with a bounded one).
# At 0.90 the lower curve is still effectively flat at chart top;
# below that, the merged-stroke assumption weakens and we fall back
# to the existing sister-fill chain.
_COINCIDENT_ANCHOR_THRESHOLD = 0.90

# Maximum **minimum** |hi - lo| over genuinely-extracted (non-sister-
# filled, non-None) cells where the lower curve sits at chart top for
# the coincident-stroke assumption to hold. When the chart artist
# draws hi and lo curves as one visible line at chart top, at least
# one cell where both curves do exist separately (typically near
# where the higher-freq curve first emerges from coincidence) sits
# within ~0.05 MTF of the lower curve. When the curves are genuinely
# independent (samyang-85mm: 30M sits at MTF 0.6 while 10M is at
# MTF 0.91, gap ~0.3 across every clean cell), no cell shows the
# touch and the gate fires. The minimum (not median) is the right
# statistic: natural divergence elsewhere in the field shouldn't veto
# anchor work where the curves demonstrably touch at the top.
_COINCIDENT_ANCHOR_MAX_PAIR_DELTA = 0.05


def _apply_coincident_top_anchor(
    samples: dict[str, tuple[float | None, ...]],
    sister_filled: dict[str, tuple[bool, ...]],
) -> tuple[dict[str, tuple[float | None, ...]], dict[str, int]]:
    """Override sister-filled or None high-freq cells with the low-freq
    value when the low-freq curve is pinned at MTF >= 0.90.

    ADR-068 (#1269): the sister-filled case. Chart families that pack
    multiple frequencies into one panel often draw the higher-frequency
    curve coincident with the lower-frequency curve while both are at
    MTF ~1.0 — the strokes overlap into a single visible line. Sister
    fallback (S~=M of the same frequency) breaks here when one
    frequency's S curve is masked by the other frequency's S curve: the
    higher-freq skeleton is empty across the coincident region, sister
    fallback fires using the diverging M sister, and the higher-freq
    cell inherits a value far from its true position.

    ADR-069 (#1277): the None case. On charts where BOTH S and M of
    the higher frequency are buried under the lower-freq strokes (e.g.
    samyang-300mm-f6-3-ed-umc-cs-reflex max+stopped panels, with all
    four curves stacked at MTF~1.0 across the full field), sister
    fallback cannot fire at all — both sisters are empty — so the cells
    stay None and break the polyline in the provenance SVG. Extending
    the anchor to fire on None cells fills those gaps from the same
    same-direction lower-freq curve. The pair gate below already
    isolates the chart-top regime correctly and protects pairs where
    hi and lo are genuinely independent (e.g. samyang-85mm).

    The fix: when a higher-freq S (or M) cell was sister-filled OR is
    None, AND the same-direction lower-freq cell at the same frac reads
    MTF >= `_COINCIDENT_ANCHOR_THRESHOLD`, override with the lower-freq
    value. The lower-freq curve cannot exceed the higher-freq by
    physics; when the lower curve is at chart top, the higher curve
    must also be at chart top (or just below); copying the lower-
    freq value is the best available anchor.

    Runs AFTER sister fallback + intra-curve interpolation, BEFORE
    center-symmetry. Cells the extractor or intra-interp filled with
    real values keep their values; only sister-filled and None cells
    are eligible for override.

    Returns ``(samples, override_count_by_field)``.
    """
    out = {field: list(values) for field, values in samples.items()}
    override_count: dict[str, int] = {field: 0 for field in samples}

    frequencies: list[tuple[int, str]] = []  # (freq, direction) entries
    for field in samples:
        if not field.startswith("freq"):
            continue
        if not (field.endswith("S") or field.endswith("M")):
            continue
        freq_str = field[4:-1]
        if not freq_str.isdigit():
            continue
        frequencies.append((int(freq_str), field[-1]))

    distinct_freqs = sorted({f for f, _ in frequencies})
    if len(distinct_freqs) < 2:
        return ({k: tuple(v) for k, v in out.items()}, override_count)

    for hi_field in samples:
        if not hi_field.startswith("freq"):
            continue
        if hi_field[-1] not in ("S", "M"):
            continue
        hi_freq_str = hi_field[4:-1]
        if not hi_freq_str.isdigit():
            continue
        hi_freq = int(hi_freq_str)
        direction = hi_field[-1]
        lower_freqs = [f for f in distinct_freqs if f < hi_freq]
        if not lower_freqs:
            continue
        lo_freq = max(lower_freqs)  # closest lower frequency
        lo_field = f"freq{lo_freq}{direction}"
        if lo_field not in samples:
            continue
        hi_values = out[hi_field]
        lo_values = out[lo_field]
        fills = sister_filled.get(hi_field, ())
        lo_fills = sister_filled.get(lo_field, ())
        # Coincident-stroke gate: only fire the anchor when the lens's
        # hi/lo curves are demonstrably close on cells where both
        # extracted independently and the lower curve sits at chart top
        # (lo >= the anchor threshold). The gate uses the **minimum**
        # |hi-lo| across qualifying cells (not the median) so it asks
        # the right question: "is there at least one anchor point on
        # this lens where hi and lo demonstrably touch?" rather than
        # "are they on average close" — natural divergence elsewhere
        # in the field is irrelevant evidence about the top-regime
        # behaviour the anchor will copy from.
        #
        # If the minimum |hi-lo| over those qualifying cells exceeds
        # _COINCIDENT_ANCHOR_MAX_PAIR_DELTA the chart has genuinely
        # separate curves with no anchor-point overlap; copying lo into
        # a sister-filled hi cell would corrupt the value. Lenses with
        # genuinely separate curves (samyang-85mm: hi ~0.6, lo ~0.91,
        # gap ~0.3 across every clean cell) have minimum |Δ| ~0.3,
        # well above the 0.05 gate. Lenses with coincident-at-top hi/lo
        # (samyang 12mm fisheye: |Δ| 0.006 at the cell closest to the
        # coincident region) pass even when corner divergence brings
        # the average up.
        clean_deltas: list[float] = []
        for i in range(len(hi_values)):
            hi_v = hi_values[i]
            lo_v = lo_values[i] if i < len(lo_values) else None
            hi_filled = i < len(fills) and fills[i]
            lo_filled = i < len(lo_fills) and lo_fills[i]
            if hi_v is None or lo_v is None:
                continue
            if hi_filled or lo_filled:
                continue
            if lo_v < _COINCIDENT_ANCHOR_THRESHOLD:
                continue
            clean_deltas.append(abs(hi_v - lo_v))
        if clean_deltas:
            if min(clean_deltas) > _COINCIDENT_ANCHOR_MAX_PAIR_DELTA:
                continue  # curves never touch — skip anchor for this pair
        for i in range(len(hi_values)):
            # Eligible: sister-filled (ADR-068) OR None (ADR-069).
            # Cells the extractor or intra-interp produced real values
            # for keep their values.
            #
            # frac=0.0 is NOT skipped: when freq{lo}{D} at center reads
            # below 1.0 due to extraction noise (e.g. 10S=0.985 on a
            # true-1.0 chart-top curve), anchoring freq{hi}{D} to that
            # noisy value is more honest than ADR-066's 1.0 physical
            # constant, because lo >= hi is a strict physical invariant
            # — hi cannot exceed lo regardless of physics at the axis.
            # Letting ADR-066 fire instead would set hi=1.0 while
            # lo=0.985, producing hi>lo (physically impossible) AND a
            # visible upward kink between center and frac=0.1 in the
            # rendered SVG. ADR-069 wins here; ADR-066 still fires for
            # cells the pair gate or threshold rules out.
            sister_eligible = i < len(fills) and fills[i]
            none_eligible = hi_values[i] is None
            if not (sister_eligible or none_eligible):
                continue
            lo_v = lo_values[i]
            if lo_v is None or lo_v < _COINCIDENT_ANCHOR_THRESHOLD:
                continue
            hi_values[i] = lo_v
            override_count[hi_field] += 1

    return ({k: tuple(v) for k, v in out.items()}, override_count)


def _apply_center_symmetry(
    samples: dict[str, tuple[float | None, ...]],
) -> tuple[dict[str, tuple[float | None, ...]], dict[str, int]]:
    """Force S = M at the optical axis (fraction 0.0).

    At position 0 sagittal and meridional MTF are equal by physics
    (B4). Three cases per frequency pair:

    1. Both S and M have a value — keep S, override M with it (not
       the average): on charts where the DP path for the M curve has
       drifted near center (Tokina 11-18, where 10M's ink doesn't
       quite reach frac 0.0 and the path lands on a nearby curve's
       stripe), averaging would split the difference between the
       right value and the drifted value. The S curve is solid-line,
       less susceptible to drift, and almost always the cleaner
       anchor.
    2. One side is None — copy the other side over.
    3. Both are None — anchor from the closest same-direction lower
       frequency if available, else MTF=1.0.

       ADR-066 (#1267) introduced the 1.0 anchor for this case. The
       diffraction-free chart's optical axis MTF is 1.0 by definition,
       and on most affected lenses (samyang-10mm stopped, samyang-
       af-12mm, etc.) the lower-freq curve also sits at chart top so
       1.0 is correct.

       ADR-072 (#1279) refines the rule: when the same-direction
       lower-freq curve has a value at center (e.g. freq10S extracts
       at 0.99 on viltrox-75 f/1.2 where the chart artist drew
       freq30 below chart top), copy from it instead. This preserves
       the physical invariant `freq{hi}{D}[0] <= freq{lo}{D}[0]`
       which the 1.0 constant violates whenever lo extracts below
       1.0. The fallback chain is:
         freq{hi}{S}[0] := freq{lo}{S}[0]
                     or freq{lo}{M}[0]   (cross-direction copy at the axis)
                     or 1.0              (no lower frequency available)
       and symmetric for the M field. ADR-069's pair gate veto on
       multi-cell coincident-top copy is intentionally local to that
       pass — at the single optical-axis cell the `hi <= lo`
       invariant holds independent of gate verdicts.

       Fires only at frac=0.0 (the right edge has no equivalent
       physical guarantee) and only when every prior stage (direct
       extraction, sister fallback, intra-curve interp, coincident-
       top anchor) failed to produce a value on either side of a
       frequency pair.

    Pairs up every `freq{N}S`/`freq{N}M` present in `samples` —
    per-frequency rule applies to every chart family (ADR-042).

    Returns ``(samples, center_anchor_count_by_field)``. The counter
    records cells filled by case 3 only; cases 1 and 2 are existing
    symmetry behaviour and remain implicit.
    """
    out = {field: list(values) for field, values in samples.items()}
    anchor_count: dict[str, int] = {field: 0 for field in samples}

    # Pre-compute the closest-lower-frequency map so each "both None"
    # case is O(1). Iterates only freq{N}{S|M} fields with integer N.
    distinct_freqs: list[int] = []
    for field in samples:
        if not field.startswith("freq"):
            continue
        if field[-1] not in ("S", "M"):
            continue
        freq_str = field[4:-1]
        if freq_str.isdigit():
            n = int(freq_str)
            if n not in distinct_freqs:
                distinct_freqs.append(n)
    distinct_freqs.sort()

    def _closest_lower(freq_n: int) -> int | None:
        candidates = [f for f in distinct_freqs if f < freq_n]
        return max(candidates) if candidates else None

    # Collect every S field present and look for the matching M.
    for s_field in [f for f in samples if f.endswith("S") and f.startswith("freq")]:
        m_field = s_field[:-1] + "M"
        if m_field not in out:
            continue
        s_val = out[s_field][0]
        m_val = out[m_field][0]
        if s_val is None and m_val is None:
            freq_str = s_field[4:-1]
            lo_freq = _closest_lower(int(freq_str)) if freq_str.isdigit() else None
            # The lower-frequency S/M fields may be absent when a band
            # produced a single curve (B2 contract) -- read via .get so a
            # missing anchor falls through the chain instead of raising.
            lo_s_vals = out.get(f"freq{lo_freq}S") if lo_freq is not None else None
            lo_m_vals = out.get(f"freq{lo_freq}M") if lo_freq is not None else None
            lo_s = lo_s_vals[0] if lo_s_vals is not None else None
            lo_m = lo_m_vals[0] if lo_m_vals is not None else None
            # Fallback chain per direction: same-direction lo -> cross-
            # direction lo (S=M at the axis by B4) -> 1.0 physical
            # constant. The ordering is order-independent across freq
            # pairs because a prior iteration's anchor leaves a value
            # in `out` that a later iteration can read as its lo.
            out[s_field][0] = (
                lo_s if lo_s is not None
                else lo_m if lo_m is not None
                else _CENTER_AXIS_MTF
            )
            out[m_field][0] = (
                lo_m if lo_m is not None
                else lo_s if lo_s is not None
                else _CENTER_AXIS_MTF
            )
            anchor_count[s_field] += 1
            anchor_count[m_field] += 1
            continue
        if s_val is None:
            out[s_field][0] = m_val
        else:
            # B4: at the optical axis, S=M. Use S for both — solid
            # strokes are less prone to centroid drift than dashed.
            out[m_field][0] = s_val
    return (
        {field: tuple(values) for field, values in out.items()},
        anchor_count,
    )


def _readings_to_dict(
    samples_per_field: dict[str, tuple[float | None, ...]],
    plot_box: PlotBox,
    image_height_mm: float,
) -> tuple[SampledReading, ...]:
    """Build the 11 SampledReading rows from per-field column samples.

    Each row's `samples` dict carries the fields present in
    `samples_per_field`. Missing fields are dropped — the schema
    (ADR-042) allows reading rows to omit frequencies the chart did
    not publish.
    """
    positions = sample_positions_mm(plot_box, image_height_mm)
    rows: list[SampledReading] = []
    for i, pos in enumerate(positions):
        row_samples: dict[str, float | None] = {
            field: values[i] for field, values in samples_per_field.items()
        }
        rows.append(SampledReading(position_mm=pos, samples=row_samples))
    return tuple(rows)


# Horizontal-bridge kernel width for the GEODESIC_DP per-field presence
# signal (#1215). The DP path rasterises one pixel per column it covers;
# dilating horizontally by this amount lets the ±10 col presence window
# match "skeleton present at this fraction" without false negatives on
# the trim-aware mask. Smaller than `_INK_PRESENCE_HALF_WIDTH * 2` so
# the dilated skeleton's right edge still reflects the trim — the
# presence window catches it, but only within its native ±10 col reach.
_DP_PRESENCE_BRIDGE_W: int = 5


def _per_field_presence_for_fallback(
    presence_masks: dict[str, np.ndarray],
    skeletons: dict[str, np.ndarray],
    profile: MtfProfile,
) -> dict[str, np.ndarray]:
    """Per-field presence mask for the sister-fallback ink check.

    For HUE_IS_CURVE / GEODESIC_DP profiles, the raw per-hue mask
    carries two curves under one hue (e.g. M-blue is freq10M + freq30M),
    so it cannot distinguish "freq30M's curve ended here" from "freq10M
    still has ink at this column" — the latter would force sister
    fallback to overwrite a correctly-None freq30M with the diverging
    freq30S value (Tokina 56 frac=1.0, see #1215). The DP-derived field
    skeleton already encodes the right-edge trim, so use it instead
    after a horizontal bridge to absorb dash-gap jitter. Other profiles
    keep the raw mask — their hue maps 1:1 to a field already.
    """
    if (
        profile.style_axis == "HUE_IS_CURVE"
        and profile.hue_meaning == "GEODESIC_DP"
    ):
        bridge = cv2.getStructuringElement(
            cv2.MORPH_RECT, (_DP_PRESENCE_BRIDGE_W, 3)
        )
        out: dict[str, np.ndarray] = {}
        for field, mask in presence_masks.items():
            skel = skeletons.get(field)
            if skel is None or not skel.any():
                out[field] = mask
                continue
            out[field] = cv2.dilate(skel.astype(np.uint8), bridge)
        return out
    return presence_masks


def _hue_masks_for_presence(
    bgr: np.ndarray, profile: MtfProfile, plot_box: PlotBox
) -> dict[str, np.ndarray]:
    """Build per-field RAW-ink masks for the ink-presence check.

    The skeleton coming out of the dispatch is the DP path rasterised
    everywhere, so it always says "ink present" — useless as a
    presence signal. We need the raw per-hue mask the dispatch
    consumed. Re-extract it here (cheap: HSV + range threshold) and
    map each hue's mask to both committed fields under that hue.

    Applies the profile's `halo_pairs` subtraction (#1216) before
    using the masks for presence — otherwise the contaminated hue's
    pre-subtraction halo ink would mark cells "present" even when the
    dispatcher's skeleton (post-subtraction) has nothing there, leaving
    `None` samples that should have triggered sister fallback.
    """
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    curve_masks = masks_by_curve_name(hsv, profile)
    if plot_box is not None:
        # Per-hue clip honours `PlotBox.y_top_insets` (#1271, ADR-067)
        # so a hue contaminated by a sister curve's AA halo can be
        # trimmed at the top without affecting the contaminator's mask.
        curve_masks = {
            name: (m & _hue_clip(m.shape, plot_box, name))
            for name, m in curve_masks.items()
        }
        curve_masks = strip_plot_box_borders(curve_masks, plot_box)
    curve_masks = _apply_declared_halo_pairs(curve_masks, profile.halo_pairs)
    curve_masks = _apply_small_below_top_cc_filter(
        curve_masks, profile.small_below_top_cc_filters
    )
    # Map per-hue raw mask to the two fields that share that hue.
    # The mapping depends on the profile; we read it from the hue
    # name convention ("S-red" → contrast10S + resolution30S, etc).
    out: dict[str, np.ndarray] = {}
    if profile.style_axis == "SPLIT_BY_DASH" and profile.hue_meaning == "GEODESIC_DP":
        # Color-named hues (one per frequency); each splits into a solid
        # (S) and dashed (M) sub-skeleton. The dashed sub-skeleton is
        # horizontally dilated to bridge dash gaps before it becomes the
        # presence signal: a raw gappy dashed skeleton makes the
        # ink-presence check read "absent" mid-gap and triggers a
        # spurious sister fallback (M←S), which is wrong precisely where
        # the dashed curve diverges from the solid one (the field edge).
        # Dilating leaves presence False only past the curve's true
        # extent, where sister fallback is genuinely warranted.
        solid_sm, dashed_sm = ("M", "S") if profile.dashed_is_sagittal else ("S", "M")
        freq_by_color = dict(zip(unique_named_hues(profile), profile.frequencies_lpmm))
        bridge = cv2.getStructuringElement(
            cv2.MORPH_RECT, (_DASH_PRESENCE_BRIDGE_W, 3)
        )
        for color_name, mask in curve_masks.items():
            split = split_sm_by_cc_width(close_and_skeletonize(mask))
            freq = freq_by_color[color_name]
            # Solid line is continuous — its own skeleton is the presence
            # signal. Dashed line is bridged so a dash within ~half a mm
            # of the field edge still marks the edge sample present; the
            # DP path holds the curve's real value there, whereas sister
            # fallback would wrongly copy the (diverging) solid value.
            for sm, sub in (
                (solid_sm, split.sagittal),
                (dashed_sm, cv2.dilate(split.meridional.astype(np.uint8), bridge)),
            ):
                out[curve_field(freq, sm)] = sub
    elif profile.style_axis == "SPLIT_BY_DASH" and profile.dashed_split_presence:
        # Single-hue B&W multifreq chart (Zeiss Touit): one neutral mask
        # holds all 2N curves, separated only by y-band (frequency) and
        # solid/dashed (S/M). There is no per-frequency hue to key on as
        # in the GEODESIC_DP branch above, so split the whole neutral mask
        # once into its solid (S) and dashed (M) sub-skeletons and
        # broadcast each across every frequency. This is a coarse
        # per-column presence signal — presence[freqNS] reads True where
        # ANY solid curve has ink at that column — but the sister fallback
        # fill VALUE still comes from the correctly band-assigned per-field
        # sample, so a dashed curve that merges into its solid sibling in
        # the interior is recovered from that sibling, while a diverging
        # corner (sibling sample None) copies nothing. See #1347.
        solid_sm, dashed_sm = ("M", "S") if profile.dashed_is_sagittal else ("S", "M")
        bridge = cv2.getStructuringElement(
            cv2.MORPH_RECT, (_DASH_PRESENCE_BRIDGE_W, 3)
        )
        for mask in curve_masks.values():  # one neutral hue
            split = split_sm_by_cc_width(close_and_skeletonize(mask))
            for sm, sub in (
                (solid_sm, split.sagittal),
                (dashed_sm, cv2.dilate(split.meridional.astype(np.uint8), bridge)),
            ):
                for freq in profile.frequencies_lpmm:
                    out[curve_field(freq, sm)] = sub
    elif profile.style_axis == "HUE_IS_CURVE" and profile.hue_meaning == "CURVE_IDENTITY":
        # Each hue identifies one specific (frequency, S/M) curve via its
        # name (e.g. `10S-red`, `10M-pink`, `30S-dark-grey`,
        # `30M-light-grey`). Map each hue mask to its single (freq, sm)
        # field. Wired (#1216) so sister fallback can fire on Samyang
        # when halo subtraction leaves a contaminated hue's mask empty
        # at high-MTF overlap points.
        for hue_name, mask in curve_masks.items():
            freq, sm = parse_curve_identity_name(hue_name)
            out[curve_field(freq, sm)] = mask
    elif profile.style_axis == "HUE_IS_CURVE" and profile.hue_meaning in (
        "SAGITTAL_MERIDIONAL", "SAGITTAL_MERIDIONAL_SINGLE_FREQ",
        "GEODESIC_DP",
    ):
        # Each hue carries one S or M label (e.g. "S-red", "M-blue"); the
        # same hue feeds every frequency this profile declares. Write the
        # raw mask into the presence-mask dict under each (freq, sm) field.
        # For SAGITTAL_MERIDIONAL_SINGLE_FREQ profiles the loop runs once
        # (one frequency per image, set per-call by the multipath
        # orchestrator).
        for hue_name, mask in curve_masks.items():
            sm = hue_name[0]  # "S" or "M"
            for freq in profile.frequencies_lpmm:
                out[curve_field(freq, sm)] = mask
    # Other dialects: presence check falls back to the skeleton itself
    # (legacy behaviour). The caller treats missing keys as "no
    # presence info — trust whatever value the sampler returned."
    return out


def extract_chart(
    image_path: str | Path,
    profile: MtfProfile,
    plot_box: PlotBox,
    image_height_mm: float,
    *,
    diagnostic_sink: "DiagnosticSink | None" = None,
) -> ExtractedChart:
    """End-to-end MTF extraction for one chart image.

    Returns 11 `SampledReading` rows (one per fixed sample point).
    Two post-extraction corrections are applied: sister fallback when
    a curve has no ink at a fraction, and center symmetry forcing S=M
    at fraction 0.0 by physics.

    Raises `NotImplementedError` for profile (style_axis, hue_meaning)
    combinations not yet wired by `dispatch.field_skeletons()`.

    When `diagnostic_sink` is supplied, every pipeline stage records
    its output via the sink (ADR-050). Extraction values are byte-
    identical with or without the sink; only side-effect output
    differs.
    """
    bgr = load_chart_bgr(image_path)
    if diagnostic_sink is not None:
        diagnostic_sink.record_source(bgr)
        diagnostic_sink.record_plotbox(bgr, plot_box)
        # Per-hue raw masks. Recorded for ADR-050 stage 03.
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        for name, mask in masks_by_curve_name(hsv, profile).items():
            diagnostic_sink.record_hue_mask(name, mask)

    skeletons = field_skeletons(bgr, profile, plot_box)
    if diagnostic_sink is not None:
        for field, skel in skeletons.items():
            diagnostic_sink.record_skeleton(field, skel, bgr)

    # Re-derive per-field raw masks for two uses: (1) tight-window
    # raw-centroid snapping at sample time (restores pixel-accuracy
    # on solid strokes), (2) wider-window ink-presence check for the
    # sister fallback. Cheap — HSV + range threshold on the chart.
    presence_masks = _hue_masks_for_presence(bgr, profile, plot_box)
    if diagnostic_sink is not None:
        for field, mask in presence_masks.items():
            diagnostic_sink.record_presence_mask(field, mask)

    samples_per_field: dict[str, tuple[float | None, ...]] = {
        field: _sample_curve(skel, plot_box, raw_mask=presence_masks.get(field))
        for field, skel in skeletons.items()
    }
    # Seed an all-None row for any field that has a presence mask but no
    # skeleton (#1347). A dashed curve that merges into its solid sibling
    # and is lost to the coverage floor produces no track, so it is absent
    # from `skeletons` entirely — and sister fallback only visits fields
    # present in `samples_per_field`. Seeding it here (scoped to the
    # split-presence profiles) lets the M<-S fallback fill it from the
    # solid sibling. Harmless for other profiles: their presence keys map
    # 1:1 to skeletons, so nothing is seeded.
    if profile.dashed_split_presence:
        for field in presence_masks:
            samples_per_field.setdefault(field, (None,) * len(SAMPLE_FRACTIONS))
    samples_before_fallback = {f: v for f, v in samples_per_field.items()}

    # Sister fallback: replace samples where the raw ink is absent
    # with the sister curve's value. Presence masks come from the
    # per-hue raw masks for most profiles, but for HUE_IS_CURVE /
    # GEODESIC_DP the raw hue mask carries BOTH frequencies of one
    # color (e.g. M-blue is freq10M and freq30M), making it useless
    # as a per-curve presence signal at the right edge — the freq30M
    # curve may have ended in pure-white space while freq10M's ink at
    # the same column still marks "present." For those fields, use the
    # per-field DP-derived skeleton instead (#1215): its trimmed right
    # edge encodes "this curve doesn't extend here," so sister fallback
    # honours the trim and leaves the cell None rather than copying a
    # diverging sister value.
    fallback_presence_masks = _per_field_presence_for_fallback(
        presence_masks, skeletons, profile
    )
    presence = (
        _ink_presence_per_field(fallback_presence_masks, plot_box)
        if fallback_presence_masks
        else {}
    )
    # Trim-aware profiles use the DP skeleton (#1215) for the presence
    # signal — its right-edge trim is an authoritative "no curve here"
    # verdict that sister fallback must respect.
    presence_authoritative = (
        profile.style_axis == "HUE_IS_CURVE"
        and profile.hue_meaning == "GEODESIC_DP"
    )
    fallback_count: dict[str, int] = {}
    sister_filled: dict[str, tuple[bool, ...]] = {}
    if presence:
        samples_per_field, fallback_count, sister_filled = _apply_sister_fallback(
            samples_per_field, presence,
            presence_is_authoritative=presence_authoritative,
        )
    # Intra-curve interpolation pass (#1254): for single-column sister-
    # filled cells whose neighbours are NOT sister-filled, interpolate
    # within the field's own curve. Sister fallback's S~=M assumption
    # fails at mid-field when S and M diverge by 0.2+ MTF (Samyang 85mm
    # stopped 30S flat at 0.97 while 30M sweeps 0.95->0.55); continuity
    # within one optical curve is the stronger prior.
    if sister_filled:
        samples_per_field, intra_interp_count = (
            _replace_sister_fills_with_intra_interp(
                samples_per_field, sister_filled,
            )
        )
    # Coincident-top anchor (#1269): override sister-filled higher-
    # frequency cells with the matching lower-frequency value when the
    # lower curve is pinned at MTF >= 0.95 — the chart artist merged
    # two near-1.0 strokes into one visible line, and the sister-fill
    # from the diverging M curve underestimates the true high-freq S
    # by a large margin.
    #
    # Skipped for `dashed_split_presence` profiles (#1347): the Touit's
    # frequency bands are drawn as separate y-bands, never coincident at
    # the top (10/20/40 sit ~0.06-0.14 MTF apart on every panel), so the
    # anchor's merged-stroke assumption never holds. With split-mask
    # sister presence now filling the dashed M curves from their correct
    # same-frequency S sibling, letting the anchor run would wrongly
    # overwrite a good same-freq fill (e.g. 20M 0.90) with the lower
    # frequency (10M 0.96) whenever both are sister-filled and no clean
    # cell exists to veto the pair.
    coincident_anchor_count: dict[str, int] = {}
    if sister_filled and not profile.dashed_split_presence:
        samples_per_field, coincident_anchor_count = (
            _apply_coincident_top_anchor(samples_per_field, sister_filled)
        )
    samples_after_fallback = {f: v for f, v in samples_per_field.items()}
    samples_per_field, center_anchor_count = _apply_center_symmetry(
        samples_per_field
    )

    if diagnostic_sink is not None:
        readings_for_sampling = _readings_to_dict(
            samples_before_fallback, plot_box, image_height_mm
        )
        diagnostic_sink.record_sampling(
            readings_for_sampling, bgr, plot_box, image_height_mm
        )
        diagnostic_sink.record_fallback(
            samples_before_fallback, samples_after_fallback, fallback_count
        )
        diagnostic_sink.record_symmetry(samples_after_fallback, samples_per_field)
        # `FileDiagnosticSink` carries extra visual-diff methods that
        # need bgr/plot_box — `DiagnosticSink` Protocol does not
        # require them. Call them duck-typed if present.
        for name, before, after in (
            ("record_fallback_visual", samples_before_fallback, samples_after_fallback),
            ("record_symmetry_visual", samples_after_fallback, samples_per_field),
        ):
            method = getattr(diagnostic_sink, name, None)
            if method is not None:
                method(before, after, bgr, plot_box, image_height_mm)

    return ExtractedChart(
        source_path=str(image_path),
        profile_name=profile.name,
        plot_box=plot_box,
        image_height_mm=image_height_mm,
        readings=_readings_to_dict(samples_per_field, plot_box, image_height_mm),
        sister_fallback_count=fallback_count,
        center_anchor_count=center_anchor_count,
        coincident_anchor_count=coincident_anchor_count,
    )
