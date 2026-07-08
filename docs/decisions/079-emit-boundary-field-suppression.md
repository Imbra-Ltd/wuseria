# ADR-079: Emit-boundary suppression of GT-refuted cells

**Status:** Accepted
**Date:** 2026-07-07

## Context

The #791 Zeiss Touit production extraction is the first per-lens emit
where Tier 1 eye-read ground truth (396 maintainer-verified cells,
#1332) proves parts of the extraction systematically wrong before they
ship. Two whole-band failure modes (the stopped-panel 40-band collapse
on the 32mm and 50mm, and the 50mm max-panel dotted-M cascade — med
|Δ| up to 0.164, tracked as #1385) sit alongside a scatter of
edge-region and crossing-region cells on otherwise-healthy fields
(12mm max up to Δ 0.18 at 11.2–12.6 mm, 32mm max 40-band Δ ~0.06 at
7–11.2 mm, 50mm stopped 20M corner Δ 0.075). The maintainer's overlay
review flagged all three lenses — a field-level skip-list catches the
collapsed bands but still ships the cell-level misses.

The existing per-pass confidence gate (ADR-052/ADR-053) cannot catch
this failure class: a collapsed track rides a NEIGHBOURING band's real
ink, so render-match sees polyline-on-ink and the priors hold — the
gate is structurally blind to misassignment. (The Touit panels do
verdict LOW today, but for an unrelated family-wide reason — raw
render-match precision 0.41–0.76 on the B&W charts — and a LOW
verdict keeps its samples per ADR-053 and carries no per-cell
information, so relying on it would still ship values that eye-read
proves wrong.) ADR-041 names the stake directly: lens pages render the
digitized data to users, and a confident-wrong chart is a public
regression.

Emitting nothing until #1385 lands is also wrong: 327 of 396 Touit
cells are in-band against maintainer GT, and the maintainer asked for
the production artifacts after S208.

## Decision

For Tier 1 anchors, gate every emitted cell against the maintainer's
ground truth at the emit boundary: a cell whose extracted value misses
GT by more than the calibration in-band tolerance is nulled.

```
                 extract_chart()  (unchanged)
                        |
                        v
   +---------------------------------------------+
   | emit_lens()                                 |
   |   verdict  <- autotriage gate (unchanged,   |
   |               runs on the raw extraction)   |
   |   samples  <- per-cell GT gate:             |
   |               |EX - GT| > 0.05  ->  null    |
   +---------------------------------------------+
                        |
                        v
          src/data/mtf-readings.ts  (site data)
```

1. `_suppress_gt_refuted_cells` in `tools/mtfdigitizer/emit.py` nulls
   any cell with `|EX - GT| > 0.05` (`_GT_CELL_TOLERANCE` — the same
   ±0.05 band the calibration runner scores as in-band; deltas rounded
   to the calibration grids' 3-dp precision). The gate applies to any
   chart with `ground_truth` populated; Tier 2 charts emit ungated as
   before (ADR-041).
2. Cells where GT is None (unreadable `?` cells) ship unverified;
   extractor Nones stay None (B2 contract). GT/extraction rows pair
   positionally on the shared sample fractions and fail loud on a
   length mismatch.
3. Un-suppression is automatic: when a fix (e.g. #1385) brings a cell
   back within tolerance against unchanged GT, the next emit ships it
   — there is no skip-list to remember to remove.
4. The confidence verdict still runs on the raw extraction, so emit
   and the autotriage CLI keep agreeing on every panel (ADR-053
   contract unchanged). The gate is publication policy downstream of
   the verdict, not a new verdict.
5. Provenance artifacts are NOT gated: `digitization-log.md`, the
   provenance SVG, and the overlay PNG keep rendering the extractor's
   actual output — they are the diagnostic record that #1385 measures
   its fix against.
6. Emit reports every nulled cell on stderr, grouped per panel and
   field with positions (no silent caps).
7. A companion `_DEFAULT_APERTURES: dict[slug, tuple[f-number, ...]]`
   maps ADR-065 role labels ("max"/"stopped") to the display f-numbers
   the site schema requires (`/^f\/\d/`), eye-read from each chart's
   printed legend — the Touit charts carry role labels in
   `ReferenceChart.apertures`, unlike TTartisan entries which carry
   f-numbers.

The null shows up on the lens page as the renderer's established
honest-absence behaviour: the polyline breaks and the table shows an
em-dash (B2 contract, ADR-038). On the Touit family the gate nulls 69
of 396 cells (12mm 9, 32mm 23, 50mm 37) while the in-band cells of the
collapsed bands — e.g. the genuinely coincident 40-band centre values
— ship correctly instead of being blanket-withheld.

## Alternatives considered

| Alternative                                                                            | Why rejected                                                                                                                                                                                                                                                  |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Emit the extractor output as-is; rely on the LOW-confidence badge                      | A LOW verdict keeps its samples (ADR-053) and names no cell — the wrong values ship regardless, and no UI renders the badge today. The gate also cannot see the misassignment itself: the collapsed track sits on real ink (the ADR-041 regression class).    |
| Field-level skip-list keyed by (slug, panel, field) with med \|Δ\| > 0.05 criterion    | First iteration of this ADR. Blocks whole bands but still ships ~19 cell-level misses (up to Δ 0.18) on median-in-band fields, and withholds the correct in-band cells of collapsed bands. A hand-maintained list also needs remembering to remove entries.   |
| Patch out-of-band cells to eye-read values (`EYE_READ_OVERRIDES` pattern, #1201/#1202) | That mechanism is scoped to single cells with per-cell test locks; at 69-cell scale it silently converts the site from extractor-sourced to hand-sourced data and every future re-emit becomes a manual merge.                                                |
| Emit max-aperture panels only (ADR-075's Path A wording read conservatively)           | Withholds anchor-grade data: the 12mm stopped panel is 90.9% in-band and the 10/20 bands on both other stopped panels are at med ≤ 0.021. The gate condition ADR-075 named (Tier 1 calibration) has landed; panel-level withholding is the wrong granularity. |
| Wait for #1385 before emitting anything                                                | Leaves the folders without production artifacts indefinitely; 327 of 396 cells are in-band today and the failure class is quantified and tracked.                                                                                                             |
| Suppress inside the pipeline (profile flag or extractor change)                        | The extraction is not wrong to ATTEMPT; the readings are the diagnostic signal #1385 needs. Publication policy belongs at the publication boundary.                                                                                                           |

## Consequences

- Nothing on a lens page can contradict the maintainer's eye-read by
  more than the calibration tolerance; gated cells render as honest
  absence until the extractor recovers them.
- Un-suppression needs no bookkeeping: a #1385 fix that brings cells
  in-band flows to the site on the next emit + re-paste; the
  calibration grids (`referenceset/readings/`) remain the per-cell
  provenance for what is gated and why.
- The gate covers the generic emitter. The brand emit scripts
  (`emit_fuji_tier2`, `emit_ttartisan_tier2`) do not apply it yet —
  their anchors were in-band at emit time; wiring the shared gate into
  them is a follow-up if a GT-refuted cell ever appears there.
- Any future Tier 1 anchor inherits the protection automatically — no
  per-brand ship/hold debate.
- Divergence risk: `digitization-log.md` (extractor output) and
  `mtf-readings.ts` (gated) intentionally disagree on the nulled cells
  until #1385 lands — the log is the diagnostic record, the site is
  the publication. specs-log.md in each Touit folder records the gated
  cell counts so the discrepancy is discoverable from the folder.
