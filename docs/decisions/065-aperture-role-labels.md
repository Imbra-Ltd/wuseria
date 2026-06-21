# ADR-065: Code-level aperture labels use brand-agnostic role names

**Status:** Accepted
**Date:** 2026-06-21

## Context

The MTF digitizer carries two layers of aperture identifiers:

1. **Code-level label** — used inside the extractor pipeline,
   ground-truth dicts, emitted artifact filenames, log section
   headings, and `ReferenceChart.apertures` / `ChartView.aperture`.
2. **Display label** — the f-stop literal shown to humans on the
   lens detail page, sourced from `src/data/mtf-readings.ts`
   (`aperture: "f/2.8"`).

TTartisan and Samyang diverged on layer 1 as each brand landed:

| Brand     | `ReferenceChart.apertures` | `ChartView.aperture` | Filenames         | Log heading         |
| --------- | -------------------------- | -------------------- | ----------------- | ------------------- |
| TTartisan | `("f/2.8", "f/8")` \*      | n/a                  | `-max` `-stopped` | `Aperture max`      |
| Samyang   | `("MAX", "F8")`            | `"F8"`               | `` `-F8`          | `Aperture MAX`/`F8` |

\* TTartisan's emitted filenames come from `profile.apertures_per_chart=
("max", "stopped")` (see `profiles/declared.py`), not from
`chart.apertures`. The `chart.apertures` f-stop literals are read by
`emit_ttartisan_tier2.py` and land in `mtf-readings.ts` as the _display_
label only. The orchestrator never sees them.

The Samyang convention bakes f-stop literals into code-level labels,
which causes:

1. **Cross-brand filename inconsistency.** A script that wants "the
   wide-open SVG for any brand" must special-case Samyang
   (`*-mtf.svg`, no suffix) vs TTartisan (`*-mtf-max.svg`). The
   primary panel has no consistent slug.
2. **Brittle to new f-stops.** If Samyang ever publishes a chart
   whose second panel is anything other than F8, every `"F8"`
   literal in `_samyang_tier2_charts.py` + `_SAMYANG_*_GT` becomes
   wrong. The data type ("the stopped-down panel") is stable; the
   f-stop value is not.
3. **Two label vocabularies for one concept.** A reader scanning
   pipeline code sees `"max"` in one place and `"MAX"` in another;
   `"stopped"` in one place and `"F8"` in another. Both refer to
   the same role.

ADR-064 formalized detector naming. This ADR completes the
cross-brand naming pass by formalizing aperture labels.

## Decision

**Code-level aperture labels MUST be brand-agnostic role names.**
The vocabulary is closed:

| Role label    | Meaning                                                                           |
| ------------- | --------------------------------------------------------------------------------- |
| `"max"`       | Wide-open / fastest aperture published                                            |
| `"stopped"`   | Single stopped-down panel published                                               |
| `"stopped-N"` | Multiple stopped-down panels — N is the index (1-based), only used when 3+ panels |

Rules:

1. `ReferenceChart.apertures` MUST hold role labels, in panel order
   matching `views` (primary first, then `additional_views`).
2. `ChartView.aperture` MUST hold a role label when set.
3. `MtfProfile.apertures_per_chart` MUST hold role labels (already
   true for TTartisan).
4. Ground-truth dict keys (`_SAMYANG_*_GT`, future analogs) MUST
   use role labels.
5. The display label (f-stop literal like `"f/2.8"`) lives ONLY in:
   - `src/data/mtf-readings.ts` (hand-curated, or emitted from a
     per-lens display table in the brand's emit script)
   - The brand scaffolder's display table (e.g. TTartisan's
     `_APERTURES_BY_SLUG = {slug: ("f/2.8", "f/8")}`), used when
     an emitter needs to translate role → f-stop for `mtf-readings.ts`
6. Emitted artifact filename slugs derive from role labels — the
   primary panel is `*-mtf-max.{svg,png,html}`, the stopped panel
   is `*-mtf-stopped.{svg,png,html}`, etc. No `*-mtf.svg` (suffixless)
   primary, no f-stop literals in any filename.
7. Production log section headings use role labels verbatim
   (`Aperture max`, `Aperture stopped`) — readers cross-reference
   the f-stop via `mtf-readings.ts` or the scaffolder's display
   table. Out of scope: showing the f-stop in the log heading
   (would need a per-brand display table on every log render).

```
+-------------------------------------------------------------+
|  ReferenceChart.apertures = ("max", "stopped")              |
|  ChartView.aperture       = "stopped"                       |
|     |                                                       |
|     v   (orchestrator uses role labels as panel identifiers)|
|  emit_<brand>_tier2.py                                      |
|     |                                                       |
|     |  scaffolder table:                                    |
|     |    _APERTURES_BY_SLUG = {slug: ("f/2.8", "f/8")}      |
|     |       (role tuple position -> f-stop display string)  |
|     v                                                       |
|  src/data/mtf-readings.ts                                   |
|     aperture: "f/2.8"   <-- display label only here         |
+-------------------------------------------------------------+
```

## Alternatives considered

**Keep brand-specific labels (status quo).** Each new brand picks
its own vocabulary; the divergence compounds. Cost of consolidation
grows with every brand added.

**Use f-stop literals everywhere.** Makes the code-level label
informative without a display table lookup. Rejected: brittle to
brand variation (some Samyang charts could legitimately publish at
F11 or F5.6 in the second panel without warning), forces every
ground-truth dict and test fixture to know each lens's actual
f-stops, and breaks the existing TTartisan convention.

**Encode the f-stop on `ChartView`.** Add `ChartView.aperture_label`
alongside `ChartView.aperture` so the role drives orchestration and
the literal drives display. Rejected: doubles the field count for
no orchestrator benefit; the display layer is already separate
(`mtf-readings.ts`).

**Show f-stop in the production log heading.** "Aperture f/2.8 (max)"
instead of "Aperture max". Better information density for readers,
but requires every log render to look up the display label from the
brand's scaffolder table. Out of scope here — if added later, do it
as a separate change that touches both brands' renderers uniformly.

## Consequences

### In this PR (code-only)

- `_SAMYANG_85_GT` / `_SAMYANG_300_GT` keys: `"MAX"` -> `"max"`,
  `"F8"` -> `"stopped"`.
- Samyang Tier 1 anchors (85mm, 300mm reflex) in `charts.py`:
  `apertures=("MAX", "F8")` -> `("max", "stopped")`;
  `ChartView.aperture="F8"` -> `"stopped"`.
- `scaffold_samyang_tier2.py`: emit `("max", "stopped")` /
  `aperture="stopped"`. Re-run with `--write` to regenerate
  `_samyang_tier2_charts.py`.
- Tests that hardcode `"MAX"` / `"F8"` literals updated to
  `"max"` / `"stopped"`.
- Existing on-disk artifacts (`samyang-*-mtf.{svg,png,html}` and
  `samyang-*-mtf-F8.{svg,png,html}`) go stale — they are not
  renamed in this PR. The production log freshness check
  (`py -m mtfdigitizer.extract --check`) will flag the Samyang
  digitization-log.md files (the `## Panel — MAX` / `## Panel — F8`
  headings no longer match the regenerated `## Panel — max` /
  `## Panel — stopped`); the next PR performs the disk migration
  and log regen together.

