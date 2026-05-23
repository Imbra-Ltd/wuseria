# Pergear 25mm f/1.8 — Specs Log

## Sources checked

| Source                               | URL                                                        | Date       | Result                                                       |
| ------------------------------------ | ---------------------------------------------------------- | ---------- | ------------------------------------------------------------ |
| Official Pergear page (Shopify JSON) | pergear.com/products/pergear-25mm.json                     | 2026-05-23 | Found: 5 elements / 3 groups                                 |
| Photozone / opticallimits            | photozone.de/sony-alpha-aps-c-lens-tests/1088-pergear25f18 | 2026-05-23 | Found: 5/3 confirmed, maxMagnification listed as "1:?"       |
| 35mmc review (Hamish Gill)           | 35mmc.com/26/07/2021/pergear-25mm-f-1-8-review/            | 2026-05-23 | Found: 10 aperture blades confirmed (vs Shopify claiming 12) |
| Radojuva                             | radojuva.com/en/2020/06/pergear-25mm-1-8-hd-mc/            | 2026-05-23 | Timeout                                                      |
| LensTip                              | lenstip.com                                                | 2026-05-23 | Not covered                                                  |
| DPReview                             | dpreview.com/products/pergear/lenses                       | 2026-05-23 | No Pergear listings                                          |
| Opticallimits / Photozone            | opticallimits.com/fuji-x/1088-pergear25f18                 | 2026-05-23 | 404 — page removed                                           |
| cameradecision.com                   | cameradecision.com                                         | 2026-05-23 | 404                                                          |
| apotelyt.com                         | apotelyt.com                                               | 2026-05-23 | Not listed                                                   |
| Amazon                               | amazon.com                                                 | 2026-05-23 | No magnification in spec table                               |
| digitalkamera.de                     | digitalkamera.de                                           | 2026-05-23 | Consent wall, no data                                        |
| alikgriffin.com                      | alikgriffin.com                                            | 2026-05-23 | No magnification in review                                   |
| Google Image Search                  | google.com (construction diagram, MTF chart)               | 2026-05-23 | Blocked by captcha                                           |

## Findings

- **opticalElements:** 5 (official Shopify, Photozone)
- **opticalGroups:** 3 (official Shopify, Photozone)
- **specialElements:** none found in any source
- **coating:** HD MC / multi-coated (full name: "Pergear 25mm f/1.8 HD.MC")
- **maxMagnification:** not published — checked 12+ sources, none list it (Photozone listed "1:?")
- **apertureBlades:** DB has 10 — correct; Shopify claims 12 but two independent reviewers counted 10
- **constructionDiagram:** not found anywhere
- **MTF chart:** found on Photozone (lab measurement, Sony E-mount APS-C, LW/PH at MTF50); saved as `mtf-chart-photozone.png`; source: `photozone.de/images/8Reviews/lenses/pergear_25_18/mtf.png`

## Caveats

- Shopify listing says 12 blades but Photozone and 35mmc both measured 10. DB value of 10 is correct.
- As of 2026-05-23, the 25mm f/1.8 appears deprecated on pergear.com (mount/color options struck through). The 25mm f/1.7 is likely the successor.
