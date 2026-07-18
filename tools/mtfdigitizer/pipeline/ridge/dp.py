"""Per-column ridge Viterbi DP and crossing detection (ADR-083)."""

from __future__ import annotations

import numpy as np

from ..types import PlotBox
from .foundation import Track


# --- Per-column ridge DP (#1100) -----------------------------------------
#
# Greedy clustering (`_cluster_into_tracks`) is column-walk-with-nearest-y:
# decisive locally but blind to curve identity across crossings. When two
# physical curves cross within a few pixels of each other (TTartisan grey
# freq30 at x≈585), the upper-history track picks up the now-upper ridge —
# even though that ridge is actually the OTHER physical curve diving up
# while the first curve continues into a different y band.
#
# Mask-based DP (`extract_two_curves_dp`) is the natural fix but documented
# blind spot #1044 fires on the exact TTartisan pattern: when one curve
# dives steeply while a parallel curve stays at higher MTF, the Viterbi
# prefers the smoother (flat) path through the dilation echo and loses the
# dive. The dilation that bridges dash gaps also bridges the dive-vs-flat
# distinction.
#
# Per-column ridge DP avoids both. Input is the per-column ridge centroids
# already computed by `_extract_ridge_points` — sparse, no dilation, no
# mask-vs-echo ambiguity. DP picks one ridge per column for each of two
# paths; the smoothness prior penalises identity-swaps; when only one
# ridge exists at a column the paths share it (curve coincidence — same
# B4 generalisation `_fill_coincident_column_gaps_extending` handles).
#
# Tuning: alpha (smoothness weight) reused from `dp_extract.py` — same
# trade-off shape, same reference-set calibration applies.


# Smoothness weight: per-column cost is `_RIDGE_DP_ALPHA * |dy|`. Carried
# over from `dp_extract._ALPHA` (Tokina reference-set calibration).
_RIDGE_DP_ALPHA: float = 0.30

# Fixed cost added when a path coasts past a column whose ridges are
# all far from its anchor (#1104). Lets pass 1 skip a lone lower-band
# ridge instead of being forced to land on it. Picked small enough that
# coasting beats jumping across a ~30 px gap (the 7artisans corner mode)
# but large enough that coasting NEVER beats landing on a ridge that
# matches the path's anchor (anchor cost ≈ 0 on a clean landing). Only
# affects passes that supply an `anchor`; without one the coast option
# is never cheaper than landing on a candidate.
_RIDGE_DP_OFF_RIDGE_PENALTY: float = 4.0

# After pass 1 finds the best path, pass 2 erases ridges within this
# vertical half-window of pass 1's path at each column (so pass 2 finds
# a different curve). Sized to admit the case where two curves run ~5px
# apart for part of the field (the second curve's ridge falls outside
# the erase window even at near-coincidence).
_RIDGE_DP_ERASE_HALF: int = 2

# Y-band coherence weight (#1104). Per-column cost adds
# `_RIDGE_DP_GAMMA * |y - anchor[col]|` when the path has an anchor.
# Each anchor is a smoothed approximation of where one curve sits;
# the cost pulls the DP toward its own anchor and away from the
# other path's band when both have valid candidates at a column.
#
# Sized so a 30px swap (the 7artisans freq10 corner mode) costs
# ~6.0 in anchor deviation per column — enough to dominate the
# 0.30*|dy| smoothness cost (max 3.0 for a 10px jump) so the DP
# rejects swaps but still picks the closer candidate when both
# anchors agree (single-ridge / coincidence columns).
_RIDGE_DP_GAMMA: float = 0.20



