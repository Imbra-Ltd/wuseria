# Specs Log — AstrHori 18mm f/5.6 Shift

## Sources checked

| Source              | URL                                                                            | Date       | Result                                                                                                              |
| ------------------- | ------------------------------------------------------------------------------ | ---------- | ------------------------------------------------------------------------------------------------------------------- |
| AstrHori official   | https://www.astrhori.cn/products/18mm-f5-6-aps-c-shift-lens-for-e-fx-l-z       | 2026-05-25 | Shopify page, specs in images only — not text-extractable                                                           |
| AstrHori official   | (same URL, product description image)                                          | 2026-05-26 | Found: optical construction diagram (high-refractive + low-dispersion glass), MTF chart (polychromatic, 0–30 cy/mm) |
| fdirect.eu          | https://fdirect.eu/b2b/astrhori-mf-18-mm-f-56-aps-c-shift-lens-for-fujifilm-x/ | 2026-05-25 | Found: 7 elements in 5 groups                                                                                       |
| Pergear             | https://www.pergear.com/products/astrhori-18mm-f5-6                            | 2026-05-25 | Found: 7 elements in 5 groups                                                                                       |
| LensTip             | —                                                                              | 2026-05-25 | Not found — no review for this lens                                                                                 |
| Radojuva            | —                                                                              | 2026-05-25 | Not found — no review for this lens                                                                                 |
| Google Image Search | "AstrHori 18mm f/5.6 optical construction diagram"                             | 2026-05-25 | Not found                                                                                                           |
| Google Image Search | "AstrHori 18mm f/5.6 MTF chart"                                                | 2026-05-25 | Not found                                                                                                           |

## Optical specs

| Field           | Value                                     | Source                                                                    |
| --------------- | ----------------------------------------- | ------------------------------------------------------------------------- |
| opticalElements | 7                                         | fdirect.eu, Pergear, Official diagram                                     |
| opticalGroups   | 5                                         | fdirect.eu, Pergear, Official diagram                                     |
| specialElements | ["3 low-dispersion", "1 high-refractive"] | Official diagram: pink = low-dispersion (3), orange = high-refractive (1) |
| coating         | undefined                                 | No coating name specified                                                 |

## Diagrams

- `construction-diagram.png` — cropped from official Shopify product image, shows 7/5 layout with high-refractive (orange) and low-dispersion (pink) elements
- `mtf-chart.png` — polychromatic AWE MTF, 0–30 cy/mm, field positions TS 0.00–14.20 mm

## Caveats

- Official product image embeds specs, construction diagram, and MTF in one tall composite JPG — not machine-readable text
- Diagram confirms special glass but does not label individual element counts — pink elements appear on 2 surfaces, orange on 1 (visual count from diagram)
- MTF shows center performance ~0.95 at 15 cy/mm, edge (TS 14.20) drops to ~0.4 at 30 cy/mm
