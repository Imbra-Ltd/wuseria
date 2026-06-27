# ADR-074: Below-top spurious-CC filter for HUE_IS_CURVE masks

**Status:** Accepted
**Date:** 2026-06-27

## Context

ADR-059 added profile-declared `halo_pairs` to subtract a contaminator's
dilated AA-ring from a contaminated hue's mask. That mechanism handles
the "saturated red has a halo bleeding into pink" shape: contamination
co-located with the contaminator's own ridge, within the vertical
dilation radius (`_HALO_DILATE_DY = 5`).

#1328 surfaced a second shape on the same Samyang family that the
halo-ring subtraction cannot reach. On the Samyang 20mm f/1.8 F8
(stopped) panel:

- The chart's real 10S curve sits flat at MTF ≈ 0.99 across the field
  (pixel-verified at every column).
- The `10S-red` raw mask has 1292 pixels at y=578-580 (the true ridge)
  PLUS 125 spurious pixels at y≈600 (MTF ≈ 0.93) where the pink 10M
  curve passes through a darker shade, landing in the `10S-red` HSV
  box (`h 168-179, s_min=140, v_min=60`).
- The 125 spurious pixels form 2 small connected components (95 and 30
  pixels). They sit ~22-26 rows below the true ridge.
- At affected columns, the 10S-red skeleton has TWO ridges in the
  sampler's bracket window. `sample_skeleton_at_fraction` takes the
  median y → falls between the two ridges. Snap-to-raw misses (real
  ink at y=578-580 is outside the ±8 snap window from y≈590), so
  the sampler returns MTF ≈ 0.94 / 0.96 instead of 0.99.

Why ADR-059's halo mechanism cannot fix this:

- The spurious red pixels at frac 0.5 sit at columns where the pink
  raw mask has 0 pixels in the same column (pink crosses through a
  darker shade that no longer matches the pink box at all). The
  vertical-only halo-ring subtraction has nothing to subtract from.
- Even if a 2D dilation were added, the contaminator/contaminated
  relationship is geometrically inverted: this is contamination
  caused by the contaminated hue's own crossing geometry, not the
  contaminator hue's halo. The halo model does not apply.

Survey across all 19 Samyang `mainstream-4color-all-solid` charts
(38 panel readings) shows the signature is highly localized to
Samyang 20mm stopped. Other panels have at most ~20-300 px secondary
CCs whose y-centroids sit close to the dominant CC's centroid — the
sampler tolerates them because both ridges share roughly the same y.
Only the Samyang 20mm 95-px CC sits 22-26 rows below the true ridge
AND is small enough to be unambiguously noise.

ADR-059 named this case in its "Alternatives considered" section:

