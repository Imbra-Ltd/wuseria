# 7Artisans 25mm f/0.95 — Specs Log

## Sources checked

| Source              | URL                                    | Date       | Result                                                                                                              |
| ------------------- | -------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)  | 7artisans.store/products/25mm-f0-95    | 2026-05-27 | Found: 11 elements / 9 groups, 3 HOYA ED                                                                            |
| LensTip             | lenstip.com/1880                       | 2026-05-27 | Confirmed: 11/9, 3 Hoya low-dispersion, mag 0.13x                                                                   |
| Radojuva            | radojuva.com                           | 2026-05-27 | Not found                                                                                                           |
| DPReview            | dpreview.com                           | 2026-05-27 | Not listed                                                                                                          |
| Google Image Search | google.com                             | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                              |
| B&H Photo           | bhphotovideo.com/c/product/1664833-REG | 2026-05-27 | Confirms 11 elements / 9 groups, 3 ED ("three ultra-low dispersion elements"), 13 blades, X-mount; no coating named |

## Findings

- **opticalElements:** 11 (official, LensTip)
- **opticalGroups:** 9 (official, LensTip)
- **specialElements:** 3 ED (official: "three HOYA ultra-low dispersion lenses"; LensTip: "3 Hoya low dispersion glass lenses")
- **coating:** none stated (no coating named on official page or B&H; unverified Amazon snippet only — not recorded)
- **maxMagnification:** 0.13 (LensTip)
- **constructionDiagram:** found — `construction-diagram.jpg` (official; legend "ED Glass" red, shows 3 ED elements — confirms 3 ED)
- **MTF chart:** found — `mtf-chart.jpg` (official; S1/T1, 10/20/30 lp/mm)

## Caveats

- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
