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

import cv2
import numpy as np

from .types import PlotBox


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
        upper_track = _extend_track_to_plot_edges(
            _densify_track(by_y[0]), plot_box
        )
        lower_track = upper_track
    else:
        # Where the original chart had only one ridge run per column
        # (the two curves coincided), share that single track value
        # across both fields — same physics as B4 at center.
        column_runs = _column_run_count(cleaned, plot_box)
        shared_upper, shared_lower = _fill_coincident_column_gaps(
            by_y[0], by_y[1], column_runs
        )
        upper_track = _extend_track_to_plot_edges(
            _densify_track(shared_upper), plot_box
        )
        lower_track = _extend_track_to_plot_edges(
            _densify_track(shared_lower), plot_box
        )

    out[curve_field(upper_freq, sm)] = _rasterize(upper_track, mask.shape)
    out[curve_field(lower_freq, sm)] = _rasterize(lower_track, mask.shape)
    return out


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
    curve coincidence — same physics as `ridge_tracks_for_hue`).

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

    Distinct from:
      - `ridge_tracks_for_hue`: HUE_IS_CURVE; hue carries S or M, the
        two tracks within the hue are two frequencies (ranked by mean_y).
      - `ridge_tracks_to_fields`: single neutral mask carrying all four
        curves; tracks ranked by mean_y for frequency, then by coverage
        within each frequency pair for S/M.
    """
    from .dispatch import curve_field  # imported here to avoid module cycle

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
        # both fields — same B4 physics as `ridge_tracks_for_hue`.
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


# #1347: fraction of plot width (from the left) treated as the "interior"
# field region when `interior_anchored` band assignment is on. On the
# multifreq-press-kit panels the wide-aperture curves crash and converge
# past the APS-C image-circle corner (field > ~10mm of a 14mm axis); the
# left 60% (field 0..~8.4mm) is where the 2N curves still separate into
# clean frequency bands, so a track's mean y THERE is a robust band
# anchor even when its global mean y is pulled down by the corner dive.
_INTERIOR_FIELD_FRACTION: float = 0.6


def _interior_mean_y(track: Track, plot_box: PlotBox) -> float:
    """Mean y of a track over the interior (left) field region.

    Falls back to the track's global `mean_y` when the track has no
    points in the interior (e.g. a fragment that exists only near the
    corner) so every track still gets a comparable band anchor.
    """
    x_cut = plot_box.x_left + _INTERIOR_FIELD_FRACTION * plot_box.width
    interior_ys = [y for x, y in track.points if x <= x_cut]
    if not interior_ys:
        return track.mean_y
    return float(np.mean(interior_ys))


def _interior_order_differs(kept: list[Track], plot_box: PlotBox) -> bool:
    """True when ordering the kept tracks by interior y differs from
    ordering them by global mean y.

    This is the signature of a curve crossing another near the corner:
    a track sitting above a sibling in the interior can dive past it as
    the wide-aperture curves crash toward the APS-C corner, so its global
    mean y overtakes the sibling's while its interior y does not. When
    the two orderings agree, the corner did not reorder the tracks and
    the global-mean-y equal split is reliable; only when they differ is
    the middle frequency at risk of being mis-filed, so only then is
    interior anchoring worth its cost -- and applying it unconditionally
    regresses flat panels whose true band populations are unbalanced
    (32mm/50mm stopped are 1/1/3, which k-means wrongly rebalances to
    1/2/2). See #1347.
    """
    by_interior = sorted(kept, key=lambda t: _interior_mean_y(t, plot_box))
    by_global = sorted(kept, key=lambda t: t.mean_y)
    return by_interior != by_global


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


def _assign_interior_anchored_bands(
    kept: list[Track],
    frequencies_lpmm: tuple[int, ...],
    plot_box: PlotBox,
    mask_shape: tuple[int, int],
) -> dict[str, np.ndarray]:
    """Assign kept tracks to (frequency, S/M) fields by interior y-band.

    Sorts tracks by interior mean y, clusters them into
    `len(frequencies_lpmm)` bands via optimal 1-D k-means, maps the
    bands top->bottom onto the (upper->lower) frequency order, and
    within each band takes S (upper) and M (lower). When a band caught
    more than the two real curves (a halo or corner fragment), the two
    highest-coverage tracks win. A band with one track reports S only;
    the sampler treats the absent field as missing data (B2 contract).
    """
    from .dispatch import curve_field  # imported here to avoid module cycle

    n_freqs = len(frequencies_lpmm)
    ordered = sorted(kept, key=lambda t: _interior_mean_y(t, plot_box))
    interior_ys = [_interior_mean_y(t, plot_box) for t in ordered]
    bounds = _optimal_1d_kmeans_bounds(interior_ys, n_freqs)

    out: dict[str, np.ndarray] = {}
    for (lo, hi), freq in zip(bounds, frequencies_lpmm):
        band = ordered[lo:hi]
        if len(band) > 2:
            band = sorted(band, key=lambda t: t.coverage, reverse=True)[:2]
        by_y = sorted(band, key=lambda t: _interior_mean_y(t, plot_box))
        out[curve_field(freq, "S")] = _rasterize(by_y[0], mask_shape)
        if len(by_y) > 1:
            out[curve_field(freq, "M")] = _rasterize(by_y[1], mask_shape)
    return out


def ridge_tracks_to_fields_multifreq(
    mask: np.ndarray,
    plot_box: PlotBox,
    frequencies_lpmm: tuple[int, ...],
    dashed_is_sagittal: bool,
    interior_anchored: bool = False,
) -> dict[str, np.ndarray]:
    """Ridge-track a single-hue mask and return per-field skeleton masks
    for an N-frequency chart.

    The 2N-curve layout: the kept tracks (by mean y) split into N
    equal-sized y-bands. Each band maps to one frequency in upper→lower
    order. Within each band the top track (smaller mean_y) is sagittal
    (S), the next is meridional (M). Fields without a qualifying track
    are absent from the result; the sampler treats them as missing
    data (B2 contract).

    `frequencies_lpmm` MUST be passed in upper→lower screen order,
    which by convention is also low→high lp/mm (a 3-freq Zeiss
    Touit chart prints 10 on top, 20 in the middle, 40 at the bottom).

    When `interior_anchored` is set (multifreq-press-kit profiles,
    #1347), the kept tracks are assigned to frequency bands by
    clustering their INTERIOR y-position rather than by the
    global-mean-y equal-size split. The equal split collapses to 1/1/3
    when a sparse dashed curve is lost to the coverage floor and then
    mis-files the middle frequency under the highest; interior
    clustering keeps the assignment correct because the frequency
    bands still separate cleanly in the interior even after the curves
    crash and converge near the corner.
    """
    from .dispatch import curve_field  # imported here to avoid module cycle

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

    # Within a frequency pair, the sagittal (S) curve is always above
    # the meridional (M) curve in OTF (physics: edge MTF degrades faster
    # on the meridional axis). In image coordinates that means S has the
    # smaller mean_y. This is profile-independent — `dashed_is_sagittal`
    # affects only the *Sigma/7Artisans* solid-vs-dashed discrimination,
    # which doesn't apply to Viltrox where all four curves are dashed.
    del dashed_is_sagittal  # unused for ridge tracking

    # Interior-anchored band assignment (#1347). Fires only for the
    # narrow case it fixes: a curve was lost to the coverage floor
    # (len(kept) < 2N, so the equal split below would collapse the bands)
    # AND the corner crash reordered the survivors. Needs at least
    # n_freqs tracks to fill the bands. When the survivors keep their
    # order, the equal split is reliable and k-means would wrongly force
    # balanced bands onto an unbalanced structure -- the flat-panel
    # regression `_interior_order_differs` guards against.
    if (
        interior_anchored
        and n_freqs <= len(kept) < expected_tracks
        and _interior_order_differs(kept, plot_box)
    ):
        return _assign_interior_anchored_bands(
            kept, frequencies_lpmm, plot_box, mask.shape
        )

    kept_sorted = sorted(kept, key=lambda t: t.mean_y)

    # Split kept tracks into N equal-size y-bands. When the kept count is
    # below 2N (e.g. coincident curves collapse a stopped panel from 6
    # to 5 tracks on Zeiss Touit k=4), the last band absorbs the
    # remainder so the highest frequency reports what data exists rather
    # than silently dropping it.
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
        out[curve_field(freq, "S")] = _rasterize(by_y[0], mask.shape)
        if len(by_y) > 1:
            out[curve_field(freq, "M")] = _rasterize(by_y[1], mask.shape)

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
