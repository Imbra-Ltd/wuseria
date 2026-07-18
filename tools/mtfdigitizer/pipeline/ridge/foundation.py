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
- **N-frequency layout** (>2 frequencies). The track-identification
  step generalizes to `2 * len(frequencies_lpmm)` tracks split into
  `len(frequencies_lpmm)` y-bands. `ridge_tracks_to_fields_multifreq`
  drives this; `ridge_tracks_to_fields` is a 2-freq convenience
  wrapper kept for Viltrox callers. Zeiss Touit's 3-frequency
  (10/20/40 lp/mm) wide-aperture panels extract cleanly; tightly
  bundled stopped panels still hit the coincidence failure mode below.

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

import numpy as np

from ..types import PlotBox


# A column run shorter than this is single-pixel noise (one anti-aliased
# stray pixel between dash and gridline). Filtered before clustering.
_MIN_RUN_LENGTH: int = 1

# A column run taller than this is vertical chrome (axis tick labels,
# axis line ink, legend box edge) that `_strip_chrome` does not catch —
# its row-coverage pass strips horizontal chrome only. Real MTF curve
# ridges measured across the reference set fit within ~3 px at p95 and
# ~13 px at p99; runs >20 px are chrome. The fisheye #1122 case fired
# 52-px and 265-px runs at the leftmost two plot columns (Y-axis "1"
# label + axis line) and corrupted downstream densify-pass interpolation.
_MAX_RUN_LENGTH: int = 20

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

# Isolated-candidate filter (#1157): a ridge candidate is a "real curve
# pixel" only if it belongs to a connected cluster spanning at least
# `_RIDGE_ISOLATION_MIN_COLS` distinct columns, where two candidates
# connect when their column distance is <= `_RIDGE_ISOLATION_DX` AND
# row distance <= `_RIDGE_ISOLATION_DY`. Standalone 1-2 column "blobs"
# (gridline fragments surviving `_strip_chrome`, JPEG/AA noise between
# real curves) are rejected. Sized to:
#   - Bridge dashed-curve gaps (dashes 3-4 px wide, gaps 3-4 px →
#     adjacent column has a candidate within ~5 rows even for sparsest
#     dashed curves), so real dashed candidates survive.
#   - Bridge the right-axis ~3-column drop-out where a dashed curve's
#     center pixels go missing before the corner (#1157 max.freq30M
#     case on TTartisan 7.5 fisheye).
#   - Drop 1-2 column blobs that the DP otherwise picks as the wrong
#     ridge (gridline fragments at y=143, mid-air noise at y=204).
_RIDGE_ISOLATION_DX: int = 4
_RIDGE_ISOLATION_DY: int = 8
_RIDGE_ISOLATION_MIN_COLS: int = 3


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

# Axis-halo strip parameters (#1165). Rows immediately adjacent to a
# stripped border row that have at least `_AXIS_HALO_MIN_COVERAGE`
# column coverage are treated as anti-aliased halo and stripped too.
# Confined to `_AXIS_HALO_DEPTH` rows of the border to avoid touching
# genuine curve readings near MTF=1.0 or MTF=0.0.
#
# Sized from the cohort:
# - TTartisan tilt-50 GFX template: 80 pixels (15.5%) at y_top+3,
#   60 pixels at y_top+4 — pure top-axis anti-aliased halo, no real
#   curve at MTF~0.99 here. Stripped.
# - TTartisan 7.5 fisheye: 2 pixels (0.4%) at each of y_top+1..+4 —
#   genuine freq10S/M near MTF=1.0 in the corner. Kept.
# Threshold 10% separates them cleanly.
_AXIS_HALO_DEPTH: int = 4
# Coverage band for axis-halo: rows with coverage in
# [_AXIS_HALO_MIN_COVERAGE, _AXIS_HALO_MAX_COVERAGE) within
# `_AXIS_HALO_DEPTH` of a border are anti-aliased halo and stripped.
# Below MIN: sparse genuine curve corners (7.5 fisheye: 0.4% near
# MTF=1.0). Above MAX: dense real curves close to the axis (Viltrox
# 10S contrast: 36-65% within y_top+1..y_top+6 because the curves
# physically sit near MTF~0.95-1.0).
_AXIS_HALO_MIN_COVERAGE: float = 0.12
_AXIS_HALO_MAX_COVERAGE: float = 0.30


