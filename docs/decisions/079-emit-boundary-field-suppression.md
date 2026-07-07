# ADR-079: Emit-boundary suppression of GT-refuted fields

**Status:** Accepted
**Date:** 2026-07-07

## Context

The #791 Zeiss Touit production extraction is the first per-lens emit
where Tier 1 eye-read ground truth (396 maintainer-verified cells,
#1332) proves specific extracted fields systematically wrong before
they ship. Six fields across three panels carry med |Δ| > 0.05
against GT (calibration.md Runs 6-8): the stopped-panel 40-band
collapse on the 32mm and 50mm (med 0.164/0.080 and 0.089/0.090) and
the 50mm max-panel dotted-M cascade (med 0.096/0.065). The
architectural fix is tracked as #1385 (Path B).

The existing per-pass confidence gate (ADR-052/ADR-053) cannot catch
this failure class: a collapsed track rides a NEIGHBOURING band's real
ink, so render-match sees polyline-on-ink and the priors hold — the
gate is structurally blind to misassignment. (The Touit panels do
verdict LOW today, but for an unrelated family-wide reason — raw
render-match precision 0.41–0.76 on the B&W charts — and a LOW
verdict keeps its samples per ADR-053 and carries no per-field
information, so relying on it would still ship curves that eye-read
proves wrong by up to 0.26.) ADR-041 names the stake directly: lens
pages render the digitized data to users, and a confident-wrong chart
is a public regression.

Emitting nothing until #1385 lands is also wrong: 30 of 36 Touit
fields are anchor-grade (med |Δ| ≤ 0.021), and the maintainer asked
for the production artifacts after S208.

## Decision

Ship the per-lens emit with the six GT-refuted fields nulled at the
emit boundary, via a declared skip-list in `tools/mtfdigitizer/emit.py`:

```
                 extract_chart()  (unchanged)
                        |
                        v
   +-------------------------------------------+
   | emit_lens()                               |
   |   verdict  <- autotriage gate (unchanged, |
   |               runs on the raw extraction) |
   |   samples  <- _SUPPRESSED_FIELDS applied: |
   |               (slug, panel role) -> null  |
   +-------------------------------------------+
                        |
                        v
          src/data/mtf-readings.ts  (site data)
```

1. `_SUPPRESSED_FIELDS: dict[(slug, aperture-role), tuple[field, ...]]`
   nulls the declared fields in the emitted samples. The entry cites
   the tracking issue (#1385); removing the entry and re-emitting is
   part of that issue's definition of done.
2. Suppression criterion: field med |Δ| > 0.05 against maintainer
   ground truth — the same ±0.05 tolerance band the calibration runner
   scores with. Edge-cell residuals with an in-band median (e.g. the
   12mm max crossing-region p95 outliers) are NOT suppressed; they are
   documented anchor residuals.
3. The confidence verdict still runs on the raw extraction, so emit
   and the autotriage CLI keep agreeing on every panel (ADR-053
   contract unchanged). Suppression is publication policy downstream
   of the gate, not a new gate.
4. Provenance artifacts are NOT suppressed: `digitization-log.md`, the
   provenance SVG, and the overlay PNG keep rendering the extractor's
   actual output — they are the diagnostic record that #1385 measures
   its fix against.
5. Emit reports every suppressed field on stderr (no silent caps).
6. A companion `_DEFAULT_APERTURES: dict[slug, tuple[f-number, ...]]`
   maps ADR-065 role labels ("max"/"stopped") to the display f-numbers
   the site schema requires (`/^f\/\d/`), eye-read from each chart's
   printed legend — the Touit charts carry role labels in
   `ReferenceChart.apertures`, unlike TTartisan entries which carry
   f-numbers.

The null shows up on the lens page as the renderer's established
honest-absence behaviour: the polyline breaks and the table shows an
em-dash (B2 contract, ADR-038).

## Alternatives considered

| Alternative                                                                                    | Why rejected                                                                                                                                                                                                                                                  |
| ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Emit the extractor output as-is; rely on the LOW-confidence badge                              | A LOW verdict keeps its samples (ADR-053) and names no field — the wrong curves ship regardless, and no UI renders the badge today. The gate also cannot see the misassignment itself: the collapsed track sits on real ink (the ADR-041 regression class).   |
| Patch the ~87 out-of-band cells to eye-read values (`EYE_READ_OVERRIDES` pattern, #1201/#1202) | That mechanism is scoped to single cells with per-cell test locks; at band scale it silently converts the site from extractor-sourced to hand-sourced data and every future re-emit becomes a manual merge.                                                   |
| Emit max-aperture panels only (ADR-075's Path A wording read conservatively)                   | Withholds anchor-grade data: the 12mm stopped panel is 90.9% in-band and the 10/20 bands on both other stopped panels are at med ≤ 0.021. The gate condition ADR-075 named (Tier 1 calibration) has landed; panel-level withholding is the wrong granularity. |
| Wait for #1385 before emitting anything                                                        | Leaves the folders without production artifacts indefinitely; 30 of 36 fields are anchor-grade today and the failure class is quantified, tracked, and suppressed field-by-field.                                                                             |
| Suppress inside the pipeline (profile flag or extractor change)                                | The extraction is not wrong to ATTEMPT; the readings are the diagnostic signal #1385 needs. Publication policy belongs at the publication boundary.                                                                                                           |

## Consequences

- The site ships 30 of 36 Touit fields now; the six suppressed fields
  render as honest absence until #1385 lands.
- Un-suppress trigger is concrete: field med |Δ| ≤ 0.05 in a
  calibration run against unchanged GT → remove the
  `_SUPPRESSED_FIELDS` entry, re-emit, refresh logs and SVGs (#1385
  definition of done).
- The suppression list is the emit-side twin of the calibration
  metrics-to-watch: both cite calibration.md, so a future maintainer
  can re-derive every entry from the recorded runs.
- Any future brand whose Tier 1 GT refutes a field inherits the
  mechanism — add a cited entry instead of debating ship/hold per
  lens.
- Divergence risk: `digitization-log.md` (extractor output) and
  `mtf-readings.ts` (suppressed) intentionally disagree on the six
  fields until #1385 lands — the log is the diagnostic record, the
  site is the publication. specs-log.md in each Touit folder names
  the suppressed fields so the discrepancy is discoverable from the
  folder.
