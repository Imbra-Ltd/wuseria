# Auto-triage gate run (#968)

First run of the auto-triage gate against the reference set.

Sister document to `calibration.md`, `scoring.md`, and `plausibility.md`.
Those three each report on one signal; this one reports on the *gate* —
the single binary decision the auto-commit + 3-panel review workflow
consumes.

## Scope

Same 3 of 8 reference charts that the other three runners cover — the
ones with both a declared profile in `profiles/declared.py` and a
hand-measured plot box.

| Chart                                     | Style family                    | Profile used              |
| ----------------------------------------- | ------------------------------- | ------------------------- |
| sigma-56mm-f1-4-dc-dn-c                   | mainstream-2color-solid-dashed  | SIGMA_2COLOR_SOLID_DASHED |
| samyang-85mm-f1-4-as-if-umc (MAX)         | mainstream-4color-all-solid     | SAMYANG_4COLOR_ALL_SOLID  |
| samyang-300mm-f6-3-ed-umc-cs-reflex (MAX) | idealized-flat                  | SAMYANG_4COLOR_ALL_SOLID  |

## How to reproduce

```
cd tools
py -m mtfdigitizer.autotriage
```

Runs `extract_chart` → `score_chart` → `check_all` → `triage` per chart
and reports the binary verdict + reason codes.

## The gate rule

```
HIGH iff:
  aggregate_precision  >= PRECISION_THRESHOLD (0.80)
  AND aggregate_iou    >= IOU_THRESHOLD       (0.20)
  AND check_all(readings) == []
LOW otherwise
```

Promoted from `scoring.md` finding 2's tentative recommendation. Pinned
empirically on this run, not picked from theory.

A LOW verdict carries a tuple of `LowReason` codes so the run log says
*why*, not just *that*, a chart was flagged:

| Reason code | Trigger | Where it routes attention |
| --- | --- | --- |
| `precision_below_threshold`     | `aggregate_precision < 0.80`     | Upstream: improve extractor's tracing density for sparse fields |
| `iou_below_threshold`           | `aggregate_iou < 0.20`           | Upstream: investigate fundamental shape mismatch |
| `render_match_undefined`        | `aggregate_iou is None`          | Upstream: the chart loaded but produced no comparable pixels — extractor / profile bug |
| `prior_failed_center_ge_edge`         | violation of the center≥edge prior         | Chart review: data is unphysical (probably plot inverted) |
| `prior_failed_ten_ge_thirty`          | violation of the 10≥30 prior               | Chart review: bands likely swapped |
| `prior_failed_not_suspiciously_flat`  | violation of the flatness prior            | Chart review: idealized / placeholder MTF, not a real lens |
| `prior_failed_in_range`               | violation of the [0, 1] prior              | Chart review: out-of-range value (defensive — extractor usually clamps) |

## Run 1 (2026-05-30)

### Per-chart

```
## sigma-56mm-f1-4-dc-dn-c (mainstream-2color-solid-dashed)
  LOW   IoU 0.223  precision 0.440  priors  0
    - precision_below_threshold

## samyang-85mm-f1-4-as-if-umc (mainstream-4color-all-solid)
  HIGH  IoU 0.224  precision 0.861  priors  0

## samyang-300mm-f6-3-ed-umc-cs-reflex (idealized-flat)
  LOW   IoU 0.273  precision 0.991  priors  3
    - prior_failed_not_suspiciously_flat
```

### Aggregate

```
charts triaged:  3
HIGH:            1
LOW:             2
```

## Findings

### 1. The gate matches the predicted separation exactly

The three runnable reference charts triage as `scoring.md` finding 2 and
`plausibility.md` finding 1 jointly predicted: one HIGH (Samyang 85mm),
one LOW for precision (Sigma 56mm), one LOW for flatness (Samyang 300mm
reflex). No threshold tuning was needed beyond the values
`scoring.md` already proposed.

### 2. Sigma 56mm classifies LOW — and that's correct behaviour

Sigma is the "canonical clean chart" and `calibration.md` confirms its
extraction is fine (median |d| 0.014, all 4 fields within ±0.05). But
render-match precision is **0.44**, far below the 0.80 floor, because
the dashed-M curves bridge sparsely (10M paired 2/11, 30M paired 0/11
per calibration.md finding 6). With most of the polyline unable to
draw, what little does draw is the only thing left to score.

The LOW verdict here is the *desired* signal: it routes the maintainer
to the upstream Sigma dashed-bridging work, not to a chart review. A
forgiving gate that said HIGH on Sigma today would hide the real
extractor weakness behind a green light.

When the bridging stage improves, Sigma's precision will climb above
0.80 and the verdict will flip to HIGH without changing this module.

### 3. Samyang 85mm IoU is 0.224 — barely clears 0.20

The IoU floor is `>= 0.20`, not `> 0.20`. Without that exact
inequality, Samyang 85mm would oscillate around the threshold on tiny
calibration changes (e.g. a 1-pixel plot-box shift could move IoU by
~0.005). The empirical headroom is one one-hundredth of a unit, which
is too narrow to assume; the test pins the boundary explicitly.

If a future run drops IoU below 0.20 for Samyang, the threshold
conversation reopens — not the gate logic. Per session 101: thresholds
move, not the extractor.

### 4. Samyang 300mm reflex correctly flags flatness — render-match alone would auto-commit it

The 300mm reflex scores render-match precision **0.991** (highest of
the three charts) and IoU 0.273 — both well above their thresholds.
Render-match alone says HIGH. The flatness prior fires on 3 of 4
fields and the AND-gate correctly demotes the chart to LOW.

This is the ADR-038 §"Confidence signal" "two-signal design is
necessary, not redundant" claim, demonstrated end-to-end: each signal
catches what the other can't.

### 5. precision_of() now lives in one place

Refactored `scorer.py`'s inline `_polyline_precision` to call
`triage.precision_of` so the precision metric has a single definition
across the two consumers. Scorer output is byte-identical to the
pre-refactor run — the function moved, not the math.

## What we need but don't have yet

- **Profiles for the other 5 reference charts.** With only 3 runnable,
  the thresholds are empirical against a 3-point distribution. Once
  the 7Artisans / Tokina / Viltrox profiles land, the gate gets a real
  stress test on 6-8 charts.
- **A confident-wrong test case.** All three runnable charts triage
  consistently with intent. We don't have a chart in the set that
  *should* clear all gates but doesn't (false-LOW) or *should* fail but
  doesn't (false-HIGH). Worth fabricating when one shows up in the
  wild.

## What does NOT need to change

- **The extractor.** Per session 101's discipline. None of these
  findings imply an extractor change.
- **The thresholds.** They behave as designed on the reference set.
  Revisit when more charts can run.
- **Render-match or plausibility priors.** The gate doesn't touch
  either module; both remain independently testable and useful on
  their own.
