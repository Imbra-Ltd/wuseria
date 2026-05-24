# Handevision IBERIT 24mm f/2.4 — Specs Log

## Sources checked

| Source              | URL                                                                                    | Date       | Result                                   |
| ------------------- | -------------------------------------------------------------------------------------- | ---------- | ---------------------------------------- |
| Kipon official (FX) | https://kipon.com/product/elegant-24mm-f2-4-for-fuji-x/                                | 2026-05-24 | Found: 8E/7G, 6 blades, physical specs   |
| Handevision.de      | handevision.de                                                                         | 2026-05-24 | Domain defunct (for sale)                |
| LensTip             | lenstip.com                                                                            | 2026-05-24 | Not found                                |
| DPReview            | dpreview.com                                                                           | 2026-05-24 | 404                                      |
| OpticalLimits       | opticallimits.com                                                                      | 2026-05-24 | Not found                                |
| Phillip Reeve       | phillipreeve.net                                                                       | 2026-05-24 | Not found                                |
| Alik Griffin        | alikgriffin.com                                                                        | 2026-05-24 | Not found                                |
| Kipon blog (MTF)    | https://kipon.com/kipon-released-mtf-curvesample-photos-for-new-elegant-series-lenses/ | 2026-05-24 | Found: MTF charts at f/2.4, f/4.0, f/5.6 |
| Kipon Download Zone | kipon.com/download-zone/                                                               | 2026-05-24 | Empty — no PDFs                          |
| Wayback Machine     | web.archive.org                                                                        | 2026-05-24 | No archived product pages                |

## Optical construction

- **Elements / Groups:** 8 / 7 (Kipon official spec table: `LENSES/GROUPS: 8/7`)
- **Special elements:** none mentioned — no ED, aspherical, or special glass
- **Coating:** not published — no coating name on any source
- **Construction diagram:** not found — Kipon/IB/E Optics does not publish diagrams
- **MTF chart:** found on Kipon blog (Zemax OpticStudio computed, 2016-10-06); 3 apertures saved: `mtf-f2.4.jpg`, `mtf-f4.0.jpg`, `mtf-f5.6.jpg`; Zemax filename: `24mmFF-000-05-2.ZMX`

## Physical spec corrections (FX mount)

| Field            | Old (DB) | New (Kipon FX) | Source                          |
| ---------------- | -------- | -------------- | ------------------------------- |
| weight           | 500      | 320            | Kipon spec table (FX column)    |
| length           | 58       | 68             | Kipon spec table (FX column)    |
| minFocusDistance | 450      | 250            | Kipon spec table: 0.25m (FX)    |
| apertureBlades   | 9        | 6              | Kipon spec table: 6 iris leaves |

## maxMagnification

Not published on any source. Cannot estimate per ADR-014.

## Caveats

- Kipon spec table lists separate values per mount family (M/NEX vs FX vs Leica SL). FX-specific values used for X-mount entry.
- Optical designer: IB/E Optics (Germany), manufacturer: Kipon/Shanghai Transvision.
