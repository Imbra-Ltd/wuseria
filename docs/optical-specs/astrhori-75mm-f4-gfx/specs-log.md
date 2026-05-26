# Specs Log — AstrHori 75mm f/4 GFX

## Sources checked

| Source              | URL                                                                                         | Date       | Result                                                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------- |
| AstrHori official   | https://www.astrhori.cn/products/75mm-f4-0-medium-format-manual-portrait-prime-lens         | 2026-05-25 | Found: 11/8, "ED lenses", "two high-refractive glass"                                                                  |
| AstrHori official   | (same URL, product parameters image)                                                        | 2026-05-26 | Found: **8 elements in 6 groups** (contradicts page text 11/8), MTF charts (10, 20, 40 lp/mm), no construction diagram |
| FujiRumors          | https://www.fujirumors.com/leaked-astrhori-75mm-f-4-for-fujifilm-gfx-first-image-and-specs/ | 2026-05-25 | Found: 8/6 (pre-release leak — matches image specs)                                                                    |
| cinegear.nl         | https://cinegear.nl/product/astrhori-75mm-f4-0-medium-format-lens-for-gfx-fujifilm-g/       | 2026-05-25 | Found: both 8/6 (editorial) and 11/8 (manufacturer text)                                                               |
| photospecialist.com | https://www.photospecialist.com/astrhori-75mm-f-4-fuji-gfx                                  | 2026-05-25 | Found: 11/8 confirmed                                                                                                  |
| LensTip             | —                                                                                           | 2026-05-25 | Not found — no review for this lens                                                                                    |
| Radojuva            | —                                                                                           | 2026-05-25 | Not found — no review for this lens                                                                                    |
| Google Image Search | "AstrHori 75mm f/4 GFX optical construction diagram"                                        | 2026-05-25 | Not found                                                                                                              |
| Google Image Search | "AstrHori 75mm f/4 GFX MTF chart"                                                           | 2026-05-25 | Not found                                                                                                              |

## Optical specs

| Field           | Value                 | Source                                                |
| --------------- | --------------------- | ----------------------------------------------------- |
| opticalElements | **disputed: 8 or 11** | Image specs: 8/6; page text: 11/8; see caveat         |
| opticalGroups   | **disputed: 6 or 8**  | Image specs: 8/6; page text: 11/8; see caveat         |
| specialElements | undefined             | ED + high-refractive present but counts not specified |
| coating         | undefined             | No coating name specified                             |

## Diagrams

- `mtf-chart.png` — MTF Graph Image with Meridional/Sagittal at 10, 20, and 40 lp/mm (空间频率), field 0–27.5mm
- No construction diagram — only product photos

## Caveats

- **Element count discrepancy:** The official product page has two contradictory values:
  - Page text (HTML): "11 elements in 8 groups"
  - Product parameters image: "8 elements in 6 groups"
  - FujiRumors pre-release leak (Aug 2022): 8/6
  - cinegear.nl has both values in different sections
  - photospecialist.com: 11/8 (likely copying page text)
- The image-based specs (8/6) match the pre-release leak and may be the original correct value; the text (11/8) may be a copy-paste error from another lens — **cannot resolve without manufacturer confirmation**
- DB currently has 11/8 — flagging for review
- Official text says "ED lenses" (no count) and "two high-refractive glass" — unlike 40mm/55mm which specify "2 ED", the 75mm omits the ED count
- MTF at 10 lp/mm: ~0.95 across field; at 40 lp/mm: ~0.9 center, slight S/M split at edge
