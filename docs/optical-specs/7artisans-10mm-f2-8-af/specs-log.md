# 7Artisans 10mm f/2.8 AF — Specs Log

## Sources checked

| Source              | URL                                                                                         | Date       | Result                                                                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)  | 7artisans.store/products/af-10mm-f2-8-aps-c-lens-for-e-fx-z                                 | 2026-05-27 | Found: 11 elements / 10 groups, ED + HR + aspherical glass; no coating named                                                        |
| B&H Photo           | bhphotovideo.com/c/product/1926880-REG                                                      | 2026-05-27 | Confirms 11/10, AF, X-mount; "two aspherical, three extra-low dispersion, and two high refractive index" elements; no coating named |
| LensTip             | lenstip.com/2273                                                                            | 2026-05-27 | Confirmed: 11/10, 7 blades, 2 aspherical + 3 ED + 2 HR, mag 0.04x, MFD 0.3m, filter 62mm; release 29.09.2025                        |
| PetaPixel           | petapixel.com/2025/09/29/7artisans-launches-af-10mm-f-2-8-ultra-wide-lens-for-aps-c-cameras | 2026-05-27 | Launch 2025-09-29 (confirms year 2025, not 2023)                                                                                    |
| Radojuva            | radojuva.com                                                                                | 2026-05-27 | Not found                                                                                                                           |
| DPReview            | dpreview.com                                                                                | 2026-05-27 | Not listed                                                                                                                          |
| Google Image Search | google.com                                                                                  | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                                              |

## Findings

- **opticalElements:** 11 (official spec table: "Optical Structure: 11 elements in 10 groups")
- **opticalGroups:** 10 (official)
- **specialElements:** 2 aspherical, 3 ED, 2 HR (triple-confirmed: B&H "two aspherical,
  three extra-low dispersion, and two high refractive index" + LensTip 2273 same +
  the official construction diagram's colour-coded legend)
- **coating:** none stated (no coating named on the official rendered page, B&H, or LensTip.
  A batch-research snippet claimed "IMC coating, 99.8% transmittance" but this could NOT be
  verified on any reachable source, so it is NOT recorded. Left undefined.)
- **maxMagnification:** 0.04 (LensTip id 2273, "0.04x"; DB was unset — filled this PR)
- **constructionDiagram:** found — `construction-diagram.jpg` (official, saved this PR)
- **MTF chart:** found — `mtf-chart.jpg` (official; OTF vs Y-field 0–14.2mm, T1-T3 / S1-S3. NOTE: the official page swaps the labels — the file captioned "AF/MF Switch Button" is the real MTF, the one captioned "MTF" is the construction diagram.)

## Caveats

- The official construction diagram color-codes the three glass types (yellow = ED,
  blue = HR, red = aspherical) but does NOT print numeric per-type counts. B&H supplies
  the counts (2 aspherical / 3 ED / 2 HR), now recorded.
- This is the only AF lens in the 7Artisans X-mount lineup. Motor type: **STM** (official
  page: "Equipped with an STM motor") — the DB previously had `afMotor: "LM"`, corrected.
- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
- **DB corrections (2026-05-27):** `afMotor` LM → **STM** (official "STM motor");
  `filterThread` 52 → **62** (official "ф62mm" + LensTip + the saved diagram's spec panel);
  `minFocusDistance` 150 → **300** (official "0.3m" + LensTip + B&H "11.8 in"); `year`
  2023 → **2025** (PetaPixel + LensTip launch 2025-09-29); `maxMagnification` filled **0.04**
  (LensTip 2273).
