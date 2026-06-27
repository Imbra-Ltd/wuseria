# ADR-075: N-frequency RIDGE_TRACKING via y-band split

**Status:** Accepted
**Date:** 2026-06-27

## Context

The MTF digitizer's RIDGE_TRACKING dispatch (ADR-049) extracts curves
from charts whose curves bundle so close that connected-component
skeletonization fuses them. The original implementation was sized for
Viltrox: 2 frequencies × {S, M} = 4 tracks, split into upper and lower
halves by mean-y. The function `ridge_tracks_to_fields` hardcoded
`n=4` for the top-N selection and `upper_freq`/`lower_freq` as
positional parameters.

The `ridge.py` module docstring named the 2-freq limit explicitly:

> **Not handling >2 frequencies.** The clustering assumes a 4-curve
> layout (2 frequencies × S/M). A 6-curve Zeiss-style 3-frequency
> chart needs a different track-identification step.

Issue #791 ("Digitize MTF charts for Carl Zeiss lenses") proposed
shipping the 3-frequency Zeiss Touit press kit family (12mm, 32mm,
50mm Macro), which publishes 10/20/40 cycles/mm on a single B&W
panel with solid/dashed S/T encoding. The 32mm chart had been in
the reference set since the original calibration probe (#933) as a
deliberately out-of-band rejection case — extraction was not
attempted because no 3-frequency profile existed.

An S196 probe (`probe_zeiss_touit_ridges.py`, throwaway, deleted)
ran the existing 2-freq ridge tracker against the 32mm wide-aperture
panel with a hand-crafted profile that declared 3 frequencies. The
greedy clusterer in `_cluster_into_tracks` produced 6 distinct
tracks cleanly; only the final `ridge_tracks_to_fields` step
collapsed them back to 4. The 2-freq lockin was confined to one
function and its callers, not a pipeline-wide assumption — the
front-end `MtfReading` data shape already supports arbitrary
frequency tuples (Fujifilm GF charts publish at {15, 20, 40} and
{10, 20, 40} today via the per-frequency orchestrator, ADR-043).

## Decision

Generalize `ridge_tracks_to_fields` to N frequencies via a new
`ridge_tracks_to_fields_multifreq` function that takes the full
frequency tuple in upper→lower screen order. The legacy 2-frequency
function becomes a thin delegating wrapper preserved for Viltrox's
dispatch site and its tests.

```
                     +-----------------------------+
                     |  ridge_tracks_to_fields_    |
                     |  multifreq(mask, plot_box,  |
                     |  frequencies_lpmm=(10,20,40), ...)
                     +-----------------------------+
                                  |
                                  v
            +---------------------+---------------------+
            |  _select_top_n_tracks(n = 2*N)            |
            +-------------------------------------------+
                                  |
                                  v
            Sort kept tracks by mean_y, slice into N bands:
              band[0]   --> highest-screen freq (lowest lp/mm)
              band[1]   --> middle freq
              ...
              band[N-1] --> lowest-screen freq (highest lp/mm)
                            (absorbs remainder when kept < 2N)
                                  |
                                  v
            Within each band: top track (smaller mean_y) = S,
            second track = M.
```

Concrete rules:

1. The dispatch site in `pipeline/dispatch.py` passes
   `profile.frequencies_lpmm` directly to the multifreq function;
   no positional unpacking of `[0], [1]` remains.
2. `_select_top_n_tracks` is called with `n = 2 * len(frequencies_lpmm)`.
3. The kept tracks are sorted by mean_y and sliced into
   `len(frequencies_lpmm)` equal-size y-bands. The last band absorbs
   the remainder when the kept count is below `2N` (coincident curves
   reduce the kept count on tightly bundled panels).
4. Within each band, the track with smaller mean_y is sagittal (S)
   by physics — edge MTF degrades faster on the meridional axis.
   `dashed_is_sagittal` does not apply to ridge-tracking (Viltrox-
   style all-dashed inputs).
5. A new declared profile `ZEISS_TOUIT_BW_3FREQ` (neutral hue,
   `frequencies_lpmm=(10, 20, 40)`, `style_axis=SPLIT_BY_DASH`,
   `hue_meaning=RIDGE_TRACKING`, `auto_suggestable=False`) wires
   the family.
6. `family_profile.PROFILE_BY_STYLE` maps the existing
   `multifreq-press-kit` style family from "deliberately absent"
   to `ZEISS_TOUIT_BW_3FREQ`.
7. The Touit 12mm and 50mm Macro charts join the reference set
   alongside the existing 32mm anchor, each with primary + stopped
   `ChartView` panels following ADR-063's Samyang stacked-panel
   pattern and ADR-065's `max`/`stopped` role labels.

## Alternatives considered

| Alternative                                                                                             | Why rejected                                                                                                                                                                                                                           |
| ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Lift the front-end `MtfReading` schema to a fixed 3-frequency shape                                     | Front-end already supports arbitrary frequency tuples (Fujifilm GF runs at {15,20,40} today). No schema change needed.                                                                                                                 |
| New `RIDGE_TRACKING_3FREQ` `HueMeaning` literal                                                         | Splits one mechanism across two code paths for a constant that's already on the profile (`frequencies_lpmm`). The generalized function reads N from there.                                                                             |
| Per-frequency separate chart files (Fujifilm `SAGITTAL_MERIDIONAL_SINGLE_FREQ` pattern, ADR-043)        | Zeiss publishes one chart with all frequencies on one panel; splitting into per-frequency images would be a fabrication.                                                                                                               |
| Build a new profile family with N-frequency clustering AND a redesigned coincidence handler in one step | Two failure modes (3-freq dispatch vs coincident-curve clustering) deserve two ADRs. Path A in #791 ships max-aperture extraction first; stopped-panel coincidence stays a documented limitation gated by Tier 1 eye-read calibration. |
| Coin a new style family name (e.g. `bw-3freq-press-kit`)                                                | The existing `multifreq-press-kit` family name is accurate; only its wiring changed (rejection-case → extracted).                                                                                                                      |

## Consequences

- 3-frequency charts in the Touit family run through the same
  RIDGE_TRACKING dispatch as Viltrox; one mechanism, two profiles.
- The 2-frequency `ridge_tracks_to_fields` keeps its existing
  signature for Viltrox callers. Byte-equivalent: the 61 existing
  ridge/Viltrox tests pass unchanged after the refactor.
- The Touit family ships in this PR without ground-truth values
  (#791's eye-read GT becomes a follow-up issue). The reference-set
  entries declare plot boxes for both panels; calibration values
  populate when a maintainer eye-reads the 396 GT cells (3 charts
  × 2 panels × 3 freqs × 2 S/M × 11 positions).
- Stopped-panel coincidence (curves bundle within ~15 px near
  MTF=0.95) collapses ridge-cluster pairs on the Touit k=4 / k=5.6
  panels. The S196 probe on Touit 32mm k=4 recovered 5 of 6
  expected tracks. Documented as a known limitation in the
  Touit profile's `notes` and in `pipeline/ridge.py`'s
  "Failure modes" section. Stopped-panel extraction is gated by
  Tier 1 eye-read calibration; until that lands, only the
  max-aperture panels contribute to per-lens emit.
- `family_profile.PROFILE_BY_STYLE` now has 9 entries (was 8).
  Only `soft-multicurve-promo` (7Artisans 35mm) remains as a
  deliberately absent fail-loud family.
- `REFERENCE_SET.md` table updates the Touit 32mm row from
  "out-of-band" to "extracted via N-freq RIDGE_TRACKING".
- Future N-frequency dialects (e.g. a Zeiss Loxia chart with 4
  frequencies) extend by declaring a new profile with the right
  hue range and frequency tuple; no further pipeline change.
