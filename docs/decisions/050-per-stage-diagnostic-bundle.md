# ADR-050: Per-stage diagnostic bundle for the MTF digitizer

**Status:** Accepted
**Date:** 2026-06-10

## Context

The MTF digitizer pipeline has nine identifiable stages — load,
plotbox, hue-masks, dispatch/skeletons, presence-masks, sampling,
sister fallback, center symmetry, emit. Each session from S128 to
S135 followed the same loop: a maintainer flagged a wrong-looking
SVG, an agent spent 30-120 minutes probing each stage in turn until
one of them was identified as the culprit, then a fix patched that
stage. The patches landed; the diagnostic effort that led to them
was thrown away.

The TTartisan triage opened in S135 lists 18 charts with varying
failure descriptions — "30lpmm completely wrong", "edge too low",
"missing segments", "max bad stopped good". None of these
descriptions name a pipeline stage. Without per-stage visibility,
every chart in the list is a 30-120 minute probe session, repeated
18 times, and the same loop will repeat for the next CV-hostile
cohort.

The pipeline already has the ingredients to expose its own state:
each stage produces an artifact (image, mask, skeleton, sample
tuple) that the next stage consumes. We just don't write them
out.

### Approaches ruled out

- **Verbose logging.** Per-stage log lines tell you what the code
  _thinks_ it did, not what it actually produced. The failure
  modes we've hit (frankenstein tracks, fused CCs, dilation echo)
  are visual; text cannot represent them.
- **One mega-overlay per chart.** The existing
  `*-overlay.png` superimposes predicted samples on the source
  chart. It's useful for the final stage but does not show the
  intermediate masks/skeletons — when the overlay is wrong, the
  overlay alone does not tell you whether the dispatch or the
  sampler failed.
- **Commit the diagnostic bundles.** Tempting because PRs would
  carry the visual diff of "this fix changed stage 4's skeleton
  here," but 18+ slugs × ~10 PNGs per chart = 180+ binary
  artifacts in the repo for transient debugging. Decision: keep
  the bundle gitignored, run on demand, regenerate when needed.

## Decision

Add an opt-in **diagnostic bundle** to the digitizer: when
`extract_chart` is called with `diagnostic=True`, it writes one
artifact per pipeline stage to `<slug>/diagnostic/` alongside the
source chart, plus a `manifest.json` capturing scalar state
(profile dispatch path, per-field fallback counts, sample tuples).
The bundle is gitignored. A CLI flag drives it for one chart or
the whole TTartisan cohort.

```
docs/optical-specs/<slug>/
  <slug>-mtf.png                  (source, committed)
  <slug>-mtf-max-overlay.png      (final overlay, committed)
  <slug>-mtf-max.svg              (emit artifact, committed)
  diagnostic/                     (gitignored)
    01-source.png                 raw input
    02-plotbox.png                chart cropped to plot bounds
    03-hue-<name>.png             per-hue raw mask (one PNG per hue)
    04-skeleton-<field>.png       per-field skeleton post-dispatch
    05-presence-<field>.png       per-field presence mask
    06-sampling.png               11 sample columns overlaid on skeleton
    07-fallback.png               diff: pre-fallback vs post-fallback samples
    08-center-symmetry.png        diff: pre-symmetry vs post-symmetry samples
    09-emit.svg                   final emit (same content as committed SVG)
    manifest.json                 dispatch path, fallback counts, sample tuples,
                                  per-stage timing, profile name, plotbox bounds
```

### Stage-to-failure-mode mapping

Each maintainer-flag failure description maps to one or two stages
to inspect first. The bundle's purpose is to make this lookup
trivial:

