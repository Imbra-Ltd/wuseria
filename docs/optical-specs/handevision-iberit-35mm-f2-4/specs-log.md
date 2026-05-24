# Handevision IBERIT 35mm f/2.4 — Specs Log

## Sources checked

| Source              | URL                                                                                    | Date       | Result                                   |
| ------------------- | -------------------------------------------------------------------------------------- | ---------- | ---------------------------------------- |
| Kipon official (FX) | https://kipon.com/product/2022-version-elegant-35mm-f2-4-for-fuji-x/                   | 2026-05-24 | Found: 6E/6G, 6 blades, physical specs   |
| Alik Griffin review | https://alikgriffin.com/handevision-35mm-f2-4-review-sample-photos/                    | 2026-05-24 | Found: confirms 6E/6G, 6 blades          |
| Handevision.de      | handevision.de                                                                         | 2026-05-24 | Domain defunct (for sale)                |
| LensTip             | lenstip.com                                                                            | 2026-05-24 | Not found                                |
| DPReview            | dpreview.com                                                                           | 2026-05-24 | 404                                      |
| OpticalLimits       | opticallimits.com                                                                      | 2026-05-24 | Not found                                |
| Phillip Reeve       | phillipreeve.net                                                                       | 2026-05-24 | Not found                                |
| Kipon blog (MTF)    | https://kipon.com/kipon-released-mtf-curvesample-photos-for-new-elegant-series-lenses/ | 2026-05-24 | Found: MTF charts at f/2.4, f/4.0, f/5.6 |
| Wayback Machine     | web.archive.org                                                                        | 2026-05-24 | Connection refused                       |

## Optical construction

- **Elements / Groups:** 6 / 6 (Kipon official + Alik Griffin review)
- **Special elements:** none mentioned — no ED, aspherical, or special glass
- **Coating:** not published — Alik Griffin notes reasonable flare resistance but no coating name given
- **Construction diagram:** not found — Kipon/IB/E Optics does not publish diagrams
- **MTF chart:** found on Kipon blog (Zemax OpticStudio computed, 2016-10-06); 3 apertures saved: `mtf-f2.4.jpg`, `mtf-f4.0.jpg`, `mtf-f5.6.jpg`

## Physical spec corrections (FX mount)

| Field            | Old (DB) | New (Kipon FX) | Source                          |
| ---------------- | -------- | -------------- | ------------------------------- |
| weight           | 300      | 280            | Kipon spec table (FX column)    |
| length           | 35       | 45             | Kipon spec table (FX column)    |
| minFocusDistance | 450      | 350            | Kipon spec table: 0.35m (FX)    |
| apertureBlades   | 9        | 6              | Kipon spec table: 6 iris leaves |

## maxMagnification

Not published on any source. Cannot estimate per ADR-014.

## Caveats

- "2022 Version" in product URL — may indicate minor revision, but optical formula (6/6) unchanged from original.
- Kipon spec table lists separate values per mount family. FX-specific values used.
