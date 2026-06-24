# ADR-070: Side-channel shape probe for grid-aligned shape errors

**Status:** Superseded by ADR-071
**Date:** 2026-06-24
**Superseded:** 2026-06-24

> Superseded same day. The premise — that samyang-85mm max panel
> exhibits a sister-fill shape collapse invisible to the ±0.05 gate
> — does not survive verification against actual extractor output.
> Truth itself records S and M near-coincident in the affected
> region; the extractor reproduces that correctly. See ADR-071 for
> the post-mortem and the corrected understanding.

## Prerequisites

This ADR sits alongside **ADR-038 §3 (fixed 11-point sampling)** and
**ADR-038 §4 (render-match IoU confidence signal)**. Both are kept;
neither is changed. The new shape probe is an additive gate that
runs on Tier 1 anchors only, supplementing the per-cell Δ table the
calibrator already produces.

It also follows **ADR-059 (cross-hue halo pairs)** and **ADR-062
(extend halo pairs to 30S/30M)**. Those introduced the dilated-mask
subtraction that motivates this ADR's gate — the same mechanism
that keeps 15+ Samyang charts within tolerance also produces the
shape error this gate detects.

## Context

`samyang-85mm-f1-4-as-if-umc` is the Tier 1 anchor for the
`samyang-4color-all-solid` profile. All 22 paired cells (max + stopped,
freq10M + freq30M) read within ±0.05 of ground truth — calibration
passes cleanly. Aggregate metrics keep advancing.

But the rendered overlay shows a **shape** error invisible to the
gate. The extracted freq30M (blue dashed) traces the freq30S
(dark-grey) dip-and-recover near frac 0.5–0.6 instead of the
light-grey curve's smooth descent. The extracted freq10M (gold
dashed) sits on freq10S (saturated red) for the first ~60% of the
field before joining its real pink curve.

```
+------------------------------------------------------------+
|  MTF chart (truth)                |  Extracted (snake)     |
|                                   |                        |
|  10S (red, solid)    ===========  |  10S ============      |
|  10M (pink, solid)   -=----===--  |  10M ==---===---  <-   |
|                       |              tracks red until corner |
|  30S (dark, solid)   ===\___/===  |  30S ===\___/===       |
|  30M (light, solid)  ===---___==  |  30M ===\___/===  <-   |
|                                      mimics 30S dip         |
+------------------------------------------------------------+
```

### Why the 11-point grid is shape-blind here

The halo-subtraction pass (ADR-059, ADR-062) dilates the dominant
S mask and subtracts it from the M mask to remove anti-aliasing
contamination. On samyang-85mm:

1. The light-grey 30M curve sits inside the dilated dark-grey 30S
   mask wherever 30S dives below MTF ~0.7 — legitimate light-grey
   pixels get erased along with the halo.
2. The 30M skeleton goes blank across frac 0.3–0.7.
3. Sister fallback copies the 30S value into the empty 30M cells.
4. The extracted magnitude lands within ±0.05 of GT because at the
   coarse 11-point grid, S and M happen to read numerically close
   in those frac slots (e.g. frac=0.5 GT=0.94 EX=0.91).

