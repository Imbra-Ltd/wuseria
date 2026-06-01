# Tokina atx-m 23mm f/1.4 X — Specs Log

Backfill for epic #1004 / sub-task #1005. The lens row in `src/data/lenses.ts`
and the artifacts in this folder (construction diagram, MTF chart, digitization
log) predate the per-lens specs-log convention; this file documents the sources
checked when those artifacts were originally collected and confirms the DB
fields against the same sources today.

## Sources checked

| Source              | URL                                       | Date       | Result                                                                                                               |
| ------------------- | ----------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------- |
| Official (Tokina)   | tokinalens.com/product/atx_m_23mm_f1_4_x/ | 2026-06-01 | Authoritative physical specs (11/10, 2 SD, multi-coating, Φ52, 276 g, 65×72 mm, MFD 0.30 m, mag 0.1×); MTF + diagram |
| LensTip             | (not indexed — see Caveats)               | 2026-06-01 | No dedicated page for the X-mount 23mm prime found                                                                   |
| Radojuva            | radojuva.com                              | 2026-06-01 | Not found                                                                                                            |
| DPReview            | dpreview.com                              | 2026-06-01 | Not listed                                                                                                           |
| Google Image Search | google.com                                | 2026-06-01 | Construction diagram + MTF chart recovered from the official product page; saved next to this log                    |
| Optical Limits      | opticallimits.com/sony/3705/              | 2026-06-01 | Review source already in `reviewSources`; confirms construction and aperture-blade count                             |

## Findings

DB row matches the official spec page on every field examined. No corrections
applied as part of this backfill.

- **opticalElements / opticalGroups:** 11 / 10 (official)
- **specialElements:** `["2 SD"]` (official)
- **coating:** `["Multi-coating"]` (official; no proprietary coating name)
- **apertureBlades:** 9, circular (official)
- **maxMagnification:** 0.1× (official)
- **filterThread / weight / dimensions:** Φ52 / 276 g / 65×72 mm (official)
- **minFocusDistance:** 300 mm (official)

## Caveats

- LensTip does not have an indexed page for the Tokina atx-m 23mm f/1.4 X
  (no entry returned by the LensTip search index nor the brand listing). The
  33mm and 56mm siblings are reviewed there; the 23mm appears to have been
  skipped. Optical Limits' Sony-E review (id 3705) is the closest third-party
  source and is already in `reviewSources`.
- The MTF chart and construction diagram in this folder come from the
  official product page. The plot box for the MTF chart was set by hand in
  `tools/mtfdigitizer/referenceset/charts.py` and verified against the
  digitization log.
