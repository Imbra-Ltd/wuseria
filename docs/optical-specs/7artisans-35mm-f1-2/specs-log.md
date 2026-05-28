# 7Artisans 35mm f/1.2 — Specs Log

## Sources checked

| Source                    | URL                                | Date       | Result                                                                                                           |
| ------------------------- | ---------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)        | 7artisans.store/products/35mm-f1-2 | 2026-05-27 | Found: 6 elements / 5 groups (Sonnar formula); no coating named                                                  |
| LensTip                   | lenstip.com/1727                   | 2026-05-27 | Confirmed: 6 elements / 5 groups, mag 0.13x, MFD 0.35m, declicked aperture; no special elements or coating named |
| Radojuva                  | radojuva.com                       | 2026-05-27 | Not found                                                                                                        |
| DPReview                  | dpreview.com                       | 2026-05-27 | Not listed                                                                                                       |
| Photosynthesis (retailer) | magazin.photosynthesis.bg/en/70184 | 2026-05-27 | v1 confirmed (5/6, 9 blades, MFD 35cm); "multi-layer coating ... minimizes unwanted glare"                       |
| Google Image Search       | google.com                         | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved                           |

## Findings

- **opticalElements:** 6 (official, confirmed by LensTip id 1727 and the construction diagram)
- **opticalGroups:** 5 (official, confirmed by LensTip id 1727; "Sonnar formula with numerous refinements")
- **specialElements:** none stated (neither official nor LensTip names ED/aspherical; line-art diagram has no glass-type legend)
- **coating:** multi-layer (NOT on the official store page or LensTip; stated by Photosynthesis retailer — "multi-layer coating ... minimizes unwanted glare". Single retailer source here (the v1 is discontinued, so B&H now lists only the Mark II), but the Mark II is officially multi-coated and the brand pattern is consistent. Recorded as `["multi-layer"]`; single-source — lower confidence than the 25mm/50mm.)
- **maxMagnification:** 0.13 (LensTip id 1727, "0.13x"; matches DB; not on official page) — matches DB value
- **constructionDiagram:** found — `construction-diagram.jpg` (official; 6 elements / 5 groups)
- **MTF chart:** found — `mtf-chart.jpg` (official; S10/T10/S30/T30 at f/1.2 and f/8)

## Caveats

- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
- **Discontinued** (marked `isDiscontinued: true` 2026-05-27): the official `.js`
  storefront reports every variant `available: false` (incl. FX mount), the product
  lists only "Silver", 7Artisans carries a separate "Used 35mm f/1.2" listing, and the
  lens is superseded by the still-selling 35mm f/1.2 Mark II. Original page still in
  catalog (not delisted), so `officialUrl` retained.

## Physical-field re-check (2026-05-28)

Full field cross-check vs LensTip 1727 (initial pass was optical + MFD only):

- **diameter:** 43 → **55** (LensTip 55×36; the prior 43 was the FILTER size — front engraving "Ø43" — wrongly placed as diameter)
- **length:** 32 → **36** (LensTip)
- weight 150, blades 9, mag 0.13x, MFD 350, filter 43 (engraving "Ø43") all CONFIRMED. LensTip 1727 matched on every optical field, so its dimensions are reliable here.
