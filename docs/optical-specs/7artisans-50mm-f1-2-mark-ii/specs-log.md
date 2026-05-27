# 7Artisans 50mm f/1.2 Mark II — Specs Log

## Sources checked

| Source              | URL                                                                     | Date       | Result                                                                                                                                                                                                                         |
| ------------------- | ----------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Official (Shopify)  | 7artisans.store/products/mf-50mm-f-1-2-aps-c-lens-for-sony-e-fuji-x-... | 2026-05-27 | Specs + diagram + MTF embedded in the section image `cdn/shop/files/50_1.2.jpg` (12000px strip): spec table (7/5, 11 blades, Φ55, MFD 0.7m), "Lens structure" diagram (1 ED yellow + 3 HR blue), and MTF (OTF vs Y-field 0–14) |
| LensTip             | lenstip.com/2291                                                        | 2026-05-27 | Confirmed: 7/5, 1 ED + 3 HR, mag 0.08x (rel. 2025-12-16)                                                                                                                                                                       |
| Radojuva            | radojuva.com                                                            | 2026-05-27 | Not found                                                                                                                                                                                                                      |
| DPReview            | dpreview.com                                                            | 2026-05-27 | Not listed                                                                                                                                                                                                                     |
| Google Image Search | google.com                                                              | 2026-05-27 | Diagram + MTF recovered from the official section image (above); cropped and saved                                                                                                                                             |

## Findings

- **opticalElements:** 7 (LensTip id 2291 + official spec table on the section image)
- **opticalGroups:** 5 (LensTip + official spec table)
- **specialElements:** 1 ED, 3 HR (LensTip: "1 ED glass element, 3 HR glass elements"; CONFIRMED by the official "Lens structure" diagram — legend yellow = Extra-low Dispersion (1 element), blue = High Refraction (3 elements))
- **coating:** none stated (the official section image, LensTip, and the original 50mm f/1.2's retailer listings name no coating; not found on a reachable source — left undefined)
- **maxMagnification:** 0.08 (LensTip)
- **constructionDiagram:** found — `construction-diagram.jpg` (official "Lens structure"; 1 ED + 3 HR, dark-background rendering)
- **MTF chart:** found — `mtf-chart.jpg` (official; OTF vs Y-field of view 0–14, T1/T2/S1/S2)

## Caveats

- The official store page embeds ALL specs inside one section image
  (`cdn/shop/files/50_1.2.jpg`, a 12000px strip) — no text spec table, and this image
  is NOT in the product gallery JSON, which is why the diagram/MTF were initially
  "not found". Recovered by scraping the rendered page for `cdn/shop/files/` images.
  The strip's own spec table independently confirms 7/5, Φ55 filter, 11 blades, MFD 0.7m.
- LensTip id 2291 (release 2025-12-16) confirms the entry is the Mark II, matching the
  store page created 2025-12-09.
