# ADR-059: Declared cross-hue halo pairs for AA-gradient subtraction

**Status:** Accepted
**Date:** 2026-06-19

## Context

The digitizer extracts curve identity from per-hue HSV masks. When two
hues' `HueRange` definitions share an HSV boundary value, the AA gradient
around the more saturated hue's curve bleeds into the less saturated
hue's mask, producing a spurious second y-band in the contaminated hue's
skeleton.

The TTartisan profile already addresses one shape of this problem
(#1095, ADR-045): on the `FREQUENCY_PER_HUE_RIDGE` dispatch branch, the
extractor auto-derives `(contaminator, contaminated)` pairs from
aperture prefix + frequency (lower-frequency hue is the contaminator,
higher-frequency same-aperture hue is the contaminated) and subtracts
the dilated contaminator from the contaminated.

S167's #1216 probe surfaced a second shape:

- **Samyang `mainstream-4color-all-solid` (`HUE_IS_CURVE/CURVE_IDENTITY`
  dispatch branch).** The contaminator is the high-saturation
  `10S-red` hue. The contaminated is the lower-saturation `10M-pink`
  hue whose `HueRange` sets `s_max=140` exactly matching red's
  `s_min=140`. Around any saturated red curve, the AA gradient
  transitions from white (S=0) to red core (S=255) passing through
  every intermediate S value, so pink catches the S∈[40,140] ring
  around every red curve pixel.
- **The contaminated/contaminator pair is NOT same-aperture-different-frequency.**
  Both Samyang hues belong to the same frequency (10 lpmm), the same
  aperture (max). The TTartisan auto-derivation cannot infer this pair.
- **The contaminated hue's skeleton at the right corner reads the
  S10-halo y-band, not the real M10 y-band.** Sampling at frac=1.0
  returns the S10-halo position (MTF ≈ 0.78) instead of the real M10
  position (MTF ≈ 0.93). Calibration: samyang-85 freq10M p95 |d|
  0.175 (worst-cell GT 0.93, EX 0.78).

A profile-level declaration is needed because the relationship is
neither aperture-derived (Samyang has no aperture multi-pass) nor
frequency-derived (both hues are 10 lpmm). The pair is a property of
the chart family's color palette, declared per profile.

## Decision

Add `MtfProfile.halo_pairs: tuple[tuple[str, str], ...] = ()` listing
`(contaminator_hue_name, contaminated_hue_name)` pairs. The dispatcher
applies the subtraction before any dispatch branch runs, so every
codepath benefits uniformly. The mask presence-check in `pipeline.py`
applies the same subtraction so sister fallback fires honestly when
the contaminated hue's mask is empty at a sample point.

```
+----------------------------------------------------------+
| field_skeletons(bgr, profile, plot_box)                  |
+----------------------------------------------------------+
        |
        |  masks_by_curve_name(hsv, profile)
        v
+----------------------------------------------------------+
| curve_masks: {hue_name -> binary_mask}                   |
+----------------------------------------------------------+
        |
        |  clip to plot_box (existing)
        v
+----------------------------------------------------------+
| curve_masks (clipped)                                    |
+----------------------------------------------------------+
        |
        |  _apply_declared_halo_pairs(curve_masks,           NEW
        |                             profile.halo_pairs)
        |  for each (contaminator, contaminated):
        |    ring = dilate(contaminator) AND NOT contaminator
        |    curve_masks[contaminated] = curve_masks[contaminated]
        |                                AND NOT ring
        v
+----------------------------------------------------------+
| curve_masks (halo-subtracted)                            |
+----------------------------------------------------------+
        |
        |  dispatch branch (any of SPLIT_BY_DASH, HUE_IS_CURVE/CURVE_IDENTITY,
        |  HUE_IS_CURVE/GEODESIC_DP, ...)
        v
+----------------------------------------------------------+
| field skeletons (per-field binary masks)                 |
+----------------------------------------------------------+
```

The subtraction uses morphological RING (`dilate(contaminator) AND NOT
contaminator`), not full dilation. The ring is the immediate exterior
shell of the contaminator where the AA gradient lives; the
contaminator's interior is spared. This protects cases where the
contaminated curve genuinely overlaps the contaminator (Samyang M10
and S10 at high MTF both sit at the plot top within a few pixels of
each other) — those columns get the contaminated mask emptied, and
sister fallback covers the gap.

Same `_HALO_DILATE_DY = 5` kernel as the existing TTartisan
mechanism. No new tunable.

## Alternatives considered

- **Tighten the contaminated `HueRange`** (e.g. raise pink's `s_min`).
  Rejected: the contaminated and contaminator masks pick up pixels of
  effectively the same HSV at the AA gradient boundary (probe data:
  upper-band H∈[171,174] S∈[40,115] V∈[220,244]; real-curve H∈[172,174]
  S∈[42,139] V∈[218,245] — overlap is nearly complete). Any tightening
  that strips the halo also strips the real curve.

- **Profile-level CC-area filter** (drop disconnected mask components
  below a width threshold). Rejected as a primary mechanism: heuristic,
  risks failing on charts with narrow real features. May still be a
  complementary cleanup for non-halo contamination (e.g. legend text
  in chart families where halo isn't the dominant signal).

- **Plot-box top exclusion** (strip the top N% of any skeleton).
  Rejected: the real M10 curve on Samyang sits at MTF≈0.93 = y≈72,
  almost exactly where the spurious y-band sat. Stripping the top kills
  the real signal.

- **Extend the TTartisan `_build_halo_exclusion_map` auto-derivation
  to cover Samyang.** Rejected: the Samyang relationship is
  not-same-aperture (Samyang has no apertures) and not-different-
  frequency (both hues are 10 lpmm). Auto-derivation would require
  adding heuristics to detect "high-saturation hue contaminates
  low-saturation hue of same-frequency-same-aperture-group," which
  is brittle and not generalizable. Explicit per-profile declaration
  is clearer and easier to extend.

- **Full dilation subtraction (no ring).** Rejected: over-subtracts at
  high-MTF overlap points. Samyang M10 and S10 both at MTF≈0.91 sit
  within 2-3 px of each other; full dilation of S10 erases M10's real
  ink at those columns; sister fallback then copies S10's value to
  M10, masking that the curves had diverged. Ring-only preserves the
  contaminator's interior so sister fallback fires honestly.

## Consequences

### Positive

- samyang-85 freq10M p95 |d|: 0.175 → 0.026 (huge win, frac=1.0
  reading GT 0.93 EX 0.78 → EX 0.93).
- samyang-85 freq10S: unchanged at p95 0.029 (no spillover).
- samyang-300 (other chart in family): freq10M paired 10/11 → 11/11;
  freq30S paired 0/11 → 5/11 (improved). No regression on freq30M.
- Aggregate calibration: 805 → 811 paired comparisons; p95 |d| 0.0526
  → 0.0505; in-band 94.5% → 94.9%.
- The mechanism is profile-declared, opt-in, default-empty: every
  existing profile is unaffected unless it declares pairs.
- Applied at the top of `field_skeletons`, so every dispatch branch
  benefits without per-branch wiring.
- Presence-mask path updated to apply the same subtraction, so sister
  fallback fires correctly when contaminated hue's mask is empty at a
  sample point (samyang-85 freq10M frac=0.1-0.5 cells now sister-filled
  from freq10S instead of reading None).

### Negative

- Adds a presence-mask handler for `HUE_IS_CURVE/CURVE_IDENTITY` that
  wasn't wired before — Samyang is the only consumer of this dispatch
  branch shipped today, so the new code path has narrow test coverage
  outside the calibration probe.
- `test_score_chart_polyline_mostly_lands_on_skeleton` previously
  asserted ≥ 0.85 mean precision across all 4 Samyang fields. Post-fix
  the freq10M skeleton is honestly sparse (M10 readings at frac=0.1-0.5
  come from sister fallback, not direct skeleton ink), and the
  polyline drawn from corrected freq10M values runs through sister-
  filled gaps. The test now excludes `freq10M` with a docstring note;
  the other 3 fields stay above the bar.

### Neutral

- The existing TTartisan `_build_halo_exclusion_map` mechanism is
  untouched. Both mechanisms coexist; the TTartisan auto-derivation
  applies inside its dispatch branch as before, the declared pairs
  apply at the top of `field_skeletons` before any branch. The two
  are not duplicative — they cover different relationships
  (aperture-derived vs. profile-declared) on different branches.
- No new tunable. The shared `_HALO_DILATE_DY = 5` covers both.

### Open

- Other `HUE_IS_CURVE/CURVE_IDENTITY` profiles may eventually need
  similar declarations. The mechanism is uniform; the declaration is
  one tuple per pair.
- If a future profile needs a different dilation radius for its halo
  pairs, the constant becomes a per-pair (or per-profile) parameter.
  Deferred until a second consumer needs it (YAGNI per `quality.md`).
