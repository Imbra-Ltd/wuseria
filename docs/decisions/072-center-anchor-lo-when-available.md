# ADR-072: Center anchor uses freq{lo}{D} when available

**Status:** Accepted
**Date:** 2026-06-24

## Prerequisites

This ADR refines **ADR-066 (center-axis physics anchor at frac=0.0,
S=M=1.0)**. ADR-066 fires when both `freq{N}S[0]` and `freq{N}M[0]`
are None after sister fallback + intra-curve interpolation + coincident-
top anchor, and slams both cells to MTF=1.0 on the B4 physics premise
that the diffraction-free chart's optical-axis MTF is 1.0.

It also depends on **ADR-068 / ADR-069 (coincident-top anchor)** for
the same-direction lower-frequency copy mechanism — this ADR extends
the same mechanism to a case where ADR-068/069's pair gate has vetoed.

## Context

`viltrox-af-75mm-f1-2-pro` f/1.2 (the Tier 1 anchor refreshed in
PR #1278) publishes a chart whose `freq30S` and `freq30M` curves sit
visibly below MTF=1.0 at the optical axis — eye-read GT records
`freq30S[0] = 0.93` and `freq30M[0] = 0.92`. The lens is a fast prime
with notable spherical aberration at f/1.2; the chart artist drew
the high-frequency curves at their true centre values, not anchored
to chart top.

On this chart:

- `freq10S` and `freq10M` extract at MTF ~0.99 at center (correct
  against GT 1.00 within 0.01).
- `freq30S` and `freq30M` skeletons miss the leftmost columns (both
  buried under the brighter freq10 strokes, similar mechanism to
  samyang-10mm stopped per ADR-066's diagnostic).
- The ADR-068/069 coincident-top anchor's pair gate (`min |hi - lo|
on clean cells where lo >= 0.90`) measures `|0.90 - 0.99| = 0.09`
  at frac 0.4 and similar gaps at frac 0.3 and 0.6 — every clean
  pair-cell has `|hi - lo| > 0.05`. The gate correctly identifies
  this as a chart where `freq30S` does NOT track `freq10S` at chart
  top, and vetoes the `(freq30S, freq10S)` pair (same for M).
- ADR-066 then fires unconditionally on the remaining "both None"
  state and slams `freq30S[0] = freq30M[0] = 1.0`.

The result:

```
freq30S at frac=0.0:  EYE=0.93, EX=1.00, |Δ|=0.070  (over ±0.05 band)
freq30M at frac=0.0:  EYE=0.92, EX=1.00, |Δ|=0.080  (over ±0.05 band)
```

This was previously masked: before PR #1268 (ADR-066) the cells
stayed None and the log printed `—` for EX so no Δ was computed.
PR #1278 refreshing the Tier 1 log surfaced the regression.

### Physical invariant violation

ADR-066's 1.0 anchor violates a strict physical invariant when
`freq{lo}{D}` extracts below 1.0 at center:

- **Physics:** MTF is monotonically non-increasing in spatial
  frequency. `freq30S[f] <= freq10S[f]` at every frac, including
  frac=0.0.
- **Observed:** `freq10S[0] = 0.99` (extracted), `freq30S[0] = 1.00`
  (ADR-066 anchor). `1.00 > 0.99` — physically impossible.

ADR-069 already encodes this argument for the non-None case. From
ADR-069 §"Per-cell decision":

> `freq{lo}{D}` on the 300mm reflex extracts at ~0.985 at center
> due to raster snap to the nearest pixel row. If ADR-066 fires for
> the high-freq curve while the low-freq sits at 0.985, then
> `freq30S = 1.0 > freq10S = 0.985` — physically impossible (MTF is
> monotonically non-increasing in frequency).

The same argument applies when ADR-066 reaches the "both None" case
because ADR-069's pair gate vetoed. The gate's veto says "do not
trust hi to track lo across the field" — it does NOT say "physics
no longer constrains hi to lie at or below lo at the single optical-
axis cell". Physics still bounds `hi <= lo` at frac=0.0.

## Decision

Extend `_apply_center_symmetry` in
`tools/mtfdigitizer/pipeline/pipeline.py`'s "both None" branch (ADR-066,
case 3) with a same-direction lower-frequency lookup:

1. When both `freq{N}S[0]` and `freq{N}M[0]` are None at frac=0.0,
   look up the closest lower frequency `freq{lo}{S}[0]` and
   `freq{lo}{M}[0]`.
2. If either lower-freq same-direction cell carries a value, anchor
   the higher-freq cell to that value:
   - `freq{N}S[0] = freq{lo}{S}[0]` if not None, else `freq{lo}{M}[0]`,
     else 1.0
   - `freq{N}M[0] = freq{lo}{M}[0]` if not None, else `freq{lo}{S}[0]`,
     else 1.0
3. If no lower frequency exists in the chart, or both lower-freq cells
   are also None, fall back to ADR-066's original 1.0 anchor.

```
                         +--- ADR-069: coincident-top anchor ---+
                         |    (vetoed on viltrox-75 by gate)    |
                         v                                      |
direct ---> sister --> intra-interp --> coincident-top ---> center-symmetry
extract     fallback   (#1254)         (ADR-068/069)       (ADR-066+ADR-072)
                                                            "both None":
                                                            1) try freq{lo}{D}[0]
                                                            2) try freq{lo}{!D}[0]
                                                            3) fall back to 1.0
