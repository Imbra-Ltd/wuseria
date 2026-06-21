# ADR-062: Extend Samyang halo_pairs to 30S-dark-grey -> 30M-light-grey

**Status:** Accepted
**Date:** 2026-06-21

## Context

ADR-059 introduced declared `halo_pairs` on `MtfProfile` to subtract a
contaminator hue's AA gradient ring from the contaminated hue's mask
before dispatch. The Samyang profile shipped with one pair —
`("10S-red", "10M-pink")` — closing #1216 on the 85mm anchor's freq10M
right-edge mis-track.

S170's #792 Samyang digitization surfaced a second occurrence of the
same shape on the **dark grey -> light grey** (30S -> 30M) pair, on
the `samyang-12mm-f2-8-ed-as-ncs-fish-eye` chart.

### Diagnostic

Pixel-level probe at the right edge (x = 445-460) of the 12mm fisheye
MAX panel:

```
upper grey curve (30S dark grey) core:   V ~ 102-103  (y ~ 170-178)
upper curve AA wrap:                     V up to ~ 187 (within 30M's band)
lower grey curve (30M light grey) core:  V ~ 178      (y ~ 270-271)
```

The Samyang profile's HSV bands:

```
30S-dark-grey:  S < 40, V in [85, 115]    (catches saturated core only)
30M-light-grey: S < 40, V in [160, 195]   (catches saturated core AND
                                           upper-curve AA wrap V in [160, 187])
```

The 30M mask therefore catches two y-bands: the legitimate light-grey
curve at y ~ 270 AND the dark-grey curve's AA halo at y ~ 170-178. The
sampler, picking the top run per column at the right edge where the
M-skeleton has gaps, lands on the halo y-band (MTF ~ 0.68) instead of
the real M30 curve (MTF ~ 0.46).

This is **structurally identical** to the 10S-red -> 10M-pink case
ADR-059 fixed: a darker, more-saturated curve's AA gradient creeping
into a lighter, less-saturated curve's HSV band, producing a spurious
second y-band the sampler latches onto where the real curve has
sister-fallback-eligible gaps.

The 85mm Tier 1 anchor calibrated `samyang-4color-all-solid` cleanly
within the pre-S170 in-band threshold because its 30S curve stays
above MTF ~ 0.85 across the field — the halo band sits at the plot
top where it overlaps the real M30 curve at high MTF, so the
mis-track produces no GT-detectable error there. The 12mm fisheye
shape exposes the contamination by having 30S dive below MTF ~ 0.7
while 30M dives further to MTF ~ 0.46, separating the two y-bands
by ~ 100 pixels.

## Decision

Add `("30S-dark-grey", "30M-light-grey")` to
`SAMYANG_4COLOR_ALL_SOLID.halo_pairs` in
`tools/mtfdigitizer/profiles/declared.py`. No new mechanism — reuses
the existing ADR-059 ring-subtraction pipeline.

```
SAMYANG_4COLOR_ALL_SOLID.halo_pairs = (
    ("10S-red",        "10M-pink"),         # ADR-059 (#1216, S167)
    ("30S-dark-grey",  "30M-light-grey"),   # ADR-062 (#792, S170)
)
```

## Alternatives considered

1. **Tighten 30M's V-band.** The 12mm fisheye's halo wrap V reaches
   ~ 187, just below 30M's `v_max=195`. Lowering `v_max` to 160 would
   exclude the halo but also clip the saturated 30M core which sits
   at V ~ 178 on this chart and other Samyangs.

2. **Broaden 30S's V-band to swallow the halo.** Raising 30S's `v_max`
   from 115 to ~ 200 would catch the wrap pixels under the dark-grey
   label, but it would also catch every legitimate light-grey curve
   pixel — the 30M curve's core V ~ 178 would be claimed by 30S.

3. **Per-chart override.** Make the halo pair a chart-level field
   rather than a profile-level field. Rejected: the contamination is
   a property of the chart family's palette (every Samyang chart with
   a dark grey 30S diving below MTF ~ 0.7 has the same wrap pattern).
   Profile-level is the right scope.

4. **No-op and route via sister fallback.** Without the halo
   subtraction the M30 mask is non-empty at the right edge, so sister
   fallback never fires; the sampler returns the halo value.
   Requires a different recovery mechanism downstream.

## Consequences

### Positive

- `samyang-85mm` anchor freq30M p95 |d| improves **0.086 -> 0.026**
  (calibrate S170, n=11).
- Aggregate calibration p95 |d| improves **0.0466 -> 0.0462**,
  in-band 95.9% -> 96.0%.
- The 12mm fisheye and other Samyang Tier 2 charts with 30S diving
  below MTF ~ 0.7 will read the legitimate 30M curve instead of the
  S30 halo (verified by diagnostic mask inspection, full Tier 2
  re-extraction deferred per #792's dual-aperture follow-up).

### Negative / accepted tradeoff

- `samyang-85mm` triage verdict flips **HIGH -> LOW** with reason
  `PRECISION_BELOW_THRESHOLD`. The 30M skeleton gets halo-emptied in
  cells the sister fallback then fills correctly (GT confirms the
  improvement); the polyline runs through skeleton-empty space,
  dragging render-match precision from ~ 0.85 to ~ 0.72 (below the
  0.80 gate).
- Same shape as the existing Sigma 56mm anchor classifying LOW for
  precision (ADR-059's documented tradeoff): a real lens with
  GT-correct extraction whose render-match precision the metric does
  not credit. The maintainer-glance routing the gate produces is the
  right operational outcome regardless of the label.
- The render-match precision metric not crediting sister-filled cells
  is a known limitation. A redesign that down-weights sister-fill is
  out of scope for this ADR; left to a separate spike.
- Test fixtures updated:
  - `test_reference_samyang_85_classified_high` renamed to
    `test_reference_samyang_85_classified_low_for_precision` with
    `LowReason.PRECISION_BELOW_THRESHOLD` assertion, mirroring the
    Sigma test's shape.
  - `test_score_chart_polyline_mostly_lands_on_skeleton` extends its
    `freq10M` exclusion to also exclude `freq30M`, the same halo-
    emptied-skeleton pattern ADR-059 first documented.

### Scope this ADR does NOT cover

- The dual-aperture (MAX + F8 panel) shape of Samyang charts. Each
  chart packs two apertures stacked vertically; the existing scaffold
  and orchestrator only handle the MAX panel. Tracked separately
  (#792 follow-up) — requires a `ChartView` aperture extension and
  per-chart F8 plot-box detection.
- Re-extraction of the 18 Tier 2 Samyangs. Deferred to the dual-
  aperture rework so each lens's per-aperture artifacts and
  digitization-log.md emit once per aperture rather than getting
  re-written when F8 support lands.
