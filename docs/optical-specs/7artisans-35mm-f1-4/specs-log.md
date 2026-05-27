# 7Artisans 35mm f/1.4 — Specs Log

## Sources checked

| Source              | URL                                               | Date       | Result                                                                                 |
| ------------------- | ------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------- |
| Official (Shopify)  | 7artisans.store/products/7artisans-35mm-f1-4-apsc | 2026-05-27 | Found: 8 elements / 5 groups, HOYA glass                                               |
| LensTip             | lenstip.com/1728                                  | 2026-05-27 | mag 0.11x; lists 10 elements / 9 groups (outlier)                                      |
| Radojuva            | radojuva.com                                      | 2026-05-27 | Not found                                                                              |
| DPReview            | dpreview.com                                      | 2026-05-27 | Not listed                                                                             |
| Google Image Search | google.com                                        | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved |

## Findings

- **opticalElements:** 8 (official, verified directly: "a 8 elements in 5 groups optical design, using Japanese Hoya Lenses")
- **opticalGroups:** 5 (official)
- **specialElements:** none stated (official: standard Japanese Hoya glass; LensTip lists no special elements)
- **coating:** none stated
- **maxMagnification:** 0.11 (LensTip)
- **constructionDiagram:** found — `construction-diagram.jpg` (official line-art; 8 elements / 5 groups)
- **MTF chart:** found — `mtf-chart.jpg` (official; T1-T3 / S1-S3)

## Caveats

- Source conflict on construction: the official store page states **8 elements / 5
  groups** (verified directly on the live page, 2026-05-27, 2019 MF lens). LensTip
  (id 1728) lists **10 elements / 9 groups** — an outlier not corroborated
  elsewhere. Per PLAYBOOK 2.8 source priority (official manufacturer first for
  construction) and direct verification, used 8/5.
- This is the manual-focus 2019 lens (handle `7artisans-35mm-f1-4-apsc`), distinct
  from the new AF 35mm f/1.4 (2025), which is not yet in the DB (tracked in #878).
- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
