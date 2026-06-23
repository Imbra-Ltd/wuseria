# ADR-067: Per-hue y_top inset on ChartView

**Status:** Accepted
**Date:** 2026-06-23

## Context

When two curves of different hues sit physically coincident at the
plot top (both at MTF~1.0 across a region), the darker / more-saturated
curve's antialiasing halo can bleed into the lighter / less-saturated
hue's HSV band. The contaminated mask then catches a spurious top-edge
band that the sampler latches onto where the contaminated curve's real
ink is absent.

ADR-059 + ADR-062 fix this for **off-plot-top** halo overlaps via
declared `halo_pairs` — the contaminator's dilated mask is subtracted
from the contaminated mask before skeletonisation. That works when the
halo subtraction does not erase the contaminated curve where it
legitimately sits.

#1257 surfaced a different shape on the
`samyang-12mm-f2-8-ed-as-ncs-fish-eye` stopped panel: the saturated
red 10S curve sits at chart-y 578-580, exactly one pixel below the
detected plot-box `y_top=575`. Its grey-valued AA halos at chart-y
577 and 581-582 (S~0, V in [177, 191]) qualify for the
`30M-light-grey` HSV band (S<40, V in [160, 195]). On this one chart
the legitimate 30M curve starts at chart-y 583, so a halo_pair
`(10S-red, 30M-light-grey)` would erase the contaminator entirely
over its full extent — and the same pair would catch every other
Samyang lens where 10S and 30M legitimately overlap at high MTF (the
300mm reflex Tier 1 anchor crashes immediately).

