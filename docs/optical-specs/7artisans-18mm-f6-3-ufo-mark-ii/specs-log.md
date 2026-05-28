# 7Artisans 18mm f/6.3 UFO Mark II — Specs Log

## Sources checked

| Source              | URL                                                                                  | Date       | Result                                                                                                                                                                                           |
| ------------------- | ------------------------------------------------------------------------------------ | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Official (Shopify)  | 7artisans.store/products/18mm-f-6-3-mark-ii-aps-c-lens-for-sony-e-fujifilm-x-nikon-z | 2026-05-27 | Found: 6 elements / 5 groups; spec panel confirms 0 diaphragm blades (fixed aperture), no filter support, MFD 0.3m. Sliced the full section composite (cdn/shop/files, 18719px) — no diagram/MTF |
| LensTip (Mark II)   | lenstip.com/2023                                                                     | 2026-05-27 | Mark II confirmed: 6 elements / 5 groups, mag 0.07x, MFD 0.3m, no filter; release 03.02.2023                                                                                                     |
| LensTip (original)  | lenstip.com/1760                                                                     | 2026-05-27 | Original 18mm = 6 elem / 4 groups, mag 0.2x, release 24.10.2020 — a DIFFERENT lens                                                                                                               |
| kleiber.me (review) | kleiber.me/blog/2025/07/05/7Artisans-18mm-f6.3-ufo-fuji-review                       | 2026-05-27 | Hands-on Fuji-X review of the Mark II ("18mm II F6.3 Ufo", €68). No spec table. OQ notes for scoring: decent for its class, vs Fujinon XF 27mm f/2.8; fixed f/6.3 = "good-weather lens".         |
| Radojuva            | radojuva.com                                                                         | 2026-05-27 | Not found                                                                                                                                                                                        |
| DPReview            | dpreview.com                                                                         | 2026-05-27 | Not listed                                                                                                                                                                                       |
| Google Image Search | google.com                                                                           | 2026-05-27 | No construction diagram or MTF chart                                                                                                                                                             |

## Findings

- **opticalElements:** 6 (official Mark II page + LensTip 2023)
- **opticalGroups:** 5 (official Mark II + LensTip 2023; the original Mk I was 6/4 — LensTip 1760)
- **specialElements:** none stated
- **coating:** none stated (no coating named on official page; not stocked at B&H; unverified Amazon snippet only — not recorded)
- **maxMagnification:** 0.07 (LensTip 2023 Mark II, "0.07x"; the DB's prior 0.2 was the ORIGINAL's value — corrected)
- **constructionDiagram:** not found (sliced the full official section composite — product/
  marketing/sample-photo + spec table only; none published, as expected for a fixed-aperture pancake)
- **MTF chart:** not found (same sweep — none published)

## Caveats

- The entry maps to the MF 18mm f/6.3 **Mark II** pancake — confirmed not by the URL slug
  alone but by the official **page title "MF 18mm f/6.3 Mark II"** and the store carrying two
  distinct products (`18mm-f6-3` original + `...-mark-ii-...`). **Model renamed to
  "18mm f/6.3 UFO Mark II" (2026-05-28)** per CLAUDE.md naming convention ("UFO" is the
  nickname; "Mark II" is the official generation marker). Optical-specs folder renamed to
  `7artisans-18mm-f6-3-ufo-mark-ii`.
- The original 18mm f/6.3 (6/4, 0.2x, 2020 — LensTip 1760) is a different lens. It is NOT a
  candidate for the DB: the official original-lens `.js` lists only a Canon EOS-M variant
  (no Fuji X), so it fails the X-mount requirement. (Contrast the 60mm/12mm originals, which
  WERE X-mount and are tracked in #878.)
- Group-count conflict RESOLVED: 6/5 is the Mark II (official + LensTip 2023); the 6/4 was
  the original (LensTip 1760).
- **DB corrections (2026-05-27):** `maxMagnification` 0.2 → **0.07** and `year` 2019 →
  **2023** — the prior 0.2/2019 were the original's values (LensTip 1760, 2020) left on the
  Mark II row; the Mark II is 0.07x, released 2023-02-03 (LensTip 2023).
