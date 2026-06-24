# ADR-071: samyang-85mm shape "snake" misdiagnosis — no gate needed

**Status:** Accepted
**Date:** 2026-06-24

## Supersedes

**ADR-070 (Side-channel shape probe for grid-aligned shape errors).**
ADR-070 proposed a new gate to detect a shape error believed to be
invisible to the ±0.05 calibration band on samyang-85mm. Verification
against actual extractor output shows the error does not exist as
described — the gate has nothing to detect.

## Context

Spike #1282 described a "snake" on samyang-85mm-f1-4-as-if-umc max
panel: extracted freq10M tracking freq10S until the corner, extracted
freq30M mimicking freq30S's dip-and-recover. The diagnosis named the
mechanism (halo subtraction erasing legitimate M pixels, sister
fallback copying S values into empty M cells) and asserted all 22
paired cells passed the ±0.05 gate cell-by-cell while the _shape_ was
wrong.

ADR-070 accepted the diagnosis and proposed a side-channel shape
probe that samples GT-vs-extracted S/M separation at per-profile
"separation-maximum" fracs. Issue #1286 was opened to implement it.

During #1286, before writing any code, the implementer measured the
GT against the actual extractor output via
`py -m mtfdigitizer.calibrate --write-readings`. The dump for
`samyang-85mm-f1-4-as-if-umc` and re-inspection of both overlay PNGs
showed the snake does not exist.

### What the data actually says

**Max panel ground truth** (`tools/mtfdigitizer/referenceset/charts.py`
`_SAMYANG_85_GT`):

| frac | 10S GT | 10M GT | abs(S-M) GT | 30S GT | 30M GT | abs(S-M) GT |
| ---- | ------ | ------ | ----------- | ------ | ------ | ----------- |
| 0.0  | 0.91   | 0.91   | 0.00        | 0.70   | 0.70   | 0.00        |
| 0.1  | 0.92   | 0.92   | 0.00        | 0.68   | 0.67   | 0.01        |
| 0.2  | 0.93   | 0.93   | 0.00        | 0.66   | 0.66   | 0.00        |
| 0.3  | 0.94   | 0.93   | 0.01        | 0.63   | 0.64   | 0.01        |
| 0.4  | 0.94   | 0.94   | 0.00        | 0.62   | 0.62   | 0.00        |
| 0.5  | 0.94   | 0.94   | 0.00        | 0.60   | 0.61   | 0.01        |
| 0.6  | 0.94   | 0.94   | 0.00        | 0.58   | 0.60   | 0.02        |
| 0.7  | 0.93   | 0.94   | 0.01        | 0.57   | 0.59   | 0.02        |
| 0.8  | 0.91   | 0.94   | 0.03        | 0.57   | 0.58   | 0.01        |
| 0.9  | 0.86   | 0.93   | 0.07        | 0.54   | 0.57   | 0.03        |
| 1.0  | 0.78   | 0.93   | 0.15        | 0.52   | 0.57   | 0.05        |

**The published chart has S and M near-coincident across most of the
field on the max panel.** Maximum GT abs(S-M) on freq10 is 0.15 at
the corner; on freq30 it is 0.05 at the corner. Mid-field the curves
genuinely overlap.

**Max panel extractor output** at the same fracs (from the readings
dump):

