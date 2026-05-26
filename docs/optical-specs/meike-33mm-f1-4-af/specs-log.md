# Meike 33mm f/1.4 AF — Specs Log

## Sources checked

| Source              | URL                                                                          | Date       | Result                                                 |
| ------------------- | ---------------------------------------------------------------------------- | ---------- | ------------------------------------------------------ |
| Official (Shopify)  | meikeglobal.com/products/3314x                                               | 2026-05-26 | No spec table — firmware changelog only                |
| Official (E-mount)  | meikeglobal.com/en-gb/collections/auto-focus-lenses/products/3314e           | 2026-05-26 | Found: 12 el / 9 gr, filter 55mm                       |
| LensTip             | lenstip.com/2152                                                             | 2026-05-26 | Specs only (no review): 12/9 confirmed, filter 55mm    |
| B&H Photo           | bhphotovideo.com/c/product/1841840-REG/meike_mk_3314cfstm_x_33mm_f_1_4_af... | 2026-05-26 | Found: 12/9, "multilayered coatings"                   |
| niaarch.com (B&H)   | niaarch.com/products/F-1-4-AF-Lens-FUJIFILM-X-MK-3314CFSTM-X-BH-Photo/...    | 2026-05-26 | Found: "1 ED lens, 1 high refraction lens, 1 UHR lens" |
| DPReview            | dpreview.com                                                                 | 2026-05-26 | Not listed                                             |
| Google Image Search | google.com                                                                   | 2026-05-26 | No construction diagram or MTF chart found             |

## Findings

- **opticalElements:** 12 (LensTip, B&H, official E-mount page)
- **opticalGroups:** 9 (LensTip, B&H, official E-mount page)
- **edElements:** 1 (niaarch.com: "1 ED lens")
- **asphericalElements:** none listed
- **hrElements:** 1 HR + 1 UHR (niaarch.com: "1 high refraction lens, 1 Ultra-high refraction lens")
- **coating:** multi-layer (B&H: "multilayered coatings"; AliExpress wiki: "multi-layer nano-coatings")
- **filterThread:** 55mm (LensTip, B&H, official E-mount page; DB corrected from 52mm)
- **maxMagnification:** 0.1 (already in DB, confirmed by LensTip)
- **constructionDiagram:** not found
- **MTF chart:** not found

## Caveats

- X-mount official page has no specs — data sourced from E-mount page and third-party listings
- niaarch.com "HR" and "UHR" elements not tracked in DB schema (only ED tracked)
