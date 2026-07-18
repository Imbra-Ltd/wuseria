"""RIDGE_TRACKING multi-frequency field assignment (ADR-083)."""

from __future__ import annotations

import numpy as np

from ..types import PlotBox
from .foundation import (
    Track,
    _cluster_into_tracks,
    _extract_ridge_points,
    _rasterize,
    _select_top_n_tracks,
    _strip_chrome,
)


# #1385: fraction of plot width (from the left) whose tracks seed the
# frequency bands under left-anchored assignment. At the left plot edge
# (u' = 0, on-axis) sagittal and meridional MTF are identical by
# rotational symmetry, so an N-frequency panel shows exactly N distinct
# curve anchors there and every continuous (solid) curve reaches it.
# Sized from the S209 kept-track probe across the six Touit panels: all
# solid band anchors enter at frac 0.0; dashed/dotted second curves
# enter at frac 0.1-0.2 and are correctly grouped either as seeds or as
# entrants for any window in [0.10, 0.25]. 0.15 keeps the seed set
# close to the physics anchor.
_LEFT_ANCHOR_WINDOW_FRACTION: float = 0.15

# #1385: how many columns past a track's entry x contribute to its
# entry-point y. One dash of the Touit dashed/dotted rendering spans
# ~6-12 px, so 10 columns average roughly one dash without reaching
# into the curve's downstream slope.
_ENTRY_PROBE_COLUMNS: int = 10


def _track_entry_x(track: Track) -> int:
    """Leftmost x-column the track occupies."""
    return min(x for x, _ in track.points)


def _entry_y(track: Track) -> float:
    """Mean y of the track's first `_ENTRY_PROBE_COLUMNS` columns."""
    x0 = _track_entry_x(track)
    ys = [y for x, y in track.points if x <= x0 + _ENTRY_PROBE_COLUMNS]
    return float(np.mean(ys))


def _nearest_y_at_x(band: list[Track], x_target: int) -> float:
    """Y of the band-member point whose x is nearest `x_target`.

    The band's curves never cross another band's, so the member point
    closest in x is a faithful local reference for "where this band is"
    at an entrant's entry column, even when every member is dashed.
    """
    best_dx = None
    best_y = 0.0
    for track in band:
        for x, y in track.points:
            dx = abs(x - x_target)
            if best_dx is None or dx < best_dx:
                best_dx = dx
                best_y = y
    return best_y


def _segment_sse(values: list[float], lo: int, hi: int) -> float:
    """Sum of squared deviations of `values[lo:hi]` about their mean."""
    segment = values[lo:hi]
    mean = sum(segment) / len(segment)
    return sum((v - mean) ** 2 for v in segment)


def _optimal_1d_kmeans_bounds(values: list[float], k: int) -> list[tuple[int, int]]:
    """Partition ascending `values` into `k` contiguous groups that
    minimize total within-group SSE (optimal 1-D k-means / Jenks
    natural breaks via dynamic programming).

    Returns `k` `(lo, hi)` index slices covering `values` in order.
    Requires `1 <= k <= len(values)`; each returned group is non-empty.

    Unlike an "N-1 largest gaps" split, the min-variance objective does
    not break when the largest gap falls *within* a band -- on flat or
    converged panels an S/M pair can spread wider than the frequency
    spacing, and gap-splitting then mis-groups them (the reason spike
    attempt 1 for #1347 was rejected). k-means keeps the tight pair
    together.
    """
    n = len(values)
    inf = float("inf")
    # dp[j][i] = min total SSE partitioning the first i values into j groups.
    dp = [[inf] * (n + 1) for _ in range(k + 1)]
    split_at = [[0] * (n + 1) for _ in range(k + 1)]
    dp[0][0] = 0.0
    for j in range(1, k + 1):
        for i in range(j, n + 1):
            for p in range(j - 1, i):
                cost = dp[j - 1][p] + _segment_sse(values, p, i)
                if cost < dp[j][i]:
                    dp[j][i] = cost
                    split_at[j][i] = p
    bounds: list[tuple[int, int]] = []
    i = n
    for j in range(k, 0, -1):
        p = split_at[j][i]
        bounds.append((p, i))
        i = p
    bounds.reverse()
    return bounds


# #1374: relative coverage margin for the within-band dashedness
# discriminator. Calibrated against the six Touit reference panels
# (probe, S208): genuine solid/dashed pairs contrast at >= 1.39x ridge
# coverage (e.g. 425/299, 418/300, 533/89), while coincident or
# same-style pairs sit at <= 1.03x (342/333 on the 32mm max 40-band,
# 562/560 on the 50mm max 10-band). 1.15 sits in the gap with room on
# both sides; below it the y-order fallback preserves prior behavior.
_BAND_SM_COVERAGE_MARGIN: float = 1.15


