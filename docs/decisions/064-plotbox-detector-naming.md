# ADR-064: Cross-brand plot-box detector naming convention

**Status:** Accepted
**Date:** 2026-06-21

## Context

The mtfdigitizer ships one plot-box detector per brand whose chart
layout warrants auto-detection: `fuji_plotbox.py`, `ttartisan_plotbox.py`,
`samyang_plotbox.py`. They share a contract — given a chart PNG,
return the plot-box coordinates the downstream extractor needs — but
the surface names drifted as each brand was added incrementally
(Fuji: S140s; TTartisan: S160s; Samyang: S171 / ADR-063):

| Field       | Fuji            | TTartisan             | Samyang               |
| ----------- | --------------- | --------------------- | --------------------- |
| result type | `FujiBoxResult` | `TTartisanBoxResult`  | `SamyangBoxes`        |
| primary box | `plot_box`      | `plot_box`            | `max_box`             |
| extra box   | n/a             | n/a                   | `f8_box`              |
| error class | (raises inline) | (raises `ValueError`) | `SamyangPlotBoxError` |

The Samyang names are accurate for _today's_ Samyang chart family
(MAX panel + F8 panel), but two problems are visible right now:

1. **Cross-brand cognitive cost.** A reader bouncing between
   `scaffold_*_tier2.py` files sees `c.boxes.max_box` in one and
   `c.detected.plot_box` in the next. The shared concept ("the
   primary plot box this detector found") has two different names.

2. **F8 is hardcoded in a field name.** If Samyang ever publishes
   a chart whose second panel is anything other than F8 (the brand's
   AF zooms already mix conventions on other axes), `f8_box` becomes
   a lie. The detector does not — and cannot — know the panel's
   aperture: it only knows there is a top panel and a bottom panel.
   The aperture label travels via the scaffolder, not the detector
   (see ADR-063: `additional_views=(ChartView(..., aperture="F8"),)`
   is constructed in the scaffolder).

Formalizing now is cheap (3 files touched, no behavior change). Next
brand that lands picks up the convention for free.

## Decision

A plot-box detector module MUST follow this naming convention:

```
+-----------------------------------------------------------+
|  <brand>_plotbox.py                                        |
|                                                            |
|    detect_<brand>_plotbox(path) -> <Brand>BoxResult        |
|                                                            |
|    @dataclass(frozen=True)                                 |
|    class <Brand>BoxResult:                                 |
|        plot_box: tuple[int, int, int, int]   # primary    |
|        # ...brand-specific extras: secondary boxes,        |
|        #    image_height_mm, scheme, notes, etc.           |
|                                                            |
|    class <Brand>PlotBoxError(RuntimeError):                |
|        """Raised when detection fails."""                  |
+-----------------------------------------------------------+
```

Concrete rules:

1. **Module name** — `<brand>_plotbox.py`.
2. **Entry point** — `detect_<brand>_plotbox(chart_path: Path)`.
3. **Result type** — `<Brand>BoxResult` (dataclass, frozen). The
   _primary_ box field MUST be named `plot_box` regardless of
   how many panels the chart contains. Brands with multiple
   panels MAY add additional box fields, but those fields MUST
   NOT bake an aperture f-number into the name. Use semantic
   names tied to the _role_ of the panel
   (`stopped_box`, `secondary_box`), not the f-stop value
   (`f8_box`, `f11_box`). The aperture label is the scaffolder's
   responsibility.
4. **Error type** — `<Brand>PlotBoxError`, subclass of
   `RuntimeError`. Detectors MUST raise this class on detection
   failure, not bare `ValueError`. Loud, named failures help the
   maintainer identify which chart broke detection.

## Alternatives considered

**Status quo (keep brand-specific names).** Cheap today, expensive
on every onboarding and on every new brand. The cross-brand
mental switching cost compounds as the digitizer grows; we already
have a third brand and a fourth (Tokina, per the open epic) is in
flight.

**Introduce a shared `BasePlotBoxResult` Protocol.** Stronger
guarantee than convention, but premature. The result dataclasses
have wildly different optional fields (Fuji has `px_per_mm` and
`tick_count`; TTartisan has `scheme`; Samyang has `image_size`)
and no scaffolder treats them polymorphically — each scaffolder
imports its detector by name. Defer until a 4th brand or a shared
consumer (e.g. a diagnostic walker) makes the abstraction pay.

**Rename to `panel_box` instead of `plot_box`.** Closer to the
multi-panel reality but breaks Fuji and TTartisan (which are
single-panel). `plot_box` is the existing convention in 2/3
modules; align the third.

## Consequences

- `SamyangBoxes` -> `SamyangBoxResult` (matches Fuji/TTartisan).
- `SamyangBoxes.max_box` -> `SamyangBoxResult.plot_box`.
- `SamyangBoxes.f8_box` -> `SamyangBoxResult.stopped_box` — name
  describes the panel's role (stopped down from MAX), not its
  f-stop. F8 is still emitted by the scaffolder via
  `additional_views=(ChartView(..., aperture="F8"),)` per ADR-063;
  that path is unchanged.
- `SamyangBoxes.image_size` retained — unique to Samyang and used
  nowhere downstream yet, but a cheap diagnostic value to keep.
- New `TTartisanPlotBoxError(RuntimeError)`; the detector raises
  it instead of bare `ValueError`.
- `scaffold_samyang_tier2.py` updates to `c.boxes.plot_box` /
  `c.boxes.stopped_box` and re-runs cleanly with `--write` to
  regenerate `_samyang_tier2_charts.py` byte-identical (only
  the underlying field names change; emitted literals stay the
  same because the scaffolder formats `PlotBoxCoords(...)`).
- Future brand detectors (Tokina next per epic #790) follow the
  convention from day one — no rename PR.
- Fuji is already conformant (`FujiBoxResult.plot_box`); only its
  error path is non-conformant (no custom error class). Out of
  scope for this PR — Fuji has not had a detection-failure mode
  worth catching specifically. Add when the need arises.
