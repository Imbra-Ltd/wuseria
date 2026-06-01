# Tokina atx-m 33mm f/1.4 X — Specs Log

Backfill for epic #1004 / sub-task #1005. The lens row in `src/data/lenses.ts`
and the artifacts in this folder predate the per-lens specs-log convention;
this file documents the sources checked when those artifacts were originally
collected and confirms the DB fields against the same sources today.

## Sources checked

| Source              | URL                                                           | Date       | Result                                                                                                              |
| ------------------- | ------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------- |
| Official (Tokina)   | tokinalens.com/product/atx_m_33mm_f1_4_x/                     | 2026-06-01 | Authoritative physical specs (10/9, 1 SD, multi-coating, Φ52, 285 g, 65×72 mm, MFD 0.40 m, mag 0.1×); MTF + diagram |
| LensTip             | lenstip.com/634.1-Lens_review-Tokina_ATX-M_33_mm_f_1.4_X.html | 2026-06-01 | Full lab review; confirms 10/9, 1 SD, multi-coating, aperture-blade count                                           |
| Radojuva            | radojuva.com                                                  | 2026-06-01 | Not found                                                                                                           |
| DPReview            | dpreview.com                                                  | 2026-06-01 | Not listed                                                                                                          |
| Google Image Search | google.com                                                    | 2026-06-01 | Construction diagram + MTF chart recovered from the official product page; saved next to this log                   |

## Findings

DB row matches the official spec page and the LensTip review on every field
examined. No corrections applied as part of this backfill.

- **opticalElements / opticalGroups:** 10 / 9 (official + LensTip)
- **specialElements:** `["1 SD"]` (official + LensTip)
- **coating:** `["Multi-coating"]` (official; no proprietary coating name)
- **apertureBlades:** 9, circular (official + LensTip)
- **maxMagnification:** 0.1× (official)
- **filterThread / weight / dimensions:** Φ52 / 285 g / 65×72 mm (official + LensTip)
- **minFocusDistance:** 400 mm (official)

## Caveats

- The MTF chart and construction diagram in this folder come from the
  official product page. The plot box for the MTF chart was set by hand in
  `tools/mtfdigitizer/referenceset/charts.py` and verified against the
  digitization log.
- LensTip's review (page id 634, release 2020-12-04) is already linked
  in `reviewSources`; it is the primary independent measurement source
  for this lens.
