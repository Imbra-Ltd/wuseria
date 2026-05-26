# Specs Log — AstrHori 85mm f/2.8 Macro Tilt

## Sources checked

| Source              | URL                                                                                                                                            | Date       | Result                                                                                                |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------- |
| AstrHori official   | https://www.astrhori.cn/products/astrhori-85mm-f2-8-macro-tilt-manual-full-frame-lens                                                          | 2026-05-25 | Shopify page, specs in images only                                                                    |
| AstrHori official   | (same URL, product description image)                                                                                                          | 2026-05-26 | Found: construction diagram (1 HR + 2 ED), MTF chart (image height, max aperture), specs table (11/8) |
| DPReview            | https://www.dpreview.com/news/1076504643/astrhori-s-329-85mm-f2-8-tilt-shift-macro-lens-is-available-for-six-mirrorless-camera-systems         | 2026-05-25 | Found: 11/8, 2 ED                                                                                     |
| Thom Hogan          | https://www.zsystemuser.com/z-mount-lenses/third-party-lenses/third-party-manual-focus/astrhori-manual-focus-lense/astrhori-85mm-f28-ts-e.html | 2026-05-25 | Found: 11/8, 2 ED, 1:1 macro                                                                          |
| Endlessly Curious   | https://www.endlesslycurious.net/lenses/astrhori/astrhori-85mm-f2-8-macro-tilt/                                                                | 2026-05-25 | Found: 2 ED + 1 high refractive (quoting AstrHori)                                                    |
| Sony Alpha Blog     | https://sonyalpha.blog/2022/06/23/astrhori-85mm-f2-8-tilt-macro-11/                                                                            | 2026-05-25 | Found: 1:1 macro confirmed                                                                            |
| LensVid             | https://lensvid.com/gear/astrhori-85mm/                                                                                                        | 2026-05-25 | Found: 11/8, 2 ED confirmed                                                                           |
| LensTip             | —                                                                                                                                              | 2026-05-25 | Not found — no review for this lens                                                                   |
| Radojuva            | https://radojuva.com/en/2023/07/anons-astrhori-85mm-f2-8-macro-tilt/                                                                           | 2026-05-25 | Announcement only, no detailed specs                                                                  |
| Google Image Search | "AstrHori 85mm f/2.8 optical construction diagram"                                                                                             | 2026-05-25 | Not found                                                                                             |
| Google Image Search | "AstrHori 85mm f/2.8 MTF chart"                                                                                                                | 2026-05-25 | Not found                                                                                             |

## Optical specs

| Field           | Value                         | Source                                              |
| --------------- | ----------------------------- | --------------------------------------------------- |
| opticalElements | 11                            | Official specs table, DPReview, Thom Hogan, LensVid |
| opticalGroups   | 8                             | Official specs table, DPReview, Thom Hogan, LensVid |
| specialElements | ["2 ED", "1 high-refractive"] | Official diagram legend + Endlessly Curious         |
| coating         | undefined                     | No coating name specified                           |

## Diagrams

- `construction-diagram.png` — cropped from official product image, shows 11/8 layout with high-refractive (blue) and ED x2 (green) elements; includes MTF chart in same image
- `mtf-chart.png` — image height MTF at maximum aperture (f/2.8), 10 and 30 lp/mm, S and M lines, 0–20mm field

## Caveats

- Marketing text says "12 elements in 8 groups" but specs table and all other sources confirm 11/8 — using 11/8
- Best-documented AstrHori lens — multiple independent sources confirm construction
- maxMagnification 1:1 confirmed by multiple sources — already in DB
- MTF at 10 lp/mm: ~0.9 center, ~0.6 edge; at 30 lp/mm: ~0.65 center, ~0.35 edge
