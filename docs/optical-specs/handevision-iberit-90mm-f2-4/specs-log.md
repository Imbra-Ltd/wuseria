# Handevision IBERIT 90mm f/2.4 — Specs Log

## Sources checked

| Source                  | URL                                                                                            | Date       | Result                                                                   |
| ----------------------- | ---------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------ |
| Kipon official (FX)     | https://kipon.com/product/elegant-90mm-f2-4-for-fuji-x/                                        | 2026-05-24 | Found: 4E/4G, 10 blades, physical specs                                  |
| Kipon blog (MTF charts) | https://kipon.com/kipon-released-mtf-curvesample-photos-for-new-elegant-series-lenses/         | 2026-05-24 | Found: MTF charts at f/2.4, f/4.0, f/5.6 (JS-rendered, not downloadable) |
| Kipon blog (2017 MTF)   | https://kipon.com/handevision-released-mtf-curve-for-new-iberit-series-lens-and-sample-photos/ | 2026-05-24 | Found: earlier MTF chart set (same lens)                                 |
| Handevision.de          | handevision.de                                                                                 | 2026-05-24 | Domain defunct (for sale)                                                |
| LensTip                 | lenstip.com                                                                                    | 2026-05-24 | Not found                                                                |
| DPReview                | dpreview.com                                                                                   | 2026-05-24 | 404                                                                      |
| OpticalLimits           | opticallimits.com                                                                              | 2026-05-24 | Not found                                                                |
| Phillip Reeve           | phillipreeve.net                                                                               | 2026-05-24 | Not found                                                                |
| Radojuva                | radojuva.com                                                                                   | 2026-05-24 | Not found                                                                |
| Wayback Machine         | web.archive.org                                                                                | 2026-05-24 | No archived product pages                                                |

## Optical construction

- **Elements / Groups:** 4 / 4 (Kipon official spec table: `LENSES/GROUPS: 4/4`)
- **Special elements:** none mentioned — no ED, aspherical, or special glass
- **Coating:** not published — no coating name on any source
- **Construction diagram:** not found
- **MTF chart:** found on Kipon blog (Zemax OpticStudio computed, 2016-10-07); 3 apertures saved: `mtf-f2.4.jpg`, `mtf-f4.0.jpg`, `mtf-f5.6.jpg`; Zemax filename: `2.4-90mm-BK43.6-4L-900-02-1.ZMX`; downloaded via Playwright (hotlink-protected, requires session cookies)

## Physical spec corrections (FX mount)

| Field            | Old (DB) | New (Kipon FX) | Source                              |
| ---------------- | -------- | -------------- | ----------------------------------- |
| weight           | 400      | 340            | Kipon spec table (FX column)        |
| minFocusDistance | 900      | 700            | Kipon spec table: 0.7m (all mounts) |
| apertureBlades   | 9        | 10             | Kipon spec table: 10 iris leaves    |

Length (79mm) and diameter (58mm) confirmed correct.

## maxMagnification

Not published on any source. Cannot estimate per ADR-014.

## Caveats

- The 90mm uniquely has 10 aperture blades (all other IBERITs have 6) — confirmed on official page.
- Spec table shows `APERTURE [F]: 2.4-1.6` which appears to be a typo for `2.4-16`.
- MTF charts exist but require manual browser download due to hotlink protection and JS rendering.
