# ADR-049: Per-column ridge DP for freq-split dispatch

**Status:** Accepted
**Date:** 2026-06-09

## Context

#1100 documented the TTartisan freq30 corner failure: the extractor
swaps S30 and T30 labels at the right corner (freq30S reads T30's
0.40 instead of S30's 0.29, freq30M reads S30's 0.29 instead of
T30's 0.40). PR #1099's spike attributed the failure to greedy
column-walk clustering plus coverage-based S/M labeling.

A probe of the greedy clusterer's per-column decisions revealed two
compounding mechanisms:

1. **Identity swap through crossings.** TTartisan grey freq30 has
   S30 and T30 crossing each other around x=585 (the corner
   crossing). Before the crossing S30 is the upper curve (lower y,
   higher MTF); after, T30 is upper. The greedy walker's
   "upper-history" track picks up whichever ridge is closest in y
   at the divergence point — which is now T30, the OTHER physical
   curve. Result: track A reads T30's corner value while having
   been S30's path for most of the field.

2. **Coverage-based labeling on a frankenstein.** The dispatch then
   labels the higher-coverage track as "solid" (= S by default). The
   frankenstein track has the highest coverage; it gets labeled S
   but is reporting T30's corner value. The lower-coverage actual
   S30 corner fragment gets labeled M. Both labels are swapped.

### Approaches ruled out

- **Slope-projecting tie-break** (#1100 option a). Wouldn't catch
  the corner crossing: at the swap, both candidates have small dy
  (1-4 px) and gentle slopes; greedy already makes the locally
  correct choice. The error is global, not local.
- **Tighter close kernel + GEODESIC_DP** (#1100 option b discussed,
  probed in this session). The TTartisan grey freq30 raw mask
  has S30 and T30 **already fused into one connected component**
  (~1080 px) because their anti-aliased halos touch at the pixel
  level. No kernel width (1, 3, 5, 7) separates them. CC-based
  dispatch loses ~90% of T30. ADR-045 documented this fusion as
  the reason FREQUENCY_PER_HUE_RIDGE exists.
- **Mask-based DP** (`extract_two_curves_dp`). Documented blind
  spot #1044 fires on the exact TTartisan pattern: S30 dives
  while T30 stays at higher MTF; Viterbi prefers the smoother
  (flat) path through dilation echo and loses the dive.
- **Continuity-based S/M on greedy tracks** (PR #1099 spike). The
  failed attempt; regressed 7artisans because greedy tracks are
  frankensteins and continuity measured on a frankenstein gives
  noisy results.

## Decision

Replace the greedy clusterer + coverage labeling in
`ridge_tracks_for_hue_freq_split` with **per-column ridge DP**:
Viterbi over the per-column ridge centroid set, two complementary
passes to extract two coherent paths, S/M assignment via mask
continuity measured on each coherent path.

```
+--------------------+        +---------------------+
| ridge centroids    |  pass1 |  upper-MTF path     |
| per column, sparse | -----> |  (one y per column) |
| (no mask, no       |        +---------------------+
|  dilation echo)    |
+--------------------+        +---------------------+
                       pass2  |  lower-MTF path     |
                       erase  |  (pass-1 ridges     |
                       ----->  |   blocked)         |
                              +---------------------+

Continuity on raw mask, in a y-band around each path:
  solid line  -> ~1.0 (ink at every column)
  dashed line -> ~0.5-0.7 (periodic ink/gap)
S/M assigned by dashed_is_sagittal mapping.
```

### Why this avoids both failure modes

- **No CC fusion problem.** Input is per-column ridge centroids,
  already computed by `_extract_ridge_points`. Each column may
  contribute 0, 1, or 2+ y-values. No close kernel involved; no
  CC connectivity required.
- **No cliff-corner blind spot.** Mask-DP's #1044 happens because
  the dilation echo of a parallel curve creates "easy" path
  alternatives that the smoothness prior prefers over the real
  dive. Per-column ridge DP has only the actual ridge centroids
  as candidates — there's no echo. When S30 dives at the corner,
  its centroid is at y=361 (OTF 0.29); the DP picks it because
  no smoother alternative exists at that column.
- **No frankenstein.** When the curves cross, DP picks the
  globally smoothest assignment of one ridge per column to each
  of two paths. After a crossing, what was the upper path picks
  up whichever ridge is the smooth continuation of its prior
  trajectory — which is the SAME physical curve, now on the
  lower side of the other.

### Tuning

- `_RIDGE_DP_ALPHA = 0.30` — smoothness weight reused from
  `dp_extract._ALPHA` (Tokina reference-set calibration). Same
  trade-off shape, same range applies.
- `_RIDGE_DP_ERASE_HALF = 2` — pass 2 erases ridges within ±2 px
  of pass 1's path per column. Sized to admit the second curve
  when curves run within ~5 px of each other (TTartisan grey
  freq30 in the left half) while still forbidding pass 2 from
  re-picking the curve pass 1 took.

### Carry-forward filter

DP carries state across empty columns via "coast at zero data
cost". For pass 1 this is correct (bridge dash gaps). For pass 2
where ridges were erased, the carry-forward state inherits pass
1's y values — exactly the kind of inter-curve contamination DP
was meant to prevent.

`_path_to_track` filters columns based on an `on_ridge` flag from
DP: a column is included iff DP picked a real ridge centroid there.
Columns where the path coasted (carry-forward) are dropped. The
downstream `_fill_coincident_column_gaps_extending` and
`_densify_track` steps handle gap-bridging via coincidence-fill
and linear interpolation — the right place to draw the line
between "real path" and "interpolated path".

## Consequences

### TTartisan 50mm f/1.2 max-aperture (closes #1100)

The headline win:

| Field   | Baseline p95 | After p95 | Change           |
| ------- | ------------ | --------- | ---------------- |
| freq10S | 0.027        | **0.013** | improved         |
| freq10M | 0.013        | **0.014** | flat             |
| freq30S | **0.140**    | **0.012** | massive (-0.128) |
| freq30M | **0.128**    | **0.020** | massive (-0.108) |

All four fields now within ±0.025 except one mid-field outlier on
freq30M (fraction 0.6: 0.43 vs GT 0.36, |Δ|=0.072). The freq30
corner inversion is **completely fixed**:

- freq30S corner reads 0.30 (was 0.40, GT 0.29) → |Δ| 0.11 → 0.011
- freq30M corner reads 0.40 (was 0.30, GT 0.40) → |Δ| 0.10 → 0.003

### Aggregate (14-anchor calibration set)

- paired comparisons: 604 → 627 (more samples paired — DP captures
  positions the greedy walker dropped)
- median |Δ|: 0.0112 (unchanged)
- p95 |Δ|: 0.0633 → 0.0640 (essentially flat)
- in band ±0.05: 93.0% → 92.5% (3-sample swing)

### Known limitation: 7artisans corner crossing

7artisans freq10S and freq10M corner samples have the same
crossing-identity-swap problem at a different magnitude:

| Field             | Baseline p95 | After p95 |
| ----------------- | ------------ | --------- |
| 7artisans freq10S | 0.054        | 0.124     |
| 7artisans freq10M | 0.064        | 0.119     |

This is the same root cause #1100 documented — at a tight
crossing the DP smoothness prior doesn't disambiguate (both
candidates have equal smoothness cost). On TTartisan the
crossing is at the right corner with enough x-distance for DP
to pick the smooth continuation; on 7artisans the crossing
geometry causes the DP to swap which path is which exactly at
the corner sample.

Mid-field samples (positions 0.0-0.9) are within ±0.05 on
7artisans for all fields. Only the corner sample is wrong.

Tracked as #1104. Likely fix: per-column dash-vs-solid detection
on the raw mask gives each path an "I'm the solid line" or "I'm
the dashed line" identity that DP can use as a soft constraint
through the crossing, breaking ties even when the smoothness
prior cannot.

### Architectural note

The `RIDGE_TRACKING` dispatch for 4-curve charts
(`ridge_tracks_to_fields`) still uses greedy clustering. Those
charts (Viltrox) don't have the same crossing pattern — the four
curves are at clearly different y bands per ADR-038. Extending
ridge-DP to the 4-curve case is a future option if a Viltrox-like
chart starts hitting curve crossings.
