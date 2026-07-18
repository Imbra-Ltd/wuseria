# ADR-083: Decompose `pipeline/ridge.py` into a data-flow-staged package

**Status:** Accepted
**Date:** 2026-07-18

## Context

`tools/mtfdigitizer/pipeline/ridge.py` is the extractor's largest module
(2104 lines after #1430/#1433). It holds the entire ridge-tracking
subsystem: mask chrome-stripping, per-column ridge extraction, track
clustering/merging, coincidence handling, the per-column Viterbi DP with
crossing detection, and the two live dispatch entry points. Its size
makes per-brand tuning navigation slow and raises the risk of edits
touching unrelated concerns — the maintainability cost #1414 (ADR-081
fidelity-neutral refactor) targets.

#1414 framed this as "decompose by its four entry points." Only three
public entry points remain — `ridge_tracks_for_hue_freq_split`,
`ridge_tracks_to_fields_multifreq`, and the 2-freq convenience wrapper
`ridge_tracks_to_fields` — because the fourth (`ridge_tracks_for_hue`)
was deleted with the dead PER_COLUMN_RIDGE dialect in #1430. The module's
functions are already ordered by data-flow stage, which is the natural
seam for cohesive modules.

## Decision

Convert `pipeline/ridge.py` into a `pipeline/ridge/` package split by
data-flow stage. Each module imports only earlier stages, so the
dependency graph is acyclic. Granularity favours a small number of
cohesive modules over maximal fragmentation — the tightly-coupled
mask->points->tracks->curves foundation stays together, and the max
module size is dominated by the DP block either way:

```
            types, numpy
                |
          foundation.py          (mask -> points -> Track -> curve:
             /    \                strip/extract, cluster/merge/select,
            /      \               rasterize/densify/coincidence + consts)
          dp.py     \
         /   \       \
     hue.py   \    fields.py      (the three dispatch entry points)
        \       \      /
         +--- __init__.py ---+    (re-exports the public + tested surface)
```

1. `foundation.py` — `Track` dataclass; chrome strip, per-column runs,
   ridge-point extraction and isolation filter; clustering, near-
   duplicate and fragment merges, top-N selection; rasterize, densify,
   edge-extend, coincidence-column fill, y-diverse pick — with the
   run-geometry / chrome / halo / merge / coincidence constants beside
   the functions that use them. The shared base both entry families call.
2. `dp.py` — the `# --- Per-column ridge DP (#1100)` block: DP passes,
   anchors, path→track, crossing detection and swap. Imports foundation.
3. `hue.py` — `ridge_tracks_for_hue_freq_split` (FREQUENCY_PER_HUE_RIDGE).
   Imports foundation + dp.
4. `fields.py` — multifreq band assignment plus
   `ridge_tracks_to_fields_multifreq` / `ridge_tracks_to_fields`
   (RIDGE_TRACKING). Imports foundation.

A finer extract/tracks/curves split can follow later if a module grows;
this first cut prioritises a low cross-import surface for an
output-neutral migration.

`__init__.py` re-exports the public entry points AND the private helpers
that `tests/test_ridge.py` imports directly, so the public import path
`from .pipeline.ridge import X` is unchanged. `dispatch.py` and
`test_ridge.py` are not modified — the unchanged test suite is the
regression oracle for the split, alongside the calibrate zero-delta gate.

Constants travel with the functions that use them (they are already
grouped next to their cluster with provenance comments — see the #1414
sub-task 2 finding), preserving the cohesion that ruled out a central
constant registry.

## Alternatives considered

| Alternative                                                               | Why rejected                                                                                                                                                |
| ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Flat sibling modules (`ridge_dp.py`, etc.) importing back into `ridge.py` | Creates import cycles — the entry points and the stages import each other. A package with a re-exporting `__init__` gives a clean acyclic graph.            |
| Split by symbol type (a `constants.py`, a `types.py`, …)                  | Orphans provenance comments from the code they explain and cuts across the data-flow cohesion; same cohesion loss the sub-task 2 registry was rejected for. |
| Update `test_ridge.py` to import from the new submodules                  | Touches the regression oracle in the same change that restructures the code under test; re-exporting from `__init__` keeps the oracle fixed.                |
| Leave `ridge.py` monolithic                                               | Fails the sub-task; the navigation cost is the thing being paid down.                                                                                       |

## Consequences

| Consequence        | Detail                                                                                                                                                                                                    |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Output-neutral     | No logic changes; verified by `py -m mtfdigitizer.calibrate` byte-identical (zero GT delta) and the unchanged `test_ridge.py`.                                                                            |
| Public API stable  | `from .pipeline.ridge import …` unchanged; `dispatch.py` and `test_ridge.py` untouched.                                                                                                                   |
| Private re-exports | `__init__.py` re-exports the underscore-prefixed helpers `test_ridge.py` imports — a deliberate package-owns-its-tested-surface choice, not a leak.                                                       |
| Navigation         | Per-brand tuning finds the relevant stage by module name — the discoverability the sub-task 2 registry was meant to provide, delivered by cohesive modules instead.                                       |
| Follow-up          | The `ridge.py` unused-import entries in #1431 are absorbed as the code moves; `ridge_tracks_to_fields` (tested, production-unused wrapper) is preserved, not removed, to keep this change output-neutral. |
