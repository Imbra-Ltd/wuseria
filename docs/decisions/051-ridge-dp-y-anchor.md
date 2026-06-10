# ADR-051: Y-band coherence anchor for ridge DP

**Status:** Accepted
**Date:** 2026-06-10

## Context

ADR-049 introduced per-column ridge DP in
`ridge_tracks_for_hue_freq_split` and closed the TTartisan freq30
corner identity-swap (#1100). Its "Known limitation: 7artisans corner
crossing" documented a regression on the 7artisans 50mm f/1.2 Mark II
calibration anchor:

| Field             | Pre-#1100 p95 | Post-#1100 p95 |
| ----------------- | ------------- | -------------- |
| 7artisans freq10S | 0.054         | 0.124          |
| 7artisans freq10M | 0.064         | 0.119          |

A probe on the 7artisans blue (freq10) hue confirmed the failure shape:
the two physical curves do NOT cross at the corner — they run parallel
about 28 px apart (upper at y≈115-127, lower at y≈140-160). But the
DP smoothness prior alone cannot distinguish them: when a dash gap
leaves only one ridge centroid at a column, the DP is forced to land on
it. If that centroid belongs to the OTHER curve, pass 1's identity
swaps. ADR-049's smoothness term penalises the swap but the global
optimum still routes pass 1 through the lower band at the corner.

The issue's proposed fix (Option 1: dash-vs-solid identity from column
run lengths) does not work here — both 7artisans curves render with
similar run-length distributions (p50=2, p95=4), so column run length
cannot separate them.

Probe also revealed that the TTartisan grey-30 case has fundamentally
different geometry: 54% of columns carry three-or-more ridges from
antialiased echoes of adjacent curves. The same fix that helps
7artisans would drag pass 1 off the legitimate TTartisan freq30 dive.
The two scenes need different DP costs.

## Decision

Add an opt-in **y-band coherence anchor** to
`_ridge_dp_one_pass` and `_ridge_dp_two_paths`. Each pass receives a
per-column anchor; the DP cost adds
`gamma * |y - anchor[col]|` to every candidate, and (only when an
anchor is supplied) lets the path **coast** past a column instead of
landing on a ridge, paying a small fixed penalty
`_RIDGE_DP_OFF_RIDGE_PENALTY` plus its own anchor cost.

Coasting is only cheaper than landing when the available ridges all sit
far from this path's anchor — exactly the 7artisans dash-gap case where
the only remaining ridge belongs to the other curve.

```
+-------------------+   +---------------------+
| ridges_by_col     |   |  compute anchors    |
| (sparse per col)  |-->|  upper = ridges[0]  |
|                   |   |  lower = ridges[1]  |
|                   |   |  (2-ridge cols only,|
|                   |   |   carry-fill else)  |
+-------------------+   +---------------------+
                                  |
                                  v
                +-------------------------------+
                |  DP pass 1 with upper anchor  |
                |  - land cost: alpha*|dy| +    |
                |               gamma*|y - up|  |
                |  - coast cost: penalty +      |
                |                gamma*|y' - up||
                +-------------------------------+
                                  |
                                  v
                +-------------------------------+
                |  DP pass 2 with lower anchor  |
                |  (pass 1 ridges erased)       |
                +-------------------------------+
```

### Anchor construction

Anchors come from columns with exactly two ridge centroids: the smaller
y seeds the upper anchor, the larger seeds the lower. Columns with one
ridge (dash gap, coincidence) or three-plus ridges (gridline / halo
contamination) contribute no seed. Missing values carry forward
(forward-fill, with a leading backward-fill from the first known seed).

The anchor is intentionally NOT box-smoothed: a smoothing window
flattens legitimate local features (e.g. the TTartisan freq30 corner
dive over ~30 columns) as easily as it cancels noise. The inner DP
already supplies smoothness via the `alpha * |dy|` term; the anchor's
job is identity, not smoothness.

### Per-profile opt-in

A new `MtfProfile.ridge_dp_y_anchor: bool` field controls activation
per profile. Defaults False — the default DP behaviour is the same
identity-free Viterbi pass that ADR-049 settled. The 7Artisans
`samecolor-dashed-sm` profile sets the flag True; TTartisan and every
other profile keeps the flag False.

