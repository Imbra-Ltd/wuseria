"""FREQUENCY_PER_HUE_RIDGE dispatch entry point (ADR-083)."""

from __future__ import annotations

import numpy as np

from ..types import PlotBox
from .dp import (
    _detect_and_swap_at_crossings,
    _path_mask_continuity,
    _path_to_track,
    _ridge_dp_two_paths,
    _ridges_by_column,
    _swap_after_rightmost_convergence,
)
from .foundation import (
    _column_run_count,
    _densify_track,
    _extend_track_to_plot_edges,
    _extract_ridge_points,
    _fill_coincident_column_gaps_extending,
    _filter_isolated_ridge_points,
    _rasterize,
    _strip_chrome,
)


def ridge_tracks_for_hue_freq_split(
    mask: np.ndarray,
    plot_box: PlotBox,
    freq: int,
    dashed_is_sagittal: bool,
    use_y_anchor: bool = False,
    force_sm_swap: bool = False,
) -> dict[str, np.ndarray]:
    """Per-hue, 2-curve variant for SPLIT_BY_DASH families: each hue
    carries one frequency with both S (solid) and T (dashed) curves.

    Used by TTartisan max-aperture (#1085): the raw black mask fuses
    solid S10 and dashed T10 antialiased halos into one connected
    component when the curves run within ~5 px of each other. The
    skeleton + CC-width split then assigns most of the fused blob to S
    and leaves only the small non-fused dashed fragments as M, missing
    most of the T curve. Per-column ridge centroids preserve two
    distinct tracks at coincidence; the top-2 by coverage are S+T.

    Higher-coverage track is solid (S by default; M when
    `dashed_is_sagittal=True`, the 7Artisans/TTartisan-T convention).
    When only one track qualifies, both fields share its value (whole-
    curve coincidence — a shared ridge is attributed to both curves,
    the same B4 physics as at center).

    Partial-field coincidence (#1095): when the two physical curves
    coincide over part of the field (e.g. left half) and diverge over
    the rest (e.g. right half), the greedy clusterer assigns the
    coincidence-region ridges to ONE track. The other track only
    receives points from the divergent region. Without remediation,
    the absent track's rasterization is empty across the coincidence
    region — the sampler then reads neighbouring ink from the present
    track for both fields, mixing the two curves. The fix:
    `_fill_coincident_column_gaps_extending` shares single-ridge
    column values into the absent track when the present value is
    continuous with the absent track's nearest endpoint, attributing
    the coincidence-region values to both curves as the B4 physics
    requires.

    Distinct from `ridge_tracks_to_fields`: that variant takes a single
    neutral mask carrying all four curves; tracks ranked by mean_y for
    frequency, then by coverage within each frequency pair for S/M.
    """
    from ..dispatch import curve_field  # imported here to avoid module cycle

    cleaned = _strip_chrome(mask, plot_box)
    points = _extract_ridge_points(cleaned, plot_box)
    # Drop isolated 1-2 column blobs (gridline fragments, mid-air noise)
    # before the DP picks them as a ridge path. See #1157.
    points = _filter_isolated_ridge_points(points)

    # Per-column ridge DP (#1100): two coherent paths through the ridge
    # set, preserving curve identity through crossings. Replaces the
    # greedy clusterer + top-N + diversity-picker chain that the
    # frankenstein corner-crossing failure mode came from.
    ridges_by_col = _ridges_by_column(points, plot_box)
    (p1_path, p1_on_ridge), (p2_path, p2_on_ridge) = _ridge_dp_two_paths(
        ridges_by_col, use_y_anchor=use_y_anchor
    )
    track1 = _path_to_track(p1_path, p1_on_ridge, plot_box)
    track2 = _path_to_track(p2_path, p2_on_ridge, plot_box)

    # Crossing detection (#1170): when one physical curve dives then
    # rises through the other, the two DP paths exchange physical
    # identity at the crossing column. Swap right-of-crossing
    # assignments so each output track follows one physical curve
    # end-to-end. No-op when the tracks never converge (parallel),
    # when only one is present, or when both pass through each other
    # without slope reversal (tilt-50-style X-crossing).
    if track1 is not None and track2 is not None:
        track1, track2 = _detect_and_swap_at_crossings(track1, track2)

    solid_sm, dashed_sm = ("M", "S") if dashed_is_sagittal else ("S", "M")
    out: dict[str, np.ndarray] = {}
    if track1 is None:
        return out
    if track2 is None or track2.coverage < 10:
        # Whole-hue coincidence: only one path found. Same value to
        # both fields — the B4 center-astigmatism physics: a coincident
        # ridge is shared across both curves, not fabricated.
        shared = _extend_track_to_plot_edges(_densify_track(track1), plot_box)
        out[curve_field(freq, solid_sm)] = _rasterize(shared, mask.shape)
        out[curve_field(freq, dashed_sm)] = _rasterize(shared, mask.shape)
        return out

    # S/M labeling on coherent paths: solid lines have ink at almost
    # every column the DP could lock onto; dashed lines have the DP
    # only catching the dash centroids. `Track.coverage` (count of
    # on-ridge columns post-`_path_to_track`) reflects this directly.
    #
    # Use coverage as the primary discriminator: the path with more
    # on-ridge columns is solid. When coverage ties, fall back to
    # `_path_mask_continuity` (in-range ink density) as tiebreaker.
    #
    # Earlier (#1100) used continuity as primary. It misfired on af-75
    # stopped freq30 (#1171 follow-up): the chart's dashed M30 curve
    # stays flat through midfield and dives only at the corner. Its DP
    # path locks onto every column (high continuity). The solid S30
    # curve dives steeply through midfield then rises at the corner;
    # the DP only catches the rise (partial coverage). Continuity
    # scored the dashed M30 higher and mislabeled S↔M. Coverage tracks
    # which path the DP could keep anchored on real ridges across the
    # full plot, which is the cleaner signal for solid-vs-dashed.
    if track1.coverage > track2.coverage:
        solid_track_raw, dashed_track_raw = track1, track2
    elif track2.coverage > track1.coverage:
        solid_track_raw, dashed_track_raw = track2, track1
    else:
        cont1 = _path_mask_continuity(track1, cleaned)
        cont2 = _path_mask_continuity(track2, cleaned)
        if cont1 >= cont2:
            solid_track_raw, dashed_track_raw = track1, track2
        else:
            solid_track_raw, dashed_track_raw = track2, track1

    # Per-lens label override (#1199). When the discriminator picks
    # the wrong solid track AND the two tracks come close in y at
    # least once (the af-35 case: dy=6 at frac 0.95 before the final
    # corner spread), the swap is restricted to columns AT and AFTER
    # the rightmost near-crossing column. Without that restriction a
    # whole-track swap fixes the corner but breaks every column where
    # the DP already had the labels right (most of the curve).
    #
    # The existing `_detect_and_swap_at_crossings` does the same
    # rightward-swap but requires BOTH tracks' slopes to reverse,
    # which fails on af-35 because the dashed M30 is smooth and
    # monotone — only the solid S30 reverses (and its rebound is too
    # narrow to register in the slope window). The per-lens override
    # bypasses the slope check: the maintainer has already
    # eye-confirmed the swap from GT.
    #
    # When no near-crossing candidate exists (tracks are well-
    # separated end-to-end), fall back to a whole-track swap — the
    # situation is then just a discriminator failure with no
    # mid-curve identity flip.
    if force_sm_swap:
        solid_track_raw, dashed_track_raw = _swap_after_rightmost_convergence(
            solid_track_raw, dashed_track_raw
        )

    column_runs = _column_run_count(cleaned, plot_box)
    shared_solid, shared_dashed = _fill_coincident_column_gaps_extending(
        solid_track_raw, dashed_track_raw, column_runs
    )
    solid_track = _extend_track_to_plot_edges(
        _densify_track(shared_solid), plot_box
    )
    dashed_track = _extend_track_to_plot_edges(
        _densify_track(shared_dashed), plot_box
    )
    out[curve_field(freq, solid_sm)] = _rasterize(solid_track, mask.shape)
    out[curve_field(freq, dashed_sm)] = _rasterize(dashed_track, mask.shape)
    return out