def _ridges_by_column(
    points: list[tuple[int, float]], plot_box: PlotBox
) -> list[list[float]]:
    """Group ridge points by column index relative to ``plot_box.x_left``.

    Returns one list per column in ``[plot_box.x_left, plot_box.x_right]``;
    each entry is the sorted list of ridge y-values at that column (may
    be empty when no ridges were detected there).
    """
    width = plot_box.x_right - plot_box.x_left + 1
    by_x: list[list[float]] = [[] for _ in range(width)]
    for x, y in points:
        col = x - plot_box.x_left
        if 0 <= col < width:
            by_x[col].append(y)
    for col_ys in by_x:
        col_ys.sort()
    return by_x


def _compute_y_anchors(
    ridges_by_col: list[list[float]],
) -> tuple[list[float | None], list[float | None]]:
    """Compute per-column y anchors for the upper and lower curves (#1104).

    For each column with exactly two ridges, the smaller y is taken as
    the upper-curve seed and the larger y as the lower-curve seed
    (image-y grows downward, so smaller y = higher MTF). Columns with
    1 ridge (dash gaps, coincidence) or 3+ ridges (contaminated by
    gridline echoes or other-curve halos) contribute no seed — they
    inherit the most recent known anchor via forward/backward fill.

    The anchor is intentionally NOT box-smoothed: a smoothing window
    flattens legitimate local features (e.g. the TTartisan freq30
    corner dive that spans ~30 columns) just as easily as it cancels
    noise. The inner DP's smoothness term already supplies the
    column-to-column smoothness; the anchor's job is to encode curve
    identity, not to be smooth.

    Returns ``(upper, lower)``, each of length ``len(ridges_by_col)``.
    Entries are ``None`` only when there are no two-ridge columns
    anywhere in the input.
    """
    n = len(ridges_by_col)
    upper_raw: list[float | None] = [None] * n
    lower_raw: list[float | None] = [None] * n
    for col, ys in enumerate(ridges_by_col):
        if len(ys) == 2:
            upper_raw[col] = ys[0]
            lower_raw[col] = ys[1]

    def _carry_fill(raw: list[float | None]) -> list[float | None]:
        filled: list[float | None] = list(raw)
        last: float | None = None
        for col in range(n):
            if filled[col] is not None:
                last = filled[col]
            elif last is not None:
                filled[col] = last
        first = next((v for v in filled if v is not None), None)
        if first is not None:
            for col in range(n):
                if filled[col] is None:
                    filled[col] = first
                else:
                    break
        return filled

    return _carry_fill(upper_raw), _carry_fill(lower_raw)


