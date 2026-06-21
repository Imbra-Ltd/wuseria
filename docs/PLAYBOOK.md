# Playbook

Operational reference for common tasks.

## 1. Git workflow

### 1.1 Start a new feature

```bash
git checkout main && git pull
git checkout -b feat/description
```

### 1.2 Commit changes

```bash
npm run lint
git add <files>
git commit -m "feat: description"
```

Commit prefixes: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `style:`,
`test:`. Subject line under 80 characters, imperative mood.

### 1.3 Create a pull request

```bash
git push -u origin feat/description
gh pr create --title "feat: description" --body "## Summary\n- ..."
```

### 1.4 Merge and clean up

```bash
gh pr merge <number> --merge
git checkout main && git pull
git branch -d feat/description
git push origin --delete feat/description
```

### 1.5 List open issues

```bash
gh issue list --state open
gh issue list --label epic --state open
```

### 1.6 Close an issue from a PR

Reference the issue in the PR body with `Closes #<number>`. GitHub closes it
automatically on merge.

## 2. Domain operations

### 2.1 Add a new lens

1. Add an entry to `src/data/lenses.ts` following the `Lens` interface
2. All boolean fields use `is`/`has` prefix (e.g. `hasAutofocus`, `isWeatherSealed`)
3. Price in USD, rounded to nearest $250
4. Only fill optical quality fields if data comes from a trusted source (see 2.4)
5. Leave optical fields empty for lenses without trusted data — they will
   appear in the Lens Explorer but be excluded from the Genre Guide
6. Run `npm run lint` to verify

### 2.2 Add a new camera

1. Add an entry to `src/data/cameras.ts` following the `Camera` interface
2. Same boolean naming and price conventions as lenses
3. Run `npm run lint` to verify

### 2.3 Add a new accessory

1. Choose the correct sub-interface in `src/types/accessory.ts` by `category`
2. Add an entry to `src/data/accessories.ts` (when created)
3. If no existing category fits, add a `GenericAccessory` entry

### 2.4 Scoring data policy

Only score lenses that have optical data from trusted review sources. Do not
guess or estimate optical quality — showing nothing is better than showing
wrong data.

- **Lens Explorer** — shows all lenses, sortable by specs. No scoring needed.
- **Genre Guide** — shows only lenses with optical data. Lenses with empty
  optical fields are excluded entirely.
- Scoring functions return `null` when optical fields are missing.

### 2.5 Trusted review sources

See `src/data/reviews.ts` for the full directory with methodology
(lab/field) and trust (1-3) ratings. Trust-3 sources:

| Trust 3             | Methodology                     |
| ------------------- | ------------------------------- |
| LensRentals         | Lab — optical bench MTF         |
| LensTip             | Lab — Imatest MTF charts        |
| OpticalLimits       | Lab — Imatest MTF               |
| DxOMark             | Lab — perceptual megapixel      |
| The Digital Picture | Lab — ISO 12233 chart           |
| ePHOTOzine          | Lab — Imatest MTF               |
| ColorFoto           | Lab — proprietary bench         |
| Dustin Abbott       | Field — systematic + lab hybrid |
| DPReview            | Field — comprehensive           |
| Phillip Reeve       | Field — manual focus specialist |
| Lloyd Chambers      | Field — systematic high-res     |
| Lonely Speck        | Field — astrophotography        |

**Do not use:** Ken Rockwell — not a trusted data source.

### 2.6 Score a lens

Prerequisite: the lens must have reviews from at least one trust 3
source. See ADR-014 for the full rubric and reference scorings.

**Step 1 — Identify sources**

Search ALL trust-3 sources for the lens before proceeding:

- Lab (trust 3): LensRentals, LensTip, OpticalLimits, DxOMark, The Digital Picture, ePHOTOzine, ColorFoto
- Field (trust 3): Dustin Abbott, DPReview, Phillip Reeve, Lloyd Chambers, Lonely Speck

Do not skip sources — missing one can leave scoreable fields empty
(e.g. Dustin Abbott provided astigmatism + bokeh data for the
Viltrox 9mm that two other sources missed).

Check if the optical formula changed between versions
(e.g. XF 27mm f/2.8 R WR uses the same optics as the original).

**Step 2 — Collect data per field**

Run targeted per-field searches — one search per optical field, not
one broad query. For slow sites (LensTip), search snippets return
cached data even when direct fetch times out.

Fields to collect (all 0-2 scale, 0.5 steps):

| Field               | Source type             | How to score                       |
| ------------------- | ----------------------- | ---------------------------------- |
| centerStopped       | lpmm at sweet spot      | % of sensor max (see ADR-014)      |
| cornerStopped       | lpmm at sweet spot      | % of sensor max                    |
| centerWideOpen      | lpmm at max aperture    | % of sensor max                    |
| cornerWideOpen      | lpmm at max aperture    | % of sensor max (often missing)    |
| astigmatism         | % S/T difference        | < 5% = 2.0, 5-10% = 1.5, etc.      |
| coma                | Point-source test only  | Qualitative word mapping           |
| sphericalAberration | Focus shift test        | Qualitative word mapping           |
| longitudinalCA      | Colour fringing test    | Qualitative word mapping           |
| lateralCA           | % at 70% from center    | LensTip scale (< 0.04% = 2.0)      |
| distortion          | % RAW uncorrected       | < 0.3% = 2.0, 0.3-1.0% = 1.5, etc. |
| vignettingWideOpen  | EV at max aperture, RAW | < 0.5 = 2.0, 0.5-1.0 = 1.5, etc.   |
| vignettingStopped   | EV at f/5.6-f/8, RAW    | Same scale                         |
| bokeh               | Qualitative assessment  | Word mapping                       |
| flareResistance     | Qualitative assessment  | Word mapping                       |

Red flags: fast lenses (f/2 or wider) should have longitudinalCA,
sphericalAberration, and coma data. Wide-angle lenses should have
lateralCA and distortion data. If a field that should be significant
is missing, search specifically before accepting undefined.

**Step 3 — Apply rubric**

For each field, apply the threshold from ADR-014. Use only discrete
values: 0, 0.5, 1.0, 1.5, 2.0. When sources disagree, use the
highest-trust source. When ambiguous, round conservative (lower).

If a field has no data from any source, leave it undefined. Do not
infer from related fields or optical construction alone.

**Step 4 — Fallback sources (only when no lab/field data exists)**

- Official MTF chart → astigmatism only (S/M divergence)
- Optical construction + zero complaints → sphericalAberration,
  CA (not coma, bokeh, or flare)

**Step 5 — Write the data**

1. Add optical fields + `sweetSpotAperture` + `reviewSources` to the
   lens entry in `src/data/lenses.ts`
2. Add reference scoring table to `docs/optical-specs/<slug>/scoring-log.md`
3. If astigmatism was scored from an official MTF chart, save the chart
   image and a companion `.md` analysis in `docs/optical-specs/<slug>/`
4. Run `npm run validate` to verify

**Step 6 — Verify**

Check that the scored lens appears in the Genre Guide for relevant
genres (once genre formulas are implemented).

### 2.7 Utility scripts

**Fetch a web page (four-tier auto-escalation):**

Run from the `tools/` directory so `python -m pagefetch` resolves the package.
For bare CLI fetches, pass `--cache-dir ../.cache/fetch` so the fetch shares the
one project cache the brand tools use — otherwise the CLI's default creates a
separate `tools/.cache/pagefetch`. (Brand tools set the cache dir automatically;
only the bare CLI needs the flag. `PAGEFETCH_CACHE_DIR` also works if you prefer
an env var, but the flag is simpler for one-off fetches.)

```bash
py -m pagefetch <url> --cache-dir ../.cache/fetch   # share the project cache
py -m pagefetch <url>              # auto mode: urllib → Playwright → Nodriver → UC
py -m pagefetch <url> --html       # raw HTML output
py -m pagefetch <url> --js         # force Playwright (JS-rendered pages)
py -m pagefetch <url> --nodriver   # force Nodriver (headed Chrome, bot bypass)
py -m pagefetch <url> --uc         # force SeleniumBase UC (headless fallback)
py -m pagefetch <url> --no-cache   # bypass cache, fetch fresh
py -m pagefetch --batch urls.txt --nodriver --output-dir out/  # batch mode
py -m pagefetch --clean-cache --cache-dir ../.cache/fetch          # purge bot/404 junk
py -m pagefetch --clean-cache --dry-run --cache-dir ../.cache/fetch   # preview only
```

Responses are cached in `.cache/fetch/` (me-fuji points the cache there via
`PAGEFETCH_CACHE_DIR`; the cache_dir precedence is `--cache-dir` / explicit
arg > env var > CWD-relative default, validated at construction). Bot-blocked
and 404/gone responses are never cached
and self-heal on read; `--clean-cache` sweeps any junk that accumulated
(ADR-037 — content-based validity, no TTL). See `tools/pagefetch/README.md`
for the architecture and
library API.

**Run the Python tool tests:**

```bash
cd tools && py -m pytest pagefetch/tests/ brandkit/tests/ mtfdigitizer/tests/ -v
```

**Run the MTF digitizer calibration runner:**

```bash
cd tools && py -m mtfdigitizer.calibrate
cd tools && py -m mtfdigitizer.calibrate --write-readings
```

