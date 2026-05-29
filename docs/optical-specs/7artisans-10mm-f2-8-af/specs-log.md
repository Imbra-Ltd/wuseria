# 7Artisans 10mm f/2.8 AF — Specs Log

## Sources checked

| Source              | URL                                                                                         | Date       | Result                                                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Official (Shopify)  | 7artisans.store/products/af-10mm-f2-8-aps-c-lens-for-e-fx-z                                 | 2026-05-27 | Found: 11 elements / 10 groups, ED + HR + aspherical glass; no coating named                                                         |
| B&H Photo           | bhphotovideo.com/c/product/1926880-REG                                                      | 2026-05-27 | Confirms 11/10, AF, X-mount; "two aspherical, three extra-low dispersion, and two high refractive index" elements; no coating named  |
| LensTip             | lenstip.com/2273                                                                            | 2026-05-27 | Confirmed: 11/10, 7 blades, 2 aspherical + 3 ED + 2 HR, mag 0.04x, MFD 0.3m, filter 62mm; release 29.09.2025                         |
| PetaPixel           | petapixel.com/2025/09/29/7artisans-launches-af-10mm-f-2-8-ultra-wide-lens-for-aps-c-cameras | 2026-05-27 | Launch 2025-09-29 (confirms year 2025, not 2023)                                                                                     |
| PhotoRumors (press) | photorumors.com/wp-content/uploads/2025/09/7Artisans-AF-10mm-f2.8-...-3.jpg                 | 2026-05-27 | Clean official construction diagram with Chinese legend — counted 2 红/aspherical + 3 黄/ED + 2 蓝/HR; saved as the diagram artifact |
| Radojuva            | radojuva.com                                                                                | 2026-05-27 | Not found                                                                                                                            |
| DPReview            | dpreview.com                                                                                | 2026-05-27 | Not listed                                                                                                                           |
| Google Image Search | google.com                                                                                  | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                                               |

## Findings

- **opticalElements:** 11 (official spec table: "Optical Structure: 11 elements in 10 groups")
- **opticalGroups:** 10 (official)
- **specialElements:** 2 aspherical, 3 ED, 2 HR (quadruple-confirmed: B&H "two aspherical,
  three extra-low dispersion, and two high refractive index" + LensTip 2273 + the official
  composite diagram + the cleaner PhotoRumors press diagram whose Chinese legend lets the
  per-type counts be read directly: 2 red 非球面 / 3 yellow ED 低色散 / 2 blue 高折射)
- **coating:** none stated (no coating named on the official rendered page, B&H, or LensTip.
  A batch-research snippet claimed "IMC coating, 99.8% transmittance" but this could NOT be
  verified on any reachable source, so it is NOT recorded. Left undefined.)
- **maxMagnification:** 0.04 (LensTip id 2273, "0.04x"; DB was unset — filled this PR)
- **constructionDiagram:** found — `construction-diagram.png` (clean dedicated cross-section
  from the PhotoRumors press release; legend **translated to English** for site consistency:
  red=Aspherical / yellow=ED (Extra-low Dispersion) / blue=High Refraction. The diagram
  itself is unmodified; only the bottom legend text was redrawn. The verbatim Chinese-legend
  original is preserved as `construction-diagram-original.png`.)
- **MTF chart:** found — `mtf-chart.png` (official; OTF vs Y-field 0–14.2mm, T1-T3 / S1-S3. NOTE: the official page swaps the labels — the file captioned "AF/MF Switch Button" is the real MTF, the one captioned "MTF" is the construction diagram.)

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
  (LensTip 2273); `weight` 280 → **232** (official "weight of just 232g" / spec table "≈232g
  (E)"; the unsourced 280 replaced. Note: 7Artisans publishes only the E-mount weight; the
  X-mount weight is not separately stated — 232g is the best sourced figure).
- B&H dimensions "ø 2.7 × L 2.8 in" (≈68.6 × 71mm) corroborate DB diameter 68.5 / length 70.