def _order_band_sm(
    by_y: list[Track],
    sm_by_coverage: bool,
    dashed_is_sagittal: bool,
) -> tuple[Track, Track | None]:
    """Order a frequency band's y-sorted tracks into (S, M).

    Default: the upper track (smaller y) is S, the next is M — the
    family-typical layout. When `sm_by_coverage` is set and the band
    holds exactly two tracks whose ridge coverage differs by at least
    `_BAND_SM_COVERAGE_MARGIN`, the higher-coverage track is the solid
    curve instead (dashes leave ridge columns empty), labeled per
    `dashed_is_sagittal`. Zeiss Touit 32mm f/1.8 GT (#1332) refutes the
    y-order assumption: the dashed M runs ABOVE solid S from ~3 mm
    outward at 10/20 lp/mm (#1374). Under the margin (coincident pairs,
    the #791 cluster-collapse bands) the y-order fallback keeps prior
    behavior. Bands with three or more tracks always use y-order — the
    extra track is a cluster-collapse symptom, out of scope here.
    """
    if len(by_y) == 1:
        return by_y[0], None
    if sm_by_coverage and len(by_y) == 2:
        hi, lo = sorted(by_y, key=lambda t: t.coverage, reverse=True)
        if hi.coverage >= _BAND_SM_COVERAGE_MARGIN * max(lo.coverage, 1):
            return (lo, hi) if dashed_is_sagittal else (hi, lo)
    return by_y[0], by_y[1]


def _assign_left_anchored_bands(
    kept: list[Track],
    frequencies_lpmm: tuple[int, ...],
    plot_box: PlotBox,
    mask_shape: tuple[int, int],
    sm_by_coverage: bool,
    dashed_is_sagittal: bool,
) -> dict[str, np.ndarray] | None:
    """Assign kept tracks to (frequency, S/M) fields anchored at the
    left plot edge (#1385, superseding the #1347 interior k-means).

    Two chart-physics invariants drive the assignment. At u' = 0 the
    sagittal and meridional MTF coincide, so the left edge shows exactly
    one anchor per frequency; and frequency bands never cross (a lower
    lp/mm curve stays above a higher one at every field position), so a
    track entering mid-field belongs to whichever band is nearest at
    its entry column.

    Steps: tracks reaching the left window seed the bands (optimal 1-D
    k-means on their left-window y, k = N); the remaining tracks join,
    in entry-x order, the band whose nearest member point at their
    entry is closest in y. Bands map top->bottom onto the
    (upper->lower) frequency order. Within each band `_order_band_sm`
    assigns S/M (#1374); a band holding more than two tracks keeps the
    two highest-coverage ones; a band left with one track reports S
    only -- the coincident-pair case -- and the sampler/sister fallback
    treats the absent M per the B2 contract.

    Returns None when fewer than N tracks reach the left window (no
    anchor per band); the caller falls back to the equal split.

    Band populations are genuinely unbalanced on these panels -- the
    S209 kept-track probe (#1385) measured 1/2/2 on the 32mm/50mm
    stopped panels (the 10-pair prints coincident, GT delta <= 0.01)
    and 1/2/3 on the 50mm max panel (fused 10-pair plus a fragmented
    40-band). A count-based equal split cannot represent that, and
    interior-mean-y k-means picks the wrong partition when a band's
    S/M spread exceeds the gap between adjacent bands (50mm stopped:
    grouping 10+20S+20M costs SSE 326 vs 344.5 for the true split).
    Anchoring at the left edge sidesteps both failure modes.
    """
    from ..dispatch import curve_field  # imported here to avoid module cycle

    n_freqs = len(frequencies_lpmm)
    x_cut = plot_box.x_left + _LEFT_ANCHOR_WINDOW_FRACTION * plot_box.width

    seeds = [t for t in kept if _track_entry_x(t) <= x_cut]
    if len(seeds) < n_freqs:
        return None

    def seed_y(track: Track) -> float:
        return float(np.mean([y for x, y in track.points if x <= x_cut]))

    seeds.sort(key=seed_y)
    bounds = _optimal_1d_kmeans_bounds([seed_y(t) for t in seeds], n_freqs)
    bands: list[list[Track]] = [list(seeds[lo:hi]) for lo, hi in bounds]

    entrants = sorted(
        (t for t in kept if _track_entry_x(t) > x_cut), key=_track_entry_x
    )
    for track in entrants:
        entry_x = _track_entry_x(track)
        entry_y = _entry_y(track)
        nearest = min(bands, key=lambda b: abs(_nearest_y_at_x(b, entry_x) - entry_y))
        nearest.append(track)

    out: dict[str, np.ndarray] = {}
    for band, freq in zip(bands, frequencies_lpmm):
        if len(band) > 2:
            band = sorted(band, key=lambda t: t.coverage, reverse=True)[:2]
        by_y = sorted(band, key=lambda t: t.mean_y)
        s_track, m_track = _order_band_sm(by_y, sm_by_coverage, dashed_is_sagittal)
        out[curve_field(freq, "S")] = _rasterize(s_track, mask_shape)
        if m_track is not None:
            out[curve_field(freq, "M")] = _rasterize(m_track, mask_shape)
    return out