def _ridge_dp_one_pass(
    ridges_by_col: list[list[float]],
    *,
    alpha: float = _RIDGE_DP_ALPHA,
    erase_window: dict[int, float] | None = None,
    anchor: list[float | None] | None = None,
    gamma: float = _RIDGE_DP_GAMMA,
) -> tuple[list[float | None], list[bool]]:
    """Single Viterbi pass: pick one y per column to minimise data + smoothness.

    Each column's candidate y-set = its ridge centroids minus any ridges
    in the optional `erase_window` (column-index → forbidden y, ±
    ``_RIDGE_DP_ERASE_HALF`` px). The DP also considers carry-forward
    from the previous column (whatever y the path was last at) so it
    can bridge empty columns.

    Returns ``(path, on_ridge)`` — two lists of length
    ``len(ridges_by_col)``. ``path[col]`` is the path's y at that column
    or ``None`` if no path here. ``on_ridge[col]`` is True iff the path
    landed on a real ridge centroid (i.e. the column had candidates AND
    the path picked one of them); False when the path carried forward
    through an empty column.

    Cost model:
      Data cost at column x placing path at y:
        0                              if y == one of column's ridges
        _RIDGE_DP_OFF_RIDGE_PENALTY    if anchor supplied AND path
                                       coasts past a column with ridges
                                       (#1104: see `_ridge_dp_two_paths`)
        0                              if column has NO ridges (carry
                                       forward is free)
      Smoothness cost transitioning from y' to y across one column:
        alpha * |y - y'|
      Anchor-coherence cost at column x placing path at y (when `anchor`
      set):
        gamma * |y - anchor[col]|
    """
    n_cols = len(ridges_by_col)
    if n_cols == 0:
        return [], []

    # Build the candidate y-set per column. The carry-forward is handled
    # at backtrack time, not as a candidate; a column with no ridges has
    # an empty candidate set and the path coasts.
    candidates_per_col: list[list[float]] = []
    for col, ys in enumerate(ridges_by_col):
        kept = []
        if erase_window and col in erase_window:
            forbidden_y = erase_window[col]
            for y in ys:
                if abs(y - forbidden_y) > _RIDGE_DP_ERASE_HALF:
                    kept.append(y)
        else:
            kept = list(ys)
        candidates_per_col.append(kept)

    def _anchor_cost(col: int, y: float) -> float:
        if anchor is None:
            return 0.0
        a = anchor[col]
        if a is None:
            return 0.0
        return gamma * abs(y - a)

    # DP forward pass. State at each column: best total cost ending at
    # each candidate y, plus the back-pointer (previous y, or None for
    # "start").
    # Represent best-cost as a dict {y: (cost, prev_y_or_None)}.
    best: list[dict[float, tuple[float, float | None]]] = [{} for _ in range(n_cols)]

    # Find the first column with at least one candidate — DP starts there.
    first_col = next((c for c, ys in enumerate(candidates_per_col) if ys), None)
    if first_col is None:
        return [None] * n_cols, [False] * n_cols
    for y in candidates_per_col[first_col]:
        best[first_col][y] = (_anchor_cost(first_col, y), None)

    # Forward over each subsequent column.
    for col in range(first_col + 1, n_cols):
        prev = best[col - 1]
        cands = candidates_per_col[col]
        if cands:
            for y in cands:
                # Min over prev candidate y's of (prev_cost + alpha * |y - y'|).
                best_cost = float("inf")
                best_prev_y = None
                for y_prev, (cost_prev, _) in prev.items():
                    cand_cost = cost_prev + alpha * abs(y - y_prev)
                    if cand_cost < best_cost:
                        best_cost = cand_cost
                        best_prev_y = y_prev
                best[col][y] = (best_cost + _anchor_cost(col, y), best_prev_y)
            # When the path has an anchor, also allow each prior state to
            # coast through this column WITHOUT landing on a ridge — the
            # #1104 case where a lone lower-band ridge would drag pass 1
            # off the upper curve through a dash gap. The anchor cost
            # still applies, so coasting is only cheaper than landing
            # when the available ridges are far from this path's anchor.
            # Without an anchor, coasting is NOT an option — the #1100
            # TTartisan freq30 dive is a legitimate 67 px jump that the
            # unanchored DP must take, not coast through.
            if anchor is not None:
                for y_prev, (cost_prev, _) in prev.items():
                    coast_cost = (
                        cost_prev
                        + _RIDGE_DP_OFF_RIDGE_PENALTY
                        + _anchor_cost(col, y_prev)
                    )
                    stored = best[col].get(y_prev)
                    if stored is None or coast_cost < stored[0]:
                        best[col][y_prev] = (coast_cost, y_prev)
        else:
            # Empty column: carry every state forward at zero cost.
            for y_prev, (cost_prev, _) in prev.items():
                best[col][y_prev] = (cost_prev, y_prev)

    # Backtrack from the last column with state to recover the path.
    last_col = next(
        (c for c in range(n_cols - 1, -1, -1) if best[c]),
        None,
    )
    if last_col is None:
        return [None] * n_cols, [False] * n_cols

    path: list[float | None] = [None] * n_cols
    on_ridge: list[bool] = [False] * n_cols
    # Find best terminal y at last_col.
    end_y, _ = min(best[last_col].items(), key=lambda kv: kv[1][0])
    cur_y = end_y
    for col in range(last_col, first_col - 1, -1):
        path[col] = cur_y
        # The path landed on a real ridge iff this column had candidates
        # AND cur_y is one of them (not a carried-forward state).
        on_ridge[col] = cur_y in candidates_per_col[col]
        if col == first_col:
            break
        prev_y = best[col][cur_y][1]
        if prev_y is None:
            break
        cur_y = prev_y
    return path, on_ridge


