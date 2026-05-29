# 7Artisans 50mm f/1.8 — Specs Log

## Sources checked

| Source                    | URL                                    | Date       | Result                                                                                                                |
| ------------------------- | -------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)        | 7artisans.store/products/50mm-f1-8     | 2026-05-27 | Found: 6 elements / 5 groups; no coating named                                                                        |
| LensTip                   | lenstip.com/1732                       | 2026-05-27 | Confirmed: 6 elements / 5 groups, mag 0.13x, MFD 0.5m, 12 blades; no special elements or coating named                |
| Radojuva                  | radojuva.com                           | 2026-05-27 | Not found                                                                                                             |
| DPReview                  | dpreview.com                           | 2026-05-27 | Not listed                                                                                                            |
| B&H Photo                 | bhphotovideo.com/c/product/1387957-REG | 2026-05-27 | Confirms 6 elements / 5 groups, 12 rounded blades, MFD 50cm; "Multi-layer coating ... applied to individual elements" |
| Photosynthesis (retailer) | magazin.photosynthesis.bg/en/70180     | 2026-05-27 | Confirms 6/5, 12 rounded blades, 50cm; "multi-layer coating ... reduce unwanted glare"                                |
| Google Image Search       | google.com                             | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                                |

## Findings

- **opticalElements:** 6 (official, confirmed by LensTip id 1732 and the construction diagram)
- **opticalGroups:** 5 (official, confirmed by LensTip id 1732)
- **specialElements:** none (official full page describes plain "6 elements in 5 groups for exceptional sharpness and minimal distortion" with no ED/aspherical/special glass; LensTip names none; the saved construction diagram is plain line-art with NO glass-type colour legend — three indicators of no special glass)
- **coating:** multi-layer (NOT on the official store page or LensTip, but stated by two retailers: B&H — "Multi-layer coating ... applied to individual elements" (the maker's standard wording) — and Photosynthesis. Recorded as `["multi-layer"]` on retailer evidence, same basis as the 25mm f/1.8.)
- **maxMagnification:** 0.13 (LensTip id 1732, "0.13x"; matches DB; official gives MFD 0.5m only) — matches DB value
- **constructionDiagram:** found — `construction-diagram.png` (official; 6 elements / 5 groups)
- **MTF chart:** found — `mtf-chart.png` (official; S10/T10/S30/T30)

## Caveats

- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".

## Physical-field re-check (2026-05-28)

Full field cross-check vs official + LensTip 1732 (initial pass was optical + MFD only):

- **weight:** 200 → **168** (official "168g" + LensTip 167g — DB was ~32g too high)
- **length:** 43 → **39** (LensTip 56×39mm)
- diameter 55, blades 12, mag 0.13x, MFD 500, filter 52 CONFIRMED.
