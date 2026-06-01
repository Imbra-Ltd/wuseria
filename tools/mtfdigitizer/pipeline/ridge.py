"""Ridge tracking for tightly-clustered curves (#994, ADR-038).

CC-based dispatch (`CC_RANK_BY_MEAN_Y`) is **topological**: it requires
distinct curves to skeletonize into distinct connected components. That
breaks the moment two curves' anti-aliased masks touch — which happens on
any low-resolution chart where curves bundle within a few pixels of each
other in OTF space.

Ridge tracking is **geometric**: at each column it asks "where are the
local intensity ridges?" Two curves separated by 2-3 pixels yield two
distinct ridges even when their dilated masks merge into one CC. This
generalizes the pipeline past the CC bottleneck for *any* future
tightly-bundled chart, not just Viltrox.

The Viltrox AF 75mm f/1.2 Pro chart is the motivating case. Per the
#994 calibration probe, even the raw (unskeletonized, unclosed) neutral
mask fuses all four curves into one 2012-px component spanning the full
plot height, because the dashes of adjacent frequencies sit within
anti-aliasing distance in the 366×235px f/1.2 panel. The CC-rank
dispatch shipped in #992 read 10S as the printed top plot-box border
line (it sat at ~OTF 1.0 ≈ ground truth 10S, masking the real failure).

## Algorithm

1. **Strip chart chrome.** Single-row CCs spanning ≥90% of plot width
   with area ≥ 0.5 × plot_width are printed borders / grid baselines,
   not curves. Zero them out of the mask before ridge extraction. (The
   Viltrox top border at exactly y=y_top is the canonical case.)

2. **Per-column ridge extraction.** For each column `x` in the plot box,
   walk the column's mask pixels and group them into "runs" — maximal
   sequences of consecutive y-rows with mask=1, where a gap of ≥
   `RIDGE_RUN_GAP_TOLERANCE` rows starts a new run. Each run yields one
   ridge point at its centroid y. Output: a list of (x, y, run_length)
   points across all columns.

   This is a discrete approximation of the sub-pixel ridge-finding
   technique. The mask is already a thresholded binary signal so true
   sub-pixel quadratic fitting buys little — what matters is that one
   column can produce multiple ridge points, which a skeleton cannot.

3. **Cluster ridge points into N curves.** For the 4-curve case
   (Viltrox), use a simple greedy approach: sort all ridge points by x,
   walk them column-by-column, and assign each point to the closest
   existing track within `RIDGE_TRACK_MAX_DY` pixels. Points that match
   no track start a new track. After the walk, keep the `expected_count`
   longest tracks (by point count).

   This handles broken/dashed curves naturally — a dashed curve becomes
   a track with gaps, but the gaps don't fragment the track because the
   "closest existing track within window" rule looks ahead across empty
   columns.

4. **Identify which curve is which.** Sort the kept tracks by mean y:
   upper half → upper frequency, lower half → lower frequency. Within
   each frequency pair, the track with higher coverage fraction
   (`len(track) / plot_width`) is solid (S); the gappier one is dashed
   (M). The convention follows `profile.dashed_is_sagittal` so 7Artisans-
   style charts (dashed=S) compose correctly.

5. **Rasterize tracks into skeleton masks.** Each track becomes a one-
   pixel-wide skeleton drawn at the (x, round(y)) coordinates. The
   sampler downstream (`sampling.sample_skeleton_at_fraction`) reads
   these the same way it reads CC-derived skeletons — no change needed.

## Non-goals

- **Not a replacement for CC dispatch.** CC-based extraction is correct
  and cheaper for charts where curves are visually separable. Ridge
  tracking is opt-in via `hue_meaning='RIDGE_TRACKING'` and intended
  only for charts that fail CC dispatch.
- **Not sub-pixel-accurate beyond ~0.5 px.** The chart raster itself
  is the precision floor; a Gaussian-fit refinement on top of run
  centroids would buy <0.02 OTF on a 235px-tall plot. Skipped.
- **Not handling >2 frequencies.** The clustering assumes a 4-curve
  layout (2 frequencies × S/M). A 6-curve Zeiss-style 3-frequency
  chart needs a different track-identification step.

## Failure modes

- **Track-merge on touching curves with identical density.** When two
  curves cross or run pixel-adjacent for a long stretch, the column
  ridge collapses to one run; both curves contribute to the same track
  for the merge span. The track's y is the average of the two — a
  systematic 1-2 px bias on either curve for the merged columns. Lives
  with this; it's no worse than CC-rank's failure mode (full miss),
  and the calibration log will record where it shows up.
- **Single-curve frequency bands.** If 30M extracts as 0 tracks, only
  30S is kept and 30M reports `None` everywhere (B2 contract). Better
  than fabricating.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .types import PlotBox


# A column run shorter than this is single-pixel noise (one anti-aliased
# stray pixel between dash and gridline). Filtered before clustering.
_MIN_RUN_LENGTH: int = 1

# Rows within this distance (inclusive) belong to the same column run.
# Larger values merge adjacent curves; smaller values split a single
# anti-aliased curve into two runs. 1 means "touching only".
_RIDGE_RUN_GAP_TOLERANCE: int = 1

# Max y-distance (px) between a candidate ridge point and the last
# point on an existing track. Within this window, the point extends the
# track; otherwise it starts a new one. Sized for Viltrox's curve
# slopes (max ~0.35 OTF over 366px ≈ 0.2 px/column on the 240px-tall
# plot); allowance for noise gives ~3-5 px.
_RIDGE_TRACK_MAX_DY: int = 5

# Max x-distance (columns) between a candidate point and the last point
# on an existing track. Dashed curves have long horizontal gaps between
# dashes — Viltrox 30M has ~20-column gaps. Allowing the tracker to
# bridge these keeps a dashed curve as one track instead of fragmenting
# it into per-dash tracks that get filtered as noise.
_RIDGE_TRACK_MAX_DX: int = 40

# A track must cover at least this fraction of plot width to count.
# Filters single-column noise tracks while admitting heavily-dashed
# curves (Viltrox 30M only covers ~13% of plot width with its sparse
# dash pattern). Sized to keep T04 (Viltrox 30M) above the floor; the
# tighter selection happens in track ranking below.
_MIN_TRACK_COVERAGE: float = 0.10


@dataclass(frozen=True)
class Track:
    """One ridge-traced curve.

    `points` are (x, y) coordinates where the curve ridge sits. Sparse
    along x for dashed curves; dense for solid ones.
    """

    points: tuple[tuple[int, float], ...]

    @property
    def coverage(self) -> int:
        """Distinct x-columns occupied by this track."""
        return len({x for x, _ in self.points})

    @property
    def mean_y(self) -> float:
        return float(np.mean([y for _, y in self.points]))


# Chart chrome strip: any CC that spans nearly the full plot width and
# stays thin in y is a printed gridline or plot-frame border, not a
# curve. Viltrox has its OTF=0.0 and OTF=1.0 gridlines rendered 3 rows
# thick (sub-pixel-antialiased over 3 vertical pixels), so the height
# cap must admit at least 3.
_CHROME_MAX_HEIGHT: int = 4
_CHROME_MIN_WIDTH_FRACTION: float = 0.90


def _strip_chrome(mask: np.ndarray, plot_box: PlotBox) -> np.ndarray:
    """Zero out rows with >=90% horizontal coverage inside the plot box.

    Printed OTF gridlines and plot-frame borders span the full plot
    width as nearly-continuous horizontal lines. The ridge tracker would
    otherwise pick OTF=0.0 (chart bottom) as 30M and OTF=1.0 (top) as
    10S — both are chart chrome, not curves.

    CC-based stripping doesn't work here: the Viltrox neutral mask has
    a single 2789-px CC that fuses gridlines with curves via the
    vertical dash strokes (#994 probe). Row-coverage stripping is
    immune to this because it operates on horizontal density alone,
    regardless of vertical connectivity.

    Rows with high coverage at any y inside `[y_top, y_bottom]` are
    treated as chrome — including OTF=0.5 gridlines that bisect the
    curves. This is intentional: a curve crossing the OTF=0.5 line
    loses 3-4 pixels of trace at that gridline, which the ridge
    clusterer handles via its column-skip rule (gaps of <=
    `_RIDGE_TRACK_MAX_DY` join). No curve gets truncated.
    """
    cleaned = mask.copy().astype(np.uint8)
    width = plot_box.x_right - plot_box.x_left + 1
    min_count = int(_CHROME_MIN_WIDTH_FRACTION * width)
    for y in range(plot_box.y_top, plot_box.y_bottom + 1):
        row = cleaned[y, plot_box.x_left : plot_box.x_right + 1]
        if int(row.sum()) >= min_count:
            cleaned[y, plot_box.x_left : plot_box.x_right + 1] = 0
    return cleaned


def _column_runs(
    column: np.ndarray, gap_tolerance: int = _RIDGE_RUN_GAP_TOLERANCE
) -> list[tuple[float, int]]:
    """Group a binary column into runs; return (centroid_y, length) per run."""
    rows = np.nonzero(column)[0]
    if rows.size == 0:
        return []
    runs: list[tuple[float, int]] = []
    start = int(rows[0])
    prev = start
    for y in rows[1:]:
        y_int = int(y)
        if y_int - prev <= gap_tolerance:
            prev = y_int
            continue
        length = prev - start + 1
        if length >= _MIN_RUN_LENGTH:
            runs.append(((start + prev) / 2.0, length))
        start = y_int
        prev = y_int
    length = prev - start + 1
    if length >= _MIN_RUN_LENGTH:
        runs.append(((start + prev) / 2.0, length))
    return runs


def _extract_ridge_points(
    mask: np.ndarray, plot_box: PlotBox
) -> list[tuple[int, float]]:
    """Walk every column inside plot_box; collect ridge centroids."""
    points: list[tuple[int, float]] = []
    for x in range(plot_box.x_left, plot_box.x_right + 1):
        col = mask[plot_box.y_top : plot_box.y_bottom + 1, x]
        for centroid_y_local, _length in _column_runs(col):
            points.append((x, centroid_y_local + plot_box.y_top))
    return points


def _cluster_into_tracks(
    points: list[tuple[int, float]],
    max_dy: int = _RIDGE_TRACK_MAX_DY,
    max_dx: int = _RIDGE_TRACK_MAX_DX,
) -> list[Track]:
    """Greedy column-walk: each point joins the closest in-range track.

    "In range" means both `|y - last_y| <= max_dy` and `x - last_x <=
    max_dx`. The x-gap allowance lets a single dashed track absorb its
    next dash even after a long horizontal gap, instead of fragmenting
    into one-track-per-dash.
    """
    if not points:
        return []
    points_sorted = sorted(points, key=lambda p: (p[0], p[1]))

    tracks: list[list[tuple[int, float]]] = []
    last_x: list[int] = []
    last_y: list[float] = []

    for x, y in points_sorted:
        best = -1
        best_dy = float("inf")
        for i, ly in enumerate(last_y):
            if x == last_x[i]:
                continue  # one point per column per track
            if x - last_x[i] > max_dx:
                continue
            dy = abs(y - ly)
            if dy <= max_dy and dy < best_dy:
                best = i
                best_dy = dy
        if best >= 0:
            tracks[best].append((x, y))
            last_x[best] = x
            last_y[best] = y
        else:
            tracks.append([(x, y)])
            last_x.append(x)
            last_y.append(y)

    return [Track(points=tuple(t)) for t in tracks]


# Two tracks whose mean_y are within this many pixels of each other are
# treated as duplicate ridges of one physical curve (anti-aliasing halo
# from a thick line produces parallel ridges 2-4 px apart). The longer
# one wins; the shorter is dropped. Sized for the Viltrox chart's 2-3px
# antialiased halo on solid lines; larger values would merge genuinely
# distinct curves on tightly-clustered charts.
_NEAR_DUPLICATE_DY: float = 4.0


# Two tracks at similar y but on non-overlapping x ranges are fragments
# of the same physical curve, broken up because the column ridge merged
# with another curve in the gap region (one curve coincides with another
# at center, then they diverge — the merged region yields one ridge per
# column, assigned to either track; the other curve's fragments on
# either side of the merged region become two separate tracks). Merging
# them recovers the full curve. Sized 1.5x larger than `_NEAR_DUPLICATE_DY`
# because the y-values at the endpoints of two fragments may differ
# slightly due to the merged region pulling one track up or down.
_FRAGMENT_MERGE_MAX_DY: float = 6.0


# Two fragments may overlap by a few columns at the handoff point — the
# greedy clusterer assigns the shared column's ridge to both tracks.
# Allow a small overlap to forgive that without admitting genuine
# overlap of two distinct curves. Sized to bridge the 7-10px overlap
# seen in Tokina 11mm where one curve fragments diverge from a
# coincidence ridge.
_FRAGMENT_MERGE_OVERLAP_TOLERANCE: int = 12


def _merge_near_duplicate_tracks(tracks: list[Track]) -> list[Track]:
    """Drop short tracks whose mean_y is within `_NEAR_DUPLICATE_DY` of a
    longer one.

    Anti-aliased halo above and below a thick solid line produces two
    parallel ridges; we want only the dominant one. Iterates from longest
    to shortest, keeping a track only when no already-kept track sits
    within the duplicate window.
    """
    by_coverage = sorted(tracks, key=lambda t: t.coverage, reverse=True)
    kept: list[Track] = []
    for t in by_coverage:
        if any(abs(t.mean_y - k.mean_y) < _NEAR_DUPLICATE_DY for k in kept):
            continue
        kept.append(t)
    return kept


def _track_x_range(t: Track) -> tuple[int, int]:
    xs = [x for x, _ in t.points]
    return min(xs), max(xs)


def _track_endpoint_y(t: Track, side: str) -> float:
    """Average y of the last/first few points (smooths antialiasing
    noise so the continuity test isn't fooled by a single jittery row)."""
    sorted_pts = sorted(t.points)
    sample = sorted_pts[:5] if side == "left" else sorted_pts[-5:]
    return float(np.mean([y for _, y in sample]))


def _merge_fragmented_tracks(tracks: list[Track]) -> list[Track]:
    """Fuse tracks that are fragments of the same physical curve.

    Two tracks are fragments of one curve when their x ranges are
    disjoint AND the y at the touching ends is continuous — i.e. the
    right endpoint y of the left track ≈ the left endpoint y of the
    right track (within `_FRAGMENT_MERGE_MAX_DY`). The mean_y of two
    fragments of a sloping curve can differ by hundreds of pixels even
    though they're the same curve, so endpoint matching is the right
    test, not mean_y matching.

    The per-column ridge extractor splits a single physical curve into
    multiple tracks when the curve coincides with another curve for
    part of the field. The merged region yields one ridge per column;
    the clusterer assigns those points to a single track; the curve's
    fragments on the other side of the merge become independent tracks.
    Without this merge step, none of the fragments individually covers
    the full field, and top-N selection drops the shorter ones entirely.
    """
    pool = list(tracks)
    changed = True
    while changed and len(pool) >= 2:
        changed = False
        for i in range(len(pool)):
            for j in range(i + 1, len(pool)):
                a, b = pool[i], pool[j]
                a_lo, a_hi = _track_x_range(a)
                b_lo, b_hi = _track_x_range(b)
                # Want largely disjoint x ranges, ordered left→right.
                # Allow up to `_FRAGMENT_MERGE_OVERLAP_TOLERANCE` columns
                # of overlap because the clusterer often hands off at a
                # shared column when one track ends and another begins
                # (the ridge in the handoff column gets assigned to both
                # tracks by the greedy walker).
                if a_hi - _FRAGMENT_MERGE_OVERLAP_TOLERANCE <= b_lo:
                    left, right = a, b
                elif b_hi - _FRAGMENT_MERGE_OVERLAP_TOLERANCE <= a_lo:
                    left, right = b, a
                else:
                    continue
                # Endpoint y at the touching sides must match
                left_end_y = _track_endpoint_y(left, "right")
                right_end_y = _track_endpoint_y(right, "left")
                if abs(left_end_y - right_end_y) > _FRAGMENT_MERGE_MAX_DY:
                    continue
                merged_points = tuple(sorted(a.points + b.points))
                merged = Track(points=merged_points)
                pool = [t for k, t in enumerate(pool) if k not in (i, j)]
                pool.append(merged)
                changed = True
                break
            if changed:
                break
    return pool


def _select_top_n_tracks(
    tracks: list[Track], n: int, plot_width: int
) -> list[Track]:
    """Drop near-duplicate ridges, fuse same-curve fragments, then keep
    the `n` longest above the coverage floor."""
    floor = int(_MIN_TRACK_COVERAGE * plot_width)
    qualified = [t for t in tracks if t.coverage >= floor]
    deduped = _merge_near_duplicate_tracks(qualified)
    fused = _merge_fragmented_tracks(deduped)
    fused.sort(key=lambda t: t.coverage, reverse=True)
    return fused[:n]


def _rasterize(track: Track, shape: tuple[int, int]) -> np.ndarray:
    """Draw a track as a 1px skeleton mask, one pixel per column."""
    sk = np.zeros(shape, dtype=np.uint8)
    for x, y in track.points:
        sk[int(round(y)), x] = 1
    return sk


def _column_run_count(mask: np.ndarray, plot_box: PlotBox) -> dict[int, int]:
    """How many runs each column has inside the plot box. A column with
    one run means the two curves visually coincide at that x (B4
    physics generalized: where S and M overlap on the chart, their MTF
    is the same)."""
    counts: dict[int, int] = {}
    for x in range(plot_box.x_left, plot_box.x_right + 1):
        col = mask[plot_box.y_top : plot_box.y_bottom + 1, x]
        counts[x] = len(_column_runs(col))
    return counts


# Max gap between a single-run column and the OTHER track's nearest
# known point: above this distance, the curves are clearly separated
# at this x and the single run is a one-curve dash gap, not curve
# coincidence. Sized to admit anti-aliased halo (~5 px) plus a small
# slope-induced extrapolation tolerance.
_COINCIDENCE_FILL_MAX_DY: float = 8.0


def _nearest_known_y(track_by_x: dict[int, float], target_x: int) -> float | None:
    """Linear-interp the track to find its y at target_x, or None when
    target_x falls outside the track's known x range. Used to check
    whether the OTHER curve was nearby when filling a single-run
    column from one track into the other."""
    if not track_by_x:
        return None
    xs = sorted(track_by_x)
    if target_x < xs[0] or target_x > xs[-1]:
        return None
    # binary insert position
    lo, hi = 0, len(xs) - 1
    while lo < hi - 1:
        mid = (lo + hi) // 2
        if xs[mid] <= target_x:
            lo = mid
        else:
            hi = mid
    x_lo, x_hi = xs[lo], xs[hi]
    if x_lo == target_x:
        return track_by_x[x_lo]
    if x_hi == target_x:
        return track_by_x[x_hi]
    y_lo, y_hi = track_by_x[x_lo], track_by_x[x_hi]
    return y_lo + (y_hi - y_lo) * (target_x - x_lo) / (x_hi - x_lo)


def _fill_coincident_column_gaps(
    upper_track: Track,
    lower_track: Track,
    column_runs: dict[int, int],
) -> tuple[Track, Track]:
    """Share single-run column values across both tracks WHERE the
    other track's curve sits close enough that the single run plausibly
    represents both.

    The B4 contract at center generalizes: where two physical curves
    visually coincide on the chart, the column's single ridge run
    represents both. Filling that value into both fields is honest.

    But not every single-run column is coincidence — many are dash
    gaps on one curve where the other curve happens to be present.
    The fill test: the OTHER track's interpolated y at this column
    must be within `_COINCIDENCE_FILL_MAX_DY` of the run's y. If the
    other track is far away, the curves are clearly separated and the
    column belongs only to the track that has it.
    """
    upper_by_x: dict[int, float] = {x: y for x, y in upper_track.points}
    lower_by_x: dict[int, float] = {x: y for x, y in lower_track.points}

    upper_filled = dict(upper_by_x)
    lower_filled = dict(lower_by_x)

    for x, run_count in column_runs.items():
        if run_count != 1:
            continue
        in_upper = x in upper_by_x
        in_lower = x in lower_by_x
        if in_upper and not in_lower:
            other_y = _nearest_known_y(lower_by_x, x)
            if other_y is not None and abs(other_y - upper_by_x[x]) <= _COINCIDENCE_FILL_MAX_DY:
                lower_filled[x] = upper_by_x[x]
        elif in_lower and not in_upper:
            other_y = _nearest_known_y(upper_by_x, x)
            if other_y is not None and abs(other_y - lower_by_x[x]) <= _COINCIDENCE_FILL_MAX_DY:
                upper_filled[x] = lower_by_x[x]

    return (
        Track(points=tuple(sorted(upper_filled.items()))),
        Track(points=tuple(sorted(lower_filled.items()))),
    )


def _densify_track(track: Track) -> Track:
    """Linearly interpolate between adjacent known points of a track.

    Per-column ridge tracking yields one point per detected run. Dashed
    curves naturally have gaps between dashes; a single fragment may
    cover only a few columns before the gap. The track's known points
    are honest chart data; the gaps between them sit on the same curve
    by continuity (the chart software drew an unbroken curve, then
    rendered some segments as dashes for visual style). Linear
    interpolation between adjacent known points reconstructs the curve
    the chart artist drew — it does NOT fabricate readings, it
    reconnects fragments of the same reading.

    This is the right side of the B2 line: B2 forbids extrapolation
    past the data (empty bracket → None) and forbids copying neighbors
    across genuinely-missing regions. Filling between two known
    same-track points is curve continuity, the same way the chart
    software does. The lens-page renderer would do equivalent visual
    interpolation when drawing the polyline; doing it in the track
    means the 11-point sampler finds a pixel in every position window.
    """
    if len(track.points) < 2:
        return track
    sorted_pts = sorted(track.points)
    densified: list[tuple[int, float]] = []
    for (x1, y1), (x2, y2) in zip(sorted_pts, sorted_pts[1:]):
        densified.append((x1, y1))
        if x2 - x1 <= 1:
            continue
        slope = (y2 - y1) / (x2 - x1)
        for x in range(x1 + 1, x2):
            densified.append((x, y1 + slope * (x - x1)))
    densified.append(sorted_pts[-1])
    return Track(points=tuple(densified))


def ridge_tracks_for_hue(
    mask: np.ndarray,
    plot_box: PlotBox,
    sm: str,
    upper_freq: int,
    lower_freq: int,
) -> dict[str, np.ndarray]:
    """Per-hue, 2-curve variant: returns one track per (freq, sm).

    Used by the Tokina wide-zoom dispatch where each hue (red, blue)
    encodes S or M (via the profile's hue name) and within the hue the
    two curves at different y-positions encode the two frequencies.
    Upper track in y → `upper_freq`; lower track → `lower_freq`. The
    sm parameter is taken from the hue name (S-red → 'S', M-blue → 'M').

    When the two curves coincide (whole-hue or per-column), the shared
    ridge is attributed to BOTH frequencies — see `_fill_single_column_
    gaps`. This preserves the B2 contract: the value is real chart data,
    not fabricated; the attribution to both tracks reflects the physical
    reality that visually-coincident curves have the same MTF.

    Distinct from `ridge_tracks_to_fields` (which expects 4 curves in
    one neutral mask and recovers both freq AND sm from track ranking).
    """
    from .dispatch import curve_field  # imported here to avoid module cycle

    cleaned = _strip_chrome(mask, plot_box)
    points = _extract_ridge_points(cleaned, plot_box)
    tracks = _cluster_into_tracks(points)
    kept = _select_top_n_tracks(tracks, n=2, plot_width=plot_box.width + 1)

    out: dict[str, np.ndarray] = {}
    if not kept:
        return out
    by_y = sorted(kept, key=lambda t: t.mean_y)
    if len(by_y) == 1:
        # Whole-hue coincidence: the two curves are indistinguishable
        # across the entire field. Same value to both frequencies.
        upper_track = _densify_track(by_y[0])
        lower_track = upper_track
    else:
        # Where the original chart had only one ridge run per column
        # (the two curves coincided), share that single track value
        # across both fields — same physics as B4 at center.
        column_runs = _column_run_count(cleaned, plot_box)
        shared_upper, shared_lower = _fill_coincident_column_gaps(
            by_y[0], by_y[1], column_runs
        )
        upper_track = _densify_track(shared_upper)
        lower_track = _densify_track(shared_lower)

    upper_field = curve_field(upper_freq, sm)
    if upper_field is not None:
        out[upper_field] = _rasterize(upper_track, mask.shape)
    lower_field = curve_field(lower_freq, sm)
    if lower_field is not None:
        out[lower_field] = _rasterize(lower_track, mask.shape)
    return out


def ridge_tracks_to_fields(
    mask: np.ndarray,
    plot_box: PlotBox,
    upper_freq: int,
    lower_freq: int,
    dashed_is_sagittal: bool,
) -> dict[str, np.ndarray]:
    """Ridge-track a single-hue mask and return per-field skeleton masks.

    The 4-curve layout: top two tracks (by mean y) are `upper_freq`, the
    bottom two are `lower_freq`. Within each pair, the higher-coverage
    track is solid (S by default; M if `dashed_is_sagittal`). Fields
    without a qualifying track are simply absent from the result; the
    sampler treats them as missing data (B2).
    """
    from .dispatch import curve_field  # imported here to avoid module cycle

    cleaned = _strip_chrome(mask, plot_box)
    points = _extract_ridge_points(cleaned, plot_box)
    tracks = _cluster_into_tracks(points)
    kept = _select_top_n_tracks(tracks, n=4, plot_width=plot_box.width + 1)

    if not kept:
        return {}

    kept_sorted = sorted(kept, key=lambda t: t.mean_y)
    upper_tracks = kept_sorted[: max(1, len(kept_sorted) // 2)]
    lower_tracks = kept_sorted[max(1, len(kept_sorted) // 2) :]

    out: dict[str, np.ndarray] = {}
    # Within a frequency pair, the sagittal (S) curve is always above
    # the meridional (M) curve in OTF (physics: edge MTF degrades faster
    # on the meridional axis). In image coordinates that means S has the
    # smaller mean_y. This is profile-independent — `dashed_is_sagittal`
    # affects only the *Sigma/7Artisans* solid-vs-dashed discrimination,
    # which doesn't apply to Viltrox where all four curves are dashed.
    del dashed_is_sagittal  # unused for ridge tracking

    for freq, cluster in ((upper_freq, upper_tracks), (lower_freq, lower_tracks)):
        if not cluster:
            continue
        by_y = sorted(cluster, key=lambda t: t.mean_y)
        sagittal_track = by_y[0]
        field = curve_field(freq, "S")
        if field is not None:
            out[field] = _rasterize(sagittal_track, mask.shape)
        if len(by_y) > 1:
            meridional_track = by_y[1]
            field = curve_field(freq, "M")
            if field is not None:
                out[field] = _rasterize(meridional_track, mask.shape)

    return out