def _ridge_dp_two_paths(
    ridges_by_col: list[list[float]],
    *,
    use_y_anchor: bool = False,
) -> tuple[
    tuple[list[float | None], list[bool]],
    tuple[list[float | None], list[bool]],
]:
    """Two passes: pass 1 finds the best path, pass 2 finds the next-best
    with pass 1's ridges erased per column.

    When ``use_y_anchor`` is True (#1104), pass 1 is pulled toward the
    **upper** y-anchor (smaller y = upper in image coordinates = higher
    MTF) and pass 2 toward the **lower** anchor. The anchor coherence
    cost lets each pass coast past a column whose ridges sit in the
    other path's band, instead of being forced to land on a ridge and
    swap identity. This fixes the identity-swap failure mode described
    in ADR-049's "Known limitation: 7artisans corner crossing".

    When ``use_y_anchor`` is False (default), the DP runs identity-free
    — global smoothness optimum across both passes. This is the #1100
    TTartisan behaviour: the freq30 dive is a legitimate 67 px jump
    that the unanchored DP takes correctly, but the anchored coast
    option can mis-attribute it as a swap. Per-profile opt-in via
    `MtfProfile.ridge_dp_y_anchor`.

    When a column has only one ridge (curve coincidence), pass 1 takes
    it; pass 2 then has no ridge at that column and coasts via
    carry-forward — the downstream
    `_fill_coincident_column_gaps_extending` step attributes the
    single-ridge value to both fields per B4 physics.

    Each pass returns ``(path, on_ridge)`` so the caller can distinguish
    columns where DP landed on a real ridge from columns where it
    coasted via carry-forward.
    """
    if use_y_anchor:
        upper_anchor, lower_anchor = _compute_y_anchors(ridges_by_col)
    else:
        upper_anchor = lower_anchor = None
    pass1 = _ridge_dp_one_pass(ridges_by_col, anchor=upper_anchor)
    pass1_path, _pass1_on_ridge = pass1
    erase: dict[int, float] = {
        col: y for col, y in enumerate(pass1_path) if y is not None
    }
    pass2 = _ridge_dp_one_pass(
        ridges_by_col, erase_window=erase, anchor=lower_anchor
    )
    return pass1, pass2


# Half-window for measuring mask continuity around a path. Sized to
# capture the anti-aliased halo of a 1-2 px stroke (2-3 px) plus a
# small slop, without admitting the neighbouring curve which sits
# 30+ px away on freq-split charts.
_PATH_CONTINUITY_BAND_HALF_Y: int = 3


def _path_mask_continuity(
    track: Track, mask: np.ndarray
) -> float:
    """Fraction of columns within a path's x range that have mask ink
    inside the y-band around the path's local y.

    Coherent DP paths (#1100) are SINGLE physical curves end-to-end,
    so this density is a clean discriminator: solid lines have ink at
    nearly every column under them (continuity ~1.0); dashed lines have
    periodic gaps (continuity ~0.5-0.7).

    Distinct from the failed attempt in the PR #1099 spike: that
    measured continuity on greedy-clustered tracks (frankensteins),
    which mixed solid and dashed segments and gave noisy results. With
    coherent paths, the measurement is the right signal.
    """
    if not track.points:
        return 0.0
    h, w = mask.shape
    xs = sorted(x for x, _ in track.points)
    x_lo, x_hi = xs[0], xs[-1]
    if x_hi <= x_lo:
        return 0.0
    by_x = {x: y for x, y in track.points}
    keys = sorted(by_x)
    import bisect

    hits = 0
    total = 0
    for x in range(x_lo, x_hi + 1):
        if x < 0 or x >= w:
            continue
        if x in by_x:
            y = by_x[x]
        else:
            idx = bisect.bisect_left(keys, x)
            x_l = keys[idx - 1]
            x_r = keys[idx]
            y_l = by_x[x_l]
            y_r = by_x[x_r]
            y = y_l + (y_r - y_l) * (x - x_l) / (x_r - x_l)
        y0 = max(0, int(y) - _PATH_CONTINUITY_BAND_HALF_Y)
        y1 = min(h, int(y) + _PATH_CONTINUITY_BAND_HALF_Y + 1)
        if mask[y0:y1, x].any():
            hits += 1
        total += 1
    return hits / total if total else 0.0


