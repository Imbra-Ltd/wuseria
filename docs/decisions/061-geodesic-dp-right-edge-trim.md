# ADR-061: Geodesic-DP right-edge flatline trim

**Status:** Accepted
**Date:** 2026-06-20

## Context

The `extract_two_curves_dp` Viterbi pass returns one (x, y) per plot
column. Its smoothness prior bridges dashed-line gaps and refuses to
hop to a parallel curve at near-touching regions. The pass has a
documented limitation (`dp_extract.py` module docstring, #1044) on
cliff corners where a curve dives off the bottom of the plot box at
the right edge — the prior holds the path at the last validated y
rather than following the curve into pure-white space.

#1213's S165 right-corner probe identified this as a profile-level
failure of `tokina-2color-frequency` distinct from #1044's cliff
shape:

| Lens                      | Field     | p95 \|d\| | Failure pattern                                                              |
| ------------------------- | --------- | --------- | ---------------------------------------------------------------------------- |
| tokina-atx-m-33mm freq30M | frac=1.0  | 0.153     | M30 frozen at y=548 across col 1105-1156; GT 0.30, EX 0.43.                  |
| tokina-atx-m-56mm freq30M | frac=1.0  | 0.211     | M30 frozen at y=716 from col ~1639; GT 0.18, EX 0.35 (worst case in cohort). |
| tokina-atx-m-33mm freq30S | frac=1.0  | 0.142     | S30 frozen at y=562; GT 0.30, EX 0.41.                                       |
| tokina-atx-m-23mm freq30S | frac=0.8+ | 0.130     | Same shape at smaller scale (curve dives past plot bottom).                  |

The DP is correctly tracing real ink up to where the curve crosses
the plot bottom, then holds its last validated y across the empty
columns at the right edge. The downstream sampler reads the held y
as a measurement.

The S168 probe also confirmed that **not every flat tail is a bug** —
some Tokina freq30 curves descend through pure-white space with a
plausible slope (Tokina 23 freq30M: y=447→631 across col 1107-1345,
smoothness prior extrapolating correctly). A blanket "no raw ink →
None" rule would drop those correct values too.

The distinguishing signal: a frozen DP path holds y CONSTANT across
many columns; a correctly-extrapolating path's y CHANGES across the
same stretch. Adding the raw-mask check as a second condition rules
out the easy false-positive (a genuinely-flat curve with real ink
behind it — Tokina 23 freq10S, which holds y=273 at the right edge
WITH ink at y=273 the whole way).

The acceptance criterion of #1215 explicitly allows frac=1.0 cells
where the curve falls below the plot box to remain `None` rather than
wrong — confirming that "no value" is preferable to "wrong value" at
the field edge.

## Decision

Add a right-edge flatline trim to `extract_two_curves_dp`. The trim
scans from the right edge inward, identifying columns that are both
(a) within ±1 px of the trace's last y AND (b) have no raw-mask ink
within ±8 rows of that y. The first column failing either condition
stops the scan. If the resulting trailing run is ≥ 12 columns, those
columns are dropped from the returned `CurvePoints`; the rasteriser
and sampler then treat them as "no curve" — the sampler returns
`None` at fractions landing in the trimmed region.

```
DP trace y across right edge of Tokina 56 freq30M:

  col: ... 1495 1519 1543 1567 1591 1615 1639 1663 1668
  y:   ... 557  559  573  602  631  693  716  716  716
                                       ^ raw ink ^ no ink anywhere near y=716
                                                 ^ no raw ink, y constant
                                                              ^ TRIM from here
```

The trim is wired into `extract_two_curves_dp` only. The single-curve
variant `extract_one_curve_dp` serves the (`SPLIT_BY_DASH`,
`GEODESIC_DP`) dispatch where the dashed-meridional curve has
legitimate column gaps that the trim's "no raw ink" check would
misread as a flatline (Sigma 56 freq30M dashed regressed from p95
0.024 to 0.366 when the trim was applied uniformly; gated to two-
curve only, it is unchanged).

### Sister fallback under authoritative presence

Trimming the curve makes the sampler return `None` at frac=1.0, but
the existing sister fallback would then substitute the sister curve's
value — which is wrong where the two curves diverge sharply at the
field edge (Tokina 56 freq30M dives to 0.18 while freq30S stays at
0.45). Two changes restore the trim's verdict:

1. **Per-field skeleton presence for HUE_IS_CURVE/GEODESIC_DP.** The
   raw per-hue mask carries both frequencies under one color (M-blue
   is freq10M AND freq30M), so it cannot distinguish "freq30M ended
   here" from "freq10M still has ink here." For these profiles the
   sister-fallback presence mask is built from the DP-derived field
   skeleton instead, dilated horizontally by 5 px to absorb minor
   sampling jitter. The skeleton encodes the trim — its right edge
   sits at the last kept column.

2. **`presence_is_authoritative` flag on `_apply_sister_fallback`.**
   When True (HUE_IS_CURVE/GEODESIC_DP), `field_presence[i] is False`
   is the trim's authoritative verdict and suppresses BOTH the
   sampler-None trigger and the sister-has-ink trigger — `None` stays
   `None`. For other profiles the flag defaults False; their
   historical behaviour (where coarse raw-mask presence is the only
   signal) is unchanged.

### Calibration impact

| Metric                | Before (S168) | After (S169) |
| --------------------- | ------------- | ------------ |
| Aggregate p95 \|d\|   | 0.0499        | 0.0466       |
| Aggregate max \|d\|   | 0.1745        | 0.1217       |
| Aggregate in-band     | 94.9%         | 95.9%        |
| Paired comparisons    | 810           | 798          |
| Tokina 33 freq30M p95 | 0.153         | 0.084        |
| Tokina 33 freq30S p95 | 0.142         | 0.040        |
| Tokina 56 freq30M p95 | 0.211         | 0.102        |
| Tokina 56 freq30S p95 | 0.096         | 0.096        |
| Tokina 23 freq30M p95 | 0.047         | 0.047        |
| Tokina 23 freq30S p95 | 0.130         | 0.137        |
| Sigma 56 freq30M p95  | 0.024         | 0.024        |

12 cells dropped (paired 810→798) are all at frac=1.0 on Tokina prime
charts where the curve genuinely falls past the plot bottom — the
intended outcome per the acceptance criterion. Tokina 23 freq30S p95
shifted from 0.130 to 0.137 because frac=1.0 (the chart's worst cell
at Δ 0.102) was trimmed and the new p95 is driven by frac=0.8
(Δ 0.122); the underlying readings did not regress.

## Alternatives considered

1. **Sampler refusal on missing raw ink** (#1215 issue hint). When
   `_snap_to_raw_centroid` returns None, return None from the sampler
   instead of falling back to the skeleton y. Simpler one-line
   change, but cannot distinguish a frozen DP path (Tokina 33/56)
   from a correctly-extrapolating one (Tokina 23 freq30M descends
   through no-ink space). Would regress Tokina 23 freq30M frac=0.9
   and 1.0 from Δ 0.015 and 0.018 to `None`. Rejected — the trim's
   AND of "y constant" + "no raw ink" cleanly distinguishes the two
   shapes.

2. **DP edge extrapolation with last-known slope.** Change the
   Viterbi pass to extrapolate trajectory past the last "real ink"
   column instead of holding y constant. Would correct the Tokina
   33/56 cases by descending the path further, but invents a slope
   model the DP does not have ground truth for. Rejected — the
   acceptance criterion explicitly endorses None over wrong, and the
   trim is a smaller, more local change than modifying the Viterbi
   smoothness prior.

3. **Stronger smoothness prior or raw-mask-weighted emission cost.**
   Module docstring (#1044) notes this would need an additional signal
   ("this y has real ink, not dilation echo" weighting). The
   docstring's S120 dead-end notes show two related attempts already
   failed (`_ALPHA=0.05` and sampler-slab-median refactor). Out of
   scope for #1215.

4. **Apply trim to `extract_one_curve_dp` too.** Initial
   implementation. Regressed Sigma 56 freq30M dashed from p95 0.024
   to 0.366 — the dashed-meridional curve's legitimate column gaps
   look like a flatline to the trim. Rejected; trim gated to the
   two-curve dispatch.

## Consequences

- New `_FLATLINE_TRIM_MIN_COLS=12`, `_FLATLINE_TRIM_DY_TOL=1`, and
  `_FLATLINE_TRIM_RAW_DY_HALF=8` constants in `dp_extract.py`. Tuned
  once against the Tokina cohort; if a future chart shows a
  legitimate flat tail shorter than 12 cols with no ink (unlikely —
  charts that print a flat MTF tail print it with ink), the
  threshold may need adjustment.
- New `_DP_PRESENCE_BRIDGE_W=5` constant in `pipeline.py`; the
  per-field skeleton dilation width for HUE_IS_CURVE/GEODESIC_DP
  presence.
- `_apply_sister_fallback` gains a kwarg `presence_is_authoritative:
bool = False`. Default preserves historical behaviour for all
  non-GEODESIC_DP-hue-is-curve profiles. Only the Tokina
  `2color-frequency` profile flips it on today; future HUE_IS_CURVE/
  GEODESIC_DP profiles inherit the same gate automatically.
- The contract of `extract_two_curves_dp` changes: returned
  `CurvePoints.points` may be shorter than `plot_box.width`. The
  existing rasteriser `curves_to_field_skeletons` already handles
  sparse points by iterating `curve.points` — no other call site
  needed updating. The pre-existing test
  `test_curves_to_field_skeletons_rasterises_at_every_column` was
  updated to reflect the new contract and renamed to
  `test_curves_to_field_skeletons_rasterises_columns_in_curve_points`.
- `extract_one_curve_dp` is documented as trim-exempt; the docstring
  explains the reason (dashed-curve column gaps).
- Tokina 23 freq30M loses a previously-correct frac=1.0 value
  (Δ 0.018 was the closest extrapolation in the cohort). This is the
  trim's intentional uniform treatment of the shape, accepted under
  #1215's acceptance criterion. The lens' freq30M p95 stays at 0.047
  because the new None cell does not contribute to p95.

## Open

- Tokina 23 freq30S frac=0.8 remains at Δ 0.122 and frac=0.2 at
  0.087. These are NOT the frozen-DP-at-right-edge shape (the freeze
  happens earlier in the trace, around col 1107, where the DP locks
  onto a wrong y and stays there across cols 1107-1300). A separate
  investigation could trace whether the curve's earlier flatline is
  also a candidate for refusal; out of scope for #1215, which is
  scoped to right-edge trim.