### Follow-up PR (disk migration)

- 60 `samyang-*-mtf.{svg,png,html}` files renamed to add `-max`
  suffix (20 lenses x 3 file types).
- 54 `samyang-*-mtf-F8.{svg,png,html}` files renamed to use
  `-stopped` suffix (18 Tier 2 lenses x 3 file types).
- All 20 `digitization-log.md` files regenerated to pick up
  the new role-label headings.
- `mtf-readings.ts` Samyang entries are NOT touched — they
  already carry display labels (`f/2.8`, `f/8`) per ADR-065 §5.

### Future brands

- Any new brand with multi-panel charts uses role labels from
  day one — Tokina (epic #790) is next.
- A brand with single-panel multi-aperture charts (the TTartisan
  pattern) declares `profile.apertures_per_chart=("max", "stopped")`;
  the orchestrator fans out one pass per role.
- A brand with stacked panels (the Samyang pattern) uses per-view
  aperture override (ADR-063) with role labels:
  `ChartView(..., aperture="stopped")`.

### Fuji

- Fuji is single-aperture per chart (per-frequency rasters) and
  uses `chart.apertures=("f/2.8",)` style f-stop literals today.
  That is a different idiom (literal IS the role since there's
  only one) and is out of scope here. If Fuji ever publishes a
  multi-aperture chart family, migrate then.