def _strip_chrome(mask: np.ndarray, plot_box: PlotBox) -> np.ndarray:
    """Zero out plot-box border rows + rows with >=90% horizontal coverage.

    Two chrome categories are stripped:

    1. **Plot-box border rows** (`y_top` and `y_bottom`) — the X-axis
       lines that bound the plot. They are chrome by construction;
       any curve ink at those exact y values would mean MTF=1.0 or
       MTF=0.0, which is degenerate and almost always border ink, not
       a real reading. Stripping these unconditionally fixes #1090
       (TTartisan 100mm-macro grey mask: bottom border at 87% coverage
       slipped below the 90% threshold and was selected as the highest-
       coverage solid track, stealing the freq30S slot from the real
       curve at MTF~0.78).

    2. **High-coverage rows** (>=90% of plot width) — printed OTF
       gridlines and any inset border lines. Without this the ridge
       tracker would pick OTF=0.0 / OTF=1.0 (chart frame) as curves.

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
    # Always strip the plot-box border rows (X-axis lines) — fixes
    # #1090 where the bottom border at 87% coverage slipped below the
    # high-coverage threshold and was misread as a curve at MTF=0.
    cleaned[plot_box.y_top, plot_box.x_left : plot_box.x_right + 1] = 0
    cleaned[plot_box.y_bottom, plot_box.x_left : plot_box.x_right + 1] = 0
    # Also strip rows within `_AXIS_HALO_DEPTH` of the border that
    # have at least `_AXIS_HALO_MIN_COVERAGE` column coverage — see
    # #1165. TTartisan tilt-50's max-10-black mask has 80 sparse halo
    # pixels at y_top+3 (15.5% coverage) from the top axis anti-
    # aliasing that survive the 90% chrome threshold. The DP latched
    # onto them as freq10M candidates when the dashed T10 curve was in
    # a dash gap, producing 0.99 spikes interleaved with real readings.
    # Threshold 12% separates that halo from genuine corner readings
    # near MTF=1.0 (~0.4% coverage on 7.5 fisheye).
    halo_min_count = int(_AXIS_HALO_MIN_COVERAGE * width)
    halo_max_count = int(_AXIS_HALO_MAX_COVERAGE * width)
    for dy in range(1, _AXIS_HALO_DEPTH + 1):
        for y in (plot_box.y_top + dy, plot_box.y_bottom - dy):
            if plot_box.y_top <= y <= plot_box.y_bottom:
                row = cleaned[y, plot_box.x_left : plot_box.x_right + 1]
                count = int(row.sum())
                if halo_min_count <= count < halo_max_count:
                    cleaned[y, plot_box.x_left : plot_box.x_right + 1] = 0
    for y in range(plot_box.y_top, plot_box.y_bottom + 1):
        row = cleaned[y, plot_box.x_left : plot_box.x_right + 1]
        if int(row.sum()) >= min_count:
            cleaned[y, plot_box.x_left : plot_box.x_right + 1] = 0
    return cleaned


def _column_runs(
    column: np.ndarray, gap_tolerance: int = _RIDGE_RUN_GAP_TOLERANCE
) -> list[tuple[float, int]]:
    """Group a binary column into runs; return (centroid_y, length) per run.

    Runs outside ``[_MIN_RUN_LENGTH, _MAX_RUN_LENGTH]`` are dropped: too
    short is anti-aliasing noise, too tall is vertical chrome (axis
    label glyphs, axis line) that `_strip_chrome`'s row-coverage pass
    misses.
    """
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
        if _MIN_RUN_LENGTH <= length <= _MAX_RUN_LENGTH:
            runs.append(((start + prev) / 2.0, length))
        start = y_int
        prev = y_int
    length = prev - start + 1
    if _MIN_RUN_LENGTH <= length <= _MAX_RUN_LENGTH:
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


def _filter_isolated_ridge_points(
    points: list[tuple[int, float]],
    *,
    dx: int = _RIDGE_ISOLATION_DX,
    dy: int = _RIDGE_ISOLATION_DY,
    min_cluster_cols: int = _RIDGE_ISOLATION_MIN_COLS,
) -> list[tuple[int, float]]:
    """Drop ridge candidates whose local cluster spans fewer than
    ``min_cluster_cols`` distinct columns.

    Two candidates are in the same cluster when their column distance is
    ``<= dx`` and row distance ``<= dy`` (transitively, via union-find).
    Real curves — even sparse dashed ones — form long multi-column
    clusters. Standalone 1-2 column "blobs" are gridline fragments
    surviving ``_strip_chrome`` (low-coverage 0.9 gridline at TTartisan
    7.5 max-grey y=143) or mid-air JPEG/AA noise (TTartisan 7.5
    max-grey y=204 between the orange S30 and T30 curves at the right
    edge). Both fool the ridge DP into picking the wrong path. See
    issue #1157.

    Conservative bridging: ``dx=4, dy=8`` keeps real dashed candidates
    even across a ~3-column drop-out before the right axis (the
    TTartisan 7.5 max.freq30M case where the curve center pixels go
    missing for x in [604, 606] but the corner pixel at x=607 is real).
    """
    if not points:
        return points
    n = len(points)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    by_col: dict[int, list[int]] = {}
    for idx, (col, _y) in enumerate(points):
        by_col.setdefault(col, []).append(idx)

    for idx, (col, y) in enumerate(points):
        for d in range(1, dx + 1):
            for other in by_col.get(col + d, ()):
                if abs(points[other][1] - y) <= dy:
                    union(idx, other)

    comp_cols: dict[int, set[int]] = {}
    for idx, (col, _y) in enumerate(points):
        comp_cols.setdefault(find(idx), set()).add(col)

    return [
        points[idx]
        for idx in range(n)
        if len(comp_cols[find(idx)]) >= min_cluster_cols
    ]


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


def _track_x_range(t: Track) -> tuple[int, int]:
    xs = [x for x, _ in t.points]
    return min(xs), max(xs)


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
    the `n` longest above the coverage floor.

    Order matters (#1097): fusion runs BEFORE the coverage floor. A
    curve that fragments into several sub-floor pieces (TTartisan T10
    dive: 67 + 48 + 9 = 124 columns split over three fragments, none
    above the 52-column floor individually) only re-enters track
    selection if it gets stitched back together first.
    """
    deduped = _merge_near_duplicate_tracks(tracks)
    fused = _merge_fragmented_tracks(deduped)
    floor = int(_MIN_TRACK_COVERAGE * plot_width)
    qualified = [t for t in fused if t.coverage >= floor]
    qualified.sort(key=lambda t: t.coverage, reverse=True)
    return qualified[:n]


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


