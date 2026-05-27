# 7Artisans 7.5mm f/2.8 Fisheye II — Specs Log

## Sources checked

| Source                    | URL                                                                                                  | Date       | Result                                                                                                                                                                  |
| ------------------------- | ---------------------------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)        | 7artisans.store/products/7-5mm-f2-8-mk-ii                                                            | 2026-05-27 | Found: 11 elements / 9 groups, 2 ED, HOYA glass; construction diagram + MTF chart embedded in a composite gallery image (generic filename)                              |
| LensTip                   | lenstip.com/1844                                                                                     | 2026-05-27 | Confirmed: 11 elements / 9 groups, 2 ED ("2 ultra-low dispersion glass elements"), 7 blades, MFD 0.15m; no coating named                                                |
| Radojuva                  | radojuva.com                                                                                         | 2026-05-27 | Not found                                                                                                                                                               |
| DPReview                  | dpreview.com                                                                                         | 2026-05-27 | Not listed                                                                                                                                                              |
| Google Image Search       | google.com                                                                                           | 2026-05-27 | Construction diagram + MTF recovered from official composite images; high-res versions sourced from the Amazon listing (saved)                                          |
| Shutterbug (review)       | shutterbug.com/content/sharp-super-affordable-and-fun-7artisans-75mm-f28-mark-ii-fisheye-lens-review | 2026-05-27 | Confirmed: rear group Hoya ED glass; front group high-refractive-index element replacing Mk I cemented glass; clean labeled diagram shows 2 red ED elements; price $139 |
| Amazon (official listing) | m.media-amazon.com (7Artisans "LENS DESCRIPTION" image)                                              | 2026-05-27 | High-res official composite: MTF chart + lens-structure diagram (2 red ED rear elements). Source of the saved artifacts.                                                |
| B&H Photo                 | bhphotovideo.com/c/product/1732941-REG                                                               | 2026-05-27 | Confirms 11 elements / 9 groups, 7 blades; lists "Multi-Layer Lens Coating"                                                                                             |

## Findings

- **opticalElements:** 11 (official, confirmed by LensTip id 1844 and the official construction diagram)
- **opticalGroups:** 9 (official, confirmed by LensTip id 1844)
- **specialElements:** 2 ED (official: "two ED lenses added"; LensTip: "2 ultra-low dispersion glass elements"; both the official and Amazon lens-structure diagrams show 2 ED elements in the rear group — three+ sources agree on 2 ED). Shutterbug also notes a high-refractive-index element in the front group (replaces Mk I cemented glass) — not separately recorded as the maker gives it no count/designation.
- **coating:** multi-layer (NOT on the official store page or LensTip, but B&H lists "Multi-Layer Lens Coating"; Shutterbug review separately remarks the front-element coating "appears to be quite satisfactory". Recorded as `["multi-layer"]` on B&H evidence.)
- **maxMagnification:** not found (official states closest focus 0.15m only; LensTip leaves magnification blank — not estimated per project rule)
- **constructionDiagram:** found — `construction-diagram.jpg` (official 7Artisans lens-structure cross-section; ED elements shown in red, rear group)
- **MTF chart:** found — `mtf-chart.jpg` (official; S1–S4 sagittal solid + T1–T4 meridional dashed, 0–12mm)

## Caveats

- The construction diagram and MTF chart are published as official 7Artisans
  artifacts but only inside composite marketing images — invisible to filename/text
  scraping (the gallery JSON filenames are generic numbers). Found by visually
  inspecting the gallery/listing images per PLAYBOOK 2.8 caveat.
- The saved artifacts are cropped from the high-res official "LENS DESCRIPTION"
  composite on the Amazon listing (1385×1467), which carries the same official MTF
  and lens-structure diagram at higher resolution than the 7artisans.store gallery.
- The earlier research pass wrongly reported "no MTF / no diagram" because it only
  checked the gallery JSON filenames, not the image contents. Corrected on review.
