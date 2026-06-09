# ADR-048: One eye-read.md per Tier 1 anchor

**Status:** Accepted
**Date:** 2026-06-09

## Context

Each Tier 1 anchor (3 today: Fuji GF 23mm, Fuji XF 23mm, TTartisan 50mm)
currently ships TWO maintainer-facing files in its
`docs/optical-specs/<slug>/` directory:

1. `extractor-prediction.md` — pre-populated with the digitizer's
   readings. Read-only-ish; the maintainer scans it for sanity.
2. `eye-read-template.md` — empty fill-in tables for the maintainer's
   own values. The maintainer then transcribes verified values into
   the `_<LENS>_GT` tuple in `referenceset/charts.py`.

Two problems with this setup:

- **Redundancy.** Both files carry the same table headers, sample
  positions, axis legend, and GT-snippet skeleton. ~80% of bytes
  duplicate.
- **Three-document flow.** The maintainer reads `eye-read-template.md`
  while glancing at `extractor-prediction.md` while editing
  `charts.py`. Three documents to keep in sync; the predictions stay
  stale the moment any cell is read independently.
- **Effort floor.** "Fill in every cell" is the visible task even when
  the extractor is mostly right. There's no path that says "I scanned
  the table, two cells are wrong, the rest are fine" without
  re-typing all of them.

## Decision

Replace the two files with one per anchor: `eye-read.md`.

```
+---------------------------------------------+
|  eye-read.md  (one per Tier 1 anchor)       |
+---------------------------------------------+
|  Pre-populated with extractor predictions   |
|                                             |
|  Each cell has one of three states:         |
|    "0.43"   = extractor's prediction,       |
|                maintainer judged it fine    |
|                (silent verification)        |
|    "0.45!"  = maintainer-corrected value    |
|                (overrides extractor)        |
|    "0.43?"  = maintainer hasn't read it,    |
|                becomes None in GT           |
|                                             |
|  Headings, sample-position legend, MTF      |
|  axis legend, GT-snippet skeleton — all     |
|  the same as today's eye-read-template.md   |
+---------------------------------------------+
```

The rule: **unmarked = silent verification**. Looking at a cell and
not changing it counts as accepting it. This treats the maintainer's
attention as the scarce resource, not their typing.

The `?` escape hatch handles the cell the maintainer genuinely
doesn't know — the curve is missing at that position, the chart is
ambiguous, etc. `?` cells become `None` in the GT tuple, same as if
the cell were never filled.

### Transcription workflow

The maintainer asks the agent to transcribe: "transcribe `<slug>`"
or equivalent. The agent:

1. Reads `eye-read.md` for the lens.
2. Parses each cell:
   - Bare number (`0.43`) → goes into GT at that value.
   - Number with `!` (`0.45!`) → goes into GT at that value.
   - Number with `?` (`0.43?`) → becomes `None` in GT.
   - Bare `?` or empty → becomes `None`.
3. Updates the matching `_<LENS>_GT` tuple in
   `referenceset/charts.py`.
4. Runs `py -m mtfdigitizer.calibrate` for the affected chart.
5. Reports per-field |Δ| deltas and the count of `!`-marked vs.
   silent-verified cells.

There's no separate "verification state" file. The eye-read.md is
the state.

### Refresh-on-rerun

When the extractor is re-run (after a `ridge.py` fix, say) and its
predictions change, `scaffold_anchor_helpers.py` rewrites
`eye-read.md`:

- Cells without a mark are refreshed to the new extractor prediction.
  (The maintainer last said "you're right" to a value; the extractor
  now has a better answer — that's the new "you're right".)
- Cells with `!` keep the maintainer's value and the mark.
- Cells with `?` keep the `?` and the displayed value.

The header text, axis legend, and GT snippet always come from the
generator (no manual editing of those parts).

### Agent rules

Per `feedback_agent_no_gt_eye_read` the agent still does NOT eye-read
cell values. The agent's role is mechanical:

- Generate `eye-read.md` (extractor's predictions + the legend).
- Transcribe to GT on request.
- Run calibrate and report.

The maintainer's role is unchanged:

- Look at the source PNG, judge each cell.
- Mark wrong cells with the corrected value + `!`.
- Mark uncertain cells with `?`.
- Leave cells they judged fine as-is.

## Alternatives considered

- **Keep the two-file split, automate the transcription.** Lighter
  refactor, but doesn't fix the redundancy or the "every cell to be
  filled" framing — the maintainer still works against two
  documents.
- **Two columns per field (`10S EX` + `10S GT`).** Explicit
  separation, but doubles table width — Fuji's 3 frequencies × 2 S/M
  × 2 columns = 12 columns. Hard to read on a screen, harder to edit.
- **Row-level status column instead of cell marks.** Forces verifying
  whole rows at a time; awkward when only one cell of four is wrong.
- **Re-run regenerates from scratch (drops marks).** Cleanest but
  loses in-progress reading work. The preserve-marks variant is more
  forgiving for the iterative case.

## Consequences

- Three Tier 1 anchors migrate (Fuji GF 23, Fuji XF 23, TTartisan 50).
  All three already have verified `_<LENS>_GT` data — their existing
  values get `!` marks in the new file at migration time.
- `scaffold_anchor_helpers.py` loses one of its two markdown
  generators; the remaining one merges the prediction table + the
  axis-legend prose.
- A new helper (`mtfdigitizer.eyeread` or extension of `charts.py`)
  parses `eye-read.md` and writes the GT tuple. Same parser handles
  the refresh-on-rerun side: the scaffolder reads the existing file
  to learn which cells are marked.
- `feedback_agent_no_gt_eye_read` still holds. The agent reads
  `eye-read.md` as a _maintainer-authored_ document and acts on it
  mechanically, but never proposes cell values of its own.
- ADR-046 (anchor readhelpers) is unaffected — the PNG-side helpers
  and the "clean source chart as base" rule stay. Only the
  markdown-side artifacts merge.
