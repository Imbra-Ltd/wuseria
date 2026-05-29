# 7Artisans 35mm f/0.95 — Specs Log

## Sources checked

| Source                   | URL                                | Date       | Result                                                                                                               |
| ------------------------ | ---------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)       | 7artisans.store/products/35mm-0-95 | 2026-05-27 | "12 aperture blades", weight "369g", MFD "0.37m"; no element count in text                                           |
| LensTip                  | lenstip.com/1758                   | 2026-05-27 | Full spec: 11 elem / 8 groups, 2 ED, mag 0.12x, 12 blades, MFD 0.37m, filter 52mm, 63×62mm, 369g; release 15.10.2020 |
| Radojuva                 | radojuva.com                       | 2026-05-27 | Not found                                                                                                            |
| DPReview                 | dpreview.com                       | 2026-05-27 | Not listed                                                                                                           |
| Google Image Search      | google.com                         | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                               |
| Amazon (7Artisans store) | amazon.com/dp/B08YJFJ6NK           | 2026-05-27 | Confirms 11 elements / 8 groups, "2 ED lens ... suppress chromatic aberration"; no coating named                     |

## Findings

- **opticalElements:** 11 (LensTip; official page omits element count in text)
- **opticalGroups:** 8 (LensTip)
- **specialElements:** 2 ED (LensTip: "2 ED glass elements")
- **coating:** none stated (no coating named on official page, Amazon full listing, or B&H — left undefined)
- **maxMagnification:** 0.12 (LensTip)
- **apertureBlades:** 12 (official "12 aperture blades" + LensTip)
- **minFocusDistance:** 0.37m / 370 (official + LensTip)
- **filterThread:** 52mm (LensTip)
- **weight:** 369g (official "369g" + LensTip)
- **dimensions:** 63 × 62mm (LensTip)
- **constructionDiagram:** found — `construction-diagram.png` (official; red/blue glass legend, 11 elements / 8 groups; 2 ED shown red)
- **MTF chart:** found — `mtf-chart.png` (official; S1-S3 / T1-T3)

## Caveats

- Construction (11/8, 2 ED) and magnification come from LensTip (id 1758, released
  15.10.2020); the official store page does not print an element count in text.
- **DB corrections (2026-05-28), full field cross-check vs official + LensTip 1758:**
  `apertureBlades` 11 → **12** (official "12 aperture blades"); `weight` 550 → **369**
  (official "369g" + LensTip — the 550 was ~181g too high); `minFocusDistance` 350 → **370**
  (official + LensTip "0.37m"); `filterThread` 50 → **52** (LensTip); `length` 67 → **62**
  (LensTip). Elements/groups/ED/mag/diameter were already correct.
- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
