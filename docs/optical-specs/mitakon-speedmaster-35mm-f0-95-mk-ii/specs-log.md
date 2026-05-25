# Mitakon Speedmaster 35mm f/0.95 Mk II — Specs Log

## Sources checked

| Source                         | URL                                                                                                          | Date       | Result                                                                                                  |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------ | ---------- | ------------------------------------------------------------------------------------------------------- |
| zyoptics.net (live)            | https://zyoptics.net/product/mitakon-speedmaster-35mm-f-0-95/                                                | 2026-05-25 | 403 (bot protection)                                                                                    |
| zyoptics.net (Wayback)         | https://web.archive.org/web/20230529045554/https://zyoptics.net/product/mitakon-speedmaster-35mm-f-0-95/     | 2026-05-25 | Found: 11E/8G, 1 ED, 2 Extra-High RI, 1 High RI                                                         |
| zyoptics.net (SeleniumBase UC) | https://zyoptics.net/product/mitakon-speedmaster-35mm-f-0-95/                                                | 2026-05-25 | Found: 11E/8G, same special elements                                                                    |
| B&H Photo (search)             | https://www.bhphotovideo.com/c/search?q=mitakon+speedmaster+35mm+0.95+fujifilm                               | 2026-05-25 | Found: "One Extra-Low Dispersion Element"                                                               |
| AllPhotoLenses                 | https://allphotolenses.com/lenses/item/c_4048.html                                                           | 2026-05-25 | Found: confirms 11/8                                                                                    |
| Alik Griffin review            | https://alikgriffin.com/mitakon-speedmaster-35mm-f0-95-ii-review-sample-photos/                              | 2026-05-25 | Found: confirms 11/8, notes "coatings are fantastic"                                                    |
| DPReview                       | dpreview.com                                                                                                 | 2026-05-25 | GDPR consent wall blocked all tiers (#870)                                                              |
| Photography Bay                | https://photographybay.com/2016/03/07/mitakon-speedmaster-35mm-f0-95-lens-gets-the-mark-ii-treatment/        | 2026-05-25 | Found: 1 ED, 2 EHR, 3 HR — confirms LensTip, contradicts zyoptics.net                                   |
| B&H Photo (product page)       | https://www.bhphotovideo.com/c/product/1226779-REG/                                                          | 2026-05-25 | Found: 1 ED, 2 EHR, 3 HR — same as Photography Bay                                                      |
| Lensrentals                    | https://www.lensrentals.com/rent/mitakon-speedmaster-35mm-f0.95-mark-ii-for-fuji-x                           | 2026-05-25 | Found: 1 ED, 2 EHR, 3 HR — same as Photography Bay                                                      |
| LensTip (Mk II specs)          | https://www.lenstip.com/1406-Mitakon_Speedmaster_35_mm_f_0.95_Mark_II-lens_specifications.html               | 2026-05-25 | Found: 11E/8G, 1 ED, 2 EHR, 3 HR (discrepancy)                                                          |
| LensTip (Mk I review)          | https://www.lenstip.com/441.1-Lens_review-Mitakon_Speedmaster_35_mm_f_0.95_Introduction.html                 | 2026-05-25 | Found: Mk I review (10E/7G, different optical design)                                                   |
| klassik-cameras.de             | https://www.klassik-cameras.de/Zhongyi35mm095.html                                                           | 2026-05-25 | Found: "11 elements in 8 groups, including 6 extra-low dispersion elements" — likely conflates ED + HRI |
| photorumors.com                | https://photorumors.com/2021/04/15/new-zhong-yi-optics-mitakon-speedmaster-35mm-f-0-95-mark-ii-lens-for-mft/ | 2026-05-25 | Found: construction diagram (official ZY Optics material)                                               |
| OpticalLimits                  | opticallimits.com                                                                                            | 2026-05-25 | 404                                                                                                     |

## Optical construction

- **Elements / Groups:** 11 / 8 (zyoptics.net spec table, confirmed by AllPhotoLenses)
- **Special elements:** 1 ED + 2 Extra-High Refractive Index + 3 High Refractive Index = 6 special elements total (B&H, Photography Bay, Lensrentals all agree; zyoptics.net listed HR as 1 — typo)
- **Coating:** not published (no branded coating name; Alik Griffin notes good coating quality)
- **Construction diagram:** found — saved as `construction-diagram.png` (from photorumors.com, official ZY Optics material). Shows 11 elements in 8 groups with colored special elements (blue, orange).
- **MTF chart:** not found

## Caveats

- B&H simplifies to "One Extra-Low Dispersion Element" and does not list HRI separately in key features
- **Resolved discrepancy:** zyoptics.net listed "2 Extra-High RI + 1 High RI" = 3 HRI total. But B&H, Photography Bay, Lensrentals, and LensTip all agree on "2 EHR + 3 HR" = 5 HRI total. The zyoptics.net HR count of 1 is a typo — correct value is 3. Total special elements: 6 (1 ED + 2 EHR + 3 HR).
- LensTip reviewed the **Mk I** (10E/7G, 10 blades, 680g) — different optical design from our Mk II (11E/8G, 9 blades, 460g). The Mk I review found single-layer MgF₂-quality coatings with 85-86% max transmission (very basic). If the Mk II uses similar coating technology, this would explain why Mitakon doesn't brand their coatings. Not directly applicable to Mk II data.
