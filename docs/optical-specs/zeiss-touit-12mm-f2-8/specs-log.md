# Carl Zeiss Touit 12mm f/2.8 — Specs Log

## Data provenance

| Date       | Source                       | URL                                                                                                                 | Result                                                                                                        |
| ---------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| 2026-05-21 | Zeiss official datasheet PDF | https://www.zeiss.com/content/dam/pno/downloads/photo-lenses/datasheets/touit-lenses/datasheet-zeiss-touit-2812.pdf | Found: full technical table, construction drawing, MTF charts (k=2.8 + k=5.6), distortion + vignetting curves |
| 2026-05-21 | Zeiss product page           | (discontinued)                                                                                                      | 404 — Touit line removed from zeiss.com; datasheet PDF is the canonical official source (see `tools/zeiss/`)  |
| 2026-05-21 | LensTip lab review           | https://www.lenstip.com/382.1-Lens_review-Carl_Zeiss_Touit_12_mm_f_2.8-Introduction.html                            | Found: lab review cross-check for OQ scoring (see `lenses.ts` fields)                                         |

## Optical construction

- `opticalElements`/`opticalGroups`: 11/8 (datasheet "Lens elements / Groups")
- `specialElements`: 2 aspherical, 3 anomalous partial dispersion (Zeiss
  Touit line materials; Distagon design)
- `coating`: T\* (Zeiss brand-standard anti-reflective coating)
- `maxMagnification`: 0.11 (datasheet "Image ratio at MOD" 1:9)

## MTF digitization (#791, ADR-075)

- Chart source: datasheet page 2 — stacked panels k=2.8 (max) + k=5.6
  (stopped), 3 frequencies (10/20/40 lp/mm), white light, B&W
  solid=sagittal dashed=tangential. Exported as
  `zeiss-touit-12mm-f2-8-mtf.png`.
- Tier 1 anchor: 132-cell maintainer eye-read GT (#1332, via #1348);
  calibration provenance in
  `tools/mtfdigitizer/referenceset/calibration.md`.
- Emit GT gate (ADR-079): 6 of 132 cells are withheld from
  `src/data/mtf-readings.ts` (|EX − GT| > 0.05) — edge-region crossing
  cells at 12.6–14 mm (max 10S/20S, stopped 20M/40M corners; also
  documented in REFERENCE_SET.md §11). The left-edge anchored band
  assignment (ADR-080, calibration Run 9) recovered three max-panel
  crossing-region cells at 9.8–11.2 mm. Per-cell provenance:
  `tools/mtfdigitizer/referenceset/readings/zeiss-touit-12mm-f2-8.md`.
  The digitization log and SVG/overlay in this folder show the
  extractor's actual output including gated cells.

## Caveats

- Distortion and vignetting curves on datasheet page 3 are measured on
  a Sony NEX-7 (E-mount body), per the datasheet's own footnote — not
  on an X-mount body.
- MTF charts specify "white light" with no measured/computed statement;
  Zeiss's published methodology (measured on production samples) is the
  basis for `mtfType: "measured"` in `mtf-readings.ts`.
- The lens is discontinued (2013–2019); prices in `lenses.ts` reflect
  used-market estimates.
