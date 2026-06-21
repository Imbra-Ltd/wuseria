# ADR-063: Samyang multi-panel per-view aperture

**Status:** Accepted
**Date:** 2026-06-21

## Context

Samyang publishes one chart image per lens containing **two stacked
panels** — MAX aperture on top, F8 on the bottom — sharing the same
x-axis (image-height in mm) and the same legend. Each panel is a
complete `{10S, 10M, 30S, 30M}` rendering at its own f-stop. The two
panels have identical templates: x range `31..461`, top panel `y
43..463`, bottom panel `y 575..995` (both 421 px tall), confirmed
by axis-line probe on the 85mm and 300mm reflex Tier 1 anchors.

ADR-044 already added a `multi-aperture-per-chart` orchestrator path
for TTartisan, where two apertures sit in **one panel encoded by
color** (black/grey = max, red/orange = stopped). That mechanism is
hue-filtered and driven by `MtfProfile.apertures_per_chart`: one
`extract_chart` pass per declared aperture, with profile hues
filtered to that aperture's color bucket. It does not fit Samyang:
both Samyang panels use the same four hue ranges (`10S-red`,
`10M-pink`, `30S-dark-grey`, `30M-light-grey`), only the plot box
differs.

Before this ADR, the 85mm and 300mm reflex Tier 1 anchors carried
only the MAX panel (the issue notes called the F8 panel "deferred"),
the eye-read `_SAMYANG_85_GT` had a single `"MAX"` key, and the 18
Tier 2 Samyangs (#1238 follow-up to #792) could only ship MAX-panel
readings — half the data each chart publishes.

The straight read of the existing `ChartView` zoom mechanism (ADR-033)
suggests a second view with a second plot_box. But the existing pass
resolver `aperture_passes_for_view(chart, image_path)` keys on
`image_path` (which is the SAME PNG for both Samyang panels) and
on the profile (`apertures_per_chart=None` for Samyang, so it falls
through to the single-pass default that labels with
`chart.apertures[0]`). There is no plumbing to tell the orchestrator
that this particular view should emit at a different aperture label.

## Decision

Add a per-view `aperture` override that:

- lives on `ChartView` (`aperture: str | None = None`) — the panel
  selector (`plot_box`) and the panel's aperture identity travel
  together
- is honored by `aperture_passes_for_view(chart, image_path, view)`
  — when set, returns a single pass labelled with `view.aperture`,
  short-circuiting both the Fujifilm per-frequency branch and the
  ADR-044 hue-filtered fan-out
- is honored by the calibration runner via a new
  `_extract_per_view_aperture_chart` path that walks `chart.views`
  and produces the same `{aperture_label: ExtractedChart}` shape as
  ADR-044's `_extract_multi_aperture_chart`
- composes with `chart.additional_views` — the primary view stays
  `aperture=None` (the chart's first aperture in `chart.apertures`
  by default), each additional view declares its own override

```
+---------------------+      +-----------------------+
|  MAX aperture       |      |  primary ChartView    |
|  (top panel)        | <--- |  plot_box=(43..463)   |
|  y 43..463          |      |  aperture=None        |
+---------------------+      +-----------------------+
+---------------------+      +-----------------------+
|  F8                 |      |  additional ChartView |
|  (bottom panel)     | <--- |  plot_box=(575..995)  |
|  y 575..995         |      |  aperture="F8"        |
+---------------------+      +-----------------------+
       shared PNG                shared style family
```

The orchestrator (`extract.py::_run_view_passes`) already walks every
view; the only change is threading `view` into the resolver call.
Legacy callers (`autotriage`, `diagnose`, `log`, `review`, `svg`) keep
the two-arg form and operate on the primary chart raster — they
predate multi-view orchestration and only handle Tier 1 calibration
paths.

The mechanism is orthogonal to ADR-044's hue-filtered fan-out:

| Mechanism               | Plot box | Hue partition | Driver                      |
| ----------------------- | -------- | ------------- | --------------------------- |
| ADR-044 hue-filtered    | 1        | per aperture  | profile.apertures_per_chart |
| ADR-063 per-view (this) | N        | shared        | view.aperture               |

A profile could in principle declare both, but no shipped profile
does today.

## Alternatives considered

1. **Add Samyang to `apertures_per_chart`** with a `MAX-`/`F8-` hue
   prefix scheme. Rejected: the two panels share hue bands, so the
   filter would empty one aperture's mask entirely. The hue-filter
   mechanism assumes per-aperture color encoding inside one plot box.

2. **Encode the panel choice in the image_path** (e.g. crop the PNG
   into two separate files, one per panel). Rejected: doubles the
   stored artifacts for no orchestrator benefit, and the source-of-
   truth PNG is the single two-panel image Samyang publishes.

3. **Match per-view aperture by `image_path` in the resolver**.
   Rejected: both Samyang panels share the same `chart_path`, so the
   path alone cannot disambiguate. A plot_box-based key would work
   structurally but the per-view aperture is metadata, not a derived
   property — keep it explicit on the view.

4. **Bolt the aperture onto `PlotBoxCoords`**. Rejected: aperture is
   an orchestrator concern (which pass label this panel emits at),
   not a coordinate.

## Consequences

### Positive

- 85mm Tier 1 anchor gains F8 panel calibration: `freq30S` p95 |d|
  reads as **0.228** (the two known dropouts where dark grey 30S
  sits one pixel below pink 10M and gets eaten by the 10S->10M halo
  subtraction); the other three F8 fields are within 0.055.
- 300mm reflex Tier 1 anchor gains F8 panel calibration (idealized-
  flat: every curve at 1.0 across both panels). All F8 deltas
  within 0.016.
- Aggregate calibration p95 |d| improves **0.0466 -> 0.0463**,
  in-band 95.9% -> 96.0%. Paired comparisons grow **810 -> 872**
  (the extra 62 are the new F8 panel cells: 2 anchors x 4 fields
  x ~8 paired fractions).
- Unblocks #1238's scaffolder step (`scaffold_samyang_tier2.py`):
  18 Tier 2 Samyangs can now declare `additional_views=(ChartView(
..., aperture="F8"),)` and the orchestrator emits per-aperture
  artifacts and digitization-log panels per ADR-041.
- Foundation for any future "multi-panel single-PNG" chart family
  (Sigma's stopped-down variants, Voigtlander APO-LANTHAR pairs)
  without touching the hue-filter mechanism.

### Negative / accepted tradeoff

- Two pass-resolution paths share the orchestrator (`apertures_per_chart`
  hue-filter from ADR-044 and `view.aperture` from this ADR). They
  are routed in `_calibrate_chart` by an `if-elif` and could be
  unified into a single "fan-out spec" if a future profile needs
  both, but no shipped profile does today (YAGNI).
- The two dropouts on 85mm freq30S F8 (p95 0.228) reflect a known
  limitation of the ADR-059 / ADR-062 halo-subtraction pipeline when
  the contaminator (10S-red) and the contaminated (10M-pink) sit
  within a few pixels of the orthogonal-hue 30S-dark-grey curve. The
  ring-subtraction mask radius spills onto the dark-grey curve at
  exactly those two cells. Tracked as a follow-up; out of scope here.
- `ChartView` now has a field that only Samyang uses (and the 18
  Tier 2 entries the scaffolder will emit). Acceptable: the field
  defaults to None so every existing entry stays unchanged.

### Scope this ADR does NOT cover

- The scaffolder `tools/mtfdigitizer/scripts/scaffold_samyang_tier2.py`
  that walks the 18 Tier 2 Samyang folders, auto-detects both panel
  plot boxes per chart, and emits `_samyang_tier2_charts.py` with
  per-lens `(max, F8)` aperture tables. Tracked under #1238's
  remaining acceptance criteria.
- Per-lens max aperture eye-read table (parallel to TTartisan's
  `_APERTURES_BY_SLUG`). The stopped aperture is universally `"F8"`
  per S170 user confirmation; max is the lens's wide-open f-number.
  Maintainer eye-read deferred to the scaffolder PR.
- A redesign of the render-match precision metric to credit sister-
  filled cells (ADR-062 §Consequences notes this as a known
  limitation).