The shape is wrong; the magnitudes at the sampled points are not.
A densified grid (Path 2 in #1282) does not fundamentally help —
adding 10 more uniform points still misses the _separation maxima_
between S and M.

### Why render-match (ADR-038 §4) also misses it

`pipeline/rendermatch.py` scores rasterized readings against the
**extractor's own skeleton** — the post-halo-subtraction skeleton.
When subtraction erases M ink, the skeleton mass moves to S's
y-position too, so the rasterized polyline (drawn at sister-fill =
S's y) and the bridged skeleton overlap at S's y. IoU stays high
for the wrong reason. The author flagged this exact failure mode
inline (`_bridge_dashed_skeleton` docstring, "known limitation when
sister fallback fires").

### Cell-state matrix for shape detection

```
                             |Δ_S-M| at the sampled frac
                             ----------------------------
                             small (< 0.1)   large (>= 0.1)
                             ------------    --------------
extractor returned M ink     calibration     calibration sees
                             sees nothing    real shape; Δ catches
                             unusual; OK     it; OK
                             (same shape)    (already gated)

sister-filled (M=S y)        *** SNAKE ***   calibration sees Δ
                             magnitude       blow up; gated
                             passes ±0.05    today
                             but shape wrong
```

The shape probe addresses the top-left quadrant. The other three
states are handled by existing gates.

## Decision

Add a **side-channel shape probe** to the calibration runner. The
probe samples Ground Truth and extracted values at **per-profile
separation-maximum fracs** — fracs chosen _because_ S and M maximally
separate there on the Tier 1 anchor. At those fracs, sister-fill
must produce a Δ much larger than ±0.05; if it does not, no
sister-fill fired and shape is sound.

### Schema

Each `MtfProfile` gains an optional `shape_probe_points` tuple:

```python
@dataclass(frozen=True)
class ShapeProbePoint:
    """One separation-maximum frac for one curve pair.

    At this frac on the Tier 1 anchor chart, the S and M curves
    visibly diverge by `min_separation` MTF or more. Any extracted
    M value within `tolerance` of S there means sister-fill or
    similar shape collapse fired — the gate fails.
    """
    aperture: str          # "max", "stopped", or single-aperture default
    frac: float            # 0.0..1.0
    s_field: str           # "freq10S" or "freq30S"
    m_field: str           # "freq10M" or "freq30M"
    min_separation: float  # GT |S - M| at this frac, ground truth
    tolerance: float       # extracted |S - M| must exceed this
```

`MtfProfile.shape_probe_points: tuple[ShapeProbePoint, ...] = ()`

Empty by default — only profiles with a known shape-blind risk
declare points. Initial population: `samyang-4color-all-solid`
only; other profiles add points as their Tier 1 anchors surface
similar mechanisms.

### Gate logic

In `calibrate.py`, after the per-cell Δ table is built, for each
chart whose profile declares `shape_probe_points`:

```
for point in profile.shape_probe_points:
    s_ex = extracted[point.aperture][point.s_field][point.frac]
    m_ex = extracted[point.aperture][point.m_field][point.frac]
    if s_ex is None or m_ex is None:
        # cannot evaluate, log as shape-probe-skipped
        continue
    if abs(s_ex - m_ex) < point.tolerance:
        # M tracked S where GT says they diverge by >= min_separation
        # -> shape collapse detected
        shape_failures.append((chart, point, abs(s_ex - m_ex)))
```

Output: a new aggregate row `Shape probe: X/Y points passed` plus
a per-failure table when any point fails. CI gate: fail the
calibration run if any shape-probe point fails on a Tier 1 anchor.
Tier 2 charts are logged but not gated (Tier 2's GT is the Tier 1
anchor's profile, so the gate is meaningful only at Tier 1).

### Initial points for samyang-4color-all-solid

Reading the published samyang-85mm chart (max panel):

| Aperture | Frac | s_field | m_field | GT abs(S-M) | tolerance |
| -------- | ---- | ------- | ------- | ----------- | --------- |
| max      | 0.5  | freq30S | freq30M | 0.37        | 0.15      |
| max      | 0.6  | freq30S | freq30M | 0.30        | 0.15      |
| max      | 0.4  | freq10S | freq10M | 0.05        | 0.04      |
| max      | 0.5  | freq10S | freq10M | 0.04        | 0.03      |

Tolerances are deliberately below `min_separation` by a wide
margin — the gate must trip _before_ sister-fill brings extracted
M all the way to S's y. The freq10 pair tolerances are tight
because the natural S-M separation on this chart is also small;
this is acceptable because the snake on 10M is real (gold dashed
visibly tracks red until corner).

The exact frac/tolerance values land with the implementation PR
after re-reading the published chart at those fracs — this ADR
fixes the _schema and gate behaviour_; the data is implementation
detail tracked as a follow-up issue.

### samyang-85mm Tier 1 anchor disposition

**The anchor stays in place. No re-EYE-read. No replacement.**

The 11-point readings are correct in magnitude. They pass the
existing Δ gate legitimately. The snake is a _shape_ error the
current schema does not see — replacing the anchor would lose the
test case that surfaced this entire class of bug.

The shape probe is the gate that now makes the snake visible.
samyang-85mm becomes the first chart to exercise both gates: it
passes the Δ gate (as it has been doing) and is _expected to fail_
the new shape gate until ADR-070's follow-up fix (root-cause halo
subtraction) lands.

### Sequencing

1. **This ADR (Path 3, #1282 spike):** schema + gate, samyang-85mm
   on `samyang-4color-all-solid` declared with the four points
   above. Implementation issue follows.
2. **After Path 3 ships and shape baseline is recorded:** open a
   follow-up issue for Path 1 (tighten halo subtraction with a
   per-pixel V-test instead of dilated-mask subtraction). The
   shape probe is the gate that confirms Path 1 actually fixes
   the snake instead of just relocating it.

## Alternatives considered

1. **Path 1 directly: tighten halo subtraction.** Replace the
   dilated-mask subtract (ADR-059/062) with a per-pixel V-channel
   test that excludes only the actual halo and preserves
   legitimate M ink. Rejected as the _first_ step because it is a
   high-risk change to a mechanism that currently keeps 15+
   Samyang charts within tolerance. Without an objective shape
   gate already in place, there is no way to tell if the tightened
   subtraction fixed the snake or just moved it elsewhere. Path 1
   becomes the natural follow-up after Path 3 establishes the
   shape baseline.

2. **Path 2: densify SAMPLE_FRACTIONS to 21 or 41 points.**
   Considered and rejected. The issue's own analysis: at 21 points
   (frac 0.05, 0.15, ...) the freq30 S/M curves still happen to
   land near each other in most slots — the snake is shape, not
   density. Even if 41 points helped statistically, the cost is
   re-EYE-reading every Tier 1 anchor across every profile family
   (~500 new reads), and the SVG output schema (ADR-038 §3) would
   stay 11-point regardless. The grid-aligned shape blindness is a
   structural property of uniform sampling, not a resolution problem.

3. **Path 4: accept as known limitation, downstream confidence
   flag.** A `shape_uncertain=true` flag emitted on readings from
   profiles where halo subtraction fired, surfaced as a "low
   confidence" badge on the public site for affected Tier 2
   lenses. Rejected: the snake stays in the shipped data. Tier 2
   Samyang lenses scored on `samyang-4color-all-solid` would
   render visibly wrong contours under a "low confidence" caveat,
   contradicting the project's trust hierarchy. The docstring
   limitation noted in `profiles/declared.py` lines 82-96 is
   honest about the bug but does nothing to surface it
   automatically.

4. **Score against the union of S and M masks when sister fallback
   fires** (proposed inline in `_bridge_dashed_skeleton` docstring
   for a different issue). Considered: this would fix render-match
   IoU when sister fallback fires on visibly-divergent curves. But
   it does not address the root snake — the M skeleton is _empty_
   in the affected region, so even union-masked IoU compares
   raster-near-S against skeleton-near-S and reports high
   agreement. It fixes a different known limitation (sister
   fallback on divergent curves), not this one.

5. **Manual visual review of every Tier 1 anchor overlay before
   merge.** Effectively the status quo (this snake was caught by
   eye against the overlay PNG). Rejected as the _only_ gate
   because (a) it does not scale to Tier 2, (b) it depends on the
   maintainer noticing every snake, and (c) the spike was opened
   precisely because reviewing the overlay one more time should
   not be the only thing standing between a shape-blind extraction
   and shipped readings. Manual overlay review continues, but
   alongside an automated gate.

## Consequences

### Positive

- The class of error #1282 surfaced becomes detectable in CI. Any
  Tier 1 anchor with a declared `shape_probe_points` tuple gates
  on both magnitude (existing Δ table) and shape (the probe).
- samyang-85mm becomes a regression test case for the Path 1
  follow-up: when halo subtraction is tightened, the shape probe
  must flip from failing to passing on this anchor.
- Profile authors gain a vocabulary for declaring "S and M
  visibly separate here" without changing the output schema. The
  gate is additive — profiles without `shape_probe_points` keep
  their existing behaviour.
- The fix path is reversible. If the per-profile points prove too
  brittle (e.g. small extraction shifts trip the gate without a
  shape collapse), the points can be re-tuned in declared.py
  without touching the gate code.

### Negative / accepted tradeoff

- One more table to read in calibration output. Mitigation: the
  shape probe summary is silent when 0 points are declared, and a
  single-line PASS row when all declared points pass — only
  failures get a verbose table.
- Tier 1 anchors that exercise halo subtraction will fail the
  shape gate at first declaration. This is intentional — they
  must fail until Path 1 fixes them. Calibration aggregate stays
  green on the Δ table (the existing gate) and the new shape
  table reports honestly. The CI gate must be wired so that the
  combined verdict reports both halves rather than failing
  silently or passing on partial green.
- The probe's points are per-chart-author judgement calls based
  on reading the published chart. Same authorship pattern as
  ground truth itself — same risk class. Documented in the
  profile docstring alongside the existing HSV band measurements.

### Scope this ADR does NOT cover

- The Path 1 follow-up itself (tighten halo subtraction). A
  separate issue and ADR will land that once the shape gate is in
  place and the baseline is captured.
- Tier 2 shape gating. Tier 2 lenses ship readings produced
  against the Tier 1 anchor's profile; their shape is only as
  good as the Tier 1 anchor's. Once Path 1 lands and the Tier 1
  shape probe is green, Tier 2 follows automatically.
- Cross-frequency shape probes (e.g. freq10M vs freq30M shape
  agreement). The same-frequency S-M separation is what halo
  subtraction breaks; cross-frequency shape is a different
  question.
- The center-anchor case (#1279, ADR-066 "both None" overshoot).
  Different code path, different mechanism — the shape probe
  could in principle gate that too, but the points and tolerances
  would be entirely different and belong to that ADR's followup.
