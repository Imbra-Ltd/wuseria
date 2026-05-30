# mtfdigitizer

Unified MTF chart digitizer for the wuseria optical database. Implements
[ADR-038](../../docs/decisions/038-unified-mtf-digitizer.md).

One adaptive pipeline replaces the per-brand scraper sprawl
(`mtf-extract-skeleton.py`, `-samyang.py`, `-sigma.py`): declared chart
profile → HSV mask → skeletonize → connected-components S/M split → 11
fixed sample points → confidence score (render-match + plausibility priors)
→ SVG + readings.

## Status

Under construction. Foundation work in progress:

- [x] [#933](https://github.com/Imbra-Ltd/wuseria/issues/933) — reference set
- [x] [#934](https://github.com/Imbra-Ltd/wuseria/issues/934) — profile abstraction + advisory auto-suggest
- [ ] [#935](https://github.com/Imbra-Ltd/wuseria/issues/935) — extraction pipeline
- [ ] Remaining tasks under epic [#932](https://github.com/Imbra-Ltd/wuseria/issues/932)

The package does not yet expose a CLI or extraction API. See the epic for the
full task list.

## Layout

```
mtfdigitizer/
  README.md           # this file
  __init__.py         # package marker + module map
  referenceset/       # eye-verified ground-truth charts (#933)
    REFERENCE_SET.md  # what's in the set, why, verified-shape notes
    charts.py         # machine-readable manifest
  profiles/           # declared chart profiles + auto-suggest (#934)
    types.py          # MtfProfile, HueRange, ProfileMatch, ProfileMismatch
    declared.py       # SIGMA_2COLOR_SOLID_DASHED, SAMYANG_4COLOR_ALL_SOLID
    suggest.py        # suggest_profile() advisory + resolve() B1 entry point
  tests/              # pytest suite (matches brandkit/pagefetch pattern)
```

## Profile system

A *profile* declares a chart's visual dialect along three axes (ADR-038 §1):

- **Color axis** — one HSV band per curve color (with S and V bounds, so
  pink-vs-red and dark-grey-vs-light-grey are distinguishable)
- **Style axis** — `SPLIT_BY_DASH` for one-hue-per-frequency dialects
  (Sigma); `HUE_IS_CURVE` for one-hue-per-curve dialects (Samyang)
- **Frequency count** — declaring 2 frequencies refuses 3-frequency charts

`resolve(image, declared)` is the entry point: it returns the declared
profile when the image agrees, raises `ProfileMismatch` when they
disagree, and falls back to the advisory auto-suggest only when
nothing is declared. **A declared profile is never silently switched** —
that's the B1 fail-loud gate from PR #931 generalized.

Two profiles ship to start (the YAGNI cut from #934 — Sigma and
Samyang are the brands we have reference data for). Other dialects
land per-brand as the digitizer encounters them in #935.

## Reference set

Eight charts span the chart-style families we encountered in
`docs/optical-specs/`:

| # | Lens                                 | Style family                      |
| - | ------------------------------------ | --------------------------------- |
| 1 | sigma-56mm-f1-4-dc-dn-c              | 2-color solid-S/dashed-M (Sigma)  |
| 2 | samyang-85mm-f1-4-as-if-umc          | 4-color all-solid (Samyang)       |
| 3 | samyang-300mm-f6-3-ed-umc-cs-reflex  | 4-color, idealized-flat at ~1.0   |
| 4 | 7artisans-50mm-f1-2-mark-ii          | 2-color same-color dashed S/M     |
| 5 | 7artisans-35mm-f1-2-mark-ii          | Soft promo, 8+ frequencies        |
| 6 | tokina-atx-m-23mm-f1-4-x             | 2-color, colors carry frequency   |
| 7 | viltrox-af-75mm-f1-2-pro             | B&W soft promo, dashed-only       |
| 8 | zeiss-touit-32mm-f1-8                | German press kit, 3 frequencies   |

Eye-verified curve shapes (key inflection points, S/M divergence, edge
falloff) live alongside each entry in `referenceset/REFERENCE_SET.md`.
The machine-readable form is `referenceset/charts.py` — a list of
`ReferenceChart` records keyed by lens slug.

The two open ADR-038 parameters proposed against this set:

- **Render-match threshold** — `0.75` IoU initial value
- **Offset tolerance band** — `±0.05` MTF units (uniform vertical offset)

Reasoning in `referenceset/REFERENCE_SET.md` §Proposed thresholds. Both will
be refined against the real extractor in #935 — these are starting points,
not final.

## Running the tests

```bash
cd tools
py -m pytest mtfdigitizer/
```
