# Meike 25mm f/0.95 — Specs Log

## Sources checked

| Source                  | URL                                       | Date       | Result                                                  |
| ----------------------- | ----------------------------------------- | ---------- | ------------------------------------------------------- |
| Official (Shopify JSON) | meikeglobal.com/products/25mm-f0-95x.json | 2026-05-26 | Found: 11 elements / 9 groups, 13 blades, 62mm filter   |
| LensTip                 | lenstip.com/1423                          | 2026-05-26 | Specs only (no review): 12/10 — conflicts with official |
| DPReview                | dpreview.com                              | 2026-05-26 | Not listed                                              |
| Google Image Search     | google.com                                | 2026-05-26 | No construction diagram or MTF chart found              |

## Findings

- **opticalElements:** 11 (official Shopify JSON spec table)
- **opticalGroups:** 9 (official Shopify JSON spec table)
- **edElements:** none listed in any source
- **asphericalElements:** none listed in any source
- **coating:** multi-layer (official page mentions "Multi-layered")
- **filterThread:** 62mm (official; LensTip says 55mm — LensTip wrong)
- **maxMagnification:** not published in any source
- **constructionDiagram:** not found
- **MTF chart:** not found

## Caveats

- LensTip lists 12 elements / 10 groups — official Shopify JSON clearly states "11 elements in 9 groups". Official wins per trust hierarchy.
- DB had apertureBlades: 12 — official says 13. Corrected.
- DB had filterThread: 55 — official says 62mm. Corrected.
- LensTip lists 0 blades and 55mm filter — both appear to be data errors.