| frac | 10S EX | 10M EX | abs Δ S | abs Δ M | 30S EX | 30M EX | abs Δ S | abs Δ M |
| ---- | ------ | ------ | ------- | ------- | ------ | ------ | ------- | ------- |
| 0.0  | 0.90   | 0.90   | 0.009   | 0.009   | 0.69   | 0.69   | 0.009   | 0.009   |
| 0.1  | 0.90   | 0.90   | 0.015   | 0.015   | 0.70   | 0.68   | 0.016   | 0.008   |
| 0.2  | 0.91   | 0.91   | 0.022   | 0.022   | 0.70   | 0.67   | 0.037   | 0.008   |
| 0.3  | 0.91   | 0.91   | 0.028   | 0.018   | 0.68   | 0.66   | 0.050   | 0.017   |
| 0.4  | 0.91   | 0.91   | 0.026   | 0.026   | 0.65   | 0.65   | 0.025   | 0.025   |
| 0.5  | 0.91   | 0.91   | 0.026   | 0.026   | 0.60   | 0.63   | 0.003   | 0.024   |
| 0.6  | 0.91   | 0.93   | 0.026   | 0.007   | 0.57   | 0.62   | 0.011   | 0.020   |
| 0.7  | 0.91   | 0.94   | 0.016   | 0.004   | 0.56   | 0.60   | 0.009   | 0.015   |
| 0.8  | 0.90   | 0.94   | 0.006   | 0.003   | 0.57   | 0.59   | 0.005   | 0.012   |
| 0.9  | 0.86   | 0.93   | 0.002   | 0.003   | 0.56   | 0.58   | 0.024   | 0.010   |
| 1.0  | 0.78   | 0.93   | 0.004   | 0.004   | 0.50   | 0.57   | 0.016   | 0.002   |

Every paired Δ is below 0.055. Extracted freq30M descends smoothly
0.69 → 0.68 → 0.67 → 0.66 → 0.65 → 0.63 → 0.62 → 0.60 → 0.59 → 0.58
→ 0.57 — matching GT's smooth descent 0.70 → 0.57. **No
dip-and-recover.** Extracted freq10M tracks extracted freq10S from
frac 0.0–0.5 because **GT records S=M at those fracs**, not because
sister-fill fired.

### What the F8 panel confirms

The stopped (F8) panel is the control case. GT records dramatic
S/M divergence on freq30:

| frac | 30S GT | 30M GT | abs(S-M) GT | 30S EX | 30M EX |
| ---- | ------ | ------ | ----------- | ------ | ------ |
| 0.5  | 0.97   | 0.84   | 0.13        | 0.96   | 0.79   |
| 0.6  | 0.97   | 0.79   | 0.18        | 0.98   | 0.74   |
| 0.7  | 0.96   | 0.75   | 0.21        | 0.96   | 0.73   |
| 0.8  | 0.95   | 0.74   | 0.21        | 0.98   | 0.73   |
| 0.9  | 0.93   | 0.66   | 0.27        | 0.96   | 0.67   |
| 1.0  | 0.92   | 0.55   | 0.37        | 0.96   | 0.54   |

Extracted freq30M dives to 0.54 at corner — matching GT's 0.55, not
freq30S's 0.92. **When the chart genuinely separates S from M, the
extractor reads them separately.** Halo subtraction (ADR-059,
ADR-062) is not erasing legitimate M pixels — if it were, F8 30M
would mimic F8 30S (flat at 0.96), and it does not.

### What the overlay PNG actually shows

The max-panel overlay shows two gold curves (10S solid + 10M dashed)
visually overlapping from frac 0.0 to ~0.6, then diverging — gold
solid drops to 0.78 at corner, gold dashed stays at 0.93. The two
blue curves (30S + 30M) descend together with subtle separation
matching GT's |Δ| ≤ 0.02 across the field.

This is **chart truth**: Samyang drew S and M near-coincident on
this lens at the published apertures because that is what the
optical performance is. The overlay is correct. The earlier reading
("blue dashed clings to dark grey then jumps") confused two visually
overlapping lines for a tracking error.

## Decision

**No new gate. No code change. ADR-070 is superseded.**

Concrete actions in this PR:

1. ADR-070 frontmatter updated to `Status: Superseded by ADR-071`.
2. `tools/mtfdigitizer/profiles/declared.py` SAMYANG_4COLOR_ALL_SOLID
   docstring "KNOWN SHAPE LIMITATION" block (lines 82–96) is removed
   — it describes a snake that does not exist in the extracted data
   and would mislead future readers.
3. Issues #1286 (Path 3 implementation) and #1287 (Path 1
   follow-up) are closed with the readings dump as evidence.
4. Issue #1282 (spike) — already closed by #1285; a follow-up
   comment links to this ADR.

### Post-mortem