```

The new lookup runs before the 1.0 anchor, so:

- On viltrox-75: `freq30S[0] = freq10S[0] = 0.99`, `freq30M[0] =
freq10M[0] = 0.99`. Restores `hi <= lo`. Reduces Δ on freq30S from
  0.070 to ~0.060 and on freq30M from 0.080 to ~0.070. Still over
  the ±0.05 band — see Consequences.
- On samyang-10mm stopped (an ADR-066-designed lens with `freq10S[0]
= freq10M[0] = 0.99` extracted, GT 1.00): `freq30S[0] = 0.99`
  instead of 1.0. Slight regression against GT (|Δ| 0.00 → 0.01,
  still well inside the band). Restores `hi <= lo`.
- On samyang-af-12mm stopped (where `freq10S[0]` and `freq10M[0]` are
  themselves None at center, then ADR-066 anchors them to 1.0 in a
  prior loop iteration): when the freq10 pair runs first, it gets
  anchored to 1.0; when freq30 runs second, lo=1.0 is available and
  freq30 gets anchored to 1.0. Identical behaviour to current code.
  This holds because `_apply_center_symmetry` iterates by S-field
  and mutates `out` in place — later iterations see prior
  anchorings. No ordering guarantee is needed beyond what the
  function already provides: lower frequencies are processed before
  higher within a freq pair, but across pairs the iteration order
  follows the input dict (insertion order). The fallback chain is
  designed to be order-independent: any prior anchor leaves a usable
  value behind.
- On samyang-300mm reflex (ADR-069 anchor fires before ADR-066):
  freq30 is already non-None by the time `_apply_center_symmetry`
  runs. Both-None case never reached. Unchanged.

### Per-cell decision

```python
if s_val is None and m_val is None:
    freq_n = int(s_field[4:-1])
    lower = _closest_lower_freq(out, freq_n)
    if lower is None:
        out[s_field][0] = _CENTER_AXIS_MTF
        out[m_field][0] = _CENTER_AXIS_MTF
    else:
        lo_s = out[f"freq{lower}S"][0]
        lo_m = out[f"freq{lower}M"][0]
        out[s_field][0] = lo_s if lo_s is not None else (
            lo_m if lo_m is not None else _CENTER_AXIS_MTF
        )
        out[m_field][0] = lo_m if lo_m is not None else (
            lo_s if lo_s is not None else _CENTER_AXIS_MTF
        )
    anchor_count[s_field] += 1
    anchor_count[m_field] += 1
