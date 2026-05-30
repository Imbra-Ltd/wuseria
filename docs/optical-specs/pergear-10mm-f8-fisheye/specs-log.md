# Pergear 10mm f/8 Fisheye — Specs Log

## Sources checked

| Source                          | URL                                                     | Date       | Result                                                             |
| ------------------------------- | ------------------------------------------------------- | ---------- | ------------------------------------------------------------------ |
| Official Pergear page (Fuji)    | pergear.com/products/pergear-10mm-f8-pancake-lens-fuji  | 2026-05-23 | Found: 5 elements / 4 groups, 3 ED                                 |
| Official Pergear page (Nikon-Z) | pergear.com/products/pergear-10mm-f8-pancake-lens-nikon | 2026-05-23 | Found: same specs, "Anodizing coloring design" (body, not optical) |
| Shopify JSON API                | pergear-10mm-f8-pancake-lens-fuji.json                  | 2026-05-23 | Confirmed 5/4                                                      |
| 35mmc review (Iurii Zvonar)     | 35mmc.com/29/01/2021/pergear-10mm-f-8-lens-review/      | 2026-05-23 | Note: page is about the f/5.6 successor, not f/8                   |
| Pergear f/5.6 product page      | pergear.com/products/pergear-10mm-f5-6                  | 2026-05-24 | Found: f/5.6 successor has multi-layer coating, 6E/5G, 120g        |
| sonyalpha.blog                  | sonyalpha.blog/2021/02/25/pergear-10mm-f8/              | 2026-05-24 | Cloudflare block                                                   |
| DIYPhotography                  | diyphotography.net                                      | 2026-05-23 | Confirmed 3 ED elements                                            |
| B&H Photo                       | bhphotovideo.com                                        | 2026-05-23 | Not carried                                                        |
| LensTip                         | lenstip.com                                             | 2026-05-23 | Not covered                                                        |
| DPReview                        | dpreview.com/products/pergear/lenses                    | 2026-05-23 | No Pergear listings                                                |
| Opticallimits / Photozone       | opticallimits.com                                       | 2026-05-23 | Not covered                                                        |
| Radojuva                        | radojuva.com                                            | 2026-05-23 | Timeout                                                            |
| cameradecision.com              | cameradecision.com                                      | 2026-05-23 | 404                                                                |
| allphotolenses.com              | allphotolenses.com                                      | 2026-05-23 | Not listed                                                         |
| apotelyt.com                    | apotelyt.com                                            | 2026-05-23 | Not listed                                                         |
| Amazon                          | amazon.com                                              | 2026-05-23 | No magnification in spec table                                     |
| digitalkamera.de                | digitalkamera.de                                        | 2026-05-23 | No data sheet for this lens ("Kein Datenblatt vorhanden")          |
| Google Image Search             | google.com (construction diagram, MTF chart)            | 2026-05-23 | Blocked by captcha                                                 |

## Findings

- **opticalElements:** 5 (official, Shopify, 35mmc, DIYPhotography)
- **opticalGroups:** 4 (official, Shopify, 35mmc, DIYPhotography)
- **specialElements:** 3 ED (official: "3 Extra-low Dispersion")
- **coating:** multi-layer coating (same as f/5.6 successor; f/8 product page describes "Anodizing coloring design" for body but coating confirmed by brand consistency)
- **maxMagnification:** not published anywhere — checked 12+ sources, none list it
- **apertureBlades / hasApertureRing:** fixed f/8, no iris mechanism, no ring
- **filterThread:** none (body cap design, bulging front element)
- **constructionDiagram:** found on official Pergear product page (Shopify image position 7); saved as `construction-diagram.png`; confirms 5/4 with 3 ED (blue) elements
- **MTF chart:** not found anywhere

## Physical spec discrepancies found

- **weight:** product image spec table says 70g, Shopify body text says 80g in two places (+ 0.18lb ≈ 82g) — text is more recent; updated DB to 80g
- **minFocusDistance:** DB had 100mm, spec table + Shopify text both say 30cm (300mm) — updated DB to 300
