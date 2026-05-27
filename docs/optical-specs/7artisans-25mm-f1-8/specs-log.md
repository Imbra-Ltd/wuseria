# 7Artisans 25mm f/1.8 — Specs Log

## Sources checked

| Source              | URL                                | Date       | Result                                                                                                          |
| ------------------- | ---------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)  | 7artisans.store/products/25mm-f1-8 | 2026-05-27 | Found: 7 elements / 5 groups; no ED/coating named                                                               |
| LensTip             | lenstip.com/1725                   | 2026-05-27 | Confirmed: 7 elements / 5 groups, mag 0.2x, MFD 0.18m, declicked aperture; no special elements or coating named |
| Radojuva            | radojuva.com                       | 2026-05-27 | Not found                                                                                                       |
| DPReview            | dpreview.com                       | 2026-05-27 | Not listed                                                                                                      |
| Google Image Search | google.com                         | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                          |

## Findings

- **opticalElements:** 7 (official, confirmed by LensTip id 1725 and the construction diagram)
- **opticalGroups:** 5 (official, confirmed by LensTip id 1725)
- **specialElements:** none stated (neither official nor LensTip names ED/aspherical; line-art diagram has no glass-type legend)
- **coating:** none stated (no coating named on official page or LensTip)
- **maxMagnification:** 0.2 (LensTip id 1725, "0.2x"; matches DB; not on official page) — matches DB value
- **constructionDiagram:** found — `construction-diagram.jpg` (official; 7 elements / 5 groups)
- **MTF chart:** found — `mtf-chart.jpg` (official; S10/T10/S30/T30 at f/1.8 and f/8)

## Caveats

- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
