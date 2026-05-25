# Mitakon Speedmaster 65mm f/1.4 GFX — Specs Log

## Sources checked

| Source                         | URL                                                                                                        | Date       | Result                                                                         |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------ |
| zyoptics.net (live)            | https://zyoptics.net/product/mitakon-speedmaster-65mm-f-1-4/                                               | 2026-05-25 | 403 (bot protection)                                                           |
| zyoptics.net (Wayback)         | https://web.archive.org/web/20190204184607id_/https://zyoptics.net/product/mitakon-speedmaster-65mm-f-1-4/ | 2026-05-25 | Found: spec table 11E/7G, description 11E/9G (conflict)                        |
| zyoptics.net (SeleniumBase UC) | https://zyoptics.net/product/mitakon-speedmaster-65mm-f-1-4/                                               | 2026-05-25 | Found: same conflict, 2 UD + 2 HRI                                             |
| B&H Photo (search)             | https://www.bhphotovideo.com/c/search?q=mitakon+speedmaster+65mm+1.4+GFX                                   | 2026-05-25 | Found: "Two Ultra-Low Dispersion Elements, Two High Refractive Index Elements" |
| DPReview                       | dpreview.com                                                                                               | 2026-05-25 | Not listed                                                                     |
| LensTip                        | lenstip.com                                                                                                | 2026-05-25 | Not found                                                                      |
| zyoptics.net (XCD page, UC)    | https://zyoptics.net/product/mitakon-speedmaster-65mm-f-1-4-xcd/                                           | 2026-05-25 | Found: MTF chart (65mm_f1.4_MTF.jpg), same optical design as GFX               |

## Optical construction

- **Elements / Groups:** 11 / 7 (zyoptics.net spec table; description prose says 9 groups — spec table preferred as structured data)
- **Special elements:** 2 UD (Ultra-low Dispersion) + 2 HRI (High Refractive Index) — from description: "2pcs of HRI (High Refractive Index) & 2pcs of UD (Ultra-low dispersion) elements"
- **Coating:** not published
- **Construction diagram:** not found
- **MTF chart:** found on zyoptics.net XCD version page (same optical design, different mount adapter); saved as `mtf-f1.4.png` (screenshot — CDN blocks direct image download); shows 10/30 LP/MM sagittal+tangential at f/1.4 across 27mm image circle

## Caveats

- Official page has conflicting group counts: description says "11 elements in 9 groups", spec table says "11 Elements in 7 Groups". Spec table used as the authoritative source. B&H also does not resolve this conflict.
- Spec table says "Diaphragm Blades 9" but database has `apertureBlades: 11` — needs verification from a second source before correcting
