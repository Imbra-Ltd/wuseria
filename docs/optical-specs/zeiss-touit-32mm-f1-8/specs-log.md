# Carl Zeiss Touit 32mm f/1.8 — Specs Log

## Data provenance

| Date       | Source                       | URL                                                                                                                 | Result                                                                                                       |
| ---------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 2026-05-21 | Zeiss official datasheet PDF | https://www.zeiss.com/content/dam/pno/downloads/photo-lenses/datasheets/touit-lenses/datasheet-zeiss-touit-1832.pdf | Found: full technical table, construction drawing, MTF charts (k=1.8 + k=4), distortion + vignetting curves  |
| 2026-05-21 | Zeiss product page           | (discontinued)                                                                                                      | 404 — Touit line removed from zeiss.com; datasheet PDF is the canonical official source (see `tools/zeiss/`) |
| 2026-05-21 | LensTip lab review           | https://www.lenstip.com/386.1-Lens_review-Carl_Zeiss_Touit_32_mm_f_1.8.html                                         | Found: lab review cross-check for OQ scoring (see `scoring-log` provenance in `lenses.ts` fields)            |

## Optical construction

- `opticalElements`/`opticalGroups`: 8/5 (datasheet "Lens elements / Groups")
- `specialElements`: none stated — the datasheet technical table lists no
  aspherical or special-glass elements for this Planar design
- `coating`: T\* (Zeiss brand-standard anti-reflective coating; the
  datasheet does not restate it, carried from Zeiss Touit line marketing)
- `maxMagnification`: 0.11 (datasheet "Image ratio at MOD" 1:9)

## MTF digitization (#791, ADR-075)

- Chart source: datasheet page 2 — stacked panels k=1.8 (max) + k=4
  (stopped), 3 frequencies (10/20/40 lp/mm), white light, B&W
  solid=sagittal dashed=tangential. Exported as
  `zeiss-touit-32mm-f1-8-mtf.png`.
- Tier 1 anchor: 132-cell maintainer eye-read GT (#1332); calibration
  provenance in `tools/mtfdigitizer/referenceset/calibration.md` Runs
  6 and 8.
- Emit GT gate (ADR-079): 23 of 132 cells are withheld from
  `src/data/mtf-readings.ts` (|EX − GT| > 0.05) — the stopped-panel
  40-band collapse from 2.8 mm outward (#1385, 9 cells per
  orientation) and 5 max-panel 40-band crossing-region cells at
  7–11.2 mm. Per-cell provenance:
  `tools/mtfdigitizer/referenceset/readings/zeiss-touit-32mm-f1-8.md`.
  The digitization log and SVG/overlay in this folder show the
  extractor's actual output including gated cells — the intentional
  discrepancy resolves when #1385 lands.

## Caveats

- Distortion and vignetting curves on datasheet page 3 are measured on
  a Sony NEX-7 (E-mount body), per the datasheet's own footnote — not
  on an X-mount body.
- MTF charts specify "white light" with no measured/computed statement;
  Zeiss's published methodology (measured on production samples) is the
  basis for `mtfType: "measured"` in `mtf-readings.ts`.
- The lens is discontinued (2013–2019); prices in `lenses.ts` reflect
  used-market estimates.
