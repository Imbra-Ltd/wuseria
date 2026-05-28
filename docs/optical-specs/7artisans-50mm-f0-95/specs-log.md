# 7Artisans 50mm f/0.95 — Specs Log

## Sources checked

| Source              | URL                                                              | Date       | Result                                                                                                                                                   |
| ------------------- | ---------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)  | 7artisans.store/products/7artisans-50mm-f0-95-large-aperture-... | 2026-05-27 | Found: 7/5, 2 ED, 13 blades; spec-table image "Min focusing distance 0.5m, Weight 418g"; labeled diagram "Filter size: 62mm, length 58mm"                |
| LensTip             | lenstip.com/1862                                                 | 2026-05-27 | 7/5, 2 Hoya low-dispersion, mag 0.15x, 13 blades, filter 62mm, weight 416g; release 06.08.2021. NOTE: LensTip MFD "0.45m" is WRONG — official says 0.5m  |
| Radojuva            | radojuva.com                                                     | 2026-05-27 | Not found                                                                                                                                                |
| DPReview            | dpreview.com                                                     | 2026-05-27 | Not listed                                                                                                                                               |
| Google Image Search | google.com                                                       | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                                                                   |
| B&H Photo           | bhphotovideo.com/c/product/1657656-REG                           | 2026-05-28 | Full spec (user-supplied; scraper was throttled): 7/5, 13 blades, filter 62mm, MFD **45cm**, weight 420g, **ø67.5 × L60.2mm**, X-mount; no coating named |

## Findings

- **opticalElements:** 7 (official, LensTip)
- **opticalGroups:** 5 (official, LensTip)
- **specialElements:** 2 ED (official: "2 pieces of ED glass"; LensTip: "2 Hoya low dispersion glass elements")
- **coating:** none stated (no coating named on official page or B&H — left undefined)
- **maxMagnification:** 0.15 (LensTip)
- **minFocusDistance:** 0.45m / 450 — CONFLICT within the maker's materials: the official
  spec-table IMAGE says 0.5m, but the official prose ("Optical structure" section), LensTip
  1862, AND B&H all say 0.45m. Resolved to **450** on the 3-independent-sources majority
  (initially recorded 500 on the spec-table image alone, before B&H confirmed 0.45m).
- **filterThread:** 62mm (official labeled diagram "Filter size: 62mm" + LensTip — DB's prior 52 corrected)
- **weight:** 418g (official spec table "418g"; LensTip 416g agrees — DB's prior 540 corrected, was ~122g too high)
- **length:** 60.2mm (B&H "L 60.2mm" — DB corrected from 58; the official diagram's "58mm"
  was a rounded/approximate figure, B&H is more precise)
- **diameter:** 67.5mm (B&H "ø 67.5mm" — DB corrected from 62; the prior 62 was the FILTER
  size mistakenly used as the body diameter, exactly the suspected swap)
- **hasCircularAperture:** false — official says only "13-blade diaphragm" (no "rounded"/
  "circular" wording), so `false` per the convention (set true only on explicit "rounded").
- **isDiscontinued / afMotor:** correctly absent — active (`.js` available:true), manual focus.
- **constructionDiagram:** found — `construction-diagram.jpg` (official product-page section
  image `50mm-F0_6.jpg`; legend **"ED Glass"** red, shows 2 ED; 7 elements / 5 groups).
  Chosen over the PARAMETER-panel version (which labels the same element "HOYA Ultra-Low
  Dispersion Glass") because "ED Glass" matches the DB `specialElements: ["2 ED"]` term and
  the 25mm f/0.95 diagram's legend.
- **MTF chart:** found — `mtf-chart.jpg` (official; from the same `50mm-F0_6.jpg`; T1/S1/T2/S2/T3/S3, 10/20/30 lp/mm)

## Caveats

- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
- **DB corrections (2026-05-28), full field cross-check vs official + LensTip 1862 + B&H:**
  `filterThread` 52 → **62**; `weight` 540 → **418**; `diameter` 62 → **67.5** (B&H; the 62
  was the filter size mis-used as diameter); `length` 58 → **60.2** (B&H, more precise than
  the diagram's rounded 58); `minFocusDistance` 500 → **450** (B&H + LensTip + official prose
  all 0.45m; only the official spec-table image said 0.5m — majority wins). 7/5, 2 ED, 13
  blades, 0.15x, year 2021 confirmed correct.