def _path_to_track(
    path: list[float | None],
    on_ridge: list[bool],
    plot_box: PlotBox,
) -> Track | None:
    """Convert a DP pass result to a `Track`, keeping only ridge-anchored columns.

    A column is included iff DP picked a real ridge centroid there
    (``on_ridge[col]`` is True). Carry-forward columns (where the path
    coasted across empty columns OR where the only candidates were
    erased by pass 2's pass-1 forbid-set) are dropped — they would
    bleed the OTHER pass's y values into this track and recreate the
    same frankenstein the DP was meant to avoid.

    The downstream `_densify_track` and
    `_fill_coincident_column_gaps_extending` steps handle the gaps via
    coincidence-fill + linear interpolation, so dropping carry-forward
    columns here is the right place to draw the line.
    """
    pts: list[tuple[int, float]] = []
    for col, y in enumerate(path):
        if y is None or not on_ridge[col]:
            continue
        x = col + plot_box.x_left
        pts.append((x, float(y)))
    if not pts:
        return None
    return Track(points=tuple(pts))


# Crossing detection (#1170, S151 spike). After the DP yields two paths
# in y-band order (smaller-mean-y first), the bands do not always
# preserve physical curve identity. When two physical curves cross
# monotonically, each curve continues in its own direction past the
# crossing, but the DP follows the y-bands — so each output track
# inherits the OTHER curve's slope after the crossing. The signature
# in DP-track space is: both tracks' y converge within
# `_CROSSING_DY_THRESHOLD`, and BOTH tracks' y-slopes reverse sign
# across the convergence. We swap right-of-crossing assignments so
# each output track follows one physical curve end-to-end.
#
# Candidate-walk vs. greedy-min (S151 finding). The af-75 stopped
# freq30 chart has a real V-crossing at col ~516 (dy=3, both tracks
# reverse slope) AND a left-edge convergence at col ~232 (dy=2.5, no
# left-history on track_b → slopes undefined). Picking the greedy
# global minimum locks onto col 232 first and exits without firing.
# Iterating local-minimum candidates left-to-right and taking the
# first one with a defined verdict catches the real crossing.
#
# Why "both reverse", not "exactly one". Earlier (#1173) the rule was
# exactly-one-reverses — modelling a single curve that dives and comes
# back up. The S151 probe on the in-the-wild af-75 chart shows that
# pattern does not occur on real MTF data; both physical curves cross
# monotonically, which produces a both-reverse signature in DP-track
# space. The synthetic V test from #1173 still passes under the new
# rule because its construction (one curve symmetric around the
# crossing, the other monotonic) was geometrically inconsistent —
# the test data was updated together with the rule.
#
# A monotonic pass-through (neither reverses; tilt-50 synthetic and
# real cases) means the DP is already tracking curve identity
# correctly — no swap. Real tilt-50 stopped freq30 has no
# sub-threshold convergence anywhere past the left edge, so the
# detector skips it entirely.

_CROSSING_DY_THRESHOLD: float = 8.0
_CROSSING_SLOPE_WINDOW: int = 10
_CROSSING_SLOPE_MIN_MAGNITUDE: float = 0.15


