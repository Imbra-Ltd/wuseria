# 7Artisans 50mm f/1.4 Tilt-Shift — Specs Log

## Sources checked

| Source                    | URL                                                             | Date       | Result                                                                                         |
| ------------------------- | --------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------- |
| Official (Shopify)        | 7artisans.store/products/50mm-f1-4-aps-c-tilt-lens-for-e-fx-m43 | 2026-05-27 | Found: 7 elements / 6 groups, MFD 0.5m, filter Φ46mm, 12 blades; no coating named              |
| LensTip                   | lenstip.com/2124                                                | 2026-05-27 | Confirmed: 7 elements / 6 groups, mag 0.13x, MFD 0.5m, 12 blades; tilt+shift; no coating named |
| B&H Photo                 | bhphotovideo.com/c/product/1831909-REG                          | 2026-05-27 | Confirms 7/6, 12 blades, MFD 0.5m, filter 46mm; no coating listed                              |
| Photosynthesis (retailer) | magazin.photosynthesis.bg/en/80002                              | 2026-05-27 | Confirms 7/6, MFD 50cm, filter 46mm; no coating named                                          |
| Amazon (7Artisans store)  | amazon.com/dp/B0D1XY1WHD                                        | 2026-05-27 | Confirms 7/6, filter Φ46mm; "Full metal and multi-coating"; distortion 1.9%                    |
| Radojuva                  | radojuva.com                                                    | 2026-05-27 | Not found                                                                                      |
| DPReview                  | dpreview.com                                                    | 2026-05-27 | Not listed                                                                                     |
| Google Image Search       | google.com                                                      | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved         |

## Findings

- **opticalElements:** 7 (official, confirmed by LensTip id 2124, B&H, Photosynthesis, and the construction diagram)
- **opticalGroups:** 6 (official, confirmed by LensTip id 2124, B&H, Photosynthesis)
- **specialElements:** none (official names only generic "Premium Optical Glass"; line-art "MIRROR STRUCTURE" diagram has no glass-type colour legend)
- **coating:** multi-layer (the official 7Artisans Amazon brand-store listing states "Full metal and multi-coating"; the 7artisans.store page, LensTip, B&H, and Photosynthesis are silent. Recorded as `["multi-layer"]` on the maker's Amazon listing.)
- **maxMagnification:** 0.13 (LensTip id 2124, "0.13x"; matches DB; official gives MFD 0.5m only) — matches DB value
- **constructionDiagram:** found — `construction-diagram.jpg` (official "MIRROR STRUCTURE" line-art; 7 elements / 6 groups, no glass-type color legend)
- **MTF chart:** found — `mtf-chart.jpg` (official; T1/S1/T2/S2, Y field of view in mm)

## Caveats

- A marketing bullet on the page sloppily reads "7 elements in groups"; the
  spec table is authoritative at 7 elements / 6 groups.
- **DB corrections (2026-05-27):** `minFocusDistance` was 400 → corrected to **500**
  (official + B&H + LensTip + Photosynthesis all state 0.5m); `filterThread` was 62 →
  corrected to **46** (official "Φ46mm" + B&H "46 mm" + Photosynthesis "46mm"; the 62
  was likely the body diameter mis-entered).
- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