# Y-diversity tie-breaker bounds for `_pick_two_tracks_y_diverse` (#1095):
# how much coverage must the 3rd-ranked track retain, and how much more
# separated from the 1st must it be in mean_y, to win the 2nd slot over
# the natural 2nd-ranked candidate.
_DIVERSITY_3RD_COVERAGE_MIN_RATIO: float = 0.4
_DIVERSITY_3RD_MEAN_Y_RATIO: float = 2.0


def _pick_two_tracks_y_diverse(by_coverage: list[Track]) -> list[Track]:
    """Pick two tracks from a coverage-sorted list, preferring y-diversity
    when a closely-paired second candidate looks like a parallel halo.

    Without diversity, ``by_coverage[:2]`` picks the two highest-coverage
    tracks — which on TTartisan max-aperture grey (#1095) means the
    solid grey line's top-edge and bottom-edge halos (10 px apart),
    not the solid + dashed curves the field is supposed to encode.
    The dashed T30 with its deep dip lands as the 3rd-ranked track and
    gets dropped.

    Rule: if the 3rd-ranked track has substantial coverage relative to
    the 2nd (≥ ``_DIVERSITY_3RD_COVERAGE_MIN_RATIO``) AND it sits much
    further from the 1st in mean_y than the 2nd does (≥
    ``_DIVERSITY_3RD_MEAN_Y_RATIO`` × the 1st→2nd distance), the 3rd
    track replaces the 2nd. The 2nd is then almost certainly a parallel
    halo of the 1st rather than the field's second physical curve, and
    the 3rd is the real second curve.

    Black 10 lp/mm at f/1.2 verifies the negative case: tracks [0]+[1]
    are 12 px apart (the genuine S10+T10 pair); the 3rd track has only
    24% of the 2nd's coverage and sits 1.8× further → ratio test fails
    → top-2 stays unchanged.
    """
    if len(by_coverage) < 3:
        return by_coverage[:2]
    first, second, third = by_coverage[0], by_coverage[1], by_coverage[2]
    coverage_ratio = third.coverage / second.coverage if second.coverage else 0.0
    first_to_second = abs(first.mean_y - second.mean_y)
    first_to_third = abs(first.mean_y - third.mean_y)
    if first_to_second == 0:
        return [first, third]
    mean_y_ratio = first_to_third / first_to_second
    if (
        coverage_ratio >= _DIVERSITY_3RD_COVERAGE_MIN_RATIO
        and mean_y_ratio >= _DIVERSITY_3RD_MEAN_Y_RATIO
    ):
        return [first, third]
    return [first, second]


