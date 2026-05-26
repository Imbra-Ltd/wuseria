# Handevision IBERIT 75mm f/2.4 — Specs Log

## Sources checked

| Source              | URL                                                                                    | Date       | Result                                   |
| ------------------- | -------------------------------------------------------------------------------------- | ---------- | ---------------------------------------- |
| Kipon official (FX) | https://kipon.com/product/elegant-75mm-f2-4-for-fuji-x/                                | 2026-05-24 | Found: 5E/5G, 6 blades, physical specs   |
| Handevision.de      | handevision.de                                                                         | 2026-05-24 | Domain defunct (for sale)                |
| LensTip             | lenstip.com                                                                            | 2026-05-24 | Not found                                |
| DPReview            | dpreview.com                                                                           | 2026-05-24 | 404                                      |
| OpticalLimits       | opticallimits.com                                                                      | 2026-05-24 | Not found                                |
| Phillip Reeve       | phillipreeve.net                                                                       | 2026-05-24 | Not found                                |
| Kipon blog (MTF)    | https://kipon.com/kipon-released-mtf-curvesample-photos-for-new-elegant-series-lenses/ | 2026-05-24 | Found: MTF charts at f/2.4, f/4.0, f/5.6 |
| Wayback Machine     | web.archive.org                                                                        | 2026-05-24 | 72 snapshots exist, connection refused   |

## Optical construction

- **Elements / Groups:** 5 / 5 (Kipon official spec table: `LENSES/GROUPS: 5/5`)
- **Special elements:** none mentioned — described as "based on classic constructions"
- **Coating:** not published — no coating name on any source
- **Construction diagram:** not found — Kipon/IB/E Optics does not publish diagrams
- **MTF chart:** found on Kipon blog (Zemax OpticStudio computed, 2016-10-06); 3 apertures saved: `mtf-f2.4.png`, `mtf-f4.0.png`, `mtf-f5.6.png`

## Physical spec corrections (FX mount)

| Field          | Old (DB) | New (Kipon FX) | Source                             |
| -------------- | -------- | -------------- | ---------------------------------- |
| weight         | 300      | 270            | Kipon spec table (M/NEX/FX column) |
| length         | 75       | 65             | Kipon spec table (M/NEX/FX column) |
| apertureBlades | 9        | 6              | Kipon spec table: 6 iris leaves    |

| minFocusDistance | 700 | 600 | Kipon spec table: 0.7/0.6 — second value is FX mount |

Diameter (58mm) confirmed correct.

## maxMagnification

Not published on any source. Cannot estimate per ADR-014.

## Caveats

- Kipon spec table shows weight 270g and length 65mm for M/NEX/FX mounts; 330g and 75mm for Leica SL/T/CL mounts. Old DB values matched the Leica SL column.