> **Profile-level CC-area filter** (drop disconnected mask components
> below a width threshold). Rejected as a primary mechanism: heuristic,
> risks failing on charts with narrow real features. May still be a
> complementary cleanup for non-halo contamination (e.g. legend text
> in chart families where halo isn't the dominant signal).

This ADR adopts the alternative as a complementary mechanism, scoped
to the case the halo path cannot reach.

## Decision

Add `MtfProfile.small_below_top_cc_filters: tuple[tuple[str, int, int], ...] = ()`.
Each tuple declares `(curve_name, min_area, max_y_delta)`. The pipeline
applies the filter to the named curve's raw mask after halo subtraction
and before skeletonization:

1. Compute 8-connectivity connected components of the curve mask
   (clipped to the plot box).
2. Identify the dominant CC (largest area) and its y-centroid (in
   panel-local row coords).
3. Zero out every other CC whose y-centroid is **more than
   `max_y_delta` rows below** the dominant CC AND whose area is
   **less than `min_area` pixels**.

A CC must satisfy BOTH conditions to be dropped. The y-delta gate
preserves legitimate near-overlap fragments (e.g. Samyang 85 stopped
where 10S and 10M both sit at MTF≈1.0 within 2-3 px of each other);
the area gate preserves legitimate dim or fragmented curves whose
mass exceeds the threshold.

```
+--------------------------------------------------------------+
| field_skeletons / pipeline.extract_chart                     |
+--------------------------------------------------------------+
        |
        |  masks_by_curve_name(hsv, profile)
        |  clip to plot_box
        v
+--------------------------------------------------------------+
| curve_masks: {hue_name -> binary_mask}                       |
+--------------------------------------------------------------+
        |
        |  _apply_declared_halo_pairs(curve_masks, halo_pairs)        ADR-059
        v
+--------------------------------------------------------------+
| curve_masks (halo-subtracted)                                |
+--------------------------------------------------------------+
        |
        |  _apply_small_below_top_cc_filter(                          NEW (ADR-074)
        |    curve_masks, small_below_top_cc_filters)
        |  for each (curve_name, min_area, max_y_delta):
        |    cc = connected_components(curve_masks[curve_name])
        |    top = argmax_area(cc)
        |    for each other cc_i:
        |      if y(cc_i) > y(top) + max_y_delta
        |         and area(cc_i) < min_area:
        |        curve_masks[curve_name] -= cc_i
        v
+--------------------------------------------------------------+
| curve_masks (filtered)                                       |
+--------------------------------------------------------------+
        |
        |  dispatch branch
        v
+--------------------------------------------------------------+
| field skeletons                                              |
+--------------------------------------------------------------+
```

Apply on `SAMYANG_4COLOR_ALL_SOLID` only:
`small_below_top_cc_filters = (("10S-red", 200, 10),)`.

The thresholds are chosen from the actual CC size distribution
across the 19 Samyang `mainstream-4color-all-solid` anchors (see
"Calibration impact" below):

- `min_area = 200`: drops the 95-px and 30-px Samyang 20mm spurious
  blobs; preserves the 222-px Samyang 85 stopped secondary CC (which
  is legitimate near-overlap, not noise).
- `max_y_delta = 10`: ensures legitimate fragments near the dominant
  CC are preserved (Samyang 8mm-f2-8 stopped has a 275-px CC at
  delta=3 from the dominant; this stays).

## Alternatives considered

| Alternative                                              | Rejected because                                                                                                                                                                                                                                                                                                                                            |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Widen ADR-059's halo subtraction to 2D (horizontal)      | Spurious red at frac 0.5 sits at a column where the pink raw mask has 0 pixels. Even unlimited horizontal dilation wouldn't subtract pixels that don't exist in the same row neighbourhood.                                                                                                                                                                 |
| Tighten the `10S-red` HSV box (raise `s_min` or `v_min`) | Legitimate dim 10S pixels on other Samyang charts (max-aperture panels at the corner) fall in the same H/S/V range as the spurious blob. Tightening would lose real ink to gain nothing.                                                                                                                                                                    |
| Sampler-side "topmost ridge" preference for S curves     | Special-purpose; would also need a guard against charts where 10S legitimately dips (Samyang 50mm-f1-4 max has 10S going from 0.91 → 0.65). The skeleton multi-ridge condition only fires on the specific bug shape; sampler can't distinguish bug from feature.                                                                                            |
| Apply filter to all four curves (10S, 10M, 30S, 30M)     | Other curves have legitimate fragmented masks: Samyang 20mm stopped 10M-pink mask has 5 CCs all in the 150-500 px range; 30S has 4 CCs all in the 70-200 px range. Filter would destroy these. The single-dominant-CC property holds only for `10S-red` because the curve sits at the very top of the panel and never crosses another curve in this family. |
| Per-chart override on `ReferenceChart`                   | More precise scope (only Samyang 20mm stopped) but the failure mode is a property of the chart family's color palette, not a property of any individual chart. Declaration belongs on the profile, like `halo_pairs`.                                                                                                                                       |

## Consequences

### Positive

- samyang-20mm stopped freq10S: `[0.99, 0.99, 1.00, 0.99, 0.99, 0.94,
0.96, 0.99, 0.96, 0.99, 0.99]` → `[0.99, 0.99, 1.00, 0.99, 0.99,
0.99, 0.99, 0.99, 0.99, 0.99, 0.99]`. Maintainer-reported defect
  resolved.
- Filter mechanism is profile-declared, opt-in, default-empty: every
  existing profile is unaffected unless it declares filters.
- Applied at the top of `field_skeletons` and in `pipeline.extract_chart`
  (presence-mask path), so every dispatch branch and the sister-fill
  presence calculation see the same cleaned masks.
- Tested on all 19 Samyang `mainstream-4color-all-solid` anchors × 2
  panels: only the bug case changes; 37 other panel readings are
  byte-identical.

### Negative

- New tunable parameters (`min_area`, `max_y_delta`) sized from the
  current data distribution. If a future Samyang chart has a
  legitimate small below-top CC, the filter would suppress it. The
  size + delta gate makes this unlikely (legitimate small CCs in this
  family always sit close to the top), but documenting the data-fit
  origin so a future maintainer can re-tune.

### Neutral

- The mechanism stacks with ADR-059. Halo subtraction runs first
  (handles the "halo of a present contaminator" case), then the
  CC filter runs (handles the "spurious mass with no nearby
  contaminator" case). Neither overlaps the other's coverage.
- No other declared profile uses the filter today. The mechanism is
  available for future profiles that need it.

### Open

- If a second consumer needs different thresholds, the constants stay
  per-declaration as they are. No global tunable.
- Other `HUE_IS_CURVE/CURVE_IDENTITY` profiles may surface similar
  cases as more brands enter Tier 2. The fix mechanism is uniform.
