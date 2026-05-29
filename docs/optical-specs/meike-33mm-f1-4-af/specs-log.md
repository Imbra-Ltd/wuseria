# Meike 33mm f/1.4 AF — Specs Log

## Sources checked

| Source                  | URL                                                                          | Date       | Result                                                          |
| ----------------------- | ---------------------------------------------------------------------------- | ---------- | --------------------------------------------------------------- |
| Official (Shopify JSON) | meikeglobal.com/products/3314x.json                                          | 2026-05-26 | Found: construction diagram, MTF chart, spec table in body HTML |
| Official (E-mount)      | meikeglobal.com/en-gb/collections/auto-focus-lenses/products/3314e           | 2026-05-26 | Found: 12 el / 9 gr, filter 55mm                                |
| LensTip                 | lenstip.com/2152                                                             | 2026-05-26 | Specs only (no review): 12/9 confirmed, filter 55mm             |
| B&H Photo               | bhphotovideo.com/c/product/1841840-REG/meike_mk_3314cfstm_x_33mm_f_1_4_af... | 2026-05-26 | Found: 12/9, "multilayered coatings"                            |
| Lens Rumors             | lens-rumors.com/meike-af-33mm-f-1-4-aps-c-lens-photos-and-mtf-chart/         | 2026-05-26 | Found: dual MTF chart (f/1.4 + f/8), Weibo leak source          |
| DPReview                | dpreview.com                                                                 | 2026-05-26 | Not listed                                                      |

## Findings

- **opticalElements:** 12 (official spec table image, LensTip, B&H)
- **opticalGroups:** 9 (official spec table image, LensTip, B&H)
- **specialElements:** 1 ED, 1 HR, 1 UHR (official construction diagram: "1 ED Element", "1 High Refractive Index Element", "1 Ultra-High Refractive Index Element")
- **coating:** HD double-sided multi-layer (official construction diagram)
- **filterThread:** 55mm (official spec table image; DB corrected from 52mm)
- **maxMagnification:** 0.1 (already in DB, confirmed by LensTip)
- **constructionDiagram:** found — saved as `construction-diagram.png`
- **MTF chart:** found — saved as `mtf-chart.png` (f/1.4, 10 + 30 lp/mm, S + M)

## MTF analysis

Source: lens-rumors.com (Weibo leak, dual chart f/1.4 + f/8)

**f/1.4 (wide open):**

- **10 lp/mm T:** ~0.97 center, drops to ~0.90 at 13mm — excellent contrast
- **10 lp/mm S:** ~0.97 center, drops to ~0.82 at 13mm — slight S/T gap at edges
- **30 lp/mm T:** ~0.86 center, drops to ~0.55 at 13mm — moderate corner falloff
- **30 lp/mm S:** ~0.82 center, drops to ~0.60 at 13mm — astigmatism visible (T/S ~5%)

**f/8 (stopped down):**

- **10 lp/mm:** ~0.95 flat across entire field — excellent uniformity
- **30 lp/mm:** ~0.82 center, drops to ~0.75 at edge — very good stopped-down resolution

## Caveats

- X-mount page renders body images via Shopify theme JS — plain HTML scrape misses them; JSON API body_html has the image URLs
- HR and UHR elements tracked in specialElements alongside ED