Runs `extract_chart()` against every reference chart with both a hand-measured
plot box and eye-read ground truth (`tools/mtfdigitizer/referenceset/charts.py`),
reports per-field absolute offset distribution + an aggregate. Output: stdout
only by default. With `--write-readings`, additionally writes one markdown
grid per chart to `tools/mtfdigitizer/referenceset/readings/<slug>.md` for
diffing across algorithm changes. Findings live in
`tools/mtfdigitizer/referenceset/calibration.md` — update the markdown after a
run that changes the numbers materially. Reference the calibration entries
when discussing the ADR-038 offset tolerance band or the 0.75 render-match
threshold.

**Run the MTF digitizer production extractor (Tier 2 per ADR-041):**

```bash
cd tools && py -m mtfdigitizer.extract <lens-slug>            # one lens, gated commit
cd tools && py -m mtfdigitizer.extract <lens-slug> --accept   # bypass HOLD, write log
cd tools && py -m mtfdigitizer.extract --all                  # every pending Tier 2 lens; stops on first HOLD
cd tools && py -m mtfdigitizer.extract --check                # re-render all production logs, fail on staleness
```

Sister to `calibrate` for production-tier lenses (Tier 2 = `plot_box` set but no
`ground_truth`). Always writes overlay PNG + SVG + 3-panel review HTML under
`docs/optical-specs/<lens-slug>/`; writes the production
`digitization-log.md` only when the confidence gate accepts (render-match
precision ≥ 0.80 AND IoU ≥ 0.20 AND all plausibility priors hold) OR
`--accept` is passed. `OVERLAY_GLANCE_REQUIRED=True` is the initial gate
posture — HIGH verdict alone does not auto-commit; maintainer glances at the
overlay PNG and re-runs with `--accept`. See ADR-041 for the two-tier
rationale and `tools/mtfdigitizer/extract.py` for the gate knob.

