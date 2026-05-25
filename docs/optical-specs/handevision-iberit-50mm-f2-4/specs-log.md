# Handevision IBERIT 50mm f/2.4 — Specs Log

## Sources checked

| Source              | URL                                                                                    | Date       | Result                                   |
| ------------------- | -------------------------------------------------------------------------------------- | ---------- | ---------------------------------------- |
| Kipon official (FX) | https://kipon.com/product/elegant-50mm-f2-4-for-fuji-x/                                | 2026-05-24 | Found: 6E/6G, 6 blades, physical specs   |
| Handevision.de      | handevision.de                                                                         | 2026-05-24 | Domain defunct (for sale)                |
| LensTip             | lenstip.com                                                                            | 2026-05-24 | Not found                                |
| DPReview            | dpreview.com                                                                           | 2026-05-24 | 404                                      |
| OpticalLimits       | opticallimits.com                                                                      | 2026-05-24 | Not found                                |
| Phillip Reeve       | phillipreeve.net                                                                       | 2026-05-24 | Not found                                |
| Radojuva            | radojuva.com                                                                           | 2026-05-24 | Timeout                                  |
| Kipon blog (MTF)    | https://kipon.com/kipon-released-mtf-curvesample-photos-for-new-elegant-series-lenses/ | 2026-05-24 | Found: MTF charts at f/2.4, f/4.0, f/5.6 |
| Wayback Machine     | web.archive.org                                                                        | 2026-05-24 | No archived product pages                |

## Optical construction

- **Elements / Groups:** 6 / 6 (Kipon official spec table: `LENSES/GROUPS: 6/6`)
- **Special elements:** none mentioned — no ED, aspherical, or special glass
- **Coating:** not published — no coating name on any source
- **Construction diagram:** not found — Kipon/IB/E Optics does not publish diagrams
- **MTF chart:** found on Kipon blog (Zemax OpticStudio computed, 2016-10-06); 3 apertures saved: `mtf-f2.4.png`, `mtf-f4.0.png`, `mtf-f5.6.png`; Zemax filename: `2.4-50mm-BK43.6-6L-B00-01-2.ZMX`

## Physical spec corrections (FX mount)

| Field            | Old (DB) | New (Kipon FX) | Source                          |
| ---------------- | -------- | -------------- | ------------------------------- |
| weight           | 300      | 310            | Kipon spec table (FX column)    |
| minFocusDistance | 450      | 600            | Kipon spec table: 0.6m (FX)     |
| apertureBlades   | 9        | 6              | Kipon spec table: 6 iris leaves |

Length (65mm) and diameter (58mm) confirmed correct.

## maxMagnification

Not published on any source. Cannot estimate per ADR-014.

## Caveats

- Kipon spec table lists separate values per mount family. FX-specific values used.
- MFD 450mm in old DB matched the Leica M spec; FX mount is 600mm.