def ridge_tracks_to_fields_multifreq(
    mask: np.ndarray,
    plot_box: PlotBox,
    frequencies_lpmm: tuple[int, ...],
    dashed_is_sagittal: bool,
    interior_anchored: bool = False,
    sm_by_coverage: bool = False,
) -> dict[str, np.ndarray]:
    """Ridge-track a single-hue mask and return per-field skeleton masks
    for an N-frequency chart.

    The 2N-curve layout: the kept tracks (by mean y) split into N
    equal-sized y-bands. Each band maps to one frequency in upper→lower
    order. Within each band S/M is assigned by `_order_band_sm`: y-order
    by default (top track is S), or coverage dashedness when the
    profile opts in via `sm_by_coverage` (#1374). Fields without a
    qualifying track are absent from the result; the sampler treats
    them as missing data (B2 contract).

    `frequencies_lpmm` MUST be passed in upper→lower screen order,
    which by convention is also low→high lp/mm (a 3-freq Zeiss
    Touit chart prints 10 on top, 20 in the middle, 40 at the bottom).

    When `interior_anchored` is set (multifreq-press-kit profiles,
    #1347/#1385), the kept tracks are assigned to frequency bands by
    `_assign_left_anchored_bands` instead of the global-mean-y
    equal-size split. The equal split assumes every band kept the same
    track count, which coincident pairs and fragmented curves refute
    (see that function's docstring); the left edge of the plot carries
    one anchor per frequency by on-axis S/M symmetry, so anchoring
    there stays correct when band populations are unbalanced.
    """
    from ..dispatch import curve_field  # imported here to avoid module cycle

    if not frequencies_lpmm:
        raise ValueError("ridge_tracks_to_fields_multifreq: empty frequencies_lpmm")

    n_freqs = len(frequencies_lpmm)
    expected_tracks = 2 * n_freqs

    cleaned = _strip_chrome(mask, plot_box)
    points = _extract_ridge_points(cleaned, plot_box)
    tracks = _cluster_into_tracks(points)
    kept = _select_top_n_tracks(
        tracks, n=expected_tracks, plot_width=plot_box.width + 1
    )

    if not kept:
        return {}

    # Within a frequency pair the S curve typically runs above M
    # (edge MTF degrades faster on the meridional axis), so y-order is
    # the default S/M assignment. It is NOT universal physics: the
    # Zeiss Touit 32mm f/1.8 GT (#1332) shows dashed M above solid S
    # from ~3 mm outward, so `sm_by_coverage` profiles discriminate by
    # ridge coverage instead (#1374). For all-dashed families (Viltrox)
    # coverage carries no solid/dashed signal — they keep the default.

    # Left-anchored band assignment (#1385, superseding the #1347
    # interior k-means). Applies whenever the profile opts in and at
    # least n_freqs tracks exist -- unconditionally, not only when
    # kept < 2N: the 50mm max panel keeps 6 tracks yet its true band
    # populations are 1/2/3 (fused 10-pair, fragmented 40-band), so
    # a full kept set does not imply the equal split is safe. Falls
    # through to the equal split when fewer than N tracks reach the
    # left window (no anchor per band).
    if interior_anchored and len(kept) >= n_freqs:
        anchored = _assign_left_anchored_bands(
            kept,
            frequencies_lpmm,
            plot_box,
            mask.shape,
            sm_by_coverage,
            dashed_is_sagittal,
        )
        if anchored is not None:
            return anchored

    kept_sorted = sorted(kept, key=lambda t: t.mean_y)

    # Split kept tracks into N equal-size y-bands. When the kept count is
    # below 2N, the last band absorbs the remainder so the highest
    # frequency reports what data exists rather than silently dropping
    # it. Profiles with unbalanced band populations (coincident pairs,
    # fragmented curves) opt into left-anchored assignment above; this
    # split remains for the 2-frequency ridge families (Viltrox).
    base = len(kept_sorted) // n_freqs
    remainder = len(kept_sorted) - base * (n_freqs - 1)

    out: dict[str, np.ndarray] = {}
    cursor = 0
    for band_index, freq in enumerate(frequencies_lpmm):
        is_last = band_index == n_freqs - 1
        take = remainder if is_last else base
        if take <= 0:
            continue
        band = kept_sorted[cursor : cursor + take]
        cursor += take
        by_y = sorted(band, key=lambda t: t.mean_y)
        s_track, m_track = _order_band_sm(by_y, sm_by_coverage, dashed_is_sagittal)
        out[curve_field(freq, "S")] = _rasterize(s_track, mask.shape)
        if m_track is not None:
            out[curve_field(freq, "M")] = _rasterize(m_track, mask.shape)

    return out


def ridge_tracks_to_fields(
    mask: np.ndarray,
    plot_box: PlotBox,
    upper_freq: int,
    lower_freq: int,
    dashed_is_sagittal: bool,
) -> dict[str, np.ndarray]:
    """Two-frequency wrapper around `ridge_tracks_to_fields_multifreq`.

    Preserved for the Viltrox dispatch site and its tests. New callers
    SHOULD use `ridge_tracks_to_fields_multifreq` with an explicit
    frequency tuple.
    """
    return ridge_tracks_to_fields_multifreq(
        mask,
        plot_box,
        frequencies_lpmm=(upper_freq, lower_freq),
        dashed_is_sagittal=dashed_is_sagittal,
    )
