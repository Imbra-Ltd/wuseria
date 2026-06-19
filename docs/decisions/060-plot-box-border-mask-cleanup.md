# ADR-060: Plot-box border line cleanup on per-hue masks

**Status:** Accepted
**Date:** 2026-06-19

## Context

The digitizer's grey HSV mask for the `ttartisan-4color-dual-aperture`
profile is permissive (`s_max=35, v_min=90, v_max=160`) to admit
faint grey 30 lp/mm curves against the chart's white background. On
the af-35 max-aperture chart the same mask also catches the chart's
plot-box right border line — a dark vertical decoration at col 603,
4 px inside the data-edge `plot_box.x_right=607`. The border column
contains 180 grey pixels spanning the full plot-box height (y=120 to
y=459) and the skeleton survives it as a single tall vertical ridge.

Downstream the ridge DP locks onto that vertical ridge while the
real M30 curve fades to zero ink in cols 603-607, so the sampler at
`frac=1.0` reads the border's y-position carried forward (extracted
0.17) instead of the M30 curve's honest "no data" answer. The result:
af-35 freq30M p95 |d| = 0.433 against an eye-read ground truth that
extrapolates the M30 curve's last visible value of 0.50 across the
faded right edge.

S166's raw-mask probe (#1217 comment) decomposed the failure into two
stacked mechanisms:

1. **Plot-box border contamination** at col 603 inside the data-edge
   box, deterministic and chart-dependent.
2. **AA-halo intermediate-band drift** at col ~510, the ridge DP
   locking onto a halo cluster between M30 and S30 instead of the
   real M30 ridge.

This ADR addresses **mechanism 1 only**. Mechanism 2 requires changes
to the ridge DP's anchor cost model and is deferred (see Open below).

### Cross-cohort geometry probe

The fix must not regress charts sharing the profile. Before-fix probe
on the three relevant lenses (probe scripts deleted post-merge):

| Chart        | `x_right` | Border col | Border px | Inside data-edge box? |
| ------------ | --------- | ---------- | --------- | --------------------- |
| af-35        | 607       | 603        | 180       | YES → contamination   |
| ttartisan-50 | 607       | 609        | 345       | NO → already excluded |
| 7artisans-50 | 653       | -          | -         | N/A (no grey curve)   |

ttartisan-50's plot-box border falls _outside_ the data-edge box (2 px
beyond `x_right`), so the existing plot-box clip already excludes it.
7Artisans uses a different profile with no grey HueRange. Only af-35
sees the contamination inside the clipped region.

## Decision

Add `strip_plot_box_borders(masks, plot_box)` to `pipeline/masks.py`
and call it from both mask-consuming call sites
(`pipeline.field_skeletons`-equivalent and `dispatch.field_skeletons`)
after the existing plot-box clip.

```
+---------------------------------------------------------+
| masks_by_curve_name(hsv, profile)                       |
+---------------------------------------------------------+
        |
        |  clip to plot_box (existing)
        v
+---------------------------------------------------------+
| curve_masks (clipped to plot-box interior)              |
+---------------------------------------------------------+
        |
        |  strip_plot_box_borders(curve_masks, plot_box)        NEW
        |  for col in [x_right - 10, x_right]:
        |    if col_mask_density >= 0.5 * plot_height:
        |      zero col across all hues
        v
+---------------------------------------------------------+
| curve_masks (borders stripped)                          |
+---------------------------------------------------------+
        |
        |  _apply_declared_halo_pairs (#1216, ADR-059)
        v
+---------------------------------------------------------+
| field skeletons                                         |
+---------------------------------------------------------+
```

The detection rule is unambiguous:

- `_BORDER_WINDOW = 10` — columns within 10 px of `x_right` are
  candidates; the rightmost ~2% of the plot box.
- `_BORDER_DENSITY_THRESHOLD = 0.5` — a column with ≥ 50% of the
  plot-box height filled is unambiguously chart decoration. Real
  curves at this position contribute 5-8 px per column (af-35 real
  M30 tail cols 597-601 carry 5-7 px each); a 180-px-tall vertical
  column has no plausible curve interpretation.

The function is a no-op on every chart where the plot-box border
falls outside the data-edge box (already clipped) or where no hue's
mask catches the border (e.g. 7Artisans grey-less profile).

## Alternatives considered

