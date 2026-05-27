# 7Artisans 35mm f/1.2 Mark II — Specs Log

## Sources checked

| Source              | URL                                             | Date       | Result                                                                                                                         |
| ------------------- | ----------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Official (Shopify)  | 7artisans.store/products/7artisans-35mm-f1-2-ii | 2026-05-27 | Found: 6 elements / 5 groups, multi-layer coated                                                                               |
| LensTip             | lenstip.com/1762                                | 2026-05-27 | Confirmed: 6 elements / 5 groups, mag 0.17x, 10 diaphragm blades                                                               |
| B&H Photo           | bhphotovideo.com/c/product/1638677-REG          | 2026-05-27 | Confirmed: 6 elements / 5 groups, 10 rounded blades, MFD 11" (~28cm); "multi-layer coating ... applied to individual elements" |
| Radojuva            | radojuva.com                                    | 2026-05-27 | Not found                                                                                                                      |
| DPReview            | dpreview.com                                    | 2026-05-27 | Not listed                                                                                                                     |
| Google Image Search | google.com                                      | 2026-05-27 | Diagram found embedded in official composite marketing image; cropped and saved (no MTF)                                       |

## Findings

- **opticalElements:** 6 (official, confirmed by LensTip id 1762, B&H, and the construction diagram)
- **opticalGroups:** 5 (official, confirmed by LensTip id 1762 and B&H; "newly redesigned optical formula")
- **specialElements:** none stated
- **coating:** multi-layer (official: "Multi-layer coating has been applied to individual elements"; confirmed by B&H with the same wording)
- **maxMagnification:** 0.17 (LensTip id 1762, "0.17x"; matches DB; official gives MFD 0.28m only) — matches DB value
- **constructionDiagram:** found — `construction-diagram.jpg` (official; 6 elements / 5 groups, redesigned formula)
- **MTF chart:** not found (no MTF published for the Mark II on official store or Amazon; do not substitute the original 35mm f/1.2 MTF)

## Caveats

- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
- Official page has an internal contradiction on aperture blades: spec table says 10,
  bokeh graphic says 9. **Resolved to 10** — both LensTip (id 1762) and B&H state 10
  rounded blades; the bokeh graphic's "9" is the outlier. DB `apertureBlades: 10` is correct.
