# Tokina atx-m 56mm f/1.4 X — Specs Log

Backfill for epic #1004 / sub-task #1005. The lens row in `src/data/lenses.ts`
and the artifacts in this folder predate the per-lens specs-log convention;
this file documents the sources checked when those artifacts were originally
collected and confirms the DB fields against the same sources today.

## Sources checked

| Source              | URL                                                   | Date       | Result                                                                                                              |
| ------------------- | ----------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------- |
| Official (Tokina)   | tokinalens.com/product/atx_m_56mm_f1_4_x/             | 2026-06-01 | Authoritative physical specs (10/9, 1 SD, multi-coating, Φ52, 315 g, 65×72 mm, MFD 0.60 m, mag 0.1×); MTF + diagram |
| LensTip             | (not indexed — see Caveats)                           | 2026-06-01 | No dedicated page for the 56mm prime; the 33mm sibling has a review but the 56mm was apparently skipped             |
| Radojuva            | radojuva.com                                          | 2026-06-01 | Not found                                                                                                           |
| DPReview            | dpreview.com                                          | 2026-06-01 | Not listed                                                                                                          |
| Google Image Search | google.com                                            | 2026-06-01 | Construction diagram + MTF chart recovered from the official product page; saved next to this log                   |
| Optical Limits      | opticallimits.com/fujifilm/tokina-atx-m-56mm-f-1-4-x/ | 2026-06-01 | Review source already in `reviewSources`; confirms construction and aperture-blade count                            |

## Findings

DB row matches the official spec page on every field examined. No corrections
applied as part of this backfill.

- **opticalElements / opticalGroups:** 10 / 9 (official)
- **specialElements:** `["1 SD"]` (official)
- **coating:** `["Multi-coating"]` (official; no proprietary coating name)
- **apertureBlades:** 9, circular (official)
- **maxMagnification:** 0.1× (official)
- **filterThread / weight / dimensions:** Φ52 / 315 g / 65×72 mm (official)
- **minFocusDistance:** 600 mm (official)

## Caveats

- LensTip does not have an indexed page for the Tokina atx-m 56mm f/1.4 X
  (the 33mm sibling at id 634 is reviewed, but the 56mm appears to have been
  skipped). Optical Limits' Fujifilm review is the primary independent source
  and is already in `reviewSources`.
- The MTF chart and construction diagram in this folder come from the
  official product page. The plot box for the MTF chart was set by hand in
  `tools/mtfdigitizer/referenceset/charts.py` and verified against the
  digitization log.
