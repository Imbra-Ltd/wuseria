# ADR-033: Per-Lens Optical Specs Folder Structure

**Status:** Accepted
**Date:** 2026-05-20

> **Pending amendment (2026-06-01, tracked in #1015).** ADR-040 introduced
> the generated `digitization-log.md`, which now carries the MTF readings
> tables, center/edge summary, and shape metrics — data the hand-written
> `analysis.md` "Readings" section duplicated in older folders. Before the
> `analysis.md` backfill (#1015) authors new files, this ADR will be amended
> so that, where a `digitization-log.md` exists, `analysis.md` **references**
> the digitized readings rather than re-tabulating them, and its remit
> narrows to the interpretive layer (astigmatism/field-curvature assessment,
> construction-based predictions, the bridge from numbers to OQ scoring
> fields). Do not author new inline-readings `analysis.md` files for lenses
> that already have a digitization-log until this is resolved.

## Context

Each lens in `docs/optical-specs/<slug>/` has accumulated files
organically: construction diagrams, MTF charts, and a `specs-log.md` that
mixes MTF readings, analysis predictions, and operational notes. The
scoring log lives in a separate monolithic file (`docs/scoring-log.md`)
with 200+ entries.

This creates several problems:

- `specs-log.md` conflates analysis (predictions from optical data) with
  operational notes (problems, data issues, provenance)
- The monolithic scoring log produces noisy diffs when scoring one lens
  and is hard to navigate
- No clear convention for what files a lens folder should contain

## Decision

Formalize the per-lens folder structure under `docs/optical-specs/<slug>/`:

```
docs/optical-specs/<slug>/
  <slug>-construction.{png,svg} # required — optical construction diagram
  <slug>-mtf-<variant>.{png,svg} # required — MTF chart images (see naming below)
  analysis.md                   # required — predictions from construction
                                #   parameters and MTF charts (readings,
                                #   astigmatism assessment, quality predictions)
  scoring-log.md                # required when scored — per-lens scoring
                                #   justification (same format as ADR-022)
  specs-log.md                      # required — technical specs provenance log
```

### MTF chart naming and canonical selection

Manufacturers commonly publish more than one MTF chart per lens:

- **Diffraction MTF** — realistic prediction including wave-optics effects
- **Geometrical MTF** — idealized ray-tracing; ignores diffraction and
  overstates performance, especially in the corners and at high
  frequencies
- **Per-focal-length charts** — zooms typically publish wide and tele;
  some publish intermediate focal lengths as well

Numeric suffixes (`-mtf-1`, `-mtf-2`, ...) carry no semantic information —
a reader must open `analysis.md` to know which file is which. New folders
MUST use named suffixes that encode the chart type and (for zooms) the
focal length:

```
<slug>-mtf.{png,svg}                                # single chart, no variants
<slug>-mtf-diffraction.{png,svg}                    # prime, diffraction only
<slug>-mtf-geometric.{png,svg}                      # prime, geometric variant
<slug>-mtf-diffraction-<focal>.{png,svg}            # zoom, e.g. -wide / -tele / -50mm
<slug>-mtf-geometric-<focal>.{png,svg}              # zoom geometric variant
```

`<focal>` is `wide`, `tele`, or an explicit focal length (e.g. `50mm`,
`150mm`) when the manufacturer publishes more than two charts on a zoom.
Use `wide`/`tele` when the manufacturer labels them that way; use the
numeric focal length when intermediate values are published.

**Canonical chart.** When more than one chart is present, the
**diffraction** chart is canonical for digitization, scoring, and any
data-extraction tool (`tools/mtfdigitizer/`). Geometrical charts are
committed for provenance only — they are not digitized and MUST NOT
drive OQ field scores.

**Zoom panels.** For zooms, **every published focal-length panel of
the diffraction chart is canonical** — typically wide MAX + tele MAX,
sometimes an intermediate focal length. Each panel is digitized into
its own `MtfChart` entry in `src/data/mtf-readings.ts` with
`focalLength` set (mm). Both panels are rendered on the lens detail
page. Aggregation for OQ field scoring is defined in ADR-014 (averaged
across panels per position). Superseded prior rule: wide-end-only was
canonical until session 118 — rejected because real zoom data shows
edge sharpness and astigmatism differ materially between wide and tele
in both directions (e.g. Sigma 17-40mm f/1.8 is dramatically sharper at
tele), and wide-only discarded that signal.

**Rationale.** Diffraction MTF is what the optics deliver; geometrical
MTF describes a hypothetical lens without diffraction and is consistently
optimistic. Scoring against the geometrical chart would inflate every
field for the ~20 lenses whose manufacturers publish both.

**Existing folders.** Files committed under the old numeric scheme
(`-mtf-1`, `-mtf-2`, ...) stay as-is until rename — tracked in #1017.
Until that rename lands, `analysis.md` MUST label each numeric file with
its chart type and focal length in the MTF charts list at the top of the
file (current convention already in use).

### Image format

Images in optical-specs folders must be **PNG or SVG**. Source images
downloaded as JPG or WebP must be converted to PNG before committing.
SVG is preferred when the source provides it — vector format preserves
chart text and diagram lines at any scale. PNG is acceptable for raster
sources. No other formats (JPG, WebP, GIF) are allowed.

### File responsibilities

- **analysis.md** — deterministic: given the construction and MTF data,
  what can we predict about optical quality? Contains MTF readings
  tables, astigmatism assessments, and construction-based predictions.
- **scoring-log.md** — justification: why was each optical field scored
  the way it was? Links sources, applies the rubric (ADR-014), records
  the trust level. Same field format as the monolithic scoring log
  defined in ADR-022.
- **specs-log.md** — technical specs provenance: auditable log of all
  research performed to find the lens's technical specifications
  (construction diagrams, MTF charts, element/group counts, coatings,
  special glass types, magnification data). Documents every source
  checked (successful or not), data extraction issues, conflicting
  sources, and lens-specific caveats. Required for every lens folder.
  Note: this is distinct from `scoring-log.md`, which covers optical
  quality field scoring justification (ADR-014 rubric application).

### specs-log.md format

```markdown
# Specs Log — <Model Name>

## Sources checked

| Source        | URL            | Date       | Result                   |
| ------------- | -------------- | ---------- | ------------------------ |
| cosina.co.jp  | https://...    | 2026-05-22 | No MTF chart             |
| LensTip       | (not reviewed) | 2026-05-22 | No data                  |
| Dustin Abbott | https://...    | 2026-05-22 | Full review, MTF + bokeh |

## Optical specs

| Field           | Value                                     | Source                        |
| --------------- | ----------------------------------------- | ----------------------------- |
| opticalElements | 7                                         | Official, Pergear             |
| opticalGroups   | 5                                         | Official, Pergear             |
| specialElements | ["3 low-dispersion", "1 high-refractive"] | Official construction diagram |
| coating         | "Multi-coating"                           | Official product page         |

## Diagrams

- `construction-diagram.png` — source and description
- `mtf-chart.png` — type (polychromatic/monochromatic), frequency range, field positions

## Classification

- Character tier: Tier 1 / Tier 2 / Tier 3 (clinical) / N/A
- Design family: Double Gauss / Sonnar / Retrofocus / etc.

## Caveats

- (e.g. X-mount vs E-mount are different optical designs)
- (e.g. manual PDF checked, no MTF inside)
```

### specs-log.md field rules

The **Sources checked** table is the core — every source checked gets a
row, whether the result was positive or negative. This prevents future
sessions from repeating the same searches and creates a traceable
audit trail for every data point.

The **Optical specs** table fields MUST mirror the database type
(`src/types/lens.ts`):

| specs-log field | DB field          | Type       |
| --------------- | ----------------- | ---------- |
| opticalElements | `opticalElements` | `number`   |
| opticalGroups   | `opticalGroups`   | `number`   |
| specialElements | `specialElements` | `string[]` |
| coating         | `coating`         | `string`   |

Do NOT use `edElements`, `asphericalElements`, or other breakdown
fields — these are subsumed by `specialElements`. The Source column
in the optical specs table provides the provenance for each value
(e.g. "3 low-dispersion per official diagram"). Unknown fields use
`undefined` with a reason (e.g. "Not mentioned by any source").

The **Diagrams** section documents saved images with source and
description. Required when construction diagrams or MTF charts exist.

### Migration

Incremental. New scores go to per-lens `scoring-log.md`. Existing
entries in the monolithic `docs/scoring-log.md` are migrated when
a lens is re-scored or its folder is otherwise touched. The monolith
remains as-is until empty.

### Cross-lens comparison

Cross-lens comparison is the database's job (`src/data/lenses.ts`).
The scoring log's purpose is provenance (justifying why a score was
given), not cross-reference. No index or summary file is needed.

### Rename existing specs-log.md

Existing `specs-log.md` files that contain MTF readings and analysis are
renamed to `analysis.md`. Every lens folder must have a `specs-log.md`
with at minimum a data provenance table.

## Alternatives considered

**Keep monolithic scoring log** — rejected because it produces noisy
diffs, is hard to navigate, and separates scoring justification from
the optical data it references.

**Keep mixed specs-log.md** — rejected because it conflates analysis
(repeatable predictions) with operational notes (one-time issues),
making both harder to maintain.

**Generate a cross-lens summary from per-lens files** — rejected as
unnecessary; `lenses.ts` already serves this role with structured,
queryable data.

## Consequences

- Existing `specs-log.md` files must be renamed to `analysis.md` (can be
  done in bulk)
- New scoring work writes to per-lens `scoring-log.md`
- Tools (`audit.py`) should be updated to check for `analysis.md`
  instead of `specs-log.md`
- The monolithic `docs/scoring-log.md` has been fully migrated and deleted
  (session 73)
