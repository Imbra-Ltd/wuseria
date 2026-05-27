# 7Artisans 55mm f/1.4 Mark II — Specs Log

## Sources checked

| Source              | URL                                                                          | Date       | Result                                                                                                                                                            |
| ------------------- | ---------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)  | 7artisans.store/products/7artisans-55mm-f1-4-mark-ii-aps-c-portrait-lens-... | 2026-05-27 | Found: 6 elements / 5 groups, multi-coated                                                                                                                        |
| LensTip             | lenstip.com/1842                                                             | 2026-05-27 | Confirmed: 6 elements / 5 groups, mag 0.18x, MFD 0.42m, 9 blades                                                                                                  |
| Radojuva            | radojuva.com                                                                 | 2026-05-27 | Not found                                                                                                                                                         |
| DPReview            | dpreview.com                                                                 | 2026-05-27 | Not listed                                                                                                                                                        |
| Google Image Search | google.com                                                                   | 2026-05-27 | Opened all 21 store gallery images + Amazon set (batch) — all product/lifestyle photos; no PARAMETER panel. No press/rumor archive surfaced a diagram/MTF either. |

## Findings

- **opticalElements:** 6 (official, confirmed by LensTip id 1842)
- **opticalGroups:** 5 (official, confirmed by LensTip id 1842)
- **specialElements:** none stated (no ED/aspherical on official or LensTip)
- **coating:** multi-layer (official: "multi-layer coating has been applied to individual elements... reduces flare and ghosting")
- **maxMagnification:** 0.18 (LensTip id 1842, "0.18x"; matches DB; official gives MFD 0.42m only)
- **constructionDiagram:** not found (store gallery is all product photos; no press/rumor archive located — but see caveat: the v1 diagram was eventually found on LeicaRumors, so this may exist somewhere not yet reached)
- **MTF chart:** not found (same as above)

## Caveats

- **DB `officialUrl` fixed (2026-05-27):** the previous shortened handle
  (`...-aps-c-portrait-lens`) returned 404; corrected to the full live handle
  (`...-for-sony-e-nikon-z-fuji-fx-canon-eos-m-olympus-m43-mirrorless-cameras`),
  which returns 200.
- Diagram/MTF "not found" is a FLOOR, not a confirmed absence: opened all 21 store
  gallery images (product/lifestyle only) and DDG press/rumor searches came up empty
  (likely rate-limited). The v1's diagram + MTF were eventually found on LeicaRumors'
  press archive, so the Mark II's may exist on a source not yet reached — worth a
  retry on lens-rumors / a 2021 announcement post.
- Active / not discontinued (official `.js` available:true).
