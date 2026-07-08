# Carl Zeiss Touit 50mm f/2.8 Macro — Specs Log

## Data provenance

| Date       | Source                       | URL                                                                                                                  | Result                                                                                                        |
| ---------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| 2026-05-21 | Zeiss official datasheet PDF | https://www.zeiss.com/content/dam/pno/downloads/photo-lenses/datasheets/touit-lenses/datasheet-zeiss-touit-2850m.pdf | Found: full technical table, construction drawing, MTF charts (k=2.8 + k=5.6), distortion + vignetting curves |
| 2026-05-21 | Zeiss product page           | (discontinued)                                                                                                       | 404 — Touit line removed from zeiss.com; datasheet PDF is the canonical official source (see `tools/zeiss/`)  |
| 2026-05-21 | LensTip lab review           | https://www.lenstip.com/418.1-Lens_review-Carl_Zeiss_Touit_M_50_mm_f_2.8.html                                        | Found: lab review cross-check for OQ scoring (see `lenses.ts` fields)                                         |

## Optical construction

- `opticalElements`/`opticalGroups`: 14/11 (datasheet "Lens elements / Groups")
- `specialElements`: 2 aspherical, 2 anomalous partial dispersion (Zeiss
  Touit line materials; Makro-Planar design)
- `coating`: T\* (Zeiss brand-standard anti-reflective coating)
- `maxMagnification`: 1 (datasheet "Image ratio at MOD" 1:1 — true macro)

## MTF digitization (#791, ADR-075)

- Chart source: datasheet page 2 — stacked panels k=2.8 (max) + k=5.6
  (stopped), 3 frequencies (10/20/40 lp/mm), white light, B&W
  solid=sagittal dotted=tangential (lighter ink than the 12/32mm
  siblings' dashed rendering). Exported as
  `zeiss-touit-50mm-f2-8-macro-mtf.png`. Larger canvas (1786x2526)
  than the siblings.
- Tier 1 anchor: 132-cell maintainer eye-read GT (#1332, PR #1378);
  calibration provenance in
  `tools/mtfdigitizer/referenceset/calibration.md` Runs 7 and 9.
- Emit GT gate (ADR-079): 2 of 132 cells are withheld from
  `src/data/mtf-readings.ts` (|EX − GT| > 0.05) — max-panel 40-band
  crossing-region cells (40S at 9.8 mm, 40M at 14 mm). The dotted-M
  coincidence cascade and the stopped-panel 40-band collapse (#1385,
  35 cells) are resolved by the left-edge anchored band assignment
  (ADR-080, calibration Run 9); the stopped panel now emits 66/66
  in-band. Per-cell provenance:
  `tools/mtfdigitizer/referenceset/readings/zeiss-touit-50mm-f2-8-macro.md`.

## Caveats

- Distortion and vignetting curves on datasheet page 3 are measured on
  a Sony NEX-7 (E-mount body), per the datasheet's own footnote — not
  on an X-mount body.
- MTF charts specify "white light" with no measured/computed statement;
  Zeiss's published methodology (measured on production samples) is the
  basis for `mtfType: "measured"` in `mtf-readings.ts`.
- The lens is discontinued (2014–2019); prices in `lenses.ts` reflect
  used-market estimates.
