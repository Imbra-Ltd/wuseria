# Eye-read — Fujifilm GF 55mm f/1.7 R WR

Scoped to the two cells where the freq40 M ridge tracker mistracks the
plateau ceiling (issue #1305). The rest of the chart is left to the
extractor; this file documents only the maintainer-overridden cells
so the override comment in `src/data/mtf-readings.ts` has a citeable
ground-truth source.

Per ADR-072 the center symmetry rule fills `(M, S) = (1.0, 1.0)` at
position 0 when both are None. That is intentional behaviour, not an
override candidate — even though physically wrong on this chart
(same class as #1279/viltrox-75). The two cells below are different:
the chart shows a clearly resolved M40 curve dipping below 1.0, the
extractor pins it at 1.0, and the chart's own dashed lines give the
correct readings.

## Source

`docs/optical-specs/fujifilm-gf-55mm-f1-7-r-wr/fujifilm-gf-55mm-f1-7-r-wr-40lp.png`
— Fujifilm-published 40 lp/mm MTF chart, single aperture (f/1.7).

The red dashed M40 curve plateaus around 0.92–0.95 across the inner-
to-mid field, dips at ~18mm, drops to ~0.55 at the edge. Eye precision
is ±0.02 per cell (half a printed gridline tick at 0.10 spacing).

## f/1.7 — freq 40 M overrides

| Position (mm) | Extractor | Eye-read | Reason                                                |
| ------------- | --------- | -------- | ----------------------------------------------------- |
| 10.76         | 1.00      | 0.95     | ridge tracker pins to plateau ceiling; chart at ~0.95 |
| 13.45         | 1.00      | 0.92     | ridge tracker pins to plateau ceiling; chart at ~0.92 |

Values stated by the maintainer in issue #1305.

## Mistrack pattern

Same family as #1279 (center-anchor overshoot) and #1301 (af-35
bend-point M30 mistrack): the ridge tracker locks onto the high-MTF
plateau ceiling instead of following the curve as it dips below 1.0.
GF 55's case is distinctive in that the mistrack is on inner-to-mid
positions, not at the center or right corner.

Long-term fix is a ridge-tracker prior that penalizes "value pinned
at 1.0 across N consecutive positions when paired direction (S) is
dropping" (fix-path-1 in #1305). Until then the override comment in
`src/data/mtf-readings.ts` carries the corrected values and the
override-respecting splice (#1301 fix-path-2) preserves them across
`emit_fuji_tier2 --write`.
