# 7Artisans 60mm f/2.8 Macro Mark II — Specs Log

## Sources checked

| Source                        | URL                                                                 | Date       | Result                                                                                                               |
| ----------------------------- | ------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)            | 7artisans.store/products/7artisans-60mm-f2-8-mark-ii-macro-lens-... | 2026-05-27 | Found: 11 elements / 8 groups, 1 ED, 1:1 macro, "Aperture (9 Blades)"; front-element photo engraved "60mm 1:2.8 Φ49" |
| LensTip                       | lenstip.com/1834                                                    | 2026-05-27 | Confirmed: 11 elements / 8 groups, mag 1x, MFD 0.175m, 9 blades; release 21.04.2021                                  |
| Radojuva                      | radojuva.com                                                        | 2026-05-27 | Not found                                                                                                            |
| DPReview                      | dpreview.com                                                        | 2026-05-27 | Not listed                                                                                                           |
| Google Image Search           | google.com                                                          | 2026-05-27 | Diagram found embedded in official Amazon composite image; cropped and saved (no MTF)                                |
| B&H Photo                     | bhphotovideo.com/c/product/1642656-REG                              | 2026-05-27 | Confirms 11 elements / 8 groups, 9 blades, filter 49mm, manual, X-mount; no coating named                            |
| 7Artisans UK (official store) | 7artisans.co.uk/products/7artisans-60mm-f-2-8-macro-...             | 2026-05-27 | Mark II: 11/8, 9 blades, filter 49mm, 1:1; "multi-layer coatings reduce flare and ghosting"                          |
| 7Artisans UK (MTF template)   | 7artisans.co.uk/cdn/shop/files/MTF_Template_copy.jpg                | 2026-05-27 | Official lens-structure diagram (1 red ED) + MTF chart (10/20/30 lp/mm, 0–13.2); MTF recovered and saved             |

## Findings

- **opticalElements:** 11 (official, confirmed by LensTip id 1834, B&H, and the construction diagram)
- **opticalGroups:** 8 (official, confirmed by LensTip id 1834, B&H)
- **specialElements:** 1 ED (official: "built-in ED (extra-low dispersion lens)"; construction diagram shows 1 red HOYA Ultra-Low Dispersion element at the front)
- **coating:** multi-layer (the official 7Artisans UK store states "multi-layer coatings reduce flare and ghosting" for the Mark II; the 7artisans.store .com page and B&H are silent. Recorded as `["multi-layer"]` on the official UK store.)
- **maxMagnification:** 1.0 (official: 1:1 "life-size" / "1x macro telephoto", MFD 0.175m)
- **constructionDiagram:** found — `construction-diagram.jpg` (official, from Amazon listing; cross-section with legend red = HOYA Ultra-Low Dispersion glass, confirms 1 ED)
- **MTF chart:** found — `mtf-chart.jpg` (official; 10/20/30 lp/mm, 0–13.2). Sourced from
  the 7Artisans UK store's `MTF_Template_copy.jpg` section image — NOT in the product
  gallery (4 product photos) or the .com store / Amazon / B&H listings, which is why it
  was initially recorded "not found". Recovered on review.

## Caveats

- IMPORTANT: the DB `officialUrl` pointed at `/products/60mm-f2-8`, which is the
  **original** 60mm f/2.8 (8 elements / 7 groups, no ED stated, up to 2:1–3:1
  with extension) — a different optical design. The Mark II is a distinct
  product at `7artisans-60mm-f2-8-mark-ii-macro-lens-...`. The DB entry is
  named "Macro Mark II", so the Mark II specs (11/8, 1 ED, 1:1) and the Mark II
  URL apply. `officialUrl` corrected in this PR.
- **Mk I material located (NOT used here — Mk I is not in the DB):** the original
  60mm f/2.8 Macro (Mk I, 2019) is documented at fujiaddict.com/2019/06/05/...,
  fujirumors.com/7artisans-60mm-f-2-8-macro-available, and a DPReview forum thread
  ("60mm f/2.8 Macro version 1"). These may carry the Mk I's own diagram/MTF. Flagged
  so Mk I assets are not confused with the Mark II's, and as a provenance starting
  point if the Mk I is ever added to the DB. The artifacts saved in THIS folder are
  the Mark II's (11/8, 1 ED), verified against the Mark II diagram and LensTip 1834.
- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
- **DB corrections (2026-05-27):** `apertureBlades` 7 → **9** (official "Aperture (9
  Blades)" + B&H + LensTip 1834 — unanimous); `filterThread` 62 → **49** (front-element
  engraving "Φ49" + B&H "49 mm"; the 62 was likely body diameter; LensTip's "39" is an
  outlier); `year` 2018 → **2021** (LensTip release 21.04.2021 — the 2018 value belonged
  to the original 60mm, not the Mark II).