```

### Why this is the right level for the rule

The ADR-068/069 pair gate veto is intentionally local to the coincident-
top anchor's domain (multi-cell copy of lo into hi across the field).
It encodes "do not assume hi tracks lo wherever lo is at chart top".

At the single frac=0.0 cell, the relevant constraint is not "does hi
track lo across the field" but "is `hi <= lo` at this one cell". The
latter is a strict physical invariant that holds regardless of the
gate's verdict. So ADR-072 firing here is not a circumvention of the
gate — it is using the gate's lo-value evidence (`lo extracts at 0.99`)
at the one cell where physics gives a tight bound.

A useful framing: ADR-066's 1.0 constant was a _prior_ applied when no
data was available. The lower-freq value is _data_, and data should
displace prior whenever it is available, regardless of upstream gating
verdicts that govern other domains.

## Alternatives considered

1. **Path 1 (issue #1279 §"Possible fix paths" option 1): Gate ADR-066's
   "both None" case on `freq{lo}{D}[0] >= 0.95`.** Rejected. The viltrox-75
   case has `freq{lo}{D}[0] = 0.99` (passes the gate), so this change
   does not affect the bug. Adding a precondition without changing the
   anchor value would only affect lenses where lo extracts well below
   0.95 at center — a different class of failure (lo also lost), where
   anchoring to lo would be wrong but anchoring to 1.0 is also wrong.
   For that class, the right answer is to leave the cell None; this ADR
   does not address it.

2. **Path 3 (issue #1279 §"Possible fix paths" option 3): Accept the
   overshoot.** Rejected. Leaving `freq30 = 1.0 > freq10 = 0.99` is a
   physical-invariant violation in committed log data. The 0.07/0.08
   deltas are visible in the Tier 1 anchor log and will show up in any
   future calibration aggregate.

3. **Path 4: Bypass ADR-066's "both None" when ADR-069's pair gate
   vetoed for that pair.** Rejected. The pair-gate veto is not exposed
   to `_apply_center_symmetry` (it lives inside
   `_apply_coincident_top_anchor`), so this would require a new
   communication channel between the two passes. It also produces a
   worse outcome: the freq30 cells stay None and the SVG re-introduces
   the visible y-axis gap that #1267 fixed.

4. **Path 5: Cap ADR-066's anchor by lo: `out[s_field][0] = min(1.0,
lo_value)`.** Effectively equivalent to this ADR but loses the
   fallback chain for the `lo is None` case. Less explicit; chose the
   path-2 phrasing for readability.

5. **Cross-direction fallback (`lo_s` -> `lo_m` -> 1.0).** Included in
   the per-cell decision above as the second tier of the fallback chain.
   The cross-direction copy is the same fallback ADR-066 already does
   in cases 1 and 2 of `_apply_center_symmetry` (copy S to M or M to S
   when one side is None). Same physics: S=M at the optical axis by B4.

6. **Pre-anchor freq10 before iterating freq30.** Considered to remove
   any ordering subtlety. Rejected: the existing in-place mutation of
   `out` already gives this for free; an explicit ordering pass adds
   code without changing behaviour.

## Consequences

### Positive

- Restores the physical invariant `freq{hi}{D}[0] <= freq{lo}{D}[0]`
  on every lens where the anchor fires AND `freq{lo}{D}` has a value
  at center.
- viltrox-75 Tier 1 anchor log: freq30S Δ at frac=0.0 drops from
  0.070 → ~0.060; freq30M Δ from 0.080 → ~0.070. Still above the
  ±0.05 band, but moving toward true value rather than away from it.
- samyang-300mm reflex: unchanged (ADR-069 fires before reaching
  here).
- samyang-af-12mm stopped: unchanged (freq10 cells anchor to 1.0
  first, freq30 cells then inherit 1.0).

### Negative / accepted tradeoff

- On lenses where the chart artist actually drew `freq30` at MTF=1.0
  at center but `freq10` extracts at 0.99 (e.g. samyang-10mm stopped),
  the anchor shifts from 1.0 → 0.99, regressing those cells by 0.01
  against GT. Accepted: 0.01 inside the ±0.05 band is well below the
  noise floor of the calibration metric, and the physical-invariant
  win on lenses like viltrox-75 outweighs a 0.01 regression on lenses
  where the prior happened to be exactly correct.
- viltrox-75 remains over the ±0.05 band on freq30S/M at frac=0.0.
  This is **data-limited, not algorithm-limited**: the extractor reads
  freq10 at 0.99 (GT 1.00) and the chart's true freq30 is 0.93 (GT).
  No anchor mechanism short of actually reading the freq30 skeleton
  in the buried-leftmost-columns region can produce a value below
  0.99 here. Recovering the freq30 skeleton from under the freq10
  red ink is a separate problem (would require dispatch / HSV
  retuning that risks regressing the 8 lenses ADR-066 was designed
  to fix). Accepted.

### Scope this ADR does NOT cover

- Cases where the same-direction lower-freq cell at center is itself
  None AND the cross-direction cell is also None. Falls through to
  the 1.0 anchor; same behaviour as before this ADR.
- Cases where the pair gate's veto signals the right answer would
  be "leave cell None" rather than "anchor to a value". The trade-off
  there is the y-axis visible gap (#1267) vs. an inaccurate filled
  value. This ADR keeps the filled value; the gap-prevention principle
  of ADR-066 is preserved.
- Recovery of buried freq30 skeleton ink on fast primes with sub-1.0
  chart-top curves. Out of scope; a separate spike against the
  dispatch / HSV layer would be needed and would risk regressing the
  ADR-066-recovered lenses.
- Charts with three or more frequencies (e.g. Zeiss 10/20/40 press
  kit). The "closest lower frequency" rule generalises naturally:
  freq40 anchors to freq20 if available, else freq10. No special
  case needed.