def _local_slope(
    points_by_x: dict[int, float], center_x: int, window: int, before: bool
) -> float | None:
    """Linear-fit slope (dy/dx) of `points_by_x` over `[center_x - window,
    center_x)` if `before` else `(center_x, center_x + window]`.

    Returns None when fewer than two points fall inside the window —
    slope is undefined.
    """
    if before:
        x_lo, x_hi = center_x - window, center_x
    else:
        x_lo, x_hi = center_x + 1, center_x + window + 1
    xs: list[int] = []
    ys: list[float] = []
    for x in range(x_lo, x_hi):
        y = points_by_x.get(x)
        if y is not None:
            xs.append(x)
            ys.append(y)
    if len(xs) < 2:
        return None
    xa = np.asarray(xs, dtype=np.float64)
    ya = np.asarray(ys, dtype=np.float64)
    slope, _ = np.polyfit(xa, ya, 1)
    return float(slope)


def _crossing_candidate_columns(
    a_by_x: dict[int, float],
    b_by_x: dict[int, float],
    common_xs: list[int],
) -> list[int]:
    """Find local minima of |y_a - y_b| below `_CROSSING_DY_THRESHOLD`.

    A column is a candidate when its dy is below threshold AND no smaller
    dy exists within `_CROSSING_SLOPE_WINDOW` columns on either side.
    This collapses runs of equally-close columns (af-75 has cols 514-521
    all near dy=3) into one representative per region — picked as the
    leftmost of the run so the slope-after window starts as far right of
    the convergence as possible.

    Returned in left-to-right order so the detector evaluates the
    earliest-firing real crossing first.
    """
    dys = [abs(a_by_x[x] - b_by_x[x]) for x in common_xs]
    candidates: list[int] = []
    n = len(common_xs)
    i = 0
    while i < n:
        if dys[i] >= _CROSSING_DY_THRESHOLD:
            i += 1
            continue
        # Find the run of consecutive sub-threshold columns.
        j = i
        while j + 1 < n and dys[j + 1] < _CROSSING_DY_THRESHOLD:
            j += 1
        # Take the leftmost minimum of the run as the candidate.
        run_min = min(dys[i : j + 1])
        for k in range(i, j + 1):
            if dys[k] == run_min:
                candidates.append(common_xs[k])
                break
        i = j + 1
    return candidates


def _slopes_reverse_at(
    a_by_x: dict[int, float],
    b_by_x: dict[int, float],
    crossing_x: int,
) -> bool | None:
    """Return True iff BOTH tracks reverse slope across `crossing_x` with
    magnitude above `_CROSSING_SLOPE_MIN_MAGNITUDE`.

    Returns None when any of the four slope fits is undefined (insufficient
    points in the before/after window) — caller treats this candidate as
    inconclusive and moves on.

    Why both, not one (#1170 / S151 spike finding). When two physical
    curves cross monotonically (the af-75 stopped freq30 case), each
    curve continues in its own direction past the crossing. The DP
    follows y-bands not curve identity, so each output track inherits
    the OTHER curve's slope after the crossing — which reverses sign
    on BOTH tracks. A V-crossing in DP-track space (both reverse) is
    the signature of curves trading identity. A monotonic-pass-through
    in DP-track space (neither reverses; tilt-50 synthetic case) means
    the DP is already tracking curve identity correctly — no swap.

    The earlier "exactly one reverses" rule from #1173 modelled a single
    diving curve that comes back up — a shape that does not actually
    occur in MTF chart data; real curves are monotonic in their dive
    direction. The S151 probe found the actual af-75 chart produces a
    classic both-reverse signature at col 516.
    """
    a_pre = _local_slope(a_by_x, crossing_x, _CROSSING_SLOPE_WINDOW, before=True)
    a_post = _local_slope(a_by_x, crossing_x, _CROSSING_SLOPE_WINDOW, before=False)
    b_pre = _local_slope(b_by_x, crossing_x, _CROSSING_SLOPE_WINDOW, before=True)
    b_post = _local_slope(b_by_x, crossing_x, _CROSSING_SLOPE_WINDOW, before=False)
    if None in (a_pre, a_post, b_pre, b_post):
        return None

    def _reverses(pre: float, post: float) -> bool:
        return (
            abs(pre) >= _CROSSING_SLOPE_MIN_MAGNITUDE
            and abs(post) >= _CROSSING_SLOPE_MIN_MAGNITUDE
            and pre * post < 0
        )

    return _reverses(a_pre, a_post) and _reverses(b_pre, b_post)


