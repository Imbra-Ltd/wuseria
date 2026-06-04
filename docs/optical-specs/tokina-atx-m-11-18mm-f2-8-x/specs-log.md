# Tokina atx-m 11-18mm f/2.8 X — Specs Log

Backfill for epic #1004 / sub-task #1005. The lens row in `src/data/lenses.ts`
and the artifacts in this folder predate the per-lens specs-log convention;
this file documents the sources checked when those artifacts were originally
collected and confirms the DB fields against the same sources today.

## Sources checked

| Source              | URL                                                                | Date       | Result                                                                                                                                                           |
| ------------------- | ------------------------------------------------------------------ | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Official (Tokina)   | tokinalens.com/product/atx_m_11_18mm_f2_8_x/                       | 2026-06-01 | Authoritative physical specs (13/11, 2 aspherical + 2 SD, multi-coating, Φ67, 320 g, 74×75 mm, MFD 0.19 m, mag 0.11×); MTF (two panels: 11mm and 18mm) + diagram |
| LensTip             | (not indexed — see Caveats)                                        | 2026-06-01 | No dedicated page for the 11-18mm zoom found                                                                                                                     |
| Radojuva            | radojuva.com                                                       | 2026-06-01 | Not found                                                                                                                                                        |
| DPReview            | dpreview.com                                                       | 2026-06-01 | Not listed                                                                                                                                                       |
| Google Image Search | google.com                                                         | 2026-06-01 | Construction diagram + both MTF panels recovered from the official product page; saved next to this log                                                          |
| Dustin Abbott       | dustinabbott.net/2025/02/tokina-atx-m-11-18mm-f2-8-x-mount-review/ | 2026-06-01 | Review source already in `reviewSources`; field measurements                                                                                                     |

## Findings

DB row matches the official spec page on every field examined. No corrections
applied as part of this backfill.

- **opticalElements / opticalGroups:** 13 / 11 (official)
- **specialElements:** `["2 aspherical", "2 SD"]` (official)
- **coating:** `["Multi-coating"]` (official; no proprietary coating name)
- **apertureBlades:** 9, circular (official)
- **maxMagnification:** 0.11× (official)
- **filterThread / weight / dimensions:** Φ67 / 320 g / 74×75 mm (official)
- **minFocusDistance:** 190 mm (official)

## Caveats

- The official product page publishes **two** MTF panels — one at the 11mm
  wide end and one at the 18mm long end. Both are stored here as
  `*-mtf-11mm.png` and `*-mtf-18mm.png` (renamed S119 per ADR-033). The
  digitizer treats each as a separate reference chart
  (`tokina-atx-m-11-18mm-f2-8-x-at-11mm` and
  `tokina-atx-m-11-18mm-f2-8-x-at-18mm` in `referenceset/charts.py`).
- The plot box for each panel was set by hand and verified against the
  printed gridlines (extrapolated one 155-px step above the 80% gridline
  to place y_top at the true MTF=100% line — see digitization-log.md).
- LensTip does not have an indexed page for this lens. Dustin Abbott's
  hands-on review (2025-02) is the primary independent source and is
  already in `reviewSources`.