#1257's first fix was a global per-chart plot-box `y_top` bump (575 → 583) on the stopped panel, declared via
`_STOPPED_Y_TOP_INSET_BY_SLUG` in the Samyang scaffolder. That hid
the spurious 30M chart-top ridge — but it also clipped the red 10S
curve out of the plot region. Sampling-time, the 10S skeleton
disappeared at frac 0.0..0.7 and sister-fallback pulled freq10S from
the diving 10M curve (~0.93..0.97). The coincident-top anchor work
in #1268 (ADR-066) then propagated the degraded freq10S into
freq30S, leaving a 0.03..0.07 MTF residual underestimate in the
region where the chart artist had drawn 30S coincident with 10S at
the plot top (#1271).

### Diagnostic — frac 0.5..0.7 freq30S on `samyang-12mm-f2-8-ed-as-ncs-fish-eye` stopped

| frac | freq10S (read) | freq10S (true) | freq30S (read) | freq30S (true) |
| ---- | -------------- | -------------- | -------------- | -------------- |
| 0.5  | 0.97           | ~1.00          | 0.97           | ~1.00          |
| 0.6  | 0.96           | ~1.00          | 0.96           | ~1.00          |
| 0.7  | 0.93           | ~1.00          | 0.93           | ~1.00          |

The 10S underestimates were the direct cause of the 30S
underestimate — the coincident-top anchor honestly propagated what
10S claimed.

### The conflict

The plot box is one rectangle shared by every per-hue mask. Bumping
`y_top` to skip 30M's halo contamination also clips 10S's own curve.
There is no value of `y_top` that satisfies both masks at once:
**575 captures 10S but lets 30M see halos; 583 hides halos but also
hides 10S**.

## Decision

Add a per-hue `y_top` inset declared on `ChartView`. The mask-clip
step in `dispatch.field_skeletons()` and `pipeline._hue_masks_for_presence()`
uses the per-hue effective `y_top` instead of the plot box's value;
sampling, scoring, and MTF conversion continue to use the plot box's
unmodified rectangle.

```
+--------------- chart plot region -----------------+
|                                                   |
|  y_top = 575  ------ axis line ------ x_left=31   |
|  y=577        AA halo (V~187, S~0)                |
|  y=578-580    saturated red 10S core (MTF~1.0)    |
|  y=581-582    AA halo (V~191, S~0)                |
|  y=583        legitimate light-grey 30M starts    |
|                                                   |
+---------------------------------------------------+

per-hue clip                  applies
----------------------------- --------------------------
10S-red                       y_top + 0  = 575 (full)
10M-pink                      y_top + 0  = 575 (full)
30S-dark-grey                 y_top + 0  = 575 (full)
30M-light-grey                y_top + 8  = 583 (skip halos)
```

### Mechanism

- `pipeline.types.PlotBox` gains an optional `y_top_insets`:
  `tuple[(hue_name, int), ...]` and a `hue_y_top(name)` accessor.
- `referenceset.charts.ChartView` gains a matching
  `y_top_insets: tuple[(str, int), ...]` field (defaults `()`).
  Lens-scoped: leaves the shared profile untouched.
- `dispatch._hue_clip(shape, plot_box, hue_name)` builds a per-hue
  boolean clip honouring the inset. Replaces the single shared `clip`
  array that previously ANDed against every mask.
- `_to_plotbox()` helpers across the consumer modules (extract,
  calibrate, log, emit, per_frequency, emit_fuji_tier2) accept the
  insets tuple from the view and forward it onto the runtime
  `PlotBox`. The chart-level callers (autotriage, plausibility,
  diagnose, etc.) pass the default empty tuple — they read `chart.plot_box`,
  not a per-view object.
- The Samyang Tier 2 scaffolder emits the inset on the stopped
  `ChartView` for the 12mm fisheye; the global stopped y_top stays
  at the detector value of 575.

## Alternatives considered

1. **Per-mask exclusion zones on `MtfProfile`.** Declare
   `mask_exclusion_zones: ((curve_name, y_lo_frac, y_hi_frac), ...)`
   on the profile. More general (supports interior strips, not just
   the top edge) but profile-scoped — every Samyang chart would share
   the inset, regressing the other 17 stopped panels whose 30M curves
   sit at chart-y 578-582 near MTF~1.0.

2. **Extend halo_pairs to a "chart-top band" subtraction.** Generalise
   ADR-062's mechanism to allow a `((y_lo, y_hi), contaminated_hue)`
   subtraction. Same scope problem as (1) — the band is chart-specific,
   not profile-specific — and conflates cross-hue contamination with
   chart-region exclusion in one mechanism.

3. **Asymmetric inset by curve at the dispatch level.** Special-case
   in the Samyang dispatch branch: clip the 30M mask with a tighter
   y_top than other masks. Same effect as the chosen approach but
   undeclared — no top-level profile / chart record of which charts
   need the override. Hard to audit.

4. **Keep the global stopped inset + per-hue escape list.** Inverted
   form: leave `y_top=583` and list `(10S-red, -8)` to escape back to
   575 for the contaminator. Mathematically equivalent for one chart
   but inverts the natural reading ("default is plot box, override is
   tighter"); also encourages negative insets which complicate the
   accessor.

## Consequences

### Positive

- `samyang-12mm-f2-8-ed-as-ncs-fish-eye` stopped panel: freq10S at
  frac 0.0..0.7 reads ~0.99 (previously 0.93..0.97 sister-filled from
  diving 10M). The coincident-top anchor's output for freq30S follows
  along — no 0.03..0.07 residual underestimate (#1271 closed).
- 30M-light-grey on the same panel still reads its legitimate curve
  (~0.62 at frac 0.6), preserving #1257's fix.
- Mechanism is lens-scoped, not profile-scoped — the other 17 Samyang
  stopped panels are unaffected, including the ones whose 30M curve
  sits in rows 578-582 at MTF~1.0.
- Calibration aggregate stable: 878 paired, p95 |d| 0.0462, in-band
  96.0%, max |d| 0.1217 — identical to ADR-066's S178 baseline (the
  12mm fisheye has no GT and so does not affect the aggregate; the
  test suite confirms no anchor regression).
- Replaces the maintainer-friendly-but-coarse global inset with a
  precise per-hue declaration — future charts with the same shape
  get a one-line entry in `_STOPPED_Y_TOP_INSETS_BY_SLUG` without
  the side effect of clipping the contaminator.

### Negative / accepted tradeoff

- `PlotBox` now carries a field that is only consulted by the mask
  clip step. Sampling, scoring, and MTF conversion ignore it. A
  reader has to know not to confuse `plot_box.y_top` with
  `plot_box.hue_y_top(name)` — the accessor is the cue, but the dual
  semantics are a mild conceptual cost.
- The scaffolder grew a small Python-literal emitter
  (`_insets_repr`). The single existing tuple is one line; multiple
  hues per chart would still render compactly.

### Scope this ADR does NOT cover

- The 30S coincident-anchor work (#1269 — when 30S skeleton is empty
  AND 10S >= 0.95 at the same column, anchor 30S to 10S). #1269 was
  blocked on #1271 because the degraded freq10S poisoned the anchor's
  input. With this ADR landed, freq10S is no longer artificially low
  and #1269 can resume.
- Right-edge per-hue inset. The same mechanism would extend (add
  `y_bottom_insets`) if a chart family needs a parallel bottom-edge
  override; no current chart does.
- Per-aperture (max vs stopped) insets within one ChartView. Each
  ChartView already carries its own plot_box and its own
  `y_top_insets`, so the per-aperture override is implicit in the
  view list — no new mechanism needed.
