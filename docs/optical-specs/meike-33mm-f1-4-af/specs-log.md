# Meike 33mm f/1.4 AF — Specs Log

## Sources checked

| Source                  | URL                                                                          | Date       | Result                                                          |
| ----------------------- | ---------------------------------------------------------------------------- | ---------- | --------------------------------------------------------------- |
| Official (Shopify JSON) | meikeglobal.com/products/3314x.json                                          | 2026-05-26 | Found: construction diagram, MTF chart, spec table in body HTML |
| Official (E-mount)      | meikeglobal.com/en-gb/collections/auto-focus-lenses/products/3314e           | 2026-05-26 | Found: 12 el / 9 gr, filter 55mm                                |
| LensTip                 | lenstip.com/2152                                                             | 2026-05-26 | Specs only (no review): 12/9 confirmed, filter 55mm             |
| B&H Photo               | bhphotovideo.com/c/product/1841840-REG/meike_mk_3314cfstm_x_33mm_f_1_4_af... | 2026-05-26 | Found: 12/9, "multilayered coatings"                            |
| DPReview                | dpreview.com                                                                 | 2026-05-26 | Not listed                                                      |

## Findings

- **opticalElements:** 12 (official spec table image, LensTip, B&H)
- **opticalGroups:** 9 (official spec table image, LensTip, B&H)
- **edElements:** 1 (official construction diagram: "1 ED Element — Suppresses chromatic aberrations")
- **asphericalElements:** none listed
- **hrElements:** 1 HR + 1 UHR (official: "1 High Refractive Index Element", "1 Ultra-High Refractive Index Element")
- **coating:** HD double-sided multi-layer (official construction diagram)
- **filterThread:** 55mm (official spec table image; DB corrected from 52mm)
- **maxMagnification:** 0.1 (already in DB, confirmed by LensTip)
- **constructionDiagram:** found — saved as `construction-diagram.jpg`
- **MTF chart:** found — saved as `mtf-chart.jpg` (f/1.4, 10 + 30 lp/mm, S + M)

## MTF analysis

Official MTF at f/1.4 (wide open):

- **10 lp/mm S:** ~0.93 center, drops to ~0.90 at edge (14mm) — excellent contrast
- **10 lp/mm M:** ~0.97 center, rises to ~0.95 at edge — very uniform
- **30 lp/mm S:** ~0.90 center, drops to ~0.65 at edge — good resolution, moderate corner falloff
- **30 lp/mm M:** ~0.88 center, drops to ~0.70 at edge — slight astigmatism (S/M gap ~5% at edge)

## Caveats

- X-mount page renders body images via Shopify theme JS — plain HTML scrape misses them; JSON API body_html has the image URLs
- "HR" and "UHR" elements not tracked in DB schema (only ED tracked via specialElements)
