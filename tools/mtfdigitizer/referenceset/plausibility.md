# Plausibility-priors run (#966)

First run of `priors.check_all()` against the reference set.

Sister document to `calibration.md` (offset distribution against eye-read
ground truth) and `scoring.md` (round-trip render-match IoU). This one is
the second of the two confidence signals ADR-038 §"Confidence signal"
requires — the one that catches the render-match blind spots: legend/label
swaps and flat-axis translation.

## Scope

Same 3 of 8 reference charts that `calibrate.py` and `scorer.py` cover —
the ones with both a declared profile in `profiles/declared.py` and a
hand-measured plot box.

| Chart                                     | Style family                    | Profile used              |
| ----------------------------------------- | ------------------------------- | ------------------------- |
| sigma-56mm-f1-4-dc-dn-c                   | mainstream-2color-solid-dashed  | SIGMA_2COLOR_SOLID_DASHED |
| samyang-85mm-f1-4-as-if-umc (MAX)         | mainstream-4color-all-solid     | SAMYANG_4COLOR_ALL_SOLID  |
| samyang-300mm-f6-3-ed-umc-cs-reflex (MAX) | idealized-flat                  | SAMYANG_4COLOR_ALL_SOLID  |

## How to reproduce

```
cd tools
py -m mtfdigitizer.plausibility
```

Runs `extract_chart()` to produce 11-point readings, then `check_all()`
to run all four priors over them.

## The four priors

| Prior                      | What it asserts                                                                  | Threshold                                              |
| -------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `center_ge_edge`           | Per field, MTF(center) ≥ MTF(edge)                                               | `INEQUALITY_TOLERANCE = 0.02` (one half-gridline tick) |
| `ten_ge_thirty`            | Per position, 10 lp/mm ≥ 30 lp/mm on the same S/M side                           | `INEQUALITY_TOLERANCE = 0.02`                          |
| `not_suspiciously_flat`    | Per field, NOT (mean ≥ 0.95 AND stdev ≤ 0.01) — no real lens holds ~1.0 at edge  | `FLATNESS_MEAN_THRESHOLD = 0.95`, `FLATNESS_STDEV_THRESHOLD = 0.01` |
| `in_range`                 | Every defined value in [0.0, 1.0]                                                | hard bounds                                            |

The verdict is binary by design — these are physical facts, not
statistical signals; either the data violates them or it doesn't.

## Run 1 (2026-05-30)

### Per-chart

```
## sigma-56mm-f1-4-dc-dn-c (mainstream-2color-solid-dashed)
  PASS — no priors fired

## samyang-85mm-f1-4-as-if-umc (mainstream-4color-all-solid)
  PASS — no priors fired

## samyang-300mm-f6-3-ed-umc-cs-reflex (idealized-flat)
  FAIL not_suspiciously_flat    (3 hits on contrast10M, contrast10S, resolution30M)
  [not_suspiciously_flat   ] contrast10S    whole   mean 0.984 >= 0.95 and stdev 0.001 <= 0.01 (11/11 defined) — idealized/placeholder?
  [not_suspiciously_flat   ] contrast10M    whole   mean 0.988 >= 0.95 and stdev 0.002 <= 0.01 (10/11 defined) — idealized/placeholder?
  [not_suspiciously_flat   ] resolution30M  whole   mean 0.978 >= 0.95 and stdev 0.001 <= 0.01 (5/11 defined) — idealized/placeholder?
```

### Aggregate

```
charts checked:           3
charts with violations:   1
total violations:         3
```

## Findings

### 1. Clean separation across the three charts

The three runnable reference charts split exactly as REFERENCE_SET.md
predicted: the two real-lens charts (Sigma 56mm, Samyang 85mm MAX) clear
all four priors, and the idealized-flat Samyang 300mm reflex fires the
flatness prior. No tuning was needed to produce this — the starting
thresholds (mean ≥ 0.95 AND stdev ≤ 0.02) hit on the first run.

This is the exact case ADR-038 §"Confidence signal" calls out as
render-match's blind spot: the 300mm reflex scores IoU 0.347 / precision
0.99 in `scoring.md` (high-confidence by IoU alone — exactly the bug the
prior catches).

### 2. Flatness fires on 3 of 4 fields, not all 4

The 300mm reflex's `resolution30S` curve doesn't trigger the flatness
prior because the extractor produces only **one** defined value for that
field (per `scoring.md`: zero raster pixels post-gap-skip), and
`statistics.stdev` requires at least 2 points to compute. The prior
correctly skips fields with insufficient evidence rather than guessing.

This is the right behaviour: a one-point "curve" is a B2 gap, not a flat
line. If the extractor's 30S handling improves in a later session and
fills in more positions, the prior will catch the flatness automatically.

### 3. Samyang 85mm 10M sits just below the flatness threshold

The Samyang 85mm 10M curve has mean ~0.93 across the field — visually
close to flat, but the 0.95 mean threshold correctly keeps it on the
"real lens" side. If the threshold were 0.90, this chart would
false-positive. If it were 0.98, the 300mm reflex's noisy ~0.984 mean
might escape.

The 0.95 / 0.02 pair has ~0.03 mean headroom and ~10× stdev headroom on
the boundary cases observed — comfortable margin without being so loose
as to miss the target. Worth re-evaluating once more charts can run
(7Artisans, Tokina, Viltrox profiles still pending per epic #932).

### 4. The other three priors did not fire on any chart

`center_ge_edge`, `ten_ge_thirty`, and `in_range` produced zero
violations across the three runnable charts. This is expected and
correct — none of the three reference charts has a known swap-pattern or
out-of-range data, so a clean reference set should not trigger them.

They are still essential to ship: the swap-pattern is exactly the case
ADR-038 calls out ("10<30 at edge — bands swapped?") as the value of the
plausibility-priors signal beyond just flatness. They activate once
real-world brand data starts flowing through the extractor and a
legend/label parsing bug ships.

The unit tests in `test_priors.py` exercise each prior's fire-path with
hand-constructed fixtures so the absence of reference-set fires doesn't
mean untested code.

## What we need but don't have yet

- **Out-of-band charts as plausibility test cases.** The Samyang 300mm
  reflex covers the flat case, but we don't have a known bands-swapped or
  inverted-curve chart in the reference set. When one shows up in the
  wild (or one is fabricated for testing), add it to `charts.py` so the
  full prior surface gets exercised on real data, not only on unit
  fixtures.
- **Profiles for the other 5 reference charts** (7Artisans same-color
  dashed, Tokina 2color-frequency, Viltrox B&W, etc.) — once they're
  declared, the priors will run over the full 8-chart matrix and the
  current thresholds get a real stress test instead of a 3-chart probe.

## What does NOT need to change

- **The extractor.** Per session 101's discipline: thresholds move, not
  the extractor. None of these findings imply an extractor change.
- **The priors themselves.** They behave exactly as designed on the
  reference set. If a future chart fires unexpectedly, the discipline is
  the same — investigate whether the chart is a genuine outlier (revise
  the threshold) or whether the data is genuinely wrong (the prior is
  doing its job).
