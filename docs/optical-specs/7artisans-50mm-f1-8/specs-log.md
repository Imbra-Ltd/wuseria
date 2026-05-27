# 7Artisans 50mm f/1.8 — Specs Log

## Sources checked

| Source              | URL                                | Date       | Result                                                                                                 |
| ------------------- | ---------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------ |
| Official (Shopify)  | 7artisans.store/products/50mm-f1-8 | 2026-05-27 | Found: 6 elements / 5 groups; no coating named                                                         |
| LensTip             | lenstip.com/1732                   | 2026-05-27 | Confirmed: 6 elements / 5 groups, mag 0.13x, MFD 0.5m, 12 blades; no special elements or coating named |
| Radojuva            | radojuva.com                       | 2026-05-27 | Not found                                                                                              |
| DPReview            | dpreview.com                       | 2026-05-27 | Not listed                                                                                             |
| Google Image Search | google.com                         | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                 |

## Findings

- **opticalElements:** 6 (official, confirmed by LensTip id 1732 and the construction diagram)
- **opticalGroups:** 5 (official, confirmed by LensTip id 1732)
- **specialElements:** none (official full page describes plain "6 elements in 5 groups for exceptional sharpness and minimal distortion" with no ED/aspherical/special glass; LensTip names none; the saved construction diagram is plain line-art with NO glass-type colour legend — three indicators of no special glass)
- **coating:** none stated (no coating named on official full page, official body_html, or LensTip. Unlike the 25mm f/1.8 — where B&H + Photosynthesis both stated multi-layer — no reachable retailer names a coating for the 50mm f/1.8, so NOT recorded by analogy. Left undefined.)
- **maxMagnification:** 0.13 (LensTip id 1732, "0.13x"; matches DB; official gives MFD 0.5m only) — matches DB value
- **constructionDiagram:** found — `construction-diagram.jpg` (official; 6 elements / 5 groups)
- **MTF chart:** found — `mtf-chart.jpg` (official; S10/T10/S30/T30)

## Caveats

- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
