# Meyer Optik Primoplan 58mm f/1.9 II — Specs Log

## Sources checked

| Source                         | URL                                                                                       | Date       | Result                                                                                                   |
| ------------------------------ | ----------------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------- |
| Official Meyer Optik page      | meyer-optik-goerlitz.com/en/lenses/primoplan-58-f1.9-ii                                   | 2026-05-24 | Found: 5 elements in 4 groups, "perfect coatings" (no proprietary name)                                  |
| nikolaus-burgard.de            | nikolaus-burgard.de (Primoplan 75 review, same design family)                             | 2026-05-24 | Confirmed: Primoplan design is enhanced Cooke triplet                                                    |
| LensTip                        | lenstip.com                                                                               | 2026-05-24 | Not covered                                                                                              |
| DPReview (Kickstarter article) | dpreview.com/news/6222647746/meyer-optic-brings-back-the-primoplan-58-f1-9-on-kickstarter | 2026-05-24 | Found: construction diagram (original design, same optics as II)                                         |
| zeissikonveb.de                | zeissikonveb.de/start/objektive/normalobjektive/primoplan.html                            | 2026-05-24 | Found: Goerz patent 1926 data sheet (5E/4G) + Schäfter f/1.5 1936 data sheet (5E/4G, higher-index glass) |
| PetaPixel                      | petapixel.com/2021/03/12/meyer-optik-gorlitz-unveils-primoplan-58mm-f-1-9-ii-lens/        | 2026-05-24 | Confirmed: 14 blades, 52mm filter, 5E/4G                                                                 |
| PhotographyBlog                | photographyblog.com/reviews/meyer_optik_gorlitz_primoplan_58mm_f1_9_review                | 2026-05-24 | Found: original (non-II) specs — 12 blades, 35mm filter (different from II)                              |
| 35mmc                          | 35mmc.com/05/07/2021/meyer-optik-gorlitz-58mm-primoplan-f-1-9-ii-the-new-version-review/  | 2026-05-24 | Review of II version, confirms modern coatings improve contrast                                          |
| liveviewer.ru                  | liveviewer.ru/2017/10/meyer-gorlitz-primoplan-1-9-58-mm-nb-1950/                          | 2026-05-24 | Blocked by hCaptcha                                                                                      |

## Findings

- **opticalElements:** 5 (official page: "5 Elements in 4 Groups")
- **opticalGroups:** 4 (official page)
- **specialElements:** none — classic design, no ED/aspherical/HR elements mentioned
- **coating:** multi-coated (official: "Highquality glasses including perfect coatings"; no proprietary name; Schott and O'Hara glass per PhotographyBlog)
- **constructionDiagram:** found on DPReview Kickstarter article; saved as `construction-diagram.jpeg`; confirms 5E/4G with cemented doublet front group, no special elements
- **MTF chart:** not found — character lens, manufacturer does not publish MTF

## Historical design lineage

Source: zeissikonveb.de — comprehensive Primoplan history with Zeiss collection data sheets.

The modern Primoplan 58 II (5E/4G) matches the **Goerz patent design (1926)**. Both the Goerz f/1.9 and Schäfter f/1.5 share the same 5E/4G topology: cemented doublet front + biconcave dispersing element + two biconvex rear elements. Schäfter achieved f/1.5 through higher-refractive-index glass, not additional elements. The II version uses the same formula with modern glass and coatings.

Saved files:

- `construction-diagram.jpeg` — modern II version (from DPReview)
- `primoplan-optical-design.jpg` — comprehensive diagram from zeissikonveb.de: construction (5E/4G f/1.9), spherical aberration curves, astigmatism/field curvature, distortion (+1.5% pincushion at 15°)

## Physical spec corrections (2026-05-24)

DB had values from original Primoplan, not the II version. Corrected from official page:

- **apertureBlades:** 15 → 14 (official: "14 aperture blades")
- **filterThread:** 37mm → 52mm (official: "Filter diameter: 52mm")
- **weight:** 200g → 230g (official: "230g - 270g", using low end for X-mount)
- **minFocusDistance:** 400mm → 500mm (official: "0,5 m")