def _detect_and_swap_at_crossings(
    track_a: Track, track_b: Track
) -> tuple[Track, Track]:
    """Swap track assignments at columns where two DP-extracted y-bands
    converge AND both tracks' slopes reverse across the convergence.

    Returns `(out_a, out_b)` — same union of points, with assignments
    swapped right of the detected crossing column.

    Detection (see module-level comment for the rationale):
      1. Find every column where `|y_a - y_b|` falls below
         `_CROSSING_DY_THRESHOLD` and is a local minimum of the dy
         series (collapses multi-column convergence runs to one
         representative).
      2. Walk candidates left-to-right; for each, compute slopes over
         a window before vs. after the candidate column. The first
         candidate where BOTH tracks reverse sign with magnitude above
         `_CROSSING_SLOPE_MIN_MAGNITUDE` is the curve-identity swap.

    Walking left-to-right (instead of greedy global-min) is what makes
    this work on real af-75 data: the global min lives at the left edge
    where track_b's slope-before is undefined (no history). The actual
    mid-plot crossing has dy=3 and a clean both-reverse signature, but
    the global-min picker reached the left-edge cluster first and
    stopped. See `_slopes_reverse_at` for the both-reverse rationale.
    """
    a_by_x = {x: y for x, y in track_a.points}
    b_by_x = {x: y for x, y in track_b.points}
    common_xs = sorted(set(a_by_x) & set(b_by_x))
    if not common_xs:
        return track_a, track_b

    crossing_x: int | None = None
    for cand in _crossing_candidate_columns(a_by_x, b_by_x, common_xs):
        verdict = _slopes_reverse_at(a_by_x, b_by_x, cand)
        if verdict is True:
            crossing_x = cand
            break
        # verdict is None (undefined slopes) or False (X-crossing) —
        # keep walking; another candidate further right may qualify.
    if crossing_x is None:
        return track_a, track_b

    # Swap LEFT of the crossing, not right. Rationale (S151): the
    # coverage-based S/M labelling downstream picks the more-fully-on-
    # ridge track as "solid" (S). On a charts like af-75 the solid
    # curve is the LOW-MTF one in midfield (heavy dive) — so post-
    # crossing the upper band IS the S curve and the label is already
    # correct. The pre-crossing assignments are the ones that need
    # inverting, because pre-crossing the S curve is the lower band
    # (mid-dive) while the upper band is M (flat).
    #
    # Singleton handling in the swap region (#1177). When a column has
    # a point in only ONE input track (the other was dropped by
    # `_path_to_track` because its on_ridge flag was False there) we
    # cannot simply keep the surviving y on its original track — that
    # bleeds a wrong-curve single-column outlier into the densified
    # track. Concrete case: af-75 stopped freq30 col 310 had only
    # track_b (lower cluster y=95.5) while the M curve was actually
    # following the upper cluster; densification through that singleton
    # produced the visible 0.13 MTF dip at frac 0.6.
    #
    # The shape of the singleton tells us what to do:
    #
    # - **Edge singletons** (consecutive run at the start of the swap
    #   region, before any column where BOTH tracks exist): both
    #   physical curves are near-coincident at this end of the plot
    #   (MTF ~0.88 left edge for af-75), so the DP only resolved one
    #   path. Mirror the surviving y to both output tracks. Same B4
    #   coincidence physics `ridge_tracks_for_hue_freq_split` already
    #   uses when track2.coverage<10.
    # - **Interior singletons** (columns where the other track existed
    #   nearby but was dropped at this exact column): the DP carried
    #   the surviving point in the wrong band for the swapped track.
    #   Drop the singleton so `_densify_track` bridges from neighbors.
    swapped_a: list[tuple[int, float]] = []
    swapped_b: list[tuple[int, float]] = []
    swap_common = sorted(x for x in a_by_x if x in b_by_x and x < crossing_x)
    first_common_x = swap_common[0] if swap_common else crossing_x

    for x, y in track_a.points:
        if x >= crossing_x:
            swapped_a.append((x, y))
        elif x in b_by_x:
            swapped_a.append((x, b_by_x[x]))
        elif x < first_common_x:
            # edge singleton — mirror onto both tracks (coincidence)
            swapped_a.append((x, y))
        # interior singleton in swap region — drop
    for x, y in track_b.points:
        if x >= crossing_x:
            swapped_b.append((x, y))
        elif x in a_by_x:
            swapped_b.append((x, a_by_x[x]))
        elif x < first_common_x:
            swapped_b.append((x, y))
        # interior singleton in swap region — drop

    # Edge-singleton coincidence: mirror track_a's edge points onto
    # track_b (and vice versa) so both tracks carry the coincident y.
    a_edge = [(x, y) for x, y in track_a.points if x < first_common_x]
    b_edge = [(x, y) for x, y in track_b.points if x < first_common_x]
    swapped_b.extend(a_edge)
    swapped_a.extend(b_edge)

    swapped_a.sort()
    swapped_b.sort()
    return Track(points=tuple(swapped_a)), Track(points=tuple(swapped_b))