Anchor activation is a per-profile property because chart geometry
varies meaningfully: 7Artisans has clean two-ridge columns, TTartisan
grey-30 has noisy three-plus-ridge columns from antialiased halos. A
single global threshold cannot capture which charts benefit and which
regress.

### Tuning

- `_RIDGE_DP_GAMMA = 0.20` — anchor cost weight; a 30 px swap costs
  6.0, enough to dominate the 0.30\*|dy| smoothness cost (max 3.0 for
  a 10 px jump) and reject swaps, while picking the closer candidate
  on single-ridge / coincidence columns (anchor cost ≈ 0)
- `_RIDGE_DP_OFF_RIDGE_PENALTY = 4.0` — fixed coast cost; sized so a
  single-column coast beats landing on a ridge ≥30 px from this path's
  anchor, but never beats landing on a ridge that matches the anchor

## Consequences

### 7artisans 50mm f/1.2 Mark II (closes #1104)

| Field   | Post-#1100 p95 | Post-#1104 p95 | Change                          |
| ------- | -------------- | -------------- | ------------------------------- |
| freq10S | 0.124          | **0.052**      | corner swap fixed               |
| freq10M | 0.119          | **0.098**      | corner fixed; pos-0.6 unrelated |
| freq30S | 0.087          | 0.087          | unchanged                       |
| freq30M | 0.069          | 0.052          | improved                        |

Corner samples (pos 1.0):

| Field   | Pre-fix | Δ         |     | Post-fix | Δ   |     |
| ------- | ------- | --------- | --- | -------- | --- | --- |
| freq10S | 0.100   | **0.029** |
| freq10M | 0.109   | **0.020** |

freq10S meets the issue's target ≤ 0.064. freq10M misses target — the
new dominant outlier is at pos 0.6 (|Δ|=0.087), a pre-existing
curve-coincidence resolution issue present in both pre-#1100 and
post-#1100 calibrations. Tracked separately.

### TTartisan and other profiles

`ridge_dp_y_anchor` defaults False; TTartisan and every non-7Artisans
profile keep the ADR-049 unanchored DP. Calibration confirms zero
delta:

| Field                       | Post-#1100 | Post-#1104 |
| --------------------------- | ---------- | ---------- |
| TTartisan max-f/1.2 freq30S | 0.012      | 0.012      |
| TTartisan max-f/1.2 freq30M | 0.095      | 0.095      |
| TTartisan stopped freq30S   | 0.192      | 0.192      |
| TTartisan stopped freq30M   | 0.199      | 0.199      |

### Aggregate (14-anchor calibration set)

- paired comparisons: 627 (unchanged)
- median |Δ|: 0.0112 → 0.0111
- p95 |Δ|: 0.0640 → 0.0638
- in band ±0.05: 92.5% → **93.0%**

### Approaches ruled out

- **Option 1 (dash-vs-solid identity from column run lengths).** The
  issue's proposed fix. Probe showed 7Artisans solid and dashed
  curves render with the same run-length distribution (p50=2, p95=4
  for both), so the signal does not separate them.
- **Box-smoothed anchors.** A 30-col smoothing window flattened the
  TTartisan freq30 dive (a 67 px legitimate jump) into noise and
  forced the DP to coast through it. Removing the smoothing fixed
  the regression — the anchor's job is identity, not smoothness.
- **Auto-detect anchor applicability from ridge distribution.** An
  initial implementation enabled anchors when 3+-ridge columns were
  rare (<10% of non-empty). It misclassified TTartisan grey-30 as
  clean after halo exclusion (post-halo 3+-ridge fraction ≈ 2%) and
  regressed the corner dive anyway. Per-profile declaration captures
  the chart-geometry signal that ridge-count heuristics miss.

### Known limitation: 7artisans pos-0.6 mid-field

freq10M p95 = 0.098 does not meet the issue's ≤ 0.064 target. The
dominant outlier shifted from the corner (now fixed) to pos 0.6
(|Δ| = 0.087). At that position the chart resolution merges the
solid and dashed curves into a single ridge centroid; the extractor
reads 0.813 OTF while GT says S = 0.860, M = 0.900. Both fields share
the single-ridge value via coincidence fill, but neither matches GT
because the actual physical curves diverge by 0.04 OTF at that
position. This is a chart-resolution limit, not a DP identity issue —
no anchor tuning can recover sub-pixel separation that the source
raster does not encode. Tracked as follow-up.
