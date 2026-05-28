# 7Artisans 25mm f/0.95 — Specs Log

## Sources checked

| Source              | URL                                    | Date       | Result                                                                                                              |
| ------------------- | -------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)  | 7artisans.store/products/25mm-f0-95    | 2026-05-27 | Found: 11 elements / 9 groups, 3 HOYA ED                                                                            |
| LensTip             | lenstip.com/1880                       | 2026-05-27 | Confirmed: 11/9, 3 Hoya low-dispersion, mag 0.13x, 13 blades, MFD 0.25m, filter 52mm; release 19.09.2021            |
| Radojuva            | radojuva.com                           | 2026-05-27 | Not found                                                                                                           |
| DPReview            | dpreview.com                           | 2026-05-27 | Not listed                                                                                                          |
| Google Image Search | google.com                             | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                              |
| B&H Photo           | bhphotovideo.com/c/product/1664833-REG | 2026-05-27 | Confirms 11 elements / 9 groups, 3 ED ("three ultra-low dispersion elements"), 13 blades, X-mount; no coating named |

## Findings

- **opticalElements:** 11 (official, LensTip)
- **opticalGroups:** 9 (official, LensTip)
- **specialElements:** 3 ED (official: "three HOYA ultra-low dispersion lenses"; LensTip: "3 Hoya low dispersion glass lenses")
- **coating:** none stated (no coating named on official page or B&H; unverified Amazon snippet only — not recorded)
- **maxMagnification:** 0.13 (LensTip 1880, official)
- **minFocusDistance:** 0.25m / 250 (official "closest focusing distance of 0.25m" + B&H "9.84 in" + LensTip — DB's prior 350 corrected)
- **filterThread:** 52mm (B&H "52 mm" + LensTip — DB's prior 58 corrected)
- **year:** 2021 (announced Sept 2021, LensTip release 19.09.2021 — DB's prior 2020 corrected)
- **constructionDiagram:** found — `construction-diagram.jpg` (official; legend "ED Glass" red, shows 3 ED elements — confirms 3 ED)
- **MTF chart:** found — `mtf-chart.jpg` (official; S1/T1, 10/20/30 lp/mm)

## Caveats

- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
- **DB corrections (2026-05-28):** `minFocusDistance` 350 → **250**, `filterThread` 58 → **52**,
  `year` 2020 → **2021**, `weight` 520 → **582** — all confirmed by official + B&H + LensTip 1880
  (B&H 587g / LensTip 582g agree; dimensions 63 × 99.7mm confirmed by LensTip). (The 7Artisans UK
  store page for "25mm f/0.95" is the **L-mount full-frame** variant — different filter/weight —
  not used for the X-mount APS-C specs.)