def _fill_coincident_column_gaps_extending(
    track_a: Track,
    track_b: Track,
    column_runs: dict[int, int],
) -> tuple[Track, Track]:
    """Variant of `_fill_coincident_column_gaps` that also fills *outside*
    a track's known x range, anchored on endpoint continuity.

    The plain `_fill_coincident_column_gaps` fills only where both
    tracks have *some* nearby known y to compare against. That works
    for the Tokina case, where both curves span the full field and
    coincidence is column-by-column. It does NOT work when one
    physical curve runs through a long single-ridge coincidence region
    at one end of the field and the other curve only appears in the
    divergent region (TTartisan max-aperture #1095): the absent track
    has no known y at the coincidence columns, so the original
    function leaves it absent.

    Generalisation: a single-run column attributes its value to BOTH
    physical curves by B4 physics. Outside the absent track's known
    x range, instead of comparing to its interpolated y (None), check
    that the present track's value at this column lies within
    `_COINCIDENCE_FILL_MAX_DY` of the absent track's *nearest endpoint*
    y. If it does, the present track's y is continuous with the absent
    track's curve at the boundary — extend the absent track by sharing
    this column's value. If it doesn't, the curves are clearly
    separated here and the column belongs only to the present track.
    """
    a_by_x: dict[int, float] = {x: y for x, y in track_a.points}
    b_by_x: dict[int, float] = {x: y for x, y in track_b.points}

    a_filled = dict(a_by_x)
    b_filled = dict(b_by_x)

    def _endpoint_y_nearest(track_by_x: dict[int, float], x: int) -> float | None:
        if not track_by_x:
            return None
        xs = sorted(track_by_x)
        if x < xs[0]:
            return track_by_x[xs[0]]
        if x > xs[-1]:
            return track_by_x[xs[-1]]
        return None  # inside range — caller already handled this case

    for x, run_count in column_runs.items():
        if run_count != 1:
            continue
        in_a = x in a_by_x
        in_b = x in b_by_x
        if in_a == in_b:
            continue  # both have it or neither does
        present, absent_by_x, present_filled, absent_filled = (
            (a_by_x[x], b_by_x, a_filled, b_filled)
            if in_a else
            (b_by_x[x], a_by_x, b_filled, a_filled)
        )
        # First try the in-range nearest-y test (same as the plain
        # function — required for the Tokina case to keep working).
        other_y = _nearest_known_y(absent_by_x, x)
        if other_y is None:
            # Out-of-range case: anchor on the absent track's nearest
            # endpoint instead. This handles the TTartisan case where
            # one curve has no points yet in the coincidence region.
            other_y = _endpoint_y_nearest(absent_by_x, x)
        if other_y is None:
            continue  # absent track is empty — nothing to anchor on
        if abs(other_y - present) <= _COINCIDENCE_FILL_MAX_DY:
            absent_filled[x] = present

    return (
        Track(points=tuple(sorted(a_filled.items()))),
        Track(points=tuple(sorted(b_filled.items()))),
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


# Maximum gap a track may be extended past to reach a plot-box edge
# (#1171). Dashed curves naturally end at the last dash before the
# edge; on TTartisan charts the gap between the last dash centroid
# and the plot edge is up to ~12 px when a dash gap aligns with the
# corner. Beyond this we refuse to extend — the corner sampler returns
# None (B2 fail-safe) and the lens-page renderer ends the polyline at
# the last known sample.
_EDGE_EXTRAPOLATION_MAX = 12


def _extend_track_to_plot_edges(track: Track, plot_box: PlotBox) -> Track:
    """Extend a densified track to the plot-box left/right edges.

    Per-column ridge tracking ends at the last dash centroid before
    the plot edge. When a dashed curve's last dash sits a few px short
    of the plot edge (the dash pattern's gap aligns with the corner),
    the sampler's 6-px edge bracket finds no skeleton pixel and the
    corner reads None.

    Extension uses the last-known y (flat) rather than the trailing
    slope: the gap is small (<= 12 px) and the densified track's
    trailing slope is dominated by inter-dash centroid noise from the
    last 2-3 dashes, which on stopped-aperture curves can be ±2 px/col
    even when the curve is visually flat — slope-extrapolation across
    6 px then overshoots by MTF ~0.08, fabricating a dive that isn't
    on the chart (tilt-50 stopped-T10 observed in #1171). Flat
    extension stays within ~MTF 0.01 of the curve's visual trajectory
    across the small gap.

    Refuses gaps > `_EDGE_EXTRAPOLATION_MAX`: past the bracket window
    we genuinely don't know the curve's behavior (it may be in a sharp
    corner crash, ADR-038 §B2). Sized to cover observed dash-gap-at-
    edge slack on the TTartisan cohort.
    """
    if not track.points:
        return track
    sorted_pts = sorted(track.points)
    extended: list[tuple[int, float]] = list(sorted_pts)

    left_x, left_y = sorted_pts[0]
    if left_x > plot_box.x_left and left_x - plot_box.x_left <= _EDGE_EXTRAPOLATION_MAX:
        head = [(x, left_y) for x in range(plot_box.x_left, left_x)]
        extended = head + extended

    right_x, right_y = extended[-1]
    if (
        right_x < plot_box.x_right
        and plot_box.x_right - right_x <= _EDGE_EXTRAPOLATION_MAX
    ):
        for x in range(right_x + 1, plot_box.x_right + 1):
            extended.append((x, right_y))

    return Track(points=tuple(extended))