def _swap_after_rightmost_convergence(
    solid: Track, dashed: Track
) -> tuple[Track, Track]:
    """Swap track assignments AT and AFTER the rightmost column where
    the two tracks come within `_CROSSING_DY_THRESHOLD` of each other.

    Used by `ridge_tracks_for_hue_freq_split` when a per-lens override
    declares the discriminator picked the wrong solid track AND the DP
    flipped curve identity at a near-crossing (af-35 stopped-30-orange:
    dy=6 px at frac 0.95 before the final corner spread). The narrower
    swap region preserves the labels the DP got right in the rest of
    the field.

    When no convergence column exists (the tracks stay >
    `_CROSSING_DY_THRESHOLD` apart end-to-end), swap the whole track —
    the situation reduces to a plain discriminator failure with no
    mid-curve identity flip.
    """
    s_by_x = {x: y for x, y in solid.points}
    d_by_x = {x: y for x, y in dashed.points}
    common_xs = sorted(set(s_by_x) & set(d_by_x))
    if not common_xs:
        # No overlap at all — swap whole tracks; the override is the
        # only signal we have.
        return dashed, solid

    near_cols = [
        x for x in common_xs
        if abs(s_by_x[x] - d_by_x[x]) < _CROSSING_DY_THRESHOLD
    ]
    if not near_cols:
        # Tracks never converge — whole-track swap.
        return dashed, solid

    swap_from_x = near_cols[-1]
    swapped_solid: list[tuple[int, float]] = []
    swapped_dashed: list[tuple[int, float]] = []
    for x, y in solid.points:
        if x >= swap_from_x:
            swapped_dashed.append((x, y))
        else:
            swapped_solid.append((x, y))
    for x, y in dashed.points:
        if x >= swap_from_x:
            swapped_solid.append((x, y))
        else:
            swapped_dashed.append((x, y))
    swapped_solid.sort()
    swapped_dashed.sort()
    return Track(points=tuple(swapped_solid)), Track(points=tuple(swapped_dashed))

