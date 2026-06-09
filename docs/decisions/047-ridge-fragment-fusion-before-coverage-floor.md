# ADR-047: Ridge fragment fusion runs before the coverage floor

**Status:** Accepted
**Date:** 2026-06-09

## Context

The TTartisan 50mm f/1.2 max-aperture chart's black T10 curve takes a
steep dive at the right corner (OTF 0.88 → 0.60 over ~150 columns).
Eye-read GT lists `freq10M` (the T10 dashed curve) ending at 0.60; the
extractor was reporting 0.88 at the same column (|Δ| = 0.28). #1097
analysed this as a "ridge clusterer fragments curves at crossings"
problem.

A probe of the ridge clusterer's intermediate state on the black hue
mask confirmed the diagnosis but localised the failure more precisely.
The greedy clusterer correctly extracts the T10 dive's ridge points
into three contiguous segments (covers 67 + 9 + 48 = 124 columns over
x=445-606), but `_select_top_n_tracks` then applies the
`_MIN_TRACK_COVERAGE` floor (52 columns, 10% of plot width) before
running fragment fusion. The three dive segments fall below the floor
individually and are dropped before `_merge_fragmented_tracks` ever
sees them. The top-3 picker keeps only the two upper-curve tracks; the
sampler then attributes the S10 (upper) value to BOTH `freq10S` and
`freq10M` at the right corner, returning 0.88 for the T10 dive.

The same physical curve fragments into multiple sub-pieces whenever
its ridge briefly coincides with (or crosses) another curve. The
coincidence-region ridge gets assigned to whichever track was closer
in y at the divergence point; the absorbed curve's fragments on the
other side of the coincidence become independent tracks. The fusion
step (`_merge_fragmented_tracks`) is designed exactly for this case —
but only sees tracks that already passed the coverage floor.

Bigger fixes considered and ruled out:

- **DP-based extraction swap (option 1 from #1097).** The
  `extract_two_curves_dp` path has a documented cliff-corner blind
  spot (#1044) on the exact pattern at issue here — when a curve
  takes a steep right-edge dive and a parallel curve at higher y is
  still visible, DP prefers the smoother (flat) path. Tokina-56 30M
  exhibited this; the TTartisan T10 dive would too.
- **Slope-extrapolated fragment match.** Tried: project each
  fragment's slope across the gap, accept the merge when both
  projections land within tolerance. Regressed 7artisans freq30S
  (p95 0.053 → 0.103) and ttartisan freq10S (p95 0.027 → 0.162) by
  over-fusing fragments that should stay separate.
- **Continuity-based S/M assignment** (mask-density inside each
  track's y-band, replacing coverage-based "denser = solid"). Tried:
  on the freq-split branch. Regressed 7artisans freq10M massively
  (med 0.022 → 0.095). The 7artisans chart's `dashed_is_sagittal=True`
  inversion interacted with continuity in a way that didn't generalise.

## Decision

In `_select_top_n_tracks`, run fragment fusion BEFORE applying the
coverage floor. Dedup (which kills antialiased halo duplicates) still
runs first; fusion stitches sub-floor fragments into larger tracks;
the floor then discards what remains too short to be a real curve.

```
Before (#1095 → #1097 baseline):
  qualified = [t for t in tracks if t.coverage >= floor]   # floor
  deduped   = _merge_near_duplicate_tracks(qualified)      # dedup
  fused     = _merge_fragmented_tracks(deduped)            # fuse
  return top-N(fused)

After (#1097):
  deduped   = _merge_near_duplicate_tracks(tracks)         # dedup
  fused     = _merge_fragmented_tracks(deduped)            # fuse
  qualified = [t for t in fused if t.coverage >= floor]    # floor
  return top-N(qualified)
```

One-line reorder. The signal that matters — "is this a real curve" —
is best measured on the fused track, not on each pre-fusion fragment.
Sub-floor fragments that fuse into a >floor track are real curves;
sub-floor fragments that stay sub-floor after fusion are noise.

## Alternatives considered

- **Lower the floor.** Direct, but admits noise tracks across the
  whole reference set. The order swap preserves the floor's noise-
  rejecting role while letting fragments combine first.
- **Skip the floor entirely on the freq-split branch.** Targets only
  the TTartisan failure but leaves the 4-curve branch
  (`ridge_tracks_to_fields`) unchanged. Sharing the order improvement
  across both branches is consistent and helps any future chart that
  fragments curves at crossings.
- **Carry sub-floor fragments through fusion as a separate pool**
  (apply the floor twice — once to pick "anchor" tracks, once to
  pick fragments allowed to fuse onto anchors). More machinery for
  the same outcome.

## Consequences

**Improvements on the TTartisan 50mm f/1.2 max-aperture anchor:**

| Field   | Baseline p95 | After p95 | Change           |
| ------- | ------------ | --------- | ---------------- |
| freq10S | 0.028        | 0.027     | stable           |
| freq10M | **0.185**    | **0.013** | massive (-0.172) |
| freq30S | 0.140        | 0.140     | unchanged        |
| freq30M | 0.128        | 0.128     | unchanged        |

freq10M's corner reading goes from 0.88 (wrong by 0.28) to 0.61
(within 0.01 of GT 0.60). freq10S correctly returns None at the
corner — the S10 corner ridge isn't in any extracted track on this
chart, and reporting None is more honest than the prior wrong
attribution.

**Paired-count drops are honest behavior.** On positions where the
extractor previously fabricated a wrong reading (taking the absorbed
curve's value), it now returns None. Cohort-level: fewer paired
samples, lower wrong-value rate. Per #1097's acceptance criteria,
freq10S and freq10M are now within the ±0.05 band; freq30S and freq30M
are NOT — that pair stays out because the failure on freq30 is a
different problem (S/M label inversion at a curve crossing, where
track-[0] is a frankenstein mixing both physical curves). Tracked
separately as a follow-up.

**Other cohort effects:**

- 7artisans freq30M p95: 0.060 → 0.052 (slight improvement)
- 7artisans freq30S p95: 0.053 → 0.095 (apparent regression — the
  fix surfaces a previously-missing sample at frac 0.4 whose |Δ| is
  0.078, dragging p95 up. Adding signal that happens to have moderate
  error is honest; the median |Δ| barely moves)
- All other charts (Sigma, Samyang, Tokina, Viltrox, Fujifilm):
  unchanged

**Aggregate:** 92.9% → 93.0% within ±0.05 band (562/604 vs 566/609).
Net paired comparisons drop by 5, in-band drop by 4.

The fusion-then-floor order makes the per-curve coherence check the
selection criterion, not the per-fragment coverage. This is the right
abstraction: the chart contains curves, and the algorithm should pick
curves, not pieces. Curves that fragment then fuse back into one
coherent track stay; fragments that never coalesce into a coherent
curve get dropped.

## Follow-up: the freq30 frankenstein problem

The grey freq=30 corner stays at |Δ|=0.11/0.10 (freq30S/freq30M)
because the greedy clusterer builds track-[0] as a "frankenstein"
mid-field path that switches between both physical curves at the
crossing. After this fix, S/M labels get assigned to the frankenstein
and its sibling, both wrong. A small follow-up issue documents three
candidate fixes (smarter clusterer tie-break, DP-with-cliff-corner
mitigation, dashed-density-on-raw-mask discriminator) and defers
choice to spike.