- **Symptom:** Spike #1282 reported that samyang-85mm max panel
  shipped a wrong-shape extraction (gold dashed tracking gold
  solid, blue dashed mimicking blue solid's dip) invisible to the
  ±0.05 calibration band.
- **Root cause:** Visual misreading of the overlay PNG. Two
  legitimately near-coincident curves on the published chart were
  interpreted as one curve tracking the other due to extractor
  error. The diagnosed mechanism (halo subtraction erasing
  legitimate M pixels → sister fallback) is real and active on
  this profile family, but does not produce the failure mode the
  spike described on this anchor.
- **Why missed:** The spike was authored on visual inspection
  alone. The actual extractor output (readings dump) was not
  checked against GT at every frac before opening the spike. The
  docstring annotation added to declared.py made the misdiagnosis
  authoritative-looking by being co-located with the working halo
  subtraction code.
- **Fix:** Supersede ADR-070, remove the misleading docstring,
  close the follow-up issues, document the post-mortem in this
  ADR.
- **Prevention:** Future spikes describing shape errors on
  reference-set lenses MUST run
  `py -m mtfdigitizer.calibrate --write-readings` and verify the
  diagnosis against the per-frac dump before the spike is
  accepted as actionable. The dump is cheap (one command, one
  file) and would have refuted this spike at intake. Added to
  PLAYBOOK §2.8 or the analogous mtfdigitizer playbook section
  in a follow-up.

## Alternatives considered

1. **Leave ADR-070 as Accepted, do not implement #1286 and #1287,
   close the issues with a note.** Rejected. An inert "Accepted"
   ADR on top of a misdiagnosis is harder to reason about later
   than an explicitly-superseded record. Future readers
   encountering ADR-070 would assume the gate exists, look for it
   in code, and not find it — a documentation-vs-code drift the
   ADR system is supposed to prevent.

2. **Keep the docstring annotation in declared.py as a known
   limitation note.** Rejected. The annotation describes a
   mechanism that does not produce the failure mode it claims on
   this anchor. Future readers debugging a different shape problem
   on a different lens would chase this hypothesis and waste time.
   The halo-subtraction mechanism is correctly documented in the
   preceding paragraphs (ADR-059, ADR-062 references); the
   "KNOWN SHAPE LIMITATION" block specifically about samyang-85mm
   sister-fill is what gets removed.

3. **Open a new spike to investigate whether the halo-subtraction
   mechanism has any failure mode on Tier 2 Samyang lenses that
   share the profile.** Considered but deferred. The F8-panel
   evidence (correct M dive against flat S on samyang-85mm)
   strongly suggests halo subtraction works as designed on this
   profile family. A speculative spike would be the same intake
   error this ADR exists to prevent. If a Tier 2 lens surfaces a
   real shape problem, open the spike against that lens with the
   readings dump attached.

## Consequences

### Positive

- The ADR record reflects the current architecture: 11-point Δ
  gate is sufficient for the samyang-4color-all-solid profile
  family as published.
- The `declared.py` docstring no longer asserts a non-existent
  limitation.
- The two follow-up issues are closed before any speculative work
  is built on top of them.
- A "spike → no-change" outcome is preserved as a recorded
  decision rather than disappearing into the git history without
  a citation point.

### Negative / accepted tradeoff

- ADR-070 lives in the ADR sequence as a superseded record.
  Acceptable: ADR-010 in the templates project documents
  supersession links as the standard mechanism for exactly this
  case.
- Three issues (#1282, #1286, #1287) close without code changes,
  which can look like wasted work in a milestone summary. The
  preventive-decision value (avoiding a 500-line gate
  implementation against a wrong premise) is the actual outcome
  and the post-mortem above captures the learning.

### Scope this ADR does NOT cover

- Whether halo subtraction has any subtle failure mode on Tier 2
  lenses sharing the profile. Out of scope for this supersession
  — open a new spike against the specific lens if one surfaces.
- Whether the 11-point grid is shape-blind for any _other_ class
  of error. The spike's broader question ("can the grid hide
  shape errors") remains open in principle; this ADR closes only
  the specific instance the spike claimed.
- The PLAYBOOK update to require a readings dump on shape-error
  spikes. Tracked as a follow-up to land in the session wrap-up
  rather than in this PR.
