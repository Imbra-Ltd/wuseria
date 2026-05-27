# 7Artisans 60mm f/2.8 Macro Mark II — Specs Log

## Sources checked

| Source              | URL                                                                 | Date       | Result                                                                                                               |
| ------------------- | ------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)  | 7artisans.store/products/7artisans-60mm-f2-8-mark-ii-macro-lens-... | 2026-05-27 | Found: 11 elements / 8 groups, 1 ED, 1:1 macro, "Aperture (9 Blades)"; front-element photo engraved "60mm 1:2.8 Φ49" |
| LensTip             | lenstip.com/1834                                                    | 2026-05-27 | Confirmed: 11 elements / 8 groups, mag 1x, MFD 0.175m, 9 blades; release 21.04.2021                                  |
| Radojuva            | radojuva.com                                                        | 2026-05-27 | Not found                                                                                                            |
| DPReview            | dpreview.com                                                        | 2026-05-27 | Not listed                                                                                                           |
| Google Image Search | google.com                                                          | 2026-05-27 | Diagram found embedded in official Amazon composite image; cropped and saved (no MTF)                                |
| B&H Photo           | bhphotovideo.com/c/product/1642656-REG                              | 2026-05-27 | Confirms 11 elements / 8 groups, 9 blades, filter 49mm, manual, X-mount; no coating named                            |

## Findings

- **opticalElements:** 11 (official, confirmed by LensTip id 1834, B&H, and the construction diagram)
- **opticalGroups:** 8 (official, confirmed by LensTip id 1834, B&H)
- **specialElements:** 1 ED (official: "built-in ED (extra-low dispersion lens)"; construction diagram shows 1 red HOYA Ultra-Low Dispersion element at the front)
- **coating:** none stated (no coating named on official page, B&H, or any reachable retailer; Amazon brand-store snippet suggested "multi-layer" but could not be verified on a confirmed Fuji-X page — not recorded)
- **maxMagnification:** 1.0 (official: 1:1 "life-size" / "1x macro telephoto", MFD 0.175m)
- **constructionDiagram:** found — `construction-diagram.jpg` (official, from Amazon listing; cross-section with legend red = HOYA Ultra-Low Dispersion glass, confirms 1 ED)
- **MTF chart:** not found (no MTF published on official store or Amazon)

## Caveats

- IMPORTANT: the DB `officialUrl` pointed at `/products/60mm-f2-8`, which is the
  **original** 60mm f/2.8 (8 elements / 7 groups, no ED stated, up to 2:1–3:1
  with extension) — a different optical design. The Mark II is a distinct
  product at `7artisans-60mm-f2-8-mark-ii-macro-lens-...`. The DB entry is
  named "Macro Mark II", so the Mark II specs (11/8, 1 ED, 1:1) and the Mark II
  URL apply. `officialUrl` corrected in this PR.
- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
- **DB corrections (2026-05-27):** `apertureBlades` 7 → **9** (official "Aperture (9
  Blades)" + B&H + LensTip 1834 — unanimous); `filterThread` 62 → **49** (front-element
  engraving "Φ49" + B&H "49 mm"; the 62 was likely body diameter; LensTip's "39" is an
  outlier); `year` 2018 → **2021** (LensTip release 21.04.2021 — the 2018 value belonged
  to the original 60mm, not the Mark II).
