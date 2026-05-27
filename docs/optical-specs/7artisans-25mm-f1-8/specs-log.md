# 7Artisans 25mm f/1.8 — Specs Log

## Sources checked

| Source                    | URL                                    | Date       | Result                                                                                                               |
| ------------------------- | -------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)        | 7artisans.store/products/25mm-f1-8     | 2026-05-27 | Found: 7 elements / 5 groups; no ED/coating named                                                                    |
| LensTip                   | lenstip.com/1725                       | 2026-05-27 | Confirmed: 7 elements / 5 groups, mag 0.2x, MFD 0.18m, declicked aperture; no special elements or coating named      |
| Radojuva                  | radojuva.com                           | 2026-05-27 | Not found                                                                                                            |
| DPReview                  | dpreview.com                           | 2026-05-27 | Not listed                                                                                                           |
| B&H Photo                 | bhphotovideo.com/c/product/1387943-REG | 2026-05-27 | Confirms 7 elements / 5 groups, 12 rounded blades, MFD 18cm; "Multilayer Coating ... applied to individual elements" |
| Photosynthesis (retailer) | magazin.photosynthesis.bg/en/70003     | 2026-05-27 | Confirms 7/5, 12 rounded blades; "multi-layer coating ... suppresses unwanted glare"                                 |
| Google Image Search       | google.com                             | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                               |

## Findings

- **opticalElements:** 7 (official, confirmed by LensTip id 1725 and the construction diagram)
- **opticalGroups:** 5 (official, confirmed by LensTip id 1725)
- **specialElements:** none stated (neither official nor LensTip names ED/aspherical; line-art diagram has no glass-type legend)
- **coating:** multi-layer (NOT on the official store page or LensTip, but stated by two retailers: B&H — "Multilayer Coating ... applied to individual elements to reduce flare and ghosting" — and Photosynthesis. The wording matches 7Artisans' own coating language on the 35mm f/1.2 II / 55mm f/1.4 pages, indicating maker boilerplate the 25mm store page simply omits. Recorded as `["multi-layer"]` on retailer evidence.)
- **maxMagnification:** 0.2 (LensTip id 1725, "0.2x"; matches DB; not on official page) — matches DB value
- **constructionDiagram:** found — `construction-diagram.jpg` (official; 7 elements / 5 groups)
- **MTF chart:** found — `mtf-chart.jpg` (official; S10/T10/S30/T30 at f/1.8 and f/8)

## Caveats

- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
