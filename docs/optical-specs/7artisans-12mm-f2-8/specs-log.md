# 7Artisans 12mm f/2.8 — Specs Log

## Sources checked

| Source                    | URL                                                                             | Date       | Result                                                                                                                                                                                                                                                      |
| ------------------------- | ------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Official (Shopify)        | 7artisans.store/products/12mm-f-2-8-aps-c-lens-for-e-eos-m-fx-m43-z             | 2026-05-27 | Found: 12 elements / 10 groups; spec panel (cdn/shop/files): 5 diaphragm blades, filter 67mm, MFD 0.15m. Swept all 13 section panels — no diagram/MTF                                                                                                       |
| LensTip (Mark II)         | lenstip.com/2012                                                                | 2026-05-27 | Mark II confirmed: 12/10, 5 blades, filter 67mm, MFD 0.15m, mag 0.1x; release 20.12.2022. (The original 12mm = LensTip 1724: 10/8, 7 blades, 77mm, mag 0.07x, 2017 — a DIFFERENT lens)                                                                      |
| Radojuva                  | radojuva.com                                                                    | 2026-05-27 | Not found                                                                                                                                                                                                                                                   |
| DPReview                  | dpreview.com                                                                    | 2026-05-27 | Not listed                                                                                                                                                                                                                                                  |
| Google Image Search       | google.com                                                                      | 2026-05-27 | No construction diagram or MTF                                                                                                                                                                                                                              |
| B&H Photo                 | bhphotovideo.com/c/product/1732945-REG                                          | 2026-05-27 | Confirms 12/10, 5 blades, filter 67mm, MFD 5.9" (~0.15m), manual, X-mount; no coating named                                                                                                                                                                 |
| Intl. retailers (checked) | yunglien.com.tw, chako.ua, stkb.co.jp, 24h.pchome.com.tw, allphotolenses c_4582 | 2026-05-27 | None yielded a verifiable Mark II coating. allphotolenses c_4582 = a DIFFERENT lens (T2-mount 7/5 fisheye); stkb.co.jp = the ORIGINAL 12mm (2018), which it notes has a construction diagram + MTF (Mk I only); TW/UA pages JS-rendered, no specs extracted |

## Findings

- **opticalElements:** 12 (official + LensTip 2012 Mark II + B&H)
- **opticalGroups:** 10 (official + LensTip 2012 + B&H)
- **specialElements:** none stated (no ED/aspherical on official, LensTip, or B&H)
- **coating:** none stated (no coating named on official page or B&H; unverified Amazon snippet only — not recorded)
- **maxMagnification:** 0.1 (LensTip 2012 Mark II, "0.1x"; the DB's prior 0.07 was the ORIGINAL 12mm's value — corrected)
- **constructionDiagram:** not found (swept all 13 official `cdn/shop/files/` section
  panels — spec table + marketing/mount/sample-photo only; no diagram)
- **MTF chart:** not found (same sweep — none published)

## Caveats

- **This entry IS the Mark II** (confirmed: its specs — 12/10, 5 blades, 67mm, MFD 0.15m,
  mag 0.1x — match LensTip 2012 / the Mark II page exactly, NOT the original LensTip 1724:
  10/8, 7 blades, 77mm, 0.07x). The DB just names it plain "12mm f/2.8". The original
  Gen-I 12mm is a different lens carried only as a "Used" listing; if it's ever added it
  needs its own row. Original-lens provenance leads (NOT used for this Mark II row):
  LensTip 1724 (10/8, 7 blades, 0.07x, 2017); stkb.co.jp 2018 launch post (has diagram + MTF);
  **photozone.de/opticallimits trust-3 lab review** (Sept 2019, Sony FE): 10/8, 7 blades, 55mm
  filter, 0.2m MFD, 292g, clickless aperture, "Zeiss Distagon-inspired, rear focusing" —
  measured lab MTF available there. The model-name should arguably gain "Mark II" — flagged
  but the rename is out of scope here.
- **DB corrections/fills (2026-05-27):** `apertureBlades` 7 → **5**; `filterThread` added
  **67**; `minFocusDistance` 200 → **150** (all official spec panel + B&H, Mark II). Plus
  `year` 2018 → **2022** and `maxMagnification` 0.07 → **0.1** (LensTip 2012 Mark II release
  20.12.2022) — the prior 2018/0.07 were the ORIGINAL 12mm's values left on the Mark II row.
