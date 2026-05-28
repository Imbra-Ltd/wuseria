# 7Artisans 35mm f/1.4 — Specs Log

## Sources checked

| Source              | URL                                               | Date       | Result                                                                                                                                                                                 |
| ------------------- | ------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)  | 7artisans.store/products/7artisans-35mm-f1-4-apsc | 2026-05-27 | Found: 8 elements / 5 groups, HOYA glass                                                                                                                                               |
| LensTip             | lenstip.com/1728                                  | 2026-05-27 | UNRELIABLE for this lens: lists 10/9 (vs official 8/5), 11 blades, MFD 0.4m, 298g, 56×50mm — all contradicted by official. Only mag 0.11x agrees. Treat LensTip 1728 as mis-cataloged. |
| Radojuva            | radojuva.com                                      | 2026-05-27 | Not found                                                                                                                                                                              |
| DPReview            | dpreview.com                                      | 2026-05-27 | Not listed                                                                                                                                                                             |
| Google Image Search | google.com                                        | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                                                                                                 |
| B&H Photo           | bhphotovideo.com/c/product/1682771-REG            | 2026-05-27 | Confirms 8 elements / 5 groups, 9 blades, X-mount; no special glass or coating named                                                                                                   |

## Findings

- **opticalElements:** 8 (official, verified directly: "a 8 elements in 5 groups optical design, using Japanese Hoya Lenses")
- **opticalGroups:** 5 (official)
- **specialElements:** none stated (official: standard Japanese Hoya glass; LensTip lists no special elements)
- **coating:** none stated (no coating named on official page or B&H; B&H confirms plain construction, Japanese Hoya glass only — left undefined)
- **maxMagnification:** 0.11 (LensTip — the one LensTip 1728 field that agrees with others)
- **minFocusDistance:** 0.35m / 350 (official "minimum focusing distance is 0.35m" — DB already correct; LensTip's 0.4m is wrong)
- **weight:** 228g (official "Weighing only 228g" — DB's prior 160 corrected; LensTip's 298g also wrong)
- **filterThread:** 46mm (DB + LensTip agree)
- **apertureBlades:** UNRESOLVED — DB 10, B&H 9 (earlier read), LensTip 11 (unreliable). No two reachable sources agree; left at DB's 10 pending a confirmable B&H/official blade count. Do NOT adopt LensTip's 11.
- **constructionDiagram:** found — `construction-diagram.jpg` (official line-art; 8 elements / 5 groups)
- **MTF chart:** found — `mtf-chart.jpg` (official; T1-T3 / S1-S3)

## Caveats

- **LensTip 1728 is mis-cataloged for this lens** — it disagrees with the official page on
  construction (10/9 vs official 8/5), blades (11), MFD (0.4m vs 0.35m), weight (298g vs
  228g), and dimensions (56×50). The official figures are used throughout; LensTip 1728's
  physical specs are NOT trusted (only its 0.11x magnification agrees and is corroborated).
- **DB correction (2026-05-28):** `weight` 160 → **228** (official "Weighing only 228g";
  the 160 was ~68g too low). Construction 8/5, MFD 350, filter 46 confirmed already correct.
- This is the manual-focus 2019 lens (handle `7artisans-35mm-f1-4-apsc`), distinct
  from the new AF 35mm f/1.4 (2025), which is not yet in the DB (tracked in #878).
- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
