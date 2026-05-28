# 7Artisans 50mm f/0.95 — Specs Log

## Sources checked

| Source              | URL                                                              | Date       | Result                                                                                                                                                  |
| ------------------- | ---------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)  | 7artisans.store/products/7artisans-50mm-f0-95-large-aperture-... | 2026-05-27 | Found: 7/5, 2 ED, 13 blades; spec-table image "Min focusing distance 0.5m, Weight 418g"; labeled diagram "Filter size: 62mm, length 58mm"               |
| LensTip             | lenstip.com/1862                                                 | 2026-05-27 | 7/5, 2 Hoya low-dispersion, mag 0.15x, 13 blades, filter 62mm, weight 416g; release 06.08.2021. NOTE: LensTip MFD "0.45m" is WRONG — official says 0.5m |
| Radojuva            | radojuva.com                                                     | 2026-05-27 | Not found                                                                                                                                               |
| DPReview            | dpreview.com                                                     | 2026-05-27 | Not listed                                                                                                                                              |
| Google Image Search | google.com                                                       | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                                                                  |
| B&H Photo           | bhphotovideo.com/c/product/1657656-REG                           | 2026-05-27 | Confirms 7 elements / 5 groups, 13 blades, ultra-low dispersion glass, X-mount; no coating named                                                        |

## Findings

- **opticalElements:** 7 (official, LensTip)
- **opticalGroups:** 5 (official, LensTip)
- **specialElements:** 2 ED (official: "2 pieces of ED glass"; LensTip: "2 Hoya low dispersion glass elements")
- **coating:** none stated (no coating named on official page or B&H — left undefined)
- **maxMagnification:** 0.15 (LensTip)
- **minFocusDistance:** 0.5m / 500 (official spec-table image "Minimum focusing distance 0.5m" — DB already correct; LensTip's 0.45m is an error, NOT adopted)
- **filterThread:** 62mm (official labeled diagram "Filter size: 62mm" + LensTip — DB's prior 52 corrected)
- **weight:** 418g (official spec table "418g"; LensTip 416g agrees — DB's prior 540 corrected, was ~122g too high)
- **length:** 58mm (official diagram "58mm" — DB already correct)
- **diameter:** 62 (DB) — UNVERIFIED: the official labeled diagram gives filter size (62mm)
  and length (58mm) but not body diameter; LensTip shows dimensions blank; B&H throttled.
  62 is plausible (barrel ≈ filter on this lens) but not independently confirmed — left as-is.
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
- **DB corrections (2026-05-28), full field cross-check vs official + LensTip 1862:**
  `filterThread` 52 → **62** (official diagram "Filter size: 62mm"); `weight` 540 → **418**
  (official spec table; LensTip 416 agrees). `minFocusDistance` KEPT at **500** — official
  says 0.5m; LensTip's 0.45m is the outlier (do not adopt). 7/5, 2 ED, 13 blades, 0.15x,
  diameter 62, length 58, year 2021 confirmed correct.
