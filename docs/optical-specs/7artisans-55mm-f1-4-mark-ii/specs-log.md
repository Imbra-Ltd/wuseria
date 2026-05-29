# 7Artisans 55mm f/1.4 Mark II — Specs Log

## Sources checked

| Source                      | URL                                                                          | Date       | Result                                                                                                                                                                     |
| --------------------------- | ---------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)          | 7artisans.store/products/7artisans-55mm-f1-4-mark-ii-aps-c-portrait-lens-... | 2026-05-27 | Found: 6 elements / 5 groups, multi-coated                                                                                                                                 |
| LensTip                     | lenstip.com/1842                                                             | 2026-05-27 | Confirmed: 6 elements / 5 groups, mag 0.18x, MFD 0.42m, 9 blades                                                                                                           |
| Radojuva                    | radojuva.com                                                                 | 2026-05-27 | Not found                                                                                                                                                                  |
| DPReview                    | dpreview.com                                                                 | 2026-05-27 | Not listed                                                                                                                                                                 |
| Google Image Search         | google.com                                                                   | 2026-05-27 | Not in the 7artisans.store gallery (all product/lifestyle photos)                                                                                                          |
| Amazon SG (7Artisans store) | amazon.sg/dp/B077ZM3VRV                                                      | 2026-05-27 | Listing image carries the official "Multi-layer Coating" panel with BOTH the construction diagram (6/5) and the MTF chart (S1-S3/T1-T3, 0–14.2). Both recovered and saved. |

## Findings

- **opticalElements:** 6 (official, confirmed by LensTip id 1842)
- **opticalGroups:** 5 (official, confirmed by LensTip id 1842)
- **specialElements:** none (no ED/aspherical on official or LensTip; the recovered construction diagram is plain line-art with no glass-type colour legend)
- **coating:** multi-layer (official: "multi-layer coating has been applied to individual elements... reduces flare and ghosting"; the Amazon SG panel repeats the same wording under a "Multi-layer Coating" header)
- **maxMagnification:** 0.18 (LensTip id 1842, "0.18x"; matches DB; official gives MFD 0.42m only)
- **constructionDiagram:** found — `construction-diagram.png` (official cross-section "7Artisans APS-C 55mm F1.4", 6/5; from the Amazon SG listing's coating panel)
- **MTF chart:** found — `mtf-chart.png` (official; S1-S3 / T1-T3, 0–14.2; same Amazon panel)

## Caveats

- **DB `officialUrl` fixed (2026-05-27):** the previous shortened handle
  (`...-aps-c-portrait-lens`) returned 404; corrected to the full live handle
  (`...-for-sony-e-nikon-z-fuji-fx-canon-eos-m-olympus-m43-mirrorless-cameras`),
  which returns 200.
- Diagram + MTF are NOT on the current 7artisans.store gallery (all product/lifestyle
  photos) and were initially recorded "not found". Recovered from the official 7Artisans
  Amazon SG listing (B077ZM3VRV), whose "Multi-layer Coating" panel embeds both — the
  same pattern as the Fisheye II (Amazon) and the v1 (LeicaRumors press archive).
- Active / not discontinued (official `.js` available:true).
- **`hasCircularAperture: false` verified correct (2026-05-27):** the official page,
  LensTip 1842, and the Amazon SG listing all describe a plain "9-blade diaphragm" with
  NO "rounded"/"circular" wording. Contrast the 35mm f/1.2 Mark II, whose official page
  says "rounded 10-blade" (flagged `true`). The DB sets `hasCircularAperture` only on an
  explicit "rounded" statement, not inferred from blade count — so `false` is intended.

## Physical-field re-check (2026-05-28)

Full field cross-check vs LensTip completed — ALL physical fields (blades, magnification,
MFD, filter, weight, dimensions, year) match LensTip exactly. No corrections needed.