- **Per-lens `dp_y_anchor_per_hue` override (Option 1 in #1217).**
  Mirrored `sm_swap_per_hue` from #1199: a new `ReferenceChart` field
  flipping `HueRange.dp_y_anchor=True` for af-35 only. Per-lens
  scoping worked (ttartisan-50 + 7artisans unchanged) but enabling
  the anchor regressed af-35: freq30M `0.113 → 0.422`, freq30S
  `0.005 → 0.344`. Root cause: the ridge DP's `_compute_y_anchors`
  needs reliable two-ridge columns to seed the anchor; on the af-35
  grey mask only 15 of 521 columns (3%) have exactly two ridges, and
  those seeds pick chart-title artifacts (y=119 = `plot_box.y_top`)
  instead of real curves. With the junk anchor enabled, the linear
  cost pulls paths toward y=119 and derails both passes. The
  mechanism would only help if the anchor signal were repaired first.

- **Snap-when-available anchor (Option 2 in #1217).** Modified the
  anchor cost to fire only when a candidate y exists within 15 px
  of the anchor at the column, in principle distinguishing
  "intermediate-halo drift" from "legitimate large move."
  Measured: af-35 freq30M `0.113 → 0.340`, af-35 freq30S
  `0.005 → 0.455`, ttartisan-50 freq30S `0.024 → 0.146`. Same root
  cause as Option 1: with anchors anchored to y=119 on af-35, snap
  mode is mostly a no-op on the right path and a regression on the
  wrong one. ttartisan-50 regressed identically to the legacy
  linear-anchor S155 measurement (curve dwell at constant y stays
  within snap tolerance of its lower anchor for many columns, then
  the dive moves the path toward an off-band candidate that snap
  still penalizes).

- **Drop the `EYE_READ_OVERRIDES[0]` entry from `mtf-readings.test.ts`
  and re-frame the af-35 max-30-grey M30 frac=1.0 cell as "extractor
  honestly emits None / sister-fallback fills it" (#1216 success
  criteria branch).** Rejected as the primary path: the eye-read GT
  `position=12.6 → M30 = 0.58` reflects the maintainer's
  extrapolation of the curve's last visible value past the fade
  region. The shipped data should carry that extrapolation, not the
  None-on-fade extractor signal. Different cell anyway — calibrate's
  frac=1.0 != mtf-readings.ts position 12.6 (`[[feedback_calibrate_panel_coords]]`).

- **Raise `s_max` on the grey HueRange** (e.g. 35 → 25) to reject
  border-line pixels. Rejected: the af-35 border at col 603 has
  measured S in [0, 20] — already below `s_max=35` but inside the
  raised band would also be inside `s_max=25`. The border colour
  cannot be separated from real grey curves by HSV alone; only the
  spatial distribution (full-height vertical) distinguishes them.

## Consequences

### Positive

- **af-35 freq30M p95 |d|: 0.433 → 0.113**, closing about 3/4 of
  the gap to the ±0.05 calibration band.
- **af-35 freq30M frac=1.0 cell flips from extracted (0.17) to None.**
  The M30 grey curve genuinely has no ink in cols 603-607 — the
  border contamination was the only thing the sampler had been
  reading. The honest answer at the curve's faded right edge is
  None, which sister-fallback then either fills from S30 or leaves
  empty depending on the downstream rule.
- **Aggregate p95 |d|: 0.0505 → 0.0499** (slight improvement).
- **Aggregate max |d|: 0.3319 → 0.1745** (af-35's frac=0.9 cell
  becomes the new worst case, replacing the frac=1.0 reading).
- **ttartisan-50 freq30S regression-guard: unchanged at p95 0.024.**
  Geometry-based safety: ttartisan-50's border falls outside the
  data-edge box, so the new strip step is a no-op on it.
- **7artisans-50: unchanged.** Different profile, no grey hue.
- **381 → 383 mtfdigitizer pytest** (+2 unit tests covering the
  fires-when-inside and no-op-when-outside cases).
- Aggregate paired comparisons drop by 1 (810 vs 811) — the af-35
  frac=1.0 cell stops contributing a paired comparison because the
  extractor now emits None. This is honest data loss, not a
  regression: the previous paired comparison was a wrong reading
  against an extrapolated GT.

### Negative

- The detection rule is geometric and density-based, not
  semantic — a future chart with a real curve that runs vertical
  for ≥ 50% of plot height within 10 px of `x_right` would be
  incorrectly stripped. No such chart exists in the reference set
  today; the YAGNI revisit trigger is "first chart whose hue mask
  legitimately fills a near-right-edge column to ≥ 50% of plot
  height."
- Does not address mechanism 2 (AA-halo intermediate-band drift at
  col ~510). af-35 freq30M is still ~0.06 above the ±0.05 band on
  its frac=0.9 reading. That reading remains on the
  `EYE_READ_OVERRIDES[0]` entry's eye-read coordinate system (pos
  12.6 mm), which stays valid as a separate cell — Option 4 does
  not affect what `mtf-readings.ts` ships.

### Neutral

- The thresholds (`_BORDER_WINDOW`, `_BORDER_DENSITY_THRESHOLD`) are
  module-level constants, not per-profile. They can move to a
  per-profile or per-chart parameter when a second consumer with
  different geometry needs different values (YAGNI per `quality.md`).
- Independent of and stackable with future ridge-DP fixes for
  mechanism 2. No code-layer coupling between this fix and a
  potential anchor-signal-repair spike.

### Open

- **Anchor-signal repair for grey-mask charts.** Both Options 1 and 2
  failed because `_compute_y_anchors` cannot find reliable seeds on
  noisy permissive-HSV masks (3% two-ridge columns on af-35 grey).
  A future spike could explore: smooth-after-fill, fragment filtering
  before seed selection, or post-DP iterative anchor refinement. The
  problem is general (any low-saturation hue with gridline pickup
  will hit the same limit) but no other lens in the current cohort
  surfaces a measurable failure that requires solving it, so it
  stays deferred until a second case appears.
- **`EYE_READ_OVERRIDES[0]` (`#1202`) stays in place.** The
  spike's original aspiration of removing the override entry once
  the extractor reads correctly is not satisfied by this ADR alone.
  The override locks `(af-35, f/1.8, pos=12.6, freq=30M, expected=0.58)`,
  which is a separate cell from the panel's frac=1.0 reading
  (`[[feedback_calibrate_panel_coords]]`). The hand-patch remains
  the source of truth for that cell.
- **Mechanism 2 (AA-halo drift) follow-up.** A new spike or implementation
  task should pick this up once the anchor-signal question is resolved
  — the two are coupled and trying to fix the drift without first
  fixing the seeds repeats the failure mode this ADR's rejected
  alternatives exhibited.
