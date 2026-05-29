# 7Artisans 25mm f/1.8 — Specs Log

## Sources checked

| Source                    | URL                                                      | Date       | Result                                                                                                                                                                       |
| ------------------------- | -------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)        | 7artisans.store/products/25mm-f1-8                       | 2026-05-27 | Found: 7 elements / 5 groups; no ED/coating named                                                                                                                            |
| LensTip                   | lenstip.com/1725                                         | 2026-05-27 | Confirmed: 7 elements / 5 groups, mag 0.2x, MFD 0.18m, declicked aperture; no special elements or coating named                                                              |
| Radojuva                  | radojuva.com                                             | 2026-05-27 | Not found                                                                                                                                                                    |
| DPReview                  | dpreview.com                                             | 2026-05-27 | Not listed                                                                                                                                                                   |
| B&H Photo                 | bhphotovideo.com/c/product/1387943-REG                   | 2026-05-27 | Confirms 7 elements / 5 groups, 12 rounded blades, MFD 18cm; "Multilayer Coating ... applied to individual elements"                                                         |
| Photosynthesis (retailer) | magazin.photosynthesis.bg/en/70003                       | 2026-05-27 | Confirms 7/5, 12 rounded blades; "multi-layer coating ... suppresses unwanted glare"                                                                                         |
| alikgriffin (review)      | alikgriffin.com/7artisans-25mm-f1-8-review-sample-photos | 2026-05-27 | Hands-on review — no spec table; notes well-controlled CA at f/1.8, visible cement at element edges. No coating/element count stated. (Review source for future OQ scoring.) |
| Google Image Search       | google.com                                               | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                                                                                       |

## Findings

- **opticalElements:** 7 (official, confirmed by LensTip id 1725 and the construction diagram)
- **opticalGroups:** 5 (official, confirmed by LensTip id 1725)
- **specialElements:** none stated (neither official nor LensTip names ED/aspherical; line-art diagram has no glass-type legend)
- **coating:** multi-layer (NOT on the official store page or LensTip, but stated by two retailers: B&H — "Multilayer Coating ... applied to individual elements to reduce flare and ghosting" — and Photosynthesis. The wording matches 7Artisans' own coating language on the 35mm f/1.2 II / 55mm f/1.4 pages, indicating maker boilerplate the 25mm store page simply omits. Recorded as `["multi-layer"]` on retailer evidence.)
- **maxMagnification:** 0.2 (LensTip id 1725, "0.2x"; matches DB; not on official page) — matches DB value
- **constructionDiagram:** found — `construction-diagram.png` (official; 7 elements / 5 groups)
- **MTF chart:** found — `mtf-chart.png` (official; S10/T10/S30/T30 at f/1.8 and f/8)

## Physical-field re-check (2026-05-28)

Full field cross-check vs LensTip 1725 + B&H 1387943 (initial pass was optical + MFD only):

- **weight:** 200 → **143** (LensTip 143g + B&H "5.04 oz / 143g" — DB was 57g too high)
- **diameter:** 50 → **51** (LensTip 51mm + B&H ø2.01" — minor)
- year 2017, blades 12, mag 0.2x, MFD 180, length 32, filter 46 all CONFIRMED (DB correct).
- `hasCircularAperture` KEPT false: B&H says "12, Rounded" but the official page does not say
  "rounded"; the DB sets circular only on explicit OFFICIAL "rounded" wording (consistent
  with the 55mm Mark II). Flagged as a possible upgrade if official confirms.

## Caveats

- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
