# ADR-044: Multi-aperture per-chart orchestrator

**Status:** Accepted
**Date:** 2026-06-07

## Context

The MTF digitizer's orchestrator (ADR-038, ADR-041) and its
per-frequency extension for Fujifilm (ADR-043) both assume each chart
image carries data for exactly **one aperture**. The aperture lives on
the `ReferenceChart.apertures` tuple (a one-element tuple for every
profile shipped before this ADR) and is treated as metadata on the lens
record, not as a per-pixel signal the extractor needs to disambiguate.

Every declared profile to date honors that assumption:

- Sigma, Samyang, 7Artisans, Tokina, Viltrox publish one chart image
  per lens at maximum aperture only — the chart contains the four
  curves `{10S, 10M, 30S, 30M}` and nothing else.
- Fujifilm publishes one chart image per spatial frequency at
  maximum aperture only — three or six images per lens, all at the
  same f-stop. ADR-043's multipath orchestrator fans out over images
  but each image is still single-aperture.

TTartisan breaks the assumption. Their MTF publication convention is
**one chart image per lens, with two apertures packed into the same
panel by color encoding**:

- **Black curves** (low V, near-zero S): 10 lp/mm at **maximum** aperture
- **Grey curves** (mid V, near-zero S): 30 lp/mm at **maximum** aperture
- **Red curves** (saturated, hue ≈ 1 in OpenCV's 0–179 range): 10 lp/mm
  at a **stopped** aperture (f/5.6 / f/8 / f/11 depending on the lens)
- **Orange curves** (saturated, hue ≈ 17): 30 lp/mm at the same
  stopped aperture

Per color, the solid line is the sagittal (S) curve and the dashed line
is the tangential (T) curve, mirroring the Sigma convention. Eight
curves total per chart: four colors × two line styles.

The legend on the right names every curve with its aperture, e.g.
`S10_F1.2`, `T10_F5.6`, `S30_Fmax`, `T30_F11`. The stopped aperture
varies per lens — the legend always carries the actual f-number; the
slug encodes the lens's max aperture only.

The survey of all 19 TTartisan charts in `docs/optical-specs/ttartisan-*`
confirms the convention is consistent across the brand (prime, macro,
fisheye, tilt, AF). The two-aperture-per-chart packing is the brand's
publication standard, not a one-off.

### Why the existing orchestrator does not fit

The single-aperture assumption is baked into the dispatch helper:

```python
def _profile_for_view(chart, image_path) -> MtfProfile:
    base = profile_for_chart(chart)
    if chart.style_family in _FUJI_STYLE_FAMILIES:
        freq = _parse_filename_frequency(image_path)
        return dataclasses.replace(base, frequencies_lpmm=(freq,))
    return base
```

`_profile_for_view` returns one profile per view. `_run_view` runs the
extractor once on that profile. `_run_all_views` produces one
`ExtractRun` per declared view, period.

Two paths considered to accommodate TTartisan-style charts:

1. **Skip the stopped aperture.** Declare the TTartisan profile with
   only the black + grey hues; emit max-aperture readings only and
   discard 50% of the published data. Rejected — same shape as the
   "treat Fujifilm as a Sigma chart with two frequencies dropped"
   alternative rejected in ADR-042. We ship every published curve or
   we don't ship the brand.
2. **Synthesize two virtual `ChartView` objects per chart image, each
   tagged with its aperture.** Rejected on structural grounds: a
   `ChartView` already declares `chart_path` + `plot_box`. Two views
   pointing at the same image with different aperture metadata would
   require either (a) extending `ChartView` with an aperture field
   (touches every reference-set entry, every CLI that walks views) or
   (b) tagging the same view differently on each iteration (mutates a
   frozen dataclass conceptually). Neither is clean.

The fix is to introduce a third dispatch path at the same layer as
Fuji's per-frequency substitution: per-aperture fan-out at
`_aperture_passes_for_view`.

## Decision

### A new profile field: `apertures_per_chart`

`MtfProfile` gains an optional field:

```python
@dataclass(frozen=True)
class MtfProfile:
    ...
    apertures_per_chart: tuple[str, ...] | None = None
```

- **None** (default) means the profile follows the single-aperture
  convention. Every existing profile keeps the default — no behavior
  change for Sigma, Samyang, 7Artisans, Tokina, Viltrox, Fujifilm.
- **A tuple of aperture labels** declares that the chart image packs N
  apertures by color encoding. The orchestrator runs the extractor
  once per aperture in this tuple, each time with the profile's
  `hues` filtered to the aperture's bucket.

The labels are opaque strings used as a name prefix on `HueRange.name`
entries (see "Hue naming convention" below). The orchestrator treats
them as identifiers, not as f-numbers — the actual numeric f-stop
lives on the parent `ReferenceChart.apertures`, in the same positions
as `apertures_per_chart`.

### Hue naming convention

Profiles with `apertures_per_chart=("a", "b", ...)` MUST name every
`HueRange` with a prefix matching one of the declared apertures plus a
hyphen. The orchestrator's filter:

```python
def _hue_filtered_profile(profile, aperture) -> MtfProfile:
    filtered = tuple(h for h in profile.hues if h.name.startswith(f"{aperture}-"))
    return dataclasses.replace(profile, hues=filtered)
```

A hue whose name does not match any aperture prefix is silently
dropped across all passes — by design, so a typo fails loud at
extraction time (the extractor sees a profile with zero hues and
refuses).

### Orchestrator change: `_aperture_passes_for_view`

The single-aperture `_profile_for_view` helper becomes the
multi-aperture fan-out `_aperture_passes_for_view`:

```python
def _aperture_passes_for_view(
    chart: ReferenceChart, image_path: Path
) -> list[tuple[str, MtfProfile]]:
    base = profile_for_chart(chart)
    if chart.style_family in _FUJI_STYLE_FAMILIES:
        freq = _parse_filename_frequency(image_path)
        substituted = dataclasses.replace(base, frequencies_lpmm=(freq,))
        return [(chart.apertures[0], substituted)]
    if base.apertures_per_chart is not None:
        return [
            (ap, _hue_filtered_profile(base, ap)) for ap in base.apertures_per_chart
        ]
    return [(chart.apertures[0] if chart.apertures else "", base)]
```

`_profile_for_view` survives as a thin back-compat shim returning the
first pass's profile, so existing callers (and tests) that predate the
fan-out keep working without modification.

`_run_view` becomes `_run_view_passes` returning `list[ExtractRun]`
(one per pass). `_run_all_views` flattens.

### A new field on `ExtractRun`: `aperture`

```python
@dataclass(frozen=True)
class ExtractRun:
    ...
    aperture: str = ""
```

The default empty string preserves back-compat for callers that
construct `ExtractRun` without populating the field (mostly tests).
Production paths through `_run_view_passes` always populate it.

The downstream `ProductionPanel` does NOT grow an aperture field —
the aperture label flows from the orchestrator to the log renderer
through the surrounding `ExtractRun` list, not through the panel
dataclass. This keeps the panel shape stable for existing single-
aperture brands.

### What this ADR does NOT do

- Does NOT declare the TTartisan profile. That lands in a follow-up PR
  (and a follow-up ADR if the profile's dispatch needs anything beyond
  what the four declared `hue_meaning` dispatch paths already cover).
- Does NOT change the schema for `ReferenceChart`, `ChartView`,
  `ProductionPanel`, or any pipeline type.
- Does NOT modify the existing five declared profiles or the
  Fujifilm profile. They retain `apertures_per_chart=None` and route
  through the unchanged single-pass path.
- Does NOT modify the `mtf-readings.ts` data shape. The emit pipeline
  for a multi-aperture brand will produce one TS object literal per
  aperture pass per lens, mirroring the way Fuji emits one panel per
  frequency-aware view; the shape on disk is unchanged.

## Alternatives considered

| Alternative                                                                 | Why rejected                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Extend `ChartView` with an `aperture` field; synthesize two views per chart | Same image, different metadata per view. Forces every existing reference-set entry to declare `aperture=None` (or get migrated). Forces every CLI that walks `chart.views` to handle the new field. The fan-out at orchestrator level is more localized — only `extract.py` and the new profile field change.                                                                                                                                                                                                                                    |
| Extend the schema on `ReferenceChart` with `apertures_per_chart`            | Same fan-out logic, declared on the chart instead of the profile. Rejected because the rule is structural to the chart STYLE (every TTartisan chart packs two apertures) rather than to individual lenses. Putting it on the profile means TTartisan declares it once and every TTartisan `ReferenceChart` inherits the behavior.                                                                                                                                                                                                                |
| Skip the stopped aperture; emit max-aperture data only                      | Discards 50% of TTartisan's published data. Same shape as ADR-042's rejected "drop the high frequency" alternative. We ship every published curve or not at all.                                                                                                                                                                                                                                                                                                                                                                                 |
| Composite the chart image into N synthetic images upfront                   | Mask the chart by aperture color bucket, save two synthetic PNGs, feed each to the existing single-pass orchestrator. Rejected as fake input: the synthetic images would carry no maintainer-verifiable provenance and would invalidate the render-match score (which compares against the source PNG). The fan-out happens at the orchestrator, not the image.                                                                                                                                                                                  |
| Declare two profiles for TTartisan and two `ReferenceChart`s per lens       | One ReferenceChart per (lens, aperture), each pointing at the same chart image. Rejected because two charts per lens doubles the entry count in the reference set (~38 TTartisan entries instead of 19) and the slug uniqueness invariant would need an aperture suffix. The orchestrator-level fan-out keeps the reference set as one-row-per-lens.                                                                                                                                                                                             |
| Defer TTartisan; pick a brand that fits the single-aperture convention      | Considered. The session-124 memory's next-brand candidates included TTartisan (19 charts) and Voigtländer (0 charts, MTF policy limits publication to APO-LANTHAR). The other un-anchored brands (#800–#814) were not surveyed for chart packing; some may also pack multiple apertures. Picking a smaller brand defers the architectural work, but the work is genuinely needed because the dual-aperture pattern is not TTartisan-specific (some Sigma Art line chart sheets pack `f/wide` + `f/8` similarly, observed but not yet onboarded). |

## Consequences

- **The orchestrator grows a second fan-out axis.** ADR-043 added
  per-frequency fan-out via Fuji's filename suffix. This ADR adds
  per-aperture fan-out via profile metadata. The two axes are
  independent — a future style family could combine both (per-frequency
  images each packing two apertures by color). The dispatch in
  `_aperture_passes_for_view` handles them as separate branches and
  composing them would be a third branch, not a rewrite.
- **Profile naming convention becomes load-bearing for multi-aperture
  profiles.** `HueRange.name` was historically free-form documentation
  (`"red"`, `"10S-saturated-red"`). For multi-aperture profiles the
  prefix is now a contract the orchestrator parses. Documented in
  `profiles/types.py` and in this ADR.
- **`_profile_for_view` is now a back-compat shim.** It returns the
  first pass's profile, which is correct for single-aperture profiles
  but lossy for multi-aperture ones. New code calls
  `_aperture_passes_for_view` directly. The shim is kept so existing
  tests don't need to migrate; it will be removed in a future cleanup
  PR once those tests are rewritten.
- **`ExtractRun` carries an aperture label.** Downstream consumers
  (the log renderer, the emit pipeline for multi-aperture brands) can
  read it. Existing consumers ignore it — the default empty string is
  benign for them.
- **No PRs ship a multi-aperture profile yet.** This PR ships the
  plumbing only. The TTartisan profile + Tier 1 anchor + Tier 2 bulk
  land in a follow-up PR (#798).
- **Test coverage: 6 new unit tests.** `_hue_filtered_profile`,
  `_aperture_passes_for_view` for standard / Fuji / multi-aperture
  shapes, the back-compat shim, and `ExtractRun.aperture` default.
  All 24 pre-existing extract tests still pass — single-aperture
  regression coverage.
- **Future brand reuse.** Any brand that packs N apertures into one
  chart image by color (TTartisan today; possibly some Sigma Art /
  Tamron product pages tomorrow) declares `apertures_per_chart` and
  registers per-aperture hue prefixes. No further orchestrator work.
