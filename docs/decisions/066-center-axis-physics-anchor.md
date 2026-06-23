# ADR-066: Center-axis physics anchor at frac=0.0 (S=M=1.0)

**Status:** Accepted
**Date:** 2026-06-23

## Context

The 11-point sampler returns `None` when no skeleton ink exists within
its bracket window of a target column (B2 fail-safe, #931). Two
downstream stages can fill that `None`: sister fallback (copy the
sister curve's value when the field's own ink is absent) and intra-
curve interpolation (replace single-cell sister-fills with a within-
curve linear interp, #1254). A third stage, `_apply_center_symmetry`,
runs after both and enforces the B4 physics rule **S=M at the optical
axis (frac=0.0)** by overriding M with S (or, if S is `None`, copying
M to S).

### Diagnostic (#1267)

On three Samyang Tier 2 stopped panels and five Fujifilm Tier 2 panels,
both `freq{N}S[0]` and `freq{N}M[0]` are still `None` after sister
fallback. Sister fallback cannot fire because both sides of the
frequency pair lack ink at frac=0.0 — it has no value to copy.

Per-field probes on `samyang-10mm-f2-8-ed-as-ncs-cs` stopped panel:

| field         | first skeleton ink column | frac equivalent |
| ------------- | ------------------------- | --------------- |
| `freq10S`     | x=43                      | ~0.028          |
| `freq10M`     | x=33                      | ~0.005          |
| **`freq30S`** | **x=138**                 | **~0.249**      |
| `freq30M`     | x=44                      | ~0.030          |

The dark-grey 30S curve sits physically underneath the saturated-red
10S across the first ~25% of the field at MTF ~ 0.99; the HSV-band
dispatch cannot separate them, leaving the 30S skeleton empty across
those columns. Both 30S and 30M are then `None` at frac=0.0, and the
existing symmetry rule's `if s_val is None and m_val is None: continue`
guard leaves them `None`.

In the rendered SVG the polyline starts at frac=0.1 instead of the
y-axis, producing a visible gap from 0 to 1.4mm — visually identical
to "the corner crashed to MTF=0" even though by physics the optical-
axis MTF is 1.0.

Affected lenses (audit across all 20 Samyang Tier 2 + Fujifilm logs):

| Lens                                                   | Missing fields at frac=0.0 |
| ------------------------------------------------------ | -------------------------- |
| `samyang-10mm-f2-8-ed-as-ncs-cs` (stopped)             | `freq30S`, `freq30M`       |
| `samyang-12mm-f2-8-ed-as-ncs-fish-eye` (stopped)       | all four                   |
| `samyang-af-12mm-f2-0` (stopped)                       | `freq10S`, `freq10M`       |
| `fujifilm-gf-55mm-f1-7-r-wr` (40lp)                    | `freq40S`, `freq40M`       |
| `fujifilm-xf-150-600mm-f5-6-8-r-lm-ois-wr` (wide-45lp) | `freq45S`, `freq45M`       |
| `fujifilm-xf-16-50mm-f2-8-4-8-r-lm-wr` (wide-45lp)     | `freq45S`, `freq45M`       |
| `fujifilm-xf-16-55mm-f2-8-r-lm-wr` (wide-45lp)         | `freq45S`, `freq45M`       |
| `fujifilm-xf-16-80mm-f4-r-ois-wr` (wide-45lp)          | `freq45S`, `freq45M`       |
| `fujifilm-xf-23mm-f2-8-r-wr` (45lp)                    | `freq45S`, `freq45M`       |
| `fujifilm-xf-8mm-f3-5-r-wr` (45lp)                     | `freq45S`, `freq45M`       |
| `ttartisan-50mm-f2-0`                                  | one pair                   |

Common pattern: a **high-frequency** pair (30 or 45 lp/mm) where both
S and M happen to be the same colour or hide under another curve
near the optical axis at MTF ~ 1.0.

## Decision

Extend `_apply_center_symmetry` in
`tools/mtfdigitizer/pipeline/pipeline.py` with a third branch: when
both `freq{N}S[0]` and `freq{N}M[0]` are `None` after sister fallback
and intra-curve interpolation, anchor both to **MTF=1.0** — the
diffraction-free optical-axis value.

```
    if s_val is None and m_val is None:
        out[s_field][0] = 1.0
        out[m_field][0] = 1.0
        anchor_count[s_field] += 1
        anchor_count[m_field] += 1
        continue
```

Three constraints that keep the rule safe:

1. **frac=0.0 only.** The right edge has no equivalent physical
   guarantee (corner MTF varies wildly across lenses); applying the
   rule there would fabricate values.
2. **Both sides None only.** When either side has a value, the
   existing symmetry rule (copy S to M, or copy the present side to
   the absent side) takes precedence. The anchor is the last-resort
   fallback.
3. **Last in the chain.** Runs after direct extraction, sister
   fallback, and intra-curve interpolation. If any earlier stage can
   produce a value, that value wins.

The fired-count is tracked per-field as
`ExtractedChart.center_anchor_count` and surfaced in the production
digitization log under a new `center-anchor` column. The column is
omitted from logs where no anchor fired (~95% of cases), so existing
clean logs stay visually unchanged.

```
| Field          | non-null | sister-fill | center-anchor |
| -------------- | -------- | ----------- | ------------- |
| freq30S        | 11/11    |  2/11       |  1/11         |
| freq30M        | 11/11    |  0/11       |  1/11         |
```

```
            +--- physics anchor (this ADR) ---+
            v                                 v
direct ---> sister --> intra-interp --> center-symmetry --> SVG
extract     fallback   (#1254)         S=M at frac=0.0
            (#1215)                    + anchor to 1.0 if
                                       both None (#1267)
```

## Alternatives considered

1. **Skeleton-aware corner extrapolation.** Scan up to ~20% of plot
   width past frac=0.0 to find the leftmost column with skeleton
   ink, and anchor frac=0.0 to that column's value. Rejected: drops
   the principled physics anchor in favour of an inferred value
   that varies with chart noise. Also loses signal — if the curve
   genuinely doesn't anchor at MTF=1.0 (unusual but possible for
   high-frequency curves with strong off-axis dispersion), the
   extrapolation hides the data gap; the physics anchor is honest
   that this cell came from a rule, not the chart.

2. **Cross-panel fallback (stopped <- max).** When stopped freq30* is
   `None` at frac=0.0 and max freq30* has a value, copy across.
   Rejected: stopping down can change center MTF (slightly), so the
   cross-copy is a weaker assumption than B4 physics. Also only
   works for multi-panel charts (Samyang); the Fujifilm 45lp panels
   are single-panel.

3. **Color V-band re-tuning.** Widen the grey V bands to capture the
   30S/30M curve cores at the contaminated columns. Rejected: would
   catch AA halo on lenses where the bands are already correct,
   regressing the existing halo-pair work (ADR-059, ADR-062).

4. **#954-style plot-box convention shift.** Set `x_left` to the
   first-data-column rather than the printed axis line. Necessary
   for tighter corner accuracy on some lenses (Sigma) but **not
   sufficient** here — shifting x_left by 1-2 px does not recover
   the 30S skeleton hidden under 10S for ~100 px past the axis line.

5. **Hand-edited per-lens overrides.** Patch the 8 affected logs/SVGs
   directly. Rejected: leaves the latent defect in the extractor for
   every future lens with the same chart-color pattern, and creates
   8 generator/manual-edit drift points.

## Consequences

### Positive

- 8 stale logs recovered to 11/11 non-null on the previously-empty
  frac=0.0 cells.
- Calibration aggregate improves from **872 paired, p95 0.0454,
  max |d| 0.1217, in-band 94.9%** (S177 baseline) to
  **878 paired (+6), p95 0.0462 (+0.0008), max |d| 0.1217
  (unchanged), in-band 96.0% (+1.1%)**. Six recovered cells on Tier 1
  anchors match their ground-truth values (which are 1.0 at frac=0.0
  for the affected fields), confirming the anchor is GT-correct
  where GT exists.
- Rendered SVGs anchor visually at the y-axis on all 8 affected
  lenses, closing the visual gap from 0 to the first plotted point
  that triggered #1267.
- Physics-principled (B4 rule) rather than chart-noise-derived; the
  rule is documented in code, tests, and ADR rather than buried as
  numeric thresholds.

### Negative / accepted tradeoff

- Render-match precision drops slightly on lenses where the anchor
  fires AND the chart's true MTF at frac=0.0 is below 1.0 (e.g.
  `fujifilm-gf-55mm-f1-7-r-wr` 40lp: 0.794 -> 0.767). The SVG now
  reads 1.00 at frac=0.0 while the chart reads ~0.98, costing a
  fraction of a precision point. Accepted: the corner anchor is
  closer to true physics than the prior missing-cell rendering, and
  the precision metric does not credit physical correctness when
  the chart artist plotted slightly below 1.0.

- The new `center-anchor` column adds one row to the log legend and
  one table column **only when the rule fires**. Clean logs (95% of
  the corpus) are byte-identical to before this ADR.

### Scope this ADR does NOT cover

- Right-edge (frac=1.0) anchor. No physics guarantee — corner MTF
  varies per lens. Lenses missing frac=1.0 stay missing; the B2
  fail-safe still applies.
- Mid-field anchoring. Sister fallback + intra-interp remain the
  rule for non-corner gaps.
- The HSV-band overlap that hides the 30S skeleton in the first ~25%
  of the Samyang stopped panel. This ADR recovers only the frac=0.0
  corner; mid-field 30S samples at frac 0.1-0.2 are still filled
  from the 30M sister (which can diverge at mid-field). A separate
  spike could revisit the dispatch's color-separation logic on
  curves that overlap structurally; not in scope here.
