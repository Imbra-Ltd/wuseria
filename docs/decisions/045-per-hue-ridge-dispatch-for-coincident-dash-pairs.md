# ADR-045: Per-hue ridge dispatch for coincident solid/dashed pairs

**Status:** Accepted
**Date:** 2026-06-07

## Context

The `SPLIT_BY_DASH` + `FREQUENCY` dispatch (ADR-038, Sigma/7Artisans
dialect) handles charts where each hue carries one spatial frequency
with two curves: solid (sagittal) and dashed (meridional). The
algorithm: for each hue mask, morphologically close + skeletonize, then
`split_sm_by_cc_width` picks the longest connected component as S and
the rest as M.

This works when the solid and dashed curves sit at clearly different
y-positions across the field — the close kernel does not bridge
vertically, the skeleton has two CCs per hue, and CC-width separates
them cleanly.

The TTartisan max-aperture pass (#798, ADR-044) breaks this
assumption. On the f/1.2 anchor chart:

- Black hue: solid S10 (MTF 0.88-0.94) and dashed T10 (MTF 0.88-0.95)
  run within **~5 px of each other in y across fields 0-10**.
- Their antialiased halos touch — the raw black mask fuses both curves
  into **one ~1172-px connected component spanning y=144..178**.
- After `close_and_skeletonize`, the fused blob produces a single
  centerline. `split_sm_by_cc_width` picks the fused CC as S (770 px)
  and only the small non-fused dashed fragments at fields 11-13 as M
  (110 px), missing ~85% of the true T10 curve.

Production verdict: `LOW`, `precision=0.595`, `IoU=0.299`,
`prior_violations=1` (#1085).

Symptom-level fixes ruled out by probes:

- **Widening the black hue's V cap** does not help — the dashed ink IS
  in the V≤80 band; the problem is connectivity, not coverage.
- **The existing `(SPLIT_BY_DASH, GEODESIC_DP)` dispatch** runs DP only
  on the meridional fragments after CC-split, so it inherits the bad
  split and the Viterbi path drifts onto axis labels or stays at the
  wrong MTF.
- **`extract_two_curves_dp` on the raw mask** has DP path 1 hug the
  dense solid; path 2 (with the erase band) gets pushed onto a
  different-color curve entirely.

## Decision

Add a new dispatch branch `(SPLIT_BY_DASH, FREQUENCY_PER_HUE_RIDGE)`
that ridge-tracks each hue independently. Within one hue (one
frequency), per-column ridge centroids preserve two distinct tracks
even where the two curves' halos visually fuse into one CC. The
**higher-coverage track is solid** (S by default; M when
`dashed_is_sagittal=True`, the 7Artisans-T-style convention).

```
              raw hue mask (one frequency)
                       |
                       v
              _strip_chrome (drop full-width
              gridlines / plot frame borders)
                       |
                       v
              _extract_ridge_points
              (per-column centroid of each
               vertical run of mask pixels)
                       |
                       v
              _cluster_into_tracks
              (greedy x-walk: each point
               joins closest in-range track)
                       |
                       v
              _select_top_n_tracks(n=2)
              (drop near-duplicate halos,
               fuse same-curve fragments,
               keep 2 longest)
                       |
                       v
        +--------------+--------------+
        |                             |
        v                             v
  higher coverage              lower coverage
        |                             |
        v                             v
        S (solid)                     M (dashed)
   (or M if dashed_is_sagittal)  (or S, ditto)
```

When only one track qualifies (whole-curve coincidence — the two
curves visually merge across the entire field), both fields share its
value. Same physics generalization as `ridge_tracks_for_hue`
(ADR-038): visually-coincident curves have the same MTF, so attributing
the shared ridge to both is honest, not fabricated.

Implementation:

- `pipeline/ridge.py::ridge_tracks_for_hue_freq_split` — new function;
  variant of `ridge_tracks_for_hue` (which is for `HUE_IS_CURVE` where
  the two tracks within a hue are two frequencies). Reuses every
  internal helper (`_strip_chrome`, `_extract_ridge_points`,
  `_cluster_into_tracks`, `_select_top_n_tracks`, `_densify_track`,
  `_rasterize`).
- `pipeline/dispatch.py` — new `(SPLIT_BY_DASH, FREQUENCY_PER_HUE_RIDGE)`
  branch wired between the existing `FREQUENCY` and
  `FREQUENCY/GEODESIC_DP` branches.
- `profiles/types.py::HueMeaning` — adds `FREQUENCY_PER_HUE_RIDGE`
  literal with a comment explaining when to pick it over `FREQUENCY`.
- `profiles/declared.py::TTARTISAN_4COLOR_DUAL_APERTURE` — switches
  from `hue_meaning="FREQUENCY"` to `hue_meaning="FREQUENCY_PER_HUE_RIDGE"`.

Result on the anchor:

| pass    | before                           | after                                 |
| ------- | -------------------------------- | ------------------------------------- |
| max     | LOW, prec 0.595, IoU 0.299, pv 1 | **HIGH, prec 0.852, IoU 0.608, pv 0** |
| stopped | LOW, prec 0.924, IoU 0.665, pv 1 | LOW, prec 0.931, IoU 0.721, pv 1      |

Spot-check on two other TTartisan lenses confirms the dispatch
generalizes: ttartisan-23mm-f1-4 max IoU 0.748, stopped 0.818;
ttartisan-25mm-f2-0 max IoU 0.538 (HIGH verdict), stopped 0.563.

## Alternatives considered

1. **Widen `max-10-black` v_max** (HSV tuning) — doesn't help; the
   ink is already in the band. Connectivity is the bottleneck, not
   pixel inclusion.

2. **Smaller close-kernel width per profile** — the close kernel is
   `(7, 1)`, purely horizontal. It does not bridge vertically; the
   raw mask is already fused via antialiased halos before the kernel
   runs. Shrinking the kernel wouldn't separate the curves.

3. **Per-profile `_RIDGE_TRACK_MAX_DY` knob** — `_RIDGE_TRACK_MAX_DY=5`
   default (Viltrox tuning) is fine for TTartisan; both S10/T10 sit
   within 5-15 px of each other and tracks form correctly. Left
   un-knobbed for now; can be exposed as a profile parameter later if
   a future brand needs a different value.

4. **Re-use `(SPLIT_BY_DASH, GEODESIC_DP)`** — runs DP only on the
   M-fragments after CC-split, inheriting the bad split. Not
   applicable when CC-split itself is the failure mode.

5. **Re-use `extract_two_curves_dp` directly on the raw mask** — DP
   path 1 hugs the dense solid; path 2 (erase ±18 px) gets pushed onto
   the wrong curve. The Tokina-style DP assumes the two curves of one
   hue have **comparable ink density**; the SPLIT_BY_DASH case has
   asymmetric density (solid >> dashed) so DP always favours solid
   twice, never finding dashed.

6. **CC_RANK_BY_MEAN_Y on merged neutral mask** — would require
   restructuring TTartisan's two hues (black + grey) into one neutral
   hue covering both V-bands. That re-introduces gridline pollution
   the current black/grey separation specifically rejects. Per-hue
   approach keeps the hue-band hygiene intact.

7. **Fold into existing `RIDGE_TRACKING`** — that dispatch operates on
   one neutral mask for the 4-curve all-grey Viltrox layout (ranks
   tracks by mean_y for frequency, by coverage for S/M within each
   pair). TTartisan has informative hues (color = frequency) and 2
   curves per hue. The shape differs enough that piggy-backing would
   require an "is this 4-curve or 2-curve-per-hue?" mode flag inside
   the function — cleaner to ship a separate function with the same
   building blocks.

## Consequences

- One more profile family available: brands whose chart template packs
  a solid and a dashed curve very close together in y (within ~5 px)
  can declare `FREQUENCY_PER_HUE_RIDGE` instead of `FREQUENCY`.
- TTartisan max-aperture pass moves from LOW (verdict-blocking) to
  HIGH on the anchor; the Tier 2 cohort's maintainer-glance review
  becomes a meaningful check instead of a rubber-stamp on broken
  data.
- The new dispatch is selected by hue_meaning, not auto-detected. A
  future brand with the same coincidence pattern must declare it
  explicitly — same hygiene rule as every other `HueMeaning` choice.
- `dashed_is_sagittal` is honored, so 7Artisans-style brands (dashed =
  sagittal) can adopt this dispatch with their existing semantics.
- No data file changes. TTartisan `mtf-readings.ts` is still empty
  (maintainer-gated emit, ADR-044); the dispatch fix unblocks the
  emit-and-glance workflow but does not auto-emit.
- Test surface: +4 unit tests in `test_ridge.py` covering S/T labelling
  (default and `dashed_is_sagittal`), whole-curve coincidence, and
  blank-mask behavior. Total pytest count: 285 → 289.
- The sparse-dash regions where the dashed line's dashes exceed
  `_RIDGE_TRACK_MAX_DY=5` per step still produce partial dropouts in
  the M field. The aggregate IoU is high enough to flip the gate, but
  individual lenses with extreme dashed-slope segments may need a
  per-profile `_RIDGE_TRACK_MAX_DY` knob in the future.