**Multi-view lenses (zooms).** A lens with `additional_views` set on its
`ReferenceChart` (today: the 5 Sigma zooms with wide + tele charts) emits
one set of inspection artifacts per view, file-named by chart stem so
nothing collides in the folder, plus a single `digitization-log.md` with
one `## Panel` section per view. The gate aggregates across views: any
LOW verdict holds the whole lens (partial commits aren't a meaningful
state when one log covers every view). Per ADR-033 the wide-end
diffraction chart is the canonical-for-scoring view; tele rides along
as supplementary data on the same log. (#1037)

**Write a per-stage diagnostic bundle for one chart (ADR-050):**

```bash
cd tools && py -m mtfdigitizer.diagnose <lens-slug>             # one chart
cd tools && py -m mtfdigitizer.diagnose --brand <prefix>        # whole brand cohort (e.g. `ttartisan`)
cd tools && py -m mtfdigitizer.diagnose --all                   # whole corpus (slow)
```

Runs `extract_chart` with a `DiagnosticSink` that writes one named PNG
per pipeline stage (source, plotbox, hue masks, skeletons, presence
masks, sampling overlay, fallback diff, symmetry diff, emit) plus a
`manifest.json` into `docs/optical-specs/<slug>/diagnostic/`. Multi-
aperture charts get one subdirectory per aperture (`max/`, `stopped/`).
The bundle is gitignored — regenerate on demand when a chart looks
wrong. Use the stage-to-symptom mapping in ADR-050 to jump from a
maintainer's failure description ("30lpmm completely wrong", "missing
segments", "edge too low") to the first PNG to inspect. Extraction
values are byte-identical with or without the sink — `py -m
mtfdigitizer.svg --check` MUST pass after every diagnose run.

**Refresh per-lens calibration-tier digitization logs (Tier 1 per ADR-041):**

```bash
cd tools && py -m mtfdigitizer.log              # Tokina lenses (default)
cd tools && py -m mtfdigitizer.log --all        # every lens with a runnable chart
cd tools && py -m mtfdigitizer.log --check      # verify committed logs are up to date
```

Writes `docs/optical-specs/<lens-slug>/digitization-log.md` for **Tier 1
calibration anchors** (lenses with eye-read ground truth). Tier 2 production
lenses use the parallel writer baked into `py -m mtfdigitizer.extract` above —
their logs omit the EYE column per ADR-041. Each log is a **generated** file —
never hand-edit. Run `--check` before committing any change that affects
pipeline output (algorithm tweaks, ground-truth corrections, plot-box edits)
and refresh the logs if it reports stale. See ADR-040 for the file format.

**Rename optical-specs MTF files to named suffixes (ADR-033):**

```bash
cd tools && py -m mtfdigitizer.rename <slug> --dry-run   # preview one folder
cd tools && py -m mtfdigitizer.rename <slug> --apply     # execute one folder
cd tools && py -m mtfdigitizer.rename --dry-run          # preview every folder
```

Reads each folder's `analysis.md` MTF charts list, maps numeric-suffix
files (`-mtf-1.png`, `-mtf-2.png`) to canonical named suffixes
(`-mtf-diffraction.png`, `-mtf-geometric.png`), and rewrites file
moves, `analysis.md` link tables, and `referenceset/charts.py`
`chart_path` literals atomically. Fails loud when a numeric file on
disk is unlabeled in `analysis.md`, when a label is unrecognised, or
when two files would collide on the same suffix (the zoom case
deferred to a follow-up PR). After applying, regenerate logs with
`py -m mtfdigitizer.log --all` (Tier 1) and
`py -m mtfdigitizer.extract --accept <slug>` (Tier 2) so the chart
path in each `digitization-log.md` matches the new file name. See
#1017 and ADR-033 §"MTF chart naming".

**Fujifilm-specific tooling (ADR-043, per-frequency chart family):**

```bash
cd tools && py -m mtfdigitizer.fuji_plotbox <chart.png>           # auto-detect plot box for one Fuji chart
cd tools && py -m mtfdigitizer.scripts.scaffold_fuji_tier2        # preview Tier 2 ReferenceChart entries
cd tools && py -m mtfdigitizer.scripts.scaffold_fuji_tier2 --write  # materialize _fuji_tier2_charts.py
cd tools && py -m mtfdigitizer.scripts.emit_fuji_tier2            # preview TS object literals
cd tools && py -m mtfdigitizer.scripts.emit_fuji_tier2 --write    # patch src/data/mtf-readings.ts
```

Fujifilm publishes one chart image per spatial frequency
(`-15lp.png`, `-20lp.png`, ...), so the standard single-image
extractor needs orchestration to merge per-frequency views. The
above tools handle that case end-to-end:

- **`fuji_plotbox`** — composes RGBA over white, detects gridlines +
  tick-label clusters, calibrates `image_height_mm` from the mount
  default (GF=26.9 mm, XF=14.2 mm — the sensor half-diagonal Fuji
  publishes MTF out to). 198/199 Fuji charts in the current corpus
  detect cleanly.
- **`scaffold_fuji_tier2`** — walks every `docs/optical-specs/fujifilm-*`
  folder, runs the detector, groups charts by lens, and emits a
  `_fuji_tier2_charts.py` module of Tier 2 `ReferenceChart` entries
  (60 lenses, 193 chart views as of #1058). Imported by `charts.py`
  via concat into `REFERENCE_CHARTS`.
- **`emit_fuji_tier2`** — translates the production digitization-log
  artifacts into TS `MtfData` literals and patches them into
  `src/data/mtf-readings.ts`. Handles prime (1 panel, all frequencies
  merged) and zoom (wide + tele × all frequencies) cases. Walks both
  Tier 1 anchors and Tier 2 bulk (every `fujifilm-permfreq` chart).
  Derives aperture and focal length from the slug; source URL is read
  from `lenses.ts:officialUrl` (fail-loud `KeyError` if missing) — see
  #1062.

Workflow when adding a new Fuji lens (or another brand using the
per-frequency convention): (1) drop the chart PNGs under the lens
folder; (2) re-run `scaffold_fuji_tier2 --write` to refresh the Tier 2
entries; (3) run `extract <slug> --accept` to commit the production
artifacts; (4) run `emit_fuji_tier2 --write` to update
mtf-readings.ts. The shared per-frequency orchestrator lives in
`tools/mtfdigitizer/per_frequency.py`.

**TTartisan-specific tooling (ADR-044, multi-aperture chart family):**

```bash
cd tools && py -m mtfdigitizer.scripts.scaffold_ttartisan_tier2          # preview Tier 2 ReferenceChart entries
cd tools && py -m mtfdigitizer.scripts.scaffold_ttartisan_tier2 --write  # materialize _ttartisan_tier2_charts.py
cd tools && py -m mtfdigitizer.scripts.emit_ttartisan_tier2              # preview TS object literals
cd tools && py -m mtfdigitizer.scripts.emit_ttartisan_tier2 --write      # patch src/data/mtf-readings.ts
```

TTartisan publishes one chart image per lens packing TWO apertures by
color encoding (black + grey at max aperture, red + orange at the
stopped aperture). The orchestrator (`extract.py:_run_view_passes`,
ADR-044) fans out one extractor pass per aperture, each with the
profile's hues filtered to one aperture's bucket. Inspection
artifacts (SVG / overlay PNG / review HTML) get an aperture suffix
so the two passes don't overwrite each other's files.

- **`ttartisan_plotbox`** — classifies each chart by counting two-digit
  x-axis tick labels (APS-C: 0/3/7/10/13 → image_height 14 mm; GFX or
  full-frame: 0/5/10/15/20 → image_height 20.5 mm) and returns a
  hand-verified template-constant plot box per scheme. Pixel auto-
  detection drifts ±2 px across the 19-chart cohort; the constants
  ship as the single source of truth.
- **`scaffold_ttartisan_tier2`** — walks `docs/optical-specs/
ttartisan-*`, runs the classifier, and writes a
  `_ttartisan_tier2_charts.py` module of 19 `ReferenceChart` entries.
  Per-lens (max, stopped) aperture pair eye-read from each chart's
  legend and shipped in the script's `_APERTURES_BY_SLUG` table —
  pixel-OCR of the legend text was too unreliable (8/19 correct on
  the 800x600 template).
- **`emit_ttartisan_tier2`** — emits TWO `MtfChart` panels per literal
  (one per aperture pass), with the actual f-numbers from
  `chart.apertures[i]` aligned positionally with the profile's
  `apertures_per_chart` labels. `source` URL from `lenses.ts:
officialUrl` (fail-loud `KeyError` if missing — see #1062).

Workflow when adding a new TTartisan lens (or another brand using
the multi-aperture-by-color convention): (1) drop the chart PNG under
the lens folder; (2) add the lens's (max, stopped) aperture pair to
`_APERTURES_BY_SLUG` (eye-read from the chart legend); (3) re-run
`scaffold_ttartisan_tier2 --write` to refresh the entries; (4) run
`extract <slug> --accept` per lens once the two-aperture overlays
look correct; (5) run `emit_ttartisan_tier2 --write` to patch
mtf-readings.ts with the cohort.

**Samyang-specific tooling (ADR-063, two-panel stacked-aperture family):**

```bash
cd tools && py -m mtfdigitizer.scripts.scaffold_samyang_tier2          # preview Tier 2 ReferenceChart entries
cd tools && py -m mtfdigitizer.scripts.scaffold_samyang_tier2 --write  # materialize _samyang_tier2_charts.py
```

Samyang publishes one chart image per lens with TWO stacked panels:
MAX aperture on top, F8 below. Both panels share the same hue palette;
only the plot box differs. The orchestrator uses the per-view aperture
override on `ChartView` (ADR-063): the primary view emits at the
chart's first aperture label (`"MAX"`), an `additional_view` with its
own `plot_box` and `aperture="F8"` emits the F8 panel. Inspection
artifacts get a `-F8` suffix for the second pass so the two views'
overlay/SVG/HTML don't overwrite each other.

- **`samyang_plotbox`** — auto-detects both panel plot boxes per chart
  via permissive-threshold axis-line probes. Handles all three canvas
  widths Samyang publishes (462/490/498 px) and the AF-series charts
  (different x_right, slightly shifted F8 y-range) uniformly. No
  per-slug plot-box overrides needed.
- **`scaffold_samyang_tier2`** — walks `docs/optical-specs/samyang-*`,
  runs the detector per chart, and writes a `_samyang_tier2_charts.py`
  module of 18 `ReferenceChart` entries with `additional_views=
(ChartView(plot_box=<F8>, aperture="F8"),)`. Per-lens
  `image_height_mm` ships in the script's `_IMAGE_HEIGHT_MM_BY_SLUG`
  table (eye-read from the chart's x-axis tick labels — typically 21.6
  for full-frame, 14.2 for APS-C; Samyang 8mm and 12mm fisheyes are
  APS-C despite no `-cs` slug suffix).

Workflow when adding a new Samyang lens (or another brand using the
multi-panel stacked-aperture convention): (1) drop the chart PNG under
the lens folder; (2) add the lens's `image_height_mm` to
`_IMAGE_HEIGHT_MM_BY_SLUG`; (3) re-run `scaffold_samyang_tier2
--write` to refresh the entries; (4) run `extract <slug> --accept`
per lens once the two-panel overlays look correct.

**Tier 1 anchor helper generation (cross-brand):**

```bash
cd tools && py -m mtfdigitizer.scripts.scaffold_anchor_helpers <slug>          # preview
cd tools && py -m mtfdigitizer.scripts.scaffold_anchor_helpers <slug> --write  # materialize
cd tools && py -m mtfdigitizer.scripts.scaffold_anchor_helpers <slug> --check  # exit 1 if stale
```

For a Tier 1 anchor `<slug>` (i.e. a `ReferenceChart` whose
`ground_truth` is set in `charts.py`), generates two maintainer
artifacts in the lens's `docs/optical-specs/<slug>/` folder:
per-view readhelper PNGs (3x upscale with green sample-position
lines + mm labels at top, plus orange dashed gridlines filling in
every 0.05 OTF the source chart does not print natively — ±0.02
eye-precision against a uniform 0.05 grid), and `eye-read.md`
(legend + tables pre-populated with the extractor's predictions —
ADR-048's cell-level marking convention: bare = silent verification,
`!` = corrected, `?` = unknown / will become None). On re-run the
scaffolder PRESERVES `!`/`?` marks and refreshes unmarked cells.

Style-family dispatch:

- `fujifilm-permfreq` — one readhelper per spatial frequency
  (`-15lp-readhelper.png`, etc.). Helper base = the per-freq source
  PNG. Orange dashed gridlines added at every 0.05 OTF except the
  chart's own printed 0.2-step lines (Fuji prints 0.0/0.2/0.4/0.6/
  0.8/1.0 natively). GT-snippet skeleton uses
  `_FUJI_<COHORT>_<FL>_GT` (e.g. `_FUJI_GF_23_GT`).
- `ttartisan-4color-dual-aperture` — one readhelper per aperture
  (`<stem>-max-readhelper.png`, `<stem>-stopped-readhelper.png`).
  Helper base = the **clean source chart PNG** (never the extractor
  overlay), so the maintainer's eye-read is not biased by the
  extractor's traced curves. Use the `<stem>-<aperture>-overlay.png`
  - the review HTML separately when comparing extractor output to
    the chart. Orange dashed gridlines added at 0.05, 0.15, ..., 0.95
    (TTartisan prints 0.1-step natively). GT-snippet skeleton uses
    `_TTARTISAN_<FL>_GT` with `"max"` / `"stopped"` aperture buckets
    (NOT f-numbers — the orchestrator keys `results_by_aperture` on
    the profile's `apertures_per_chart` tuple; mismatched keys
    fail-loud in calibrate.py). For `ttartisan-af-NNmm-...` and
    `ttartisan-tilt-NNmm-...` slugs the GT-var prepends the variant:
    `_TTARTISAN_AF_NN_GT` / `_TTARTISAN_TILT_NN_GT` (kept in sync
    between `eyeread.gt_var_for_chart` and
    `scaffold_anchor_helpers._gt_var_for_chart`).

Workflow for promoting a lens to Tier 1: (1) add a `ReferenceChart`
entry to `REFERENCE_CHARTS` in `charts.py` with `_<LENS>_GT` of
None placeholders + the preamble comment template; (2) add the slug
to the brand scaffolder's `_TIER1_SKIP_SLUGS` so re-runs don't
re-introduce the duplicate; (3) re-run the brand scaffolder
(`--write`) so `_<brand>_tier2_charts.py` drops the entry; (4) run
`scaffold_anchor_helpers <slug> --write` to emit the readhelper
PNGs + `eye-read.md`; (5) maintainer reviews `eye-read.md`,
overwrites wrong cells with `!`, marks unreadable cells with `?`;
(6) `py -m mtfdigitizer.eyeread <slug> --apply` transcribes the
file into `_<LENS>_GT` in `charts.py`; (7)
`py -m mtfdigitizer.calibrate` reports per-field median |Δ| against
the new anchor. To add a new style family, extend
`_resolve_helper_views` and `_extras_for` in
`scaffold_anchor_helpers.py`.

**When an eye-read cell changes after Tier 1 promotion (#1201)**:
GT in `charts.py` is the truth anchor, but the user-facing artifacts
are rendered from the **extractor's output**, not the GT. If the
extractor still produces the old value, three downstream artifacts
must be hand-patched to match GT:

1. `src/data/mtf-readings.ts` — the website's source data; emitted by
   `emit_*_tier2 --write`; future emit runs will overwrite the patch
   unless the extractor is fixed (track the risk via a follow-up
   issue, see #1202).
2. `docs/optical-specs/<slug>/<stem>-<aperture>.svg` — provenance
   SVG rendered by `render_svg(extracted)` in `extract.py`. Hand-patch
   the polyline points + dot circles to the corrected y coordinates.
3. `docs/optical-specs/<slug>/<stem>-<aperture>-overlay.png` — the
   overlay on the original chart, rendered by `render_overlay(
extracted.readings, ...)` in `review.py`. Re-render with a one-shot
   probe script that calls `render_overlay()` directly with the
   readings dict patched at the corrected fractions, then delete the
   probe.

`digitization-log.md` is intentionally NOT patched — it is the
auto-generated diagnostic record of the extractor's actual output and
remains the signal for the future extractor fix. Document the
hand-patches in `eye-read.md` under a "Manual artifact patches"
section so a future maintainer / re-emit knows the discrepancy is
intentional.

**Before authoring an `analysis.md` MTF charts list for a folder that
does not yet have one:** check the source product page for parallel
chart sets. Multi-mount lenses (DG DN releases with a later Fujifilm X
mount addition, lenses with optional teleconverters) often publish
the same wide/tele chart pair multiple times — once per mount / TC
configuration. Match each numeric-suffix file on disk against the
source page's chart-section DOM order before transcribing labels.
Wuseria is X-mount only, so keep only the X-mount chart set; delete
the L/Sony FF and TC-only variants. Trusting an unverified prose
summary caused #1032 (the Sigma 100-400mm incident).

**Run the MTF digitizer render-match scorer:**

```bash
cd tools && py -m mtfdigitizer.scorer
```

Sister to `calibrate`: runs `extract_chart()` then `score_chart()` against the
same runnable subset, reports per-field render-match IoU + a polyline-on-skeleton
precision side metric + an aggregate. The IoU half of the threshold calibration
described in `tools/mtfdigitizer/referenceset/REFERENCE_SET.md` §"What
'calibration against the set' actually means". Output: stdout only. Findings
live in `tools/mtfdigitizer/referenceset/scoring.md` — update after a run that
materially changes the numbers. Reference scoring entries when discussing the
0.75 IoU threshold revision (the first run found the threshold fails 3/3
charts due to sparse-polyline vs dense-skeleton size asymmetry).

**Run the MTF digitizer plausibility-priors runner:**

```bash
cd tools && py -m mtfdigitizer.plausibility
```

Runs `extract_chart()` then `check_all()` against the same runnable subset,
reports which of the four physical-plausibility priors (`center_ge_edge`,
`ten_ge_thirty`, `not_suspiciously_flat`, `in_range`) fire per chart. The
second of the two confidence signals ADR-038 §"Confidence signal" requires —
catches render-match's flat-axis blind spot (the 300mm reflex case).
Output: stdout only. Findings live in
`tools/mtfdigitizer/referenceset/plausibility.md` — update after a run that
materially changes the numbers.

**Run the MTF digitizer auto-triage gate:**

```bash
cd tools && py -m mtfdigitizer.autotriage
```

Combines both confidence signals into one HIGH/LOW verdict per
extraction pass (ADR-052 — one per (chart, aperture) for ADR-044
multi-aperture; one per chart for single-aperture):
`precision ≥ 0.80 AND IoU ≥ 0.20 AND priors_pass` ⇒ HIGH, else LOW with
reason codes. Reason codes route attention to extractor-side work
(`precision_below_threshold`, `iou_below_threshold`,
`render_match_undefined`) vs chart-side work (`prior_failed_*`). Stdout
prints the per-pass verdict and aggregate; also writes one 3-panel
review file per LOW pass under `docs/optical-specs/<slug>/` (HIGH passes
skip, per ADR-038 §"Workflow"). Multi-aperture review files carry the
aperture suffix (`<slug>-{max,stopped}-review.html`) per ADR-044 + ADR-052.
The runner covers every chart with a `plot_box` (currently 101 of 103,
producing ~120 per-pass verdicts) — the ground-truth filter that
restricted earlier runs to the 14 calibration charts was lifted in
ADR-052. Findings live in `tools/mtfdigitizer/referenceset/triage.md` —
update after a run that materially changes the numbers. LOW passes are
the authoritative input for RC investigation: consume the `*-review.html`
files plus the reason codes, not eye-read diagnostics.

**Render an MTF chart's provenance SVG from its readings:**

```bash
cd tools && py -m mtfdigitizer.svg              # writes SVGs for the 3 runnable charts
cd tools && py -m mtfdigitizer.svg --check      # dry-run for CI/tests
```

Pure-Python SVG writer over `ExtractedChart` readings. Provenance role
only: lens-page rendering stays with `src/components/static/MtfChart.astro`,
which renders from the same `MtfData` shape at build time. Output:
`docs/optical-specs/<slug>/<chart-stem>.svg`. ViewBox 320×218 — the data
area is at the same coordinates as `MtfChart.astro` (320×200), the extra
18px is a legend strip the standalone SVG carries in-document. Honors
the B2 None contract: a None reading breaks the polyline at that vertex.

**Render an MTF chart's 3-panel review file:**

```bash
cd tools && py -m mtfdigitizer.review           # writes review files for every runnable reference chart
cd tools && py -m mtfdigitizer.review --check   # dry-run for CI/tests
```

Emits one static HTML composite per chart (left = original PNG, right =
SVG from #971, bottom = overlay PNG with extractor polylines registered
to the same `PlotBox`). The standalone runner emits for every runnable
chart (useful for on-demand maintainer inspection of a HIGH chart); the
autotriage runner emits only for LOW charts (the production workflow,
per ADR-038 §"Workflow"). Output: `<chart-stem>-review.html` +
`<chart-stem>-overlay.png` under `docs/optical-specs/<slug>/`. HTML is
JS-free per the ADR — a viewer, not an editor. Replaces the deprecated
`tools/mtf-overlay.html` whose hand-tuned calibration is superseded by
deterministic plot-box registration.

ADR-044 multi-aperture charts (TTartisan cohort) fan out to one
`(review HTML, overlay PNG)` pair per aperture pass via
`aperture_passes_for_view`, with stems `<chart-stem>-<aperture>` (e.g.
`ttartisan-50mm-f1-2-mtf-max-review.html` +
`ttartisan-50mm-f1-2-mtf-stopped-review.html`). Matches `svg.py`'s
`<chart-stem>-<aperture>.svg` and the per-pass review files
`autotriage.py` writes. Single-aperture charts keep their existing
1-pair output with no `-<aperture>` suffix.

**Refresh stale review artifacts (regenerate-and-commit hygiene):**

When the extractor changes shift overlay geometry, the committed
`<chart-stem>-overlay.png` artifacts drift from their source. The
refresh workflow:

1. Branch: `chore/refresh-stale-overlays` (or scope-specific name).
2. Run `py -m mtfdigitizer.review` from `tools/`.
3. **Filter platform noise from real diffs:** the regenerator writes
   CRLF line endings on Windows; HTMLs with no template changes still
   show as `M` in `git status`. Use `git diff --ignore-all-space <file>`
   to identify CRLF-only diffs — drop them with `git checkout --`
   before staging. Real changes are the binary PNG diffs and any
   genuinely new/changed HTML content.
4. **Visual spot-check each refreshed PNG:** open the overlay in any
   image viewer and confirm polylines trace the source curves cleanly.
   Binary diffs are opaque to `git diff`; the visual check is the only
   way to catch a buggy regenerator producing garbage that still
   tests-pass.
5. Stage only the real artifact changes (+ any genuinely missing
   review pairs surfaced by the run). Commit as `chore(mtf):` with
   a note on which extractor change drove the refresh.

**Emit a digitized chart's readings as a TypeScript literal for the site:**

```bash
cd tools && py -m mtfdigitizer.emit <slug>                        # measured (default)
cd tools && py -m mtfdigitizer.emit --mtf-type=computed <slug>   # Sigma / Fujifilm
cd tools && py -m mtfdigitizer.emit <slug> <slug>                # multiple
```

Bridges the digitizer's `ExtractedChart` Python output to the site's
`MtfData` shape in `src/data/mtf-readings.ts`. Prints the TS object
literal to stdout; per-field null counts to stderr. Paste into
`mtf-readings.ts` and `npm run check && npm run build` to verify.
The lens page picks it up via `mtfReadings[slug]` and renders via
`MtfChart.astro` (themed inline SVG + table). Closes the digitizer→site
loop ADR-038 §"Output" envisaged; the committed provenance SVG (from
`mtfdigitizer.svg`) stays an artifact, not the display source.

`--mtf-type` selects the `mtfType` field on the emitted entry: `computed`
for manufacturer optical-design charts (Sigma, Fujifilm), `measured` for
review-lab charts from a tested sample (LensTip, Optical Limits). Default:
`measured` (matches the campaign's majority case).

The slug must be in `referenceset/charts.py` with a populated `plot_box`,
and the source URL must be in `_DEFAULT_SOURCES` (in `emit.py`). For
zooms (multi-view charts via `additional_views`), the slug must also be
in `_DEFAULT_FOCAL_LENGTHS` with one mm value per view in primary-then-
additional order — emit raises a clear error if missing. Per ADR-033 every
published focal-length panel becomes its own `MtfChart` entry with
`focalLength` set; the detail page labels each block "f/X.X @ Nmm".
Per ADR-041 production-tier charts can emit with `ground_truth=None`.
Rows with all four fields null are dropped; `MtfReading` fields are
`number | null` (since the lens-page MTF rendering work) so the B2 None
contract flows through.

**Audit spec field coverage per brand:**

```bash
npx tsx scripts/audit-brand.ts              # all brands summary
npx tsx scripts/audit-brand.ts Fujifilm     # single brand detail
```

**Fetch Fujifilm optical specs, images, and coatings (Playwright):**

```bash
py tools/fujifilm/fetch_specs.py                    # fetch all missing data
py tools/fujifilm/fetch_specs.py --dry-run           # list what would be fetched
py tools/fujifilm/fetch_specs.py --filter gf         # filter by model substring
py tools/fujifilm/fetch_specs.py --specs-only        # only extract specs text
py tools/fujifilm/fetch_specs.py --images-only       # only download images
py tools/fujifilm/fetch_specs.py --coatings-only     # only extract coatings
py tools/fujifilm/audit.py                           # audit data completeness
py tools/fujifilm/audit.py --missing                 # show only incomplete lenses
```

**Fetch Samyang optical specs, MTF charts, and construction diagrams (urllib):**

```bash
py tools/samyang/fetch_specs.py                    # fetch all (specs + images)
py tools/samyang/fetch_specs.py --dry-run           # list lenses without fetching
py tools/samyang/fetch_specs.py --filter 12mm       # filter by model substring
py tools/samyang/fetch_specs.py --specs-only        # only extract specs text
py tools/samyang/fetch_specs.py --images-only       # only download images
py tools/samyang/audit.py                           # audit data completeness
py tools/samyang/audit.py --missing                 # show only incomplete lenses
```

**Fetch Samyang MTF charts:**

```bash
py scripts/fetch-samyang-mtf.py             # fetch all to docs/mtf-charts/
py scripts/fetch-samyang-mtf.py --seq 351   # fetch one by product seq
py scripts/fetch-samyang-mtf.py --dry-run   # list without downloading
py scripts/fetch-samyang-mtf.py --temp      # download to temp/ (testing)
```

**Fetch Sigma optical specs, MTF charts, and construction diagrams (urllib):**

```bash
py tools/sigma/fetch_specs.py                    # fetch all (specs + images)
py tools/sigma/fetch_specs.py --dry-run           # list lenses without fetching
py tools/sigma/fetch_specs.py --filter 12mm       # filter by model substring
py tools/sigma/fetch_specs.py --specs-only        # only extract specs text
py tools/sigma/fetch_specs.py --images-only       # only download images
py tools/sigma/audit.py                           # audit data completeness
py tools/sigma/audit.py --missing                 # show only incomplete lenses
```

**Fetch Viltrox optical specs and download images (Shopify JSON + HTML scraping):**

```bash
py tools/viltrox/fetch_specs.py                    # fetch all specs from Shopify API
py tools/viltrox/fetch_specs.py --dry-run           # list lenses without fetching
py tools/viltrox/fetch_specs.py --filter 13mm       # filter by model substring
py tools/viltrox/download_images.py                 # download all theme images to cache
py tools/viltrox/download_images.py --dry-run       # list image URLs only
py tools/viltrox/download_images.py --filter 27mm   # filter by model substring
py tools/viltrox/audit.py                           # audit data completeness
py tools/viltrox/audit.py --missing                 # show only incomplete lenses
```

**Fetch Tamron optical specs (urllib, dual-page parsing — main + /spec.html):**

```bash
py tools/tamron/fetch_specs.py                    # fetch all specs + images
py tools/tamron/fetch_specs.py --dry-run           # list lenses without fetching
py tools/tamron/fetch_specs.py --filter 17-70mm    # filter by model substring
py tools/tamron/audit.py                           # audit data completeness
py tools/tamron/audit.py --missing                 # show only incomplete lenses
```

**Fetch Tokina optical specs (urllib, alt-text scraping):**

All 11 brands are migrated onto the `pagefetch` + `brandkit` architecture
(ADR-035) — brand parsing lives in `tools/<brand>/extractor.py`, the pipeline
in `brandkit`; `fetch_specs.py`/`audit.py` are thin delegators. The same
flags work for every brand (substitute the brand directory below). The
`--verify` flag (#779) cross-validates stored physical specs against the
official page — implemented for all brands except zeiss (N/A, PDF-only).
When using `--verify` to drive a `lenses.ts` data pass, confirm the
extractor is reliable first: a systematic extraction bug makes `--verify`
report false divergences and blindly applying its page values corrupts good
data (e.g. #906 truncated comma-formatted weights). Treat a physically
implausible page value as a tool bug, fix and re-verify; cross-check a
suspect official page (e.g. an `/en-us/` page serving the wrong lens's
data) against `/global/` or an independent source before overwriting.
Tokina shown as the example:

```bash
py tools/tokina/fetch_specs.py                    # fetch all specs + images
py tools/tokina/fetch_specs.py --dry-run           # list lenses without fetching
py tools/tokina/fetch_specs.py --filter 23mm       # filter by model substring
py tools/tokina/fetch_specs.py --verify            # cross-validate physical specs (#779)
py tools/tokina/audit.py                           # audit data completeness
py tools/tokina/audit.py --missing                 # show only incomplete lenses
```

**Fetch Carl Zeiss Touit PDF datasheets (discontinued lenses, no live pages):**

```bash
py tools/zeiss/fetch_specs.py                     # download all PDF datasheets
py tools/zeiss/fetch_specs.py --dry-run            # list lenses without downloading
py tools/zeiss/fetch_specs.py --filter 12mm        # filter by model substring
py tools/zeiss/audit.py                            # audit data completeness
py tools/zeiss/audit.py --missing                  # show only incomplete lenses
```

Note: Zeiss MTF charts and construction diagrams must be extracted manually from the downloaded PDFs.

**Fetch TTartisan optical specs (urllib, spec table + prose parsing):**

```bash
py tools/ttartisan/fetch_specs.py                    # fetch all specs + images
py tools/ttartisan/fetch_specs.py --dry-run           # list lenses without fetching
py tools/ttartisan/fetch_specs.py --filter 23mm       # filter by model substring
py tools/ttartisan/fetch_specs.py --specs-only        # only extract specs text
py tools/ttartisan/fetch_specs.py --images-only       # only download images
py tools/ttartisan/audit.py                           # audit data completeness
py tools/ttartisan/audit.py --missing                 # show only incomplete lenses
```

Note: TTartisan pages use two site patterns — main site (ttartisan.com) with
query-param routing and Shopify store (ttartisan.store). Some pages embed
Shopify CDN images not detectable by the scraper. Some older pages use
legacy timestamp URLs instead of named Specification-\*.webp files.
Construction diagrams are authoritative for special elements — page text
often omits glass types that diagrams show.

**Fetch Venus Laowa optical specs (SeleniumBase UC mode — Cloudflare bypass):**

```bash
py tools/venus/fetch_specs.py                    # fetch all specs + images
py tools/venus/fetch_specs.py --dry-run           # list lenses without fetching
py tools/venus/fetch_specs.py --filter 10mm       # filter by model substring
py tools/venus/fetch_specs.py --specs-only        # only extract specs text
py tools/venus/fetch_specs.py --images-only       # only download images
py tools/venus/audit.py                           # audit data completeness
py tools/venus/audit.py --missing                 # show only incomplete lenses
```

Note: venuslens.net uses Cloudflare Turnstile which blocks plain urllib and
Playwright. Requires `py -m pip install seleniumbase` (installs Undetected
Chrome driver). Runs headed (non-headless) — a browser window will open
briefly per page. Some construction diagrams use Chinese filenames not
detectable by the tool; manual page inspection may find additional images.

**Extract MTF readings from chart PNGs:**

Use `tools/mtfdigitizer/` — unified digitizer per ADR-038. Requires Python

- scikit-image + opencv-python.

Charts live per-lens under `docs/optical-specs/<slug>/` (ADR-033) as
`mtf-chart.{png,jpg}`, or `mtf-f<aperture>.png` per aperture.

Five chart families have declared profiles today (Sigma, Samyang,
7Artisans, Tokina, Viltrox). Profile declaration is the authority; an
unrecognized chart fails loud rather than being mis-traced (ADR-038 §1).

The end-to-end entry point is `extract_chart(image_path, profile,
plot_box, image_height_mm)` (no CLI yet — callable from Python). See
`tools/mtfdigitizer/README.md` for the dispatch table and known limits.

Run the calibration suite against the reference set:

```bash
cd tools
py -m mtfdigitizer.calibrate
```

**List unscored lenses:**

```bash
npx tsx scripts/list-unscored.ts           # list all lenses without optical scores
```

**Compute genre marks:**

```bash
npx tsx scripts/compute-marks.ts print      # print all computed marks
npx tsx scripts/compute-marks.ts patch       # patch lenses.ts with marks
```

### 2.8 Fill and verify tech specs per brand

#### Phase 1 — Prepare

1. **Verify the brand's full lineup** — confirm every X-mount and GFX lens
   the brand offers before researching individual specs. Cross-reference
   official catalog, retailers (B&H, Adorama), and
   [alikgriffin.com](https://alikgriffin.com/a-complete-list-of-fujifilm-x-mount-lenses/).
   Create a separate issue for any missing lenses.
2. **Audit gaps** — run `npx tsx scripts/audit-brand.ts <Brand>`
3. **Run extraction tool** if available: `py tools/<brand>/fetch_specs.py`

#### Phase 2 — Research each lens

4. **Generate research URLs** — `py tools/lookup.py "<lens name>"`
5. **Check each source** and record result in `specs-log.md` (found / not found / 404 / paywall).
   Every specs-log MUST include a row for at least these five sources:
   - Official manufacturer page
   - LensTip (`py tools/lenstip/search.py "<lens>"` resolves the page ID)
   - Radojuva
   - DPReview
   - Google Image Search (construction diagram + MTF chart)
   - If these five come up empty, continue down the source reference table
     below until data is found or all sources are exhausted
6. **Check Shopify JSON for embedded images** — if the official site is
   Shopify-based, fetch `<product-url>.json` and extract image URLs from
   `body_html`. Construction diagrams, MTF charts, and spec tables are
   often embedded as images invisible to text scraping. Download and
   visually inspect candidate images.
7. **Verify EVERY field, not just optical ones** — cross-check the full DB entry
   against official + LensTip + B&H (+ retailer/press as needed), field by field:
   optical (element/group counts, special elements, coatings) AND physical
   (`weight`, `diameter`, `length`, `apertureBlades`, `filterThread`,
   `minFocusDistance`, `maxMagnification`, `year`). The physical fields are where
   pre-existing rows hide the most errors — they are not optional. When auditing an
   existing lens, build a DB-value-vs-each-source table and resolve every mismatch;
   do not assume a field already present is correct.

#### Phase 3 — Commit per lens

8. Update `specs-log.md` FIRST — the specs-log is the primary deliverable
9. Edit `lenses.ts` — apply the verified data
10. Confirm both files updated before moving to the next lens
11. Run `npm run validate`
12. If adding `maxMagnification` to a scored lens, also add `macro` genre mark

#### Maintenance

- **Audit false negatives** — `py tools/lenstip/audit_specslog.py --fix`
- **Rebuild LensTip index** quarterly — `py tools/lenstip/build_index.py`

#### Source reference (priority order)

| Source                        | Best for                                  | Notes                                  |
| ----------------------------- | ----------------------------------------- | -------------------------------------- |
| Official manufacturer         | Dimensions, filter thread, build features | Always check first                     |
| DPReview                      | Comprehensive specs incl. magnification   | Archived but still available           |
| LensTip                       | maxMagnification on budget lenses         | Opaque numeric IDs — use the index     |
| Radojuva                      | Hands-on magnification measurements       | Multi-language, search all variants    |
| digitalkamera.de              | Dimensions                                | Rarely has magnification               |
| cameradecision.com            | Spec comparison                           | 403s on direct fetch, use Playwright   |
| Mobile01                      | Construction diagrams, Chinese brands     | Requires SeleniumBase UC               |
| Photography Life              | Spec tables, diagrams, special elements   | Predictable URL pattern                |
| Dustin Abbott / Phillip Reeve | Trust-3 field measurements                | Thorough optical analysis              |
| Duclos Lenses                 | Cinema lens specs                         | Length, weight, min focus              |
| Google Image Search           | Construction diagrams, MTF charts         | Text searches miss non-English sources |

#### Caveats

- **LensTip IDs:** URL names are ignored; only the numeric ID matters. Verify
  `Manufacturer` and `Model` on the page — wrong IDs redirect silently.
- **Image filenames:** do not filter by filename keywords — news sites use
  generic names (e.g. `APO200F14-lens.jpg` for a combined diagram + MTF).
  For pages with < 10 images, visually check all content images.
- **Mount variants:** if lenses share optical design across mounts, update
  BOTH specs-logs.
- **Shopify section images (`/cdn/shop/files/`):** diagrams and MTF charts often
  live NOT in the product gallery (`product.images[]`) nor inline `body_html`, but
  as theme/section graphics referenced only in the rendered page HTML (filenames
  like `MTF_Template.jpg`, `01.png`, `50mm-F0_6.jpg`). Scrape the full rendered HTML
  for `cdn/shop/files/*.{jpg,png}` and open **EVERY** one — do NOT sample a subset
  (a hand-picked range silently skips the one image that has the diagram/MTF). For a
  set of N images, download all and build a contact sheet to scan at once. Note the
  product _page_ and the product _gallery_ (`product.images[]`) are DIFFERENT image
  sets — check both. Also check the brand's official Amazon/regional store listings
  (US, SG, UK), which often host the highest-res official composite (diagram + MTF)
  and state coatings the `.com` store omits. Request the largest image with `?width=3200`.
- **Cropping the diagram/MTF out of a composite:** use `tools/crop-artifact.py` —
  do NOT hand-guess pixel coordinates (they silently truncate or off-center the
  result). It detects the content bounding box from the corner-median background:

  ```bash
  py tools/crop-artifact.py in.jpg --out construction-diagram.jpg            # auto bbox
  py tools/crop-artifact.py in.jpg --split --left  --out construction-diagram.jpg  # left half of a side-by-side composite
  py tools/crop-artifact.py in.jpg --split --right --out mtf-chart.jpg              # right half
  py tools/crop-artifact.py in.jpg --region 120,80,1480,1040 --out mtf-chart.jpg    # explicit box when auto over/under-reaches
  py tools/crop-artifact.py in.jpg --check                                   # advisory edge-touch report (non-blocking)
  ```

  Always eyeball the output — a tight axis box or a wide lens housing legitimately
  reaches the margin, so `--check` is advisory only.

- **Generation check (Mark II vs original):** before trusting a "Mark II" row,
  confirm the entry's generation against the official **page title** and the lens's
  specs (not the URL slug alone). Rows created by copying the original frequently
  retain the original's `year`, `maxMagnification`, `apertureBlades`, and
  `filterThread` while carrying Mark II optical construction. Verify each against the
  Mark II's own LensTip entry / spec table. Ensure the model name includes the
  generation marker per the naming convention.
- **Source-conflict resolution:** when LensTip (or any secondary source) contradicts
  the official page on construction, the official page wins. If a secondary source is
  wrong on one verifiable field, treat ALL its unverified fields as suspect (it may be
  mis-cataloged for the lens) — do NOT adopt its other figures. Leave a field
  unresolved and flagged rather than overwrite with a contradicted source.
- **Discontinuation:** judge from the official `.js` storefront endpoint
  (`<product-url>.js` → `available` per variant), NOT the page's "Sold out" text — a
  sold-out variant is not a discontinued lens. All-variant `available:false` + a
  "Used" listing + a successor model = discontinued (`isDiscontinued: true`).
- **alikgriffin.com tables:** AJAX-loaded (Ninja Tables plugin), not in page
  HTML. Use the admin-ajax API endpoint or ask the user to paste the table.
- **DuckDuckGo fallback:** when Google or Bing block with CAPTCHAs, use
  DuckDuckGo HTML search — it works with plain urllib (~1s):
  `py -m pagefetch "https://html.duckduckgo.com/html/?q=<query>"` (from `tools/`)

## 3. Quality

### 3.1 Validate pipeline

The full quality gate runs all checks in sequence. Run before every commit:

```bash
npm run validate
```

Pipeline steps (exits on first failure):

| Step       | Command               | What it checks                                    |
| ---------- | --------------------- | ------------------------------------------------- |
| Lint       | `npm run lint`        | ESLint + sonarjs — code smells, unused vars       |
| Format     | `npm run format`      | Prettier — consistent style                       |
| Type check | `npm run check`       | astro check — `.astro` files and TypeScript types |
| Test       | `npm test`            | Vitest — unit + component tests with coverage     |
| Build      | `npm run build`       | Astro build — full static site generation         |
| Link check | `npm run check:links` | Trailing slash validation on internal links       |

Manual / scheduled (network — not in `validate`):

| Check          | Command                        | What it checks                                                                                                                                                                                                                                 |
| -------------- | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| External links | `npm run check:external-links` | Every external URL in `src/data/*.ts` (officialUrl + review links) is reachable. Bot-blocked/rate-limited hosts (403/429/503/timeout) report as UNVERIFIABLE, not dead. Runs weekly via `external-links.yml`; also a pre-release check (§5.1). |

### 3.2 Pre-commit hooks (husky + lint-staged)

Every commit is gated by `.husky/pre-commit`. Runs automatically — no manual
step needed.

**What runs:**

1. `gitleaks protect --staged` — blocks commits containing secrets (skipped if
   gitleaks is not installed locally)
2. `lint-staged` — runs per file type on staged files only:
   - `*.{ts,tsx}` — `eslint --fix` + `prettier --write`
   - `*.astro` — `prettier --write`
   - `*.{json,md,css}` — `prettier --write`

Configuration: `lint-staged` key in `package.json`, hook in `.husky/pre-commit`.

### 3.3 Formatting (Prettier)

Prettier owns all formatting — no style debates in code review. Runs at all
three quality gate layers (editor on save, pre-commit via lint-staged, CI via
`npm run format`).

```bash
npm run format              # check (CI mode, exits non-zero on diff)
npx prettier --write <file> # fix a single file
```

Configuration: `.prettierrc` + `prettier-plugin-astro` for `.astro` files.

### 3.4 Type checking (astro check)

Validates `.astro` files, TypeScript types, and content schemas. Part of the
validate pipeline.

```bash
npm run check
```

Catches type errors that ESLint and the TypeScript compiler miss in `.astro`
files — Astro's template syntax requires its own checker.

### 3.5 Testing (Vitest)

**Run tests (single run with coverage):**

```bash
npm test
```

Coverage text summary prints to the console. Threshold enforcement: statements
85%, branches 80%, functions 90%, lines 85%.

**Watch mode (development):**

```bash
npm run test:watch
```

**Generate local reports (coverage + test results):**

```bash
npm run test:report
```

Generates:

- `reports/tests/index.html` — interactive HTML test report (pass/fail, timing, filter by file)
- `reports/coverage/index.html` — interactive HTML coverage map (click into files, see uncovered lines)

Open either in a browser. The `reports/` directory is gitignored.

**Writing tests:**

- Test factories in `src/test/factories.ts` — use `makeLens`, `makeExplorerLens`,
  `makeCamera` instead of inline objects
- `makeExplorerLens` mirrors the `ExplorerLens` shape (booleans default to
  `undefined`, matching real data)
- Use `getAllByText` for explorer content (table + cards both render)
- Use `getByRole("combobox", { name: /label/i })` for select filters
- Use `screen.getAllByRole("button", { name: "Yes" })` for boolean chip filters

**Test structure:**

| File                                                                | Covers                                         |
| ------------------------------------------------------------------- | ---------------------------------------------- |
| `src/utils/scoring.test.ts`                                         | Genre scoring, OQ, helpers, field picker       |
| `src/utils/formatting.test.ts`                                      | Shutter + FL formatting                        |
| `src/utils/slug.test.ts`                                            | URL slug generation                            |
| `src/hooks/useSort.test.ts`                                         | Sort hook (strings, numbers, booleans, nulls)  |
| `src/hooks/useUrlFilters.test.ts`                                   | URL filter sync hook                           |
| `src/data/lenses.test.ts`                                           | Data validation (uniqueness, ranges, booleans) |
| `src/data/genres.test.ts`                                           | Genre config validation                        |
| `src/components/interactive/LensExplorer/LensExplorer.test.tsx`     | Lens filters + sort                            |
| `src/components/interactive/CameraExplorer/CameraExplorer.test.tsx` | Camera filters + sort                          |
| `src/components/interactive/GenreGuide/GenreGuide.test.tsx`         | Genre tabs, filters, matrices                  |
| `src/components/interactive/GenreGuide/exposure.test.ts`            | Exposure calculations                          |

### 3.6 Code quality (eslint-plugin-sonarjs + unicorn)

SonarQube-equivalent code smell detection runs via ESLint at all three quality
gate layers (editor, pre-commit, CI). Type-checked linting is enabled via
`projectService` — 67 sonarjs rules that require type information are active.
Configuration is in `eslint.config.js`.

Explicitly enabled rules:

| Rule                               | What it catches                             |
| ---------------------------------- | ------------------------------------------- |
| `cognitive-complexity`             | Functions exceeding complexity threshold    |
| `no-nested-conditional`            | Deeply nested if/switch statements          |
| `no-nested-template-literals`      | Template literals inside template literals  |
| `redundant-type-aliases`           | Type aliases that add no information        |
| `unicorn/no-zero-fractions`        | Unnecessary `.0` in numeric literals        |
| `unicorn/prefer-number-properties` | `parseInt()` instead of `Number.parseInt()` |

Also enforced via ESLint core: `max-depth: 3`, `no-console`.
Also enforced via `sonarjs.configs.recommended`: 67 type-checked rules including
`no-alphabetical-sort`, `prefer-read-only-props`, `prefer-regexp-exec`.

```bash
npm run lint
```

### 3.7 Site quality (Lighthouse)

Lighthouse runs automatically on every PR that affects the served bytes,
against 4 key pages (`/`, `/lenses/`, `/cameras/`, `/genre/`).
Configuration is in `lighthouserc.json`.

PRs that change only `package.json` and `package-lock.json` (e.g.
Dependabot bumps) skip the Lighthouse job — the build still runs to
verify deps compile, but Lighthouse does not. See ADR-039 for the
rationale. Code, content, workflow, and `lighthouserc.json` changes
continue to trigger Lighthouse as before.

| Category       | Threshold | Level |
| -------------- | --------- | ----- |
| Performance    | >= 80     | error |
| Accessibility  | >= 90     | warn  |
| SEO            | >= 90     | warn  |
| Best Practices | >= 90     | warn  |

**Run locally:**

```bash
npm run lighthouse
```

This builds the site and runs Lighthouse against all 4 pages (3 runs each).
HTML reports are written to `reports/lighthouse/` — open any `.report.html`
in a browser for full scores, diagnostics, and opportunities.

### 3.8 Link checking (lychee)

Lychee checks for broken internal links in the built site. Runs in CI on
every PR. Requires [lychee](https://github.com/lycheeverse/lychee) installed
locally (see ONBOARDING prerequisites).

```bash
npm run build
lychee --offline --no-progress --root-dir dist dist/
```

Checks all internal links in the static output. Exits non-zero on broken links.

### 3.9 Secret scanning (gitleaks)

Gitleaks scans for accidentally committed secrets. Runs in CI on every PR.
Requires [gitleaks](https://github.com/gitleaks/gitleaks) installed locally
(see ONBOARDING prerequisites).

```bash
gitleaks detect --source . --config .gitleaks.toml
```

Scans the full repo history. Exits non-zero if secrets are found.

### 3.10 Static analysis (CodeQL)

CodeQL runs automatically on every PR via `.github/workflows/codeql.yml`.
Scans JavaScript and TypeScript for security vulnerabilities and code quality
issues. No local setup needed — GitHub-native, results appear in the Security
tab.

### 3.11 Dependency updates (Dependabot)

Dependabot opens weekly PRs for outdated npm packages and GitHub Actions.
Configuration is in `.github/dependabot.yml`. PRs are labeled `chore` + `P3`.

Review Dependabot PRs:

```bash
gh pr list --author app/dependabot
```

**Weekly queue triage.** When ten-ish PRs are stacked, fast-scan CI per PR
to separate green-and-safe from broken:

```bash
for pr in <id> <id> ...; do gh pr checks $pr; echo; done
```

This surfaces failing PRs in seconds; the failure type (build vs links vs
gate) is visible without opening the run page.

**Sibling lockfile-conflict cascade.** Each squash-merge bumps
`package-lock.json`, so every other open PR with a lockfile change
conflicts after the first merge. Plan for it: merge a batch in parallel
(2-3 simultaneous `gh pr merge` calls — one or two will lose the race),
then `gh pr comment <N> --body "@dependabot rebase"` on each conflicted
loser, wait for rebase + CI, merge. Distinct from the co-dependent-bumps
pathology below — here each PR is independent, just lockfile-coupled.

**Fix-PR-first for lint-rule bumps.** When a bump adds an ESLint rule
that flags existing source (e.g. sonarjs 4.1.0's `prefer-specific-assertions`):

1. Write the fix in the older rule's API on a separate branch — usually
   forward-compatible (`expect(x).toHaveLength(N)` works on both old and
   new sonarjs). One reviewable PR, one bump PR, two clean diffs.
2. Merge the fix-PR to main.
3. `gh pr comment <bump-PR> --body "@dependabot rebase"` so the bump
   rebases against new main and CI goes green.

Do NOT push the fix directly onto Dependabot's branch — keeps the bump
as Dependabot's own clean commit, recreatable on future weekly runs
without surprise.

**Co-dependent bumps.** `package.json` uses `^` ranges, so the lockfile pins the actual version. When Dependabot splits interlocked packages (e.g. `react` and `react-dom`) into separate PRs, each PR's CI runs in isolation against current `main` — but merging one alone shifts the lockfile and breaks main with `Incompatible versions` on the next merge.

Three resolution paths, in order of preference:

1. **Group them in `.github/dependabot.yml`** so Dependabot ships a single multi-bump PR going forward. Add a `groups:` block under the npm ecosystem (current config groups the react ecosystem this way; copy that pattern for any new interlocked set):
   ```yaml
   groups:
     react:
       patterns:
         - react
         - react-dom
         - "@types/react"
         - "@types/react-dom"
   ```
2. **Rebase a single Dependabot PR** with `gh pr comment <N> --body "@dependabot rebase"` ONLY if the PR already covers all interlocked packages but is just behind main. Rebase will NOT add a missing package to a single-package PR — Dependabot's file scope is fixed by its grouping config at PR creation time.
3. **Manual combined bump** when (1) wasn't in place at creation time and (2) doesn't apply. Branch off main, `npm install <pkgA>@<v> <pkgB>@<v> <types>@<v>` together, run `npm run validate`, open one PR closing the split Dependabot PRs as superseded:
   ```bash
   git checkout -b chore/<pkg>-<version>
   npm install <pkgA>@<v> <pkgB>@<v>
   npm run validate
   # commit, push, PR
   gh pr close <split-PR-A> --comment "Superseded by #<new>" --delete-branch
   gh pr close <split-PR-B> --comment "Superseded by #<new>" --delete-branch
   ```
   Then add the `groups:` entry per (1) so it doesn't recur.

### 3.12 Analytics verification (Umami)

Umami Cloud tracks page views with zero cookies and no consent banner.
The script loads from `cloud.umami.is` via the base layout. Run this
manual check after changes to navigation, View Transitions, or the
analytics integration.

**Prerequisites:**

- Access to https://cloud.umami.is/ (login credentials)
- Chrome DevTools (or equivalent)

**Step 1 — Script loads:**

1. Open https://wuseria.com
2. DevTools → Network → filter `script.js`
3. Refresh the page

Expected: `cloud.umami.is/script.js` returns **200 OK**, ~5-6 KB.
No console errors.

**Step 2 — Page views register:**

1. Open the Umami dashboard → select wuseria.com → Realtime view
2. Navigate through several pages: Lenses → Cameras → Genre → Wiki →
   any individual lens detail page
3. Check the dashboard

Expected: each page path appears (`/lenses/`, `/cameras/`, `/genre/`,
`/wiki/`, `/lenses/[slug]`). Count matches pages visited.

**Step 3 — No duplicate events:**

1. DevTools → Network → clear the log
2. Click one navigation link (e.g. Cameras)
3. Filter by `cloud.umami.is`

Expected: exactly **1 `send`** request per navigation. If 2+ fire
for a single click, that's a duplicate event bug.

**Step 4 — Fresh page load:**

1. Clear the Network log
2. Type `wuseria.com` in the address bar and press Enter (full load)
3. Filter by `cloud.umami.is`

Expected: `script.js` + exactly **1 `send`** request.

**Last verified:** 2026-05-03 — all checks pass.

### 3.13 Search indexing (Google Search Console)

GSC surfaces indexing issues that require code fixes (e.g. trailing slash
inconsistencies, excluded pages, crawl errors). Run this check after routing
changes, new page types, or sitemap updates — and periodically (~monthly).

**Prerequisites:**

- Access to [Google Search Console](https://search.google.com/search-console)
  for wuseria.com

**Step 1 — Coverage check:**

1. Open GSC → Pages
2. Check "Not indexed" count and reasons

Red flags: "Page with redirect", "Duplicate without user-selected canonical",
"Excluded by noindex tag", "Crawled — currently not indexed" on pages that
should be indexed.

**Step 2 — Sitemap validation:**

1. Open GSC → Sitemaps
2. Verify `sitemap-index.xml` status is "Success"
3. Compare submitted page count with expected (currently 461 pages)

If count is off, check that `@astrojs/sitemap` is generating correctly and
no pages are accidentally excluded.

**Step 3 — URL inspection:**

For new page types or routing changes, inspect a sample URL:

1. GSC → URL Inspection → paste the URL
2. Verify: "URL is on Google" or "URL can be indexed"
3. Check canonical URL matches the page URL

**Step 4 — Core Web Vitals:**

1. GSC → Core Web Vitals
2. Check for "Poor" or "Needs improvement" URLs

Any regression is a bug — cross-reference with Lighthouse (3.7) to identify
the cause.

**Last verified:** 2026-05-14 — 106/461 pages indexed (23%), no critical
coverage issues.

### 3.14 Page performance (PageSpeed Insights)

[PageSpeed Insights](https://pagespeed.web.dev/) complements Lighthouse CI
(3.7) with real-user field data from the Chrome User Experience Report (CrUX).
Local Lighthouse runs produce lab data only — PSI adds how actual visitors
experience the site. Run after layout changes, new page types, or when GSC
(3.13) flags Core Web Vitals regressions.

**Step 1 — Test key pages:**

Run these URLs through https://pagespeed.web.dev/:

1. `https://wuseria.com/`
2. `https://wuseria.com/lenses/`
3. `https://wuseria.com/genre/`
4. A sample lens detail page (e.g. `https://wuseria.com/lenses/xf-23mm-f1-4-r/`)

**Step 2 — Check field data (CrUX):**

If field data is available, verify Core Web Vitals pass:

| Metric | Good threshold |
| ------ | -------------- |
| LCP    | < 2.5s         |
| INP    | < 200ms        |
| CLS    | < 0.1          |

If field data shows "Not enough data", rely on lab data only.

**Step 3 — Review lab diagnostics:**

Check the Opportunities and Diagnostics sections for:

- Render-blocking resources
- Unused JavaScript/CSS
- Image optimization opportunities
- Layout shift sources

Any performance score below 80 is a bug — cross-reference with Lighthouse CI
(3.7) to confirm it reproduces locally before fixing.

**Last verified:** not yet baselined.

### 3.15 Technical SEO crawl (Screaming Frog)

[Screaming Frog SEO Spider](https://www.screamingfrog.co.uk/seo-spider/) is a
desktop crawler that audits the site like a search engine. Catches redirect
chains, orphan pages, canonical mismatches, and
structured data errors. Free for up to 500 URLs (site currently has 461 pages).

**Prerequisites:**

- [Screaming Frog SEO Spider](https://www.screamingfrog.co.uk/seo-spider/)
  installed locally
- Free tier limit: 500 URLs (site currently has 461 pages). When the site
  exceeds 500, either buy a license or crawl selectively by filtering to
  specific directories (e.g. `/lenses/`, `/wiki/`)

**Step 1 — Crawl the site:**

1. Open Screaming Frog
2. Enter `https://wuseria.com/`
3. Start crawl — wait for completion

**Step 2 — Check key reports:**

| Tab              | What to check                                       |
| ---------------- | --------------------------------------------------- |
| Internal         | Response codes — no 3xx chains, no 4xx/5xx          |
| Page Titles      | No missing, duplicate, or truncated titles          |
| Meta Description | No missing or duplicate descriptions                |
| H1               | Exactly one H1 per page, no duplicates across pages |
| H2               | No skipped heading levels (H1 → H3)                 |
| Canonicals       | Every page has a self-referencing canonical         |
| Structured Data  | JSON-LD validates, no errors                        |
| Images           | No missing alt text on content images               |

**Step 3 — Check for orphan pages:**

1. Crawl Analysis → Orphan Pages
2. Cross-reference with sitemap (Configuration → Spider → Crawl → check
   "Crawl linked XML Sitemaps")

Any page in the sitemap but not linked internally is an orphan — fix the
internal linking or remove from sitemap.

**Step 4 — Export issues:**

Export findings as CSV for tracking. Issues with direct code fixes (missing
meta, broken canonicals, redirect chains) are bugs.

**Last verified:** not yet baselined.

### 3.16 SEO manual test plan

Periodic checklist covering GSC, Umami, Lighthouse, structured data, and
technical SEO spot checks. See [`docs/audits/seo-test-plan.md`](audits/seo-test-plan.md).

## 4. Maintenance

### 4.1 Update quality conventions

```bash
git submodule update --remote docs/solid-ai-templates
git add docs/solid-ai-templates
git commit -m "chore: bump solid-ai-templates submodule"
```

### 4.2 Update architecture decisions

1. Create an ADR in `docs/decisions/` using the format: context, decision, alternatives, consequences
2. ADRs are immutable once merged — create a new ADR to supersede an old one

### 4.3 Run the prototype

All prototype resources live in `docs/prototype/`. To run:

```bash
cp docs/prototype/index.html index.html
cp docs/prototype/main.jsx src/main.jsx
cp docs/prototype/App.jsx src/App.jsx
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Clean up after:

```bash
rm index.html src/main.jsx src/App.jsx
```

The prototype uses old field names (pre-migration) and is kept for reference
only. Do not commit the copied files.

## 5. Release and deploy

### 5.1 Release

#### Pre-release checks (run before `npm run release`)

Per `base/git.md`, complete these gates first — do not tag with any
critical finding unresolved:

```bash
git branch --no-merged main                          # investigate any unmerged work
git fsck --unreachable --no-reflogs | grep commit    # verify no orphaned commits lost
npm run check:external-links                          # external officialUrl/review links (0 dead)
```

1. **Unmerged branches / orphaned commits** — investigate any results;
   confirm no unique work would be lost by tagging the current `main`.
2. **External link check** — `npm run check:external-links` must report
   `0 dead` (unverifiable bot-blocked hosts are acceptable). The weekly
   `external-links.yml` cron also runs this.
3. **360-degree analysis** — run a fresh 360 (see `base/workflow/360.md`,
   four parallel role agents) and record the result as a verbose dated
   report in `docs/audits/YYYY-MM-DD-360.md` (per-dimension findings
   tables + the rationale for each grade — not just a score table). The
   release SHOULD NOT ship with critical findings unresolved; non-critical
   findings become issues. (This project stores dated audit reports under
   `docs/audits/` rather than a single `docs/360-audit.md` history file —
   see the upstream deviation note in CLAUDE.md §5.2.)
4. **Structure audit** — verify the §5.2 MUSTs (standard docs, README
   sections, config/SEO files) if the project structure changed since
   the last audit.

#### Tag the release

```bash
# From main, with clean working directory:
npm run release -- A.B.C
```

The script validates preconditions (on main, clean tree, valid semver),
bumps `package.json`, commits, pushes, and creates a PR. After the PR
merges:

```bash
git checkout main && git pull
git tag vA.B.C && git push origin vA.B.C

# Verify the manifest version matches the tag (base/git.md post-release check)
node -p "require('./package.json').version"   # must equal A.B.C
git describe --tags --abbrev=0                 # must be vA.B.C

# Create the GitHub Release — a pushed tag alone does NOT create one
gh release create vA.B.C --title "vA.B.C" --generate-notes

# Clean up the release branch
git branch -d chore/release-vA.B.C
git push origin --delete chore/release-vA.B.C
```

The git **tag** and the GitHub **Release** are separate artifacts: pushing
the tag creates the git ref; `gh release create` creates the Releases-page
entry with notes auto-generated from the PRs merged since the previous tag.
The deploy (§5.2) runs on the release-bump merge to `main`, independent of
the tag.

### 5.2 Deploy

Deployment is automated via GitHub Actions on push to `main`. No manual steps
required.