| Symptom                   | First stage to inspect | Then                                                |
| ------------------------- | ---------------------- | --------------------------------------------------- |
| "missing segments"        | 03 (hue mask)          | 04 (skeleton)                                       |
| "30lpmm completely wrong" | 03 (hue mask)          | 04 (skeleton, freq-split dispatch)                  |
| "edge too low"            | 04 (skeleton)          | 06 (sampling at fraction 1.0)                       |
| "corner crossing swapped" | 04 (skeleton)          | 07 (sister fallback flipped labels)                 |
| "max wrong stopped ok"    | 03 (per-aperture mask) | 04 (skeleton with stopped curves masked out)        |
| "overlay not refreshed"   | 09 (emit)              | provenance only — check committed SVG vs diagnostic |

A maintainer (or agent) reading the bundle should be able to
identify which stage broke from the per-stage PNGs alone, without
re-running probe scripts.

### Diagnostic contract

The diagnostic bundle is part of the digitizer's public surface:

- Every pipeline change MUST keep the bundle producing meaningful
  output. If a stage is restructured, its artifact name and
  semantics may change, but a corresponding artifact MUST exist
  in the new pipeline shape.
- The diagnostic bundle MUST NOT change extraction values. Running
  with `diagnostic=True` produces the same `ExtractedChart` as
  `diagnostic=False`; only side-effect output differs. Anything
  computed for the bundle alone (diff PNGs, manifest entries)
  MUST be derived from the same intermediate state the pipeline
  was already going to compute.
- The bundle MUST be gitignored. Committing diagnostic artifacts
  is the same anti-pattern as committing log files — they go
  stale, bloat the repo, and the right place for them is on
  demand on the developer's machine.

### CLI

A new entry point on `python -m mtfdigitizer`:

```
py -m mtfdigitizer diagnose <slug>           # one chart
py -m mtfdigitizer diagnose --brand ttartisan # whole brand cohort
py -m mtfdigitizer diagnose --all            # whole corpus (slow)
```

Output paths derive from each chart's `optical-specs/<slug>/`
location, writing into `<slug>/diagnostic/`. Re-running overwrites
previous bundles in place (idempotent).

### Tuning

- Image artifacts are PNG (lossless, ~50-200 KB per chart total
  bundle — fine for on-disk).
- Skeleton PNGs are rendered as the skeleton overlaid on a
  faded copy of the source, not on a black background — visual
  context for "is this skeleton tracking the right curve" beats
  raw bitmap precision.
- Sample-column overlay (stage 06) uses the same render
  treatment as the committed `*-overlay.png` so they are
  visually comparable.

## Consequences

### Triage speed

The S128-S135 loop took 30-120 minutes per chart from "this looks
wrong" to "this stage is the culprit." With the bundle, the same
identification is intended to take 5-10 minutes:
open `diagnostic/`, scan the stage PNGs in order, identify the
first stage where reality diverges from expectation.

The 18-chart TTartisan triage (next session) is the first
real-world test of whether this estimate holds. If it holds, the
"generic approach" to CV-hostile cohorts becomes "regenerate the
bundle, classify by stage, fix per stage" — a process that scales.

### Pipeline as documented contract

Once every stage produces a named artifact, the stages themselves
become a documented contract. A future contributor (or agent) can
read the bundle to understand the pipeline without reading
`pipeline.py` — the artifacts are the interface, the code is the
implementation.

This raises the cost of unprincipled pipeline restructuring
slightly (the bundle has to keep producing meaningful output), and
that is the right trade-off — the loose coupling between stages
was already the source of the original failures (#1107 was
`svg.py` silently not reaching TTartisan since ADR-044 landed).

### What this does not do

The bundle identifies _which_ stage failed; it does not fix the
failure. The triage step (planned next) classifies the 18
TTartisan failures by stage and then opens per-stage sub-issues.
The bundle is the input to that triage, not its output.

For multi-aperture charts, each aperture pass produces its own
bundle subdirectory (`diagnostic/max/`, `diagnostic/stopped/`),
mirroring the `<stem>-max.svg` / `<stem>-stopped.svg` emit
convention. Stage 7 (sister fallback) and stage 8 (center
symmetry) artifacts are always generated, even when the
correction did not fire — an empty diff is itself a useful signal
("no correction was applied here").
