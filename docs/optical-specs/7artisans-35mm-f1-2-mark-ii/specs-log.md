# 7Artisans 35mm f/1.2 Mark II — Specs Log

## Sources checked

| Source              | URL                                             | Date       | Result                                                                                                                                        |
| ------------------- | ----------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)  | 7artisans.store/products/7artisans-35mm-f1-2-ii | 2026-05-27 | Found: 6 elements / 5 groups, multi-layer coated                                                                                              |
| LensTip             | lenstip.com/1762                                | 2026-05-27 | Confirmed: 6 elements / 5 groups, mag 0.17x, 10 diaphragm blades                                                                              |
| B&H Photo           | bhphotovideo.com/c/product/1638677-REG          | 2026-05-27 | Confirmed: 6 elements / 5 groups, 10 rounded blades, MFD 11" (~28cm); "multi-layer coating ... applied to individual elements"                |
| Radojuva            | radojuva.com                                    | 2026-05-27 | Not found                                                                                                                                     |
| DPReview            | dpreview.com                                    | 2026-05-27 | Not listed                                                                                                                                    |
| Google Image Search | google.com                                      | 2026-05-27 | Official gallery "PARAMETER" panel (image 4_55ceb826…jpg) holds BOTH a labeled cross-section diagram and an MTF chart; both cropped and saved |

## Findings

- **opticalElements:** 6 (official, confirmed by LensTip id 1762, B&H, and the construction diagram)
- **opticalGroups:** 5 (official, confirmed by LensTip id 1762 and B&H; "newly redesigned optical formula")
- **specialElements:** none stated
- **coating:** multi-layer (official: "Multi-layer coating has been applied to individual elements"; confirmed by B&H with the same wording)
- **maxMagnification:** 0.17 (LensTip id 1762, "0.17x"; matches DB; official gives MFD 0.28m only) — matches DB value
- **constructionDiagram:** found — `construction-diagram.jpg` (official cross-section labeled "7Artisans 35mm F1.2 Mark II", from the gallery PARAMETER panel)
- **MTF chart:** found — `mtf-chart.jpg` (official; "ZP1 - f35.720/Fn1.30 - INF" field-angle MTF, MTF 0–1 vs Y-field angle 0–21°, T/S Diff Limit + T/S 5/10/20/30 lpmm). NOTE: this is a field-angle MTF (Zemax-style), a different format from the lp/mm-vs-image-height charts on the manual primes.

## Caveats

- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts.
- The MTF was initially reported "not found" (the batch re-inspection saw a vertical
  exploded diagram but missed the gallery "PARAMETER" panel that carries both a
  cross-section and an MTF). Recovered on this review and saved; the construction
  artifact was upgraded to the labeled cross-section from the same panel.
- Official page has an internal contradiction on aperture blades: spec table says 10,
  bokeh graphic says 9. **Resolved to 10** — both LensTip (id 1762) and B&H state 10
  rounded blades; the bokeh graphic's "9" is the outlier. DB `apertureBlades: 10` is correct.
