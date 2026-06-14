"""Machine-readable MTF reference set (#933, extended in #953).

Eight eye-verified charts spanning the chart-style families found in
`docs/optical-specs/`. Used to calibrate the render-match threshold and
offset tolerance band of the digitizer (ADR-038 §4).

Six of the eight charts carry ground-truth values + a hand-measured
plot box — the subset `extract_chart()` can run today (the five declared
profiles in `profiles/declared.py`: Sigma, Samyang, 7Artisans, Tokina,
Viltrox). The two remaining (the 7Artisans 35mm soft promo and the
Zeiss Touit press kit) are tracked for fail-loud shape coverage; both
are deliberately out-of-band and must be refused by the profile gate.

Field semantics:

- `slug`              — lens slug; matches `docs/optical-specs/<slug>/`
- `chart_path`        — relative path from repo root
- `style_family`      — one of the declared families (see notes below)
- `apertures`         — list of apertures plotted in the chart
- `frequencies_lpmm`  — spatial frequencies plotted (lp/mm)
- `image_height_mm`   — chart x-axis extent in mm
- `notes`             — one-line shape summary; full verification in REFERENCE_SET.md
- `plot_box`          — hand-measured pixel corners of the plot region (or None)
- `ground_truth`      — eye-read MTF values at the 11 SAMPLE_FRACTIONS
                        (`{aperture_label: {field_name: tuple_of_11_values_or_None}}`),
                        or None for charts not yet calibrated

Style families (single source of truth):

- `mainstream-2color-solid-dashed`  — Sigma-style: two hues, S solid / M dashed
- `mainstream-4color-all-solid`     — Samyang-style: 4 hues, all solid
- `samecolor-dashed-sm`             — Chinese: one hue per frequency, S/M = solid/dashed
- `2color-frequency`                — Tokina prime: red=S/blue=M, frequency by y-band
- `2color-frequency-cc-rank`        — Tokina wide-zoom: same palette, frequency by per-hue CC rank
- `bw-dashed-promo`                 — soft B&W promo, all-dashed
- `multifreq-press-kit`             — German press kit, 3 frequencies, B&W solid/dashed
- `idealized-flat`                  — placeholder/marketing flat at ~1.0
- `soft-multicurve-promo`           — soft promo with many spatial frequencies
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlotBoxCoords:
    """Pixel corners of the plot region in the source PNG.

    Same semantics as `pipeline.types.PlotBox` but lives here so the
    reference set has no import dependency on `pipeline`.
    `to_plotbox()` lifts to the runtime type.
    """

    x_left: int
    x_right: int
    y_top: int
    y_bottom: int


# Ground-truth shape: one tuple of 11 values per (aperture, field).
# A value is the eye-read MTF at the corresponding SAMPLE_FRACTIONS index,
# or None when the curve genuinely does not extend to that position
# (e.g. the curve is clipped past the visible edge). 11 entries, always.
GroundTruthCurves = dict[str, dict[str, tuple[float | None, ...]]]


@dataclass(frozen=True)
class ChartView:
    """One MTF chart for a lens.

    A prime publishes one chart, a zoom publishes wide + tele. Each view
    owns its own pixel raster and its own plot box (the auto-detector
    returns slightly different boxes per chart even within the same
    lens). All other lens-level attributes — style family, apertures,
    image-height extent — live on `ReferenceChart` and are shared
    across views.
    """

    chart_path: str
    plot_box: PlotBoxCoords | None = None


@dataclass(frozen=True)
class ReferenceChart:
    """One eye-verified reference chart entry.

    A lens has at least one primary chart (`chart_path` + `plot_box`)
    and zero or more additional views (`additional_views` — used by
    zooms to publish the tele-end chart alongside the canonical
    wide-end chart per ADR-033). Calibration-tier callers (calibrate,
    log, emit, scorer, plausibility, autotriage) read only the primary
    chart — they were written before multi-view zooms existed and never
    walk `additional_views`. Only the production extractor
    (`extract.py`) fans out over every view to emit per-view artifacts
    and a single multi-panel digitization-log.md per lens (#793).
    """

    slug: str
    chart_path: str
    style_family: str
    apertures: tuple[str, ...]
    frequencies_lpmm: tuple[int, ...]
    image_height_mm: float
    notes: str
    # Calibration-only fields, populated where the chart can run through
    # `extract_chart()` today. None on the five charts whose profile or
    # plot-box hasn't been declared yet.
    plot_box: PlotBoxCoords | None = None
    ground_truth: GroundTruthCurves | None = None
    # Additional chart views beyond the primary. Empty for primes; a
    # zoom lists its tele-end chart here so the production extractor
    # emits one log per lens with one panel per chart.
    additional_views: tuple[ChartView, ...] = ()

    @property
    def views(self) -> tuple[ChartView, ...]:
        """Every chart this lens publishes — primary first, then any extras."""
        primary = ChartView(chart_path=self.chart_path, plot_box=self.plot_box)
        return (primary, *self.additional_views)


# Eye-read ground truth tables for the runnable subset. Each tuple holds
# 11 MTF values at the SAMPLE_FRACTIONS (0.0, 0.1, …, 1.0) — i.e. at the
# image-height positions the calibration runner samples. Values were read
# from the source PNG against the chart's printed gridlines; the precision
# is ~±0.02 (one gridline tick is 0.10–0.20, eye-reading to half a tick).
# Same provenance as the prose shape notes in REFERENCE_SET.md.

# Sigma 56mm — x positions: 0, 1.4, 2.8, 4.2, 5.6, 7.0, 8.4, 9.8, 11.2, 12.6, 14.0
_SIGMA_56_GT: GroundTruthCurves = {
    "f/1.4": {
        # Red solid — 10S — flat at top until knee near 11mm
        "freq10S": (0.97, 0.97, 0.97, 0.97, 0.97, 0.97, 0.97, 0.97, 0.94, 0.86, 0.68),
        # Red dashed — 10M — sits slightly above 10S until edge
        "freq10M": (0.97, 0.97, 0.97, 0.97, 0.97, 0.97, 0.97, 0.97, 0.96, 0.93, 0.87),
        # Blue solid — 30S — starts ~0.86, slow sag, steep edge drop
        "freq30S": (0.86, 0.86, 0.86, 0.85, 0.84, 0.82, 0.81, 0.80, 0.74, 0.60, 0.33),
        # Blue dashed — 30M — sits above 30S, gentler edge drop
        "freq30M": (0.87, 0.87, 0.87, 0.88, 0.87, 0.86, 0.86, 0.85, 0.83, 0.68, 0.60),
    },
}

# Samyang 85mm MAX panel — x positions: 0, 2.16, 4.32, 6.48, 8.64, 10.8, 12.96, 15.12, 17.28, 19.44, 21.6
_SAMYANG_85_GT: GroundTruthCurves = {
    "MAX": {
        # Dark red — 10S — flat near top, sharp knee past 17mm
        "freq10S": (0.91, 0.92, 0.93, 0.94, 0.94, 0.94, 0.94, 0.93, 0.91, 0.86, 0.78),
        # Pink — 10M — similar to 10S but holds at edge
        "freq10M": (0.91, 0.92, 0.93, 0.93, 0.94, 0.94, 0.94, 0.94, 0.94, 0.93, 0.93),
        # Dark grey — 30S — gradual drop with a slight uptick at edge
        "freq30S": (0.70, 0.68, 0.66, 0.63, 0.62, 0.60, 0.58, 0.57, 0.57, 0.54, 0.52),
        # Light grey — 30M — near-linear drop
        "freq30M": (0.70, 0.67, 0.66, 0.64, 0.62, 0.61, 0.60, 0.59, 0.58, 0.57, 0.57),
    },
}

# Samyang 300mm reflex — x positions: 0, 1.4, 2.8, ..., 14.0
# All four curves pinned at 1.0 across the entire field (idealized-flat).
# This chart's value in the set is the plausibility prior, not a render-match
# test — every extractor scores this chart well by IoU and that's the bug
# the prior catches. Ground truth here is "what the chart literally shows."
_SAMYANG_300_GT: GroundTruthCurves = {
    "MAX": {
        "freq10S": (1.0,) * 11,
        "freq10M": (1.0,) * 11,
        "freq30S": (1.0,) * 11,
        "freq30M": (1.0,) * 11,
    },
}

# 7Artisans 50mm — x positions: 0, 1.4, 2.8, 4.2, 5.6, 7.0, 8.4, 9.8, 11.2, 12.6, 14.0
# Eye-read against chart's 0.2 OTF gridlines. The blue (10 lp/mm) pair
# appears nearly overlapping in the source rendering; S/M separation
# is small (~0.02 OTF). Green (30 lp/mm) has the more interesting
# astigmatism feature: S1 (dashed = sagittal per dashed_is_sagittal)
# dips to ~0.45 around 9.8mm then recovers to ~0.47 at the edge.
_SEVENARTISANS_50_GT: GroundTruthCurves = {
    "f/1.2": {
        # Blue solid — 10M — upper of the blue pair (T1 label)
        "freq10M": (0.92, 0.92, 0.92, 0.92, 0.92, 0.91, 0.90, 0.89, 0.88, 0.85, 0.78),
        # Blue dashed — 10S — lower of the blue pair (T2 label)
        "freq10S": (0.91, 0.91, 0.91, 0.90, 0.89, 0.88, 0.86, 0.82, 0.78, 0.74, 0.70),
        # Green solid — 30M — middle curve (S2 label); smooth fall
        "freq30M": (0.79, 0.78, 0.76, 0.72, 0.68, 0.64, 0.62, 0.60, 0.55, 0.50, 0.47),
        # Green dashed — 30S — the curve with the dip-and-recover (S1 label)
        "freq30S": (0.78, 0.76, 0.72, 0.66, 0.58, 0.52, 0.48, 0.46, 0.45, 0.46, 0.47),
    },
}

# TTartisan 50mm f/1.2 — Tier 1 anchor for the
# `ttartisan-4color-dual-aperture` style family (ADR-044). One chart
# packs both apertures via color encoding: black = 10 lp/mm at f/1.2,
# red = 10 lp/mm at f/5.6, grey = 30 lp/mm at f/1.2, orange = 30 lp/mm
# at f/5.6; solid = S (sagittal), dashed = T (tangential) per the
# chart legend (`S10_F1.2`, `T10_F1.2`, ...). The multi-aperture
# orchestrator (ADR-044, #1074) fans out one extractor pass per
# aperture; calibrate.py iterates `ground_truth.items()` per aperture
# label and compares to the matching pass's readings.
#
# Image format: 800x600 px RGB (the standard TTartisan template).
#
# Image height: 14.0 mm (APS-C — Fuji X mount).
#
# X tick labels at 0, 3, 7, 10, 13 mm fall at x = 87, 198, 347, 458,
# 570 (37.143 px/mm = 520 px / 14 mm). Plot-box x edges are at the
# data edge per #954 convention: x_left=87 sits one pixel inside the
# printed left axis at x=86; x_right=607 sits one pixel inside the
# printed right axis at x=608.
#
# Y gridlines at MTF 1.0, 0.9, ..., 0.0 fall at y = 115, 150, 184,
# 219, 254, 288, 323, 357, 392, 426, 461 (34.5 px per 0.1 OTF =
# 345 px / 1.0 OTF). y_top=116 and y_bottom=461 enclose the data
# area; y=115 (MTF 1.0) is the printed top axis line. Eye precision
# at the 0.1 gridline spacing is ~±0.02 (half a gridline tick is
# 0.05).
#
# Sample fractions (SAMPLE_FRACTIONS × image_height_mm = 14.0):
# 0.00, 1.40, 2.80, 4.20, 5.60, 7.00, 8.40, 9.80, 11.20, 12.60,
# 14.00 mm.
#
# Plot box (data-edge convention):
# x_left=87  (data edge inside the printed left axis at x=86)
# x_right=607 (data edge inside the printed right axis at x=608)
# y_top=116  (data edge below the printed MTF=1.0 axis at y=115)
# y_bottom=461 (data edge above the printed MTF=0.0 axis at y=462)
#
# DRAFT ground truth: TO BE FILLED IN BY THE MAINTAINER via eye-read
# of the chart against its printed gridlines (11 horizontal lines at
# MTF 0.0/0.1/.../1.0 plus the printed labels "0", "0.1", ..., "1"
# in the y gutter). Per `feedback_agent_no_gt_eye_read`, the agent
# does NOT eye-read these values — they exist as `None` placeholders
# below until the maintainer enters them.
#
# Two apertures × two frequencies × {S, M} × 11 sample fractions =
# 88 values to read. Field order below mirrors the legend's
# top-to-bottom order on the chart: f/1.2 first (max aperture pass),
# then f/5.6 (stopped aperture pass); within each aperture freq10
# then freq30; within each frequency S (solid) then M (dashed —
# the chart labels this 'T' for tangential, but the runtime field
# name stays freq{N}M for consistency with all other entries).
#
# Aperture keys are the profile's orchestrator labels (`"max"` /
# `"stopped"`), NOT the chart's f-numbers — calibrate.py keys
# `results_by_aperture` on the profile's `apertures_per_chart`
# tuple. The chart's f-number labels live on `ReferenceChart.apertures`
# in the same positional order.
_TTARTISAN_50_GT: GroundTruthCurves = {
    "max": {  # f/1.2 — black/grey curves
        # Black solid — 10S — f/1.2 sagittal at 10 lp/mm
        "freq10S": (0.88, 0.89, 0.90, 0.92, 0.91, 0.88, 0.85, 0.83, 0.86, 0.88, 0.77),
        # Black dashed — 10M (chart label T10_F1.2) — f/1.2 tangential
        "freq10M": (0.88, 0.90, 0.90, 0.90, 0.90, 0.87, 0.85, 0.83, 0.79, 0.73, 0.60),
        # Grey solid — 30S — f/1.2 sagittal at 30 lp/mm
        "freq30S": (0.41, 0.43, 0.49, 0.53, 0.52, 0.46, 0.41, 0.40, 0.45, 0.48, 0.29),
        # Grey dashed — 30M (chart label T30_F1.2) — f/1.2 tangential
        "freq30M": (0.41, 0.42, 0.46, 0.50, 0.50, 0.45, 0.36, 0.30, 0.30, 0.36, 0.40),
    },
    "stopped": {  # f/5.6 — red/orange curves
        # Red solid — 10S — f/5.6 sagittal at 10 lp/mm
        "freq10S": (0.95, 0.95, 0.95, 0.95, 0.96, 0.95, 0.94, 0.93, 0.93, 0.95, 0.95),
        # Red dashed — 10M (chart label T10_F5.6) — f/5.6 tangential
        "freq10M": (0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.94, 0.93, 0.93, 0.94, 0.93),
        # Orange solid — 30S — f/5.6 sagittal at 30 lp/mm
        "freq30S": (0.77, 0.79, 0.81, 0.84, 0.85, 0.83, 0.78, 0.73, 0.72, 0.77, 0.84),
        # Orange dashed — 30M (chart label T30_F5.6) — f/5.6 tangential
        "freq30M": (0.77, 0.79, 0.81, 0.83, 0.82, 0.79, 0.74, 0.70, 0.72, 0.76, 0.69),
    },
}

# TTartisan 7.5mm f/2.0 fisheye — second Tier 1 anchor for the
# `ttartisan-4color-dual-aperture` style family (ADR-041 permits
# multiple anchors per (brand, style_family); the Fujifilm GF 23 / XF
# 23 pair set the precedent). Cross-validates the dispatch against
# a fisheye design where edge behavior is dominated by the field
# crash characteristic — a stress case the 50/1.2 anchor does not
# exercise. Also exercises the #1122 vertical-chrome strip on the
# 30M curve, where the dispatch had been picking the y-axis spine
# as a ridge candidate.
#
# Image format: 800x600 px RGB (same TTartisan template as 50/1.2).
# Image height: 14.0 mm (APS-C — Fuji X mount).
# Plot box: detector-detected, same data-edge convention as 50/1.2.
#
# Chart legend: solid = S (sagittal), dashed = T (tangential);
# black/grey = f/2 (max), red/orange = f/8 (stopped); within each
# aperture, the higher-luminance color (black, red) is 10 lp/mm and
# the lower-luminance (grey, orange) is 30 lp/mm.
#
# Ground truth lives in
# `docs/optical-specs/ttartisan-7-5mm-f2-0-fisheye/eye-read.md`
# (ADR-048). The tuple below is auto-transcribed from that file by
# `py -m mtfdigitizer.eyeread ttartisan-7-5mm-f2-0-fisheye --apply` —
# do not hand-edit. Cells are currently the extractor's mechanical
# predictions; maintainer review pending.
_TTARTISAN_7_GT: GroundTruthCurves = {
    "max": {
        "freq10S": (0.95, 0.95, 0.95, 0.94, 0.92, 0.91, 0.90, 0.90, 0.90, 0.81, 0.92),
        "freq10M": (0.95, 0.95, 0.95, 0.94, 0.94, 0.94, 0.94, 0.93, 0.90, None, 0.75),
        "freq30S": (0.71, 0.72, 0.73, 0.69, 0.61, 0.54, 0.53, 0.49, 0.46, 0.54, 0.57),
        "freq30M": (0.71, 0.72, 0.75, 0.75, 0.72, 0.67, 0.66, 0.70, 0.69, 0.57, 0.48),
    },
    "stopped": {
        "freq10S": (0.92, 0.93, 0.93, 0.93, 0.92, 0.92, 0.92, 0.92, 0.91, 0.91, 0.90),
        "freq10M": (0.92, 0.93, 0.93, 0.93, 0.93, 0.93, 0.93, 0.93, 0.92, 0.93, 0.93),
        "freq30S": (0.77, 0.77, 0.76, 0.75, 0.73, 0.70, 0.70, 0.70, 0.69, 0.65, 0.58),
        "freq30M": (0.77, 0.78, 0.79, 0.80, 0.80, 0.79, 0.77, 0.76, 0.78, 0.79, 0.79),
    },
}

# Tokina atx-m 23mm — x positions: 0, 1.4, 2.8, ..., 14.0
# Beige bg, red = S (solid), blue = M (dotted), upper pair = 10 lp/mm,
# lower pair = 30 lp/mm. The 30S red has a curious local maximum near
# 5mm (rising from ~0.67 to ~0.73). Gridlines at 0/50/100% only — eye
# precision is ~±0.03.
_TOKINA_23_GT: GroundTruthCurves = {
    "f/1.4": {
        # Red solid upper — 10S
        "freq10S": (0.95, 0.97, 0.95, 0.92, 0.93, 0.92, 0.92, 0.90, 0.92, 0.85, 0.82),
        # Blue dotted upper — 10M
        "freq10M": (0.94, 0.93, 0.91, 0.92, 0.90, 0.90, 0.87, 0.82, 0.74, 0.68, 0.62),
        # Red solid lower — 30S — has the local max near 5mm
        "freq30S": (0.67, 0.70, 0.73, 0.72, 0.62, 0.55, 0.58, 0.55, 0.65, 0.58, 0.55),
        # Blue dotted lower — 30M — steepest edge falloff
        "freq30M": (0.68, 0.65, 0.60, 0.57, 0.58, 0.58, 0.58, 0.55, 0.55, 0.48, 0.32),
    },
}

# Tokina atx-m 33mm — same chart template as the 23mm.
# Beige bg, red solid = S, blue dotted = M; upper pair = 10 lp/mm,
# lower pair = 30 lp/mm. Sample positions every 1.4mm to 14mm.
_TOKINA_33_GT: GroundTruthCurves = {
    "f/1.4": {
        # Red solid upper — 10S
        "freq10S": (0.95, 0.96, 0.93, 0.95, 0.91, 0.92, 0.91, 0.92, 0.87, 0.81, 0.76),
        # Blue dotted upper — 10M; gentler decline to edge
        "freq10M": (0.95, 0.94, 0.96, 0.95, 0.92, 0.90, 0.85, 0.80, 0.74, 0.67, 0.60),
        # Red solid lower — 30S; small peak ~5mm, dip then edge fall
        "freq30S": (0.72, 0.69, 0.71, 0.72, 0.71, 0.65, 0.55, 0.50, 0.57, 0.55, 0.30),
        # Blue dotted lower — 30M; steady decline, edge crash
        "freq30M": (0.72, 0.67, 0.62, 0.58, 0.55, 0.50, 0.45, 0.42, 0.45, 0.41, 0.30),
    },
}

# Tokina atx-m 56mm — same chart template as the 23mm/33mm.
_TOKINA_56_GT: GroundTruthCurves = {
    "f/1.4": {
        # Red solid upper — 10S; bumpy with small peak near 4mm
        "freq10S": (0.93, 0.90, 0.88, 0.93, 0.87, 0.86, 0.85, 0.78, 0.72, 0.70, 0.65),
        # Blue dotted upper — 10M; smoother, holds high then drops at edge
        "freq10M": (0.93, 0.90, 0.88, 0.90, 0.89, 0.87, 0.88, 0.85, 0.80, 0.75, 0.62),
        # Red solid lower — 30S; mid-field bumpy, falls to ~0.45 plateau
        "freq30S": (0.72, 0.65, 0.60, 0.65, 0.62, 0.65, 0.63, 0.55, 0.45, 0.43, 0.45),
        # Blue dotted lower — 30M; plateau then crash past 12mm
        "freq30M": (0.70, 0.65, 0.62, 0.58, 0.55, 0.55, 0.55, 0.55, 0.52, 0.45, 0.18),
    },
}

# Tokina atx-m 11-18mm at 11mm panel — white bg, red solid = S,
# blue dashed = M. Different visual style from 23mm (white bg, gridlines
# every 20%) but same color/style convention; profile still
# TOKINA_2COLOR_FREQUENCY. Ground truth is pixel-level (see
# `tools/_probe_tokina_centerread.py` history) — eye-reading at the
# 20% gridline spacing was producing systematic errors; mechanical
# read from the source PNG is the corrected single source of truth.
# Positions 0.0 and 14.0 are None: the source curves don't extend to
# the printed y-axis line / right plot border in the chart artwork.
_TOKINA_11_18_AT_11_GT: GroundTruthCurves = {
    "F2.8": {
        "freq10S": (None, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.98, 0.92, None),
        "freq10M": (None, 1.00, 1.00, 1.00, 0.99, 0.98, 0.95, 0.92, 0.91, 0.88, None),
        "freq30S": (None, 0.98, 0.94, 0.88, 0.84, 0.83, 0.85, 0.84, 0.76, 0.60, None),
        "freq30M": (None, 0.96, 0.90, 0.89, 0.89, 0.79, 0.69, 0.59, 0.54, 0.48, None),
    },
}

# Tokina atx-m 11-18mm at 18mm panel — same template, same pixel-probe
# methodology. 18mm shows steeper edge falloff than 11mm (expected for
# the long end of a wide zoom).
_TOKINA_11_18_AT_18_GT: GroundTruthCurves = {
    "F2.8": {
        "freq10S": (None, 1.00, 1.00, 1.00, 1.00, 0.99, 0.98, 0.95, 0.91, 0.83, 0.74),
        "freq10M": (None, 1.00, 1.00, 0.99, 0.99, 0.98, 0.96, 0.93, 0.90, 0.88, None),
        "freq30S": (None, 0.91, 0.88, 0.83, 0.79, 0.74, 0.66, 0.55, 0.49, 0.48, 0.43),
        "freq30M": (None, 0.89, 0.82, 0.79, 0.78, 0.71, 0.61, 0.51, 0.42, 0.35, None),
    },
}

# Viltrox 75mm — x positions: 0, 1.4, 2.8, ..., 14.0
# f/1.2 panel only (top). All B&W curves; per the legend, solid = S,
# dashed = M. Curves bunch tightly near 1.0 at center; 30M (lowest
# dashed grey) has the most edge falloff (~0.65). F8 panel (single
# light-blue curve, idealized-flat) is not declared.
_VILTROX_75_GT: GroundTruthCurves = {
    "f/1.2": {
        "freq10S": (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.99, 0.99, 0.97, 0.95, 0.95),
        "freq10M": (0.99, 0.99, 0.98, 0.98, 0.97, 0.97, 0.95, 0.92, 0.88, 0.85, 0.82),
        "freq30S": (0.93, 0.93, 0.93, 0.93, 0.92, 0.92, 0.91, 0.90, 0.87, 0.82, 0.75),
        "freq30M": (0.92, 0.91, 0.90, 0.90, 0.89, 0.88, 0.86, 0.82, 0.78, 0.72, 0.65),
    },
}

# Sigma 30mm f/1.4 DC DN C — x positions: 0, 1.4, 2.8, ..., 14.0
# Same official chart template as the 56mm (identical 2991x1964 layout,
# APS-C 14mm image circle), so the 56mm plot box transfers directly.
# DRAFT ground truth: eye-read by the digitizer pilot (#1015 / brand
# digitization campaign), pending maintainer spot-check before this is
# treated as calibration-grade. Red=10 lp/mm (S solid, M dashed),
# blue=30 lp/mm. 10S/M flat ~0.91; 30S sags 0.77→0.38 with a steep edge,
# 30M holds higher at the edge (~0.57).
_SIGMA_30_GT: GroundTruthCurves = {
    "f/1.4": {
        "freq10S": (0.91, 0.91, 0.92, 0.92, 0.92, 0.92, 0.92, 0.92, 0.91, 0.86, 0.77),
        "freq10M": (0.91, 0.91, 0.91, 0.91, 0.91, 0.91, 0.91, 0.92, 0.92, 0.91, 0.90),
        "freq30S": (0.77, 0.76, 0.76, 0.75, 0.74, 0.73, 0.72, 0.71, 0.67, 0.59, 0.38),
        "freq30M": (0.77, 0.76, 0.73, 0.72, 0.70, 0.70, 0.70, 0.69, 0.63, 0.58, 0.57),
    },
}

# Fujifilm GF 23mm f/4 R LM WR — Tier 1 anchor for the
# `fujifilm-permfreq` style family (ADR-043). 282x212 px per chart;
# three frequencies (15/20/40 lp/mm) sit in their own files
# (`-15lp.png`, `-20lp.png`, `-40lp.png`) — blue solid = S,
# red dashed = M, single max aperture (f/4).
#
# Image height: 26.9 mm. Tick marks at y=185-186 sit at exactly
# x = 58, 102, 145, 189, 232 for "5", "10", "15", "20", "25" mm
# respectively (4 spacings of 43.5 px = 8.7 px/mm). The printed
# gridline runs from x=15 (corresponds to 0 mm, the leftmost tick
# position) to x=249 (which projects to (249-15)/8.7 = 26.9 mm —
# almost the full GF 44x33 sensor half-diagonal of 27.5 mm).
# Fujifilm draws the data area past the "25" tick label by ~17 px
# without an explicit tick there; the curves extend to x=249, not
# x=232.
#
# Sample fractions (SAMPLE_FRACTIONS × image_height_mm = 26.9):
# 0.00, 2.69, 5.38, 8.07, 10.76, 13.45, 16.14, 18.83, 21.52, 24.21,
# 26.90 mm.
#
# Plot box (measured against printed gridlines):
# x_left=15 (gridline left edge, also "0 mm" tick position)
# x_right=249 (gridline right edge, ~26.9 mm)
# y_bottom=184 (bottommost printed gridline = MTF 0.0)
# y_top=4 (extrapolated one gridline spacing above y=40, MTF=0.8;
# the MTF=1.0 line is unprinted but spacing is 36 px/0.2).
#
# DRAFT ground truth: TO BE FILLED IN BY THE MAINTAINER via eye-read
# of the three source PNGs against the chart's printed gridlines
# (5 horizontal lines at MTF 0.0/0.2/0.4/0.6/0.8 plus the implied
# 1.0 boundary at the top of the curve area). Per
# `feedback_agent_no_gt_eye_read`, the agent does NOT eye-read these
# values — they exist as `None` placeholders below until the
# maintainer enters them.
#
# Reading guidance (gridline ticks): 0.0 baseline, 0.2 line is 4
# divisions below the top; eye precision is ~±0.02-0.03 (half a
# gridline tick is 0.10). Order of fields below: freq{N}S then
# freq{N}M for each of the three frequencies.
_FUJI_GF_23_GT: GroundTruthCurves = {
    "f/4": {
        # 15 lp/mm — blue solid (S) holds ~0.99 to ~16 mm then knees
        # down to 0.75 at the edge; red dashed (M) holds higher, only
        # dipping to 0.92 at 26.9 mm.
        "freq15S": (0.99, 0.99, 0.99, 0.99, 0.98, 0.98, 0.97, 0.94, 0.88, 0.82, 0.75),
        "freq15M": (0.99, 0.99, 0.99, 0.99, 0.98, 0.98, 0.97, 0.96, 0.96, 0.94, 0.92),
        # 20 lp/mm — S knees harder past 16 mm down to 0.58 at the
        # edge; M holds in the 0.79–0.97 band with a small wobble.
        "freq20S": (0.97, 0.97, 0.97, 0.95, 0.94, 0.92, 0.89, 0.81, 0.71, 0.63, 0.58),
        "freq20M": (0.97, 0.97, 0.95, 0.95, 0.94, 0.91, 0.89, 0.89, 0.89, 0.86, 0.79),
        # 40 lp/mm — most aggressive falloff. S drops to 0.46 at the
        # edge; M oscillates from dashed-line print pattern.
        "freq40S": (0.89, 0.90, 0.88, 0.84, 0.79, 0.74, 0.71, 0.67, 0.60, 0.53, 0.46),
        "freq40M": (0.89, 0.90, 0.86, 0.84, 0.82, 0.72, 0.73, 0.71, 0.74, 0.70, 0.53),
    },
}

# Fujifilm XF 23mm f/1.4 R LM WR — second Tier 1 anchor for the
# `fujifilm-permfreq` style family (ADR-043). XF (APS-C) lenses
# publish at 15 + 45 lp/mm and to the APS-C sensor half-diagonal
# of 14.2 mm — different scale from the GF cohort. Adding the second
# anchor cross-validates the dispatch against the XF body of charts
# (per ADR-041, more than one anchor per (brand, style_family) is
# allowed and useful).
#
# Image format: 376x282 px, RGBA with transparent background — the
# loader composites over white before extraction.
#
# Image height: 14.2 mm (APS-C 23.5x15.6 mm half-diagonal ≈ 14.1 mm;
# Fujifilm labels the rightmost tick as "14.2 mm" explicitly).
#
# Tick label centers at x = 16, 125, 231.5, 315 → 0, 5, 10, 14.2 mm.
# Dark x-axis baseline at y=245 runs from x=19 to x=319 (300 px wide).
# Calibration: (319 - 19) / 14.2 = 21.13 px/mm. Plot box uses the
# crisp dark-axis bounds.
#
# Sample fractions (SAMPLE_FRACTIONS × image_height_mm = 14.2):
# 0.00, 1.42, 2.84, 4.26, 5.68, 7.10, 8.52, 9.94, 11.36, 12.78,
# 14.20 mm.
#
# Plot box:
# x_left=19 (left edge of dark x-axis, = 0 mm)
# x_right=319 (right edge of dark x-axis, = 14.2 mm)
# y_bottom=245 (dark x-axis baseline = MTF 0.0)
# y_top=40 (extrapolated one gridline spacing above y=81, MTF=0.8;
# the MTF=1.0 line is unprinted; light gridline spacing is 41 px/0.2).
#
# DRAFT ground truth: TO BE FILLED IN BY THE MAINTAINER. Per
# `feedback_agent_no_gt_eye_read` the agent does NOT eye-read these
# values; placeholders below until the maintainer fills them in.
# Only ONE aperture (f/1.4 max) and TWO frequencies (15 + 45) — total
# 11 × 2 × 2 = 44 values to read.
#
# Reading guidance: four printed light gridlines at MTF 0.2/0.4/0.6/0.8,
# dark axis at MTF 0.0. The MTF 1.0 line is unprinted but is the same
# 41-px spacing above the topmost light gridline (y≈40).
_FUJI_XF_23_GT: GroundTruthCurves = {
    "f/1.4": {
        # 15 lp/mm — blue solid (S) and red dashed (M). Both start
        # at 0.96, S knees down to 0.81 at edge; M holds in the
        # 0.94–0.96 band until a sharp drop to 0.86 at the corner.
        # Position 1.4 mm filled at 0.96 by eyeball (extractor returned
        # None — first off-center sample landed in a print gap, the
        # curve is clearly at the same ~0.96 level as positions 0.0
        # and 2.8 mm in the source PNG).
        "freq15S": (0.96, 0.96, 0.95, 0.95, 0.93, 0.91, 0.88, 0.85, 0.83, 0.82, 0.81),
        "freq15M": (0.96, 0.96, 0.95, 0.96, 0.96, 0.96, 0.95, 0.94, 0.94, 0.92, 0.86),
        # 45 lp/mm — S has a dip-and-recover shape: 0.80 at center,
        # drops to 0.51 at 9.9 mm, climbs back to 0.58 at edge.
        # M holds in 0.72 band through ~7 mm, then drops to 0.48 at
        # the corner.
        "freq45S": (0.80, 0.79, 0.76, 0.73, 0.66, 0.58, 0.53, 0.51, 0.53, 0.56, 0.58),
        "freq45M": (0.80, 0.75, 0.72, 0.72, 0.72, 0.72, 0.69, 0.68, 0.67, 0.60, 0.48),
    },
}


REFERENCE_CHARTS: tuple[ReferenceChart, ...] = (
    ReferenceChart(
        slug="sigma-56mm-f1-4-dc-dn-c",
        chart_path="docs/optical-specs/sigma-56mm-f1-4-dc-dn-c/sigma-56mm-f1-4-dc-dn-c-mtf-diffraction.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=("f/1.4",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="canonical clean chart; 10S/M flat ~0.97 to 10mm then dips; 30S falls 0.86→0.3 at edge",
        # Plot-box convention: corners at the **data edge**, not at the
        # printed axis lines. Sigma's printed y-axis sits at x=186 but
        # the leftmost curve column is x=311; the printed x-axis ends
        # at x=2987 but the rightmost curve column is x=2980. Measuring
        # to the data edge makes fraction-0.0 and fraction-1.0 samples
        # land inside the curve mask. Verified by tick-position probe:
        # the printed "0" tick is at x=309, "12.5" tick at x=2694, and
        # image_height_mm=14.0 extends 1.5mm past "12.5" to x=2980. (#954)
        plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=83, y_bottom=1700),
        ground_truth=_SIGMA_56_GT,
    ),
    ReferenceChart(
        slug="sigma-30mm-f1-4-dc-dn-c",
        chart_path="docs/optical-specs/sigma-30mm-f1-4-dc-dn-c/sigma-30mm-f1-4-dc-dn-c-mtf-diffraction.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=("f/1.4",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="brand-campaign pilot; same template as 56mm. 10S/M flat ~0.91; 30S sags 0.77→0.38, 30M holds ~0.57 at edge. DRAFT GT pending maintainer verification.",
        # Identical official template to the 56mm (2991x1964, APS-C 14mm),
        # so the data-edge plot box transfers unchanged. (#954 convention)
        plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=83, y_bottom=1700),
        ground_truth=_SIGMA_30_GT,
    ),
    # Sigma DC DN C primes — scaffolded for the brand campaign (#1018).
    # Same official template family as 30mm/56mm; canonical diffraction
    # chart is `-mtf-diffraction.png` per ADR-033. Plot box and ground
    # truth are left None until a maintainer eye-reads the 11x4 GT
    # values and confirms the plot-box pixel coordinates. 16mm and 23mm
    # should transfer the 56mm box unchanged (both are 2991x1964); 12mm
    # (2988x1954) and 15mm (2993x1953) need a fresh measurement.
    ReferenceChart(
        slug="sigma-12mm-f1-4-dc-dn-c",
        chart_path="docs/optical-specs/sigma-12mm-f1-4-dc-dn-c/sigma-12mm-f1-4-dc-dn-c-mtf-diffraction.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=("f/1.4",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="Tier 2 (ADR-041) — #1018. Image 2988x1954 (10 px shorter than 56mm template); plot box auto-detected via #950 detect_sigma_plot_box().",
        plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=77, y_bottom=1694),
    ),
    ReferenceChart(
        slug="sigma-15mm-f1-4-dc-dn-c",
        chart_path="docs/optical-specs/sigma-15mm-f1-4-dc-dn-c/sigma-15mm-f1-4-dc-dn-c-mtf-diffraction.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=("f/1.4",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="Tier 2 (ADR-041) — #1018. Image 2993x1953 (different origin from 56mm template); plot box auto-detected via #950 detect_sigma_plot_box().",
        plot_box=PlotBoxCoords(x_left=314, x_right=2985, y_top=75, y_bottom=1693),
    ),
    ReferenceChart(
        slug="sigma-16mm-f1-4-dc-dn-c",
        chart_path="docs/optical-specs/sigma-16mm-f1-4-dc-dn-c/sigma-16mm-f1-4-dc-dn-c-mtf-diffraction.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=("f/1.4",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="Tier 2 (ADR-041) — production pilot for #1021. Image 2991x1964 matches 56mm template; 56mm plot box transferred unchanged.",
        plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=83, y_bottom=1700),
    ),
    ReferenceChart(
        slug="sigma-23mm-f1-4-dc-dn-c",
        chart_path="docs/optical-specs/sigma-23mm-f1-4-dc-dn-c/sigma-23mm-f1-4-dc-dn-c-mtf-diffraction.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=("f/1.4",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="Tier 2 (ADR-041) — #1018. Image 2991x1964 matches 56mm template; 56mm plot box transferred unchanged.",
        plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=83, y_bottom=1700),
    ),
    # Sigma zooms — #793. Same chart family as the DC DN C primes; the
    # canonical chart per folder is the wide-end diffraction MTF per
    # ADR-033, taken from the Fujifilm X mount edition where the source
    # publishes a separate X-mount chart set (only the 100-400mm does).
    # Plot box transferred from the 56mm template — verified by
    # detect_sigma_plot_box() returning the same (309, 2980, 83, 1700)
    # coordinates on the four 2991x1964 entries. The 17-40mm Art uses
    # a slightly different rendering (2988x1953, with a hand-measured
    # offset) and required the #1036 detector fix to be added at all.
    ReferenceChart(
        slug="sigma-10-18mm-f2-8-dc-dn-c",
        chart_path="docs/optical-specs/sigma-10-18mm-f2-8-dc-dn-c/sigma-10-18mm-f2-8-dc-dn-c-mtf-diffraction-wide.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=("f/2.8",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="Tier 2 (ADR-041) — #793. Image 2991x1964 matches 56mm template; 56mm plot box transferred unchanged. Wide + tele panels share one digitization-log.md.",
        plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=83, y_bottom=1700),
        additional_views=(
            ChartView(
                chart_path="docs/optical-specs/sigma-10-18mm-f2-8-dc-dn-c/sigma-10-18mm-f2-8-dc-dn-c-mtf-diffraction-tele.png",
                plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=83, y_bottom=1700),
            ),
        ),
    ),
    ReferenceChart(
        slug="sigma-16-300mm-f3-5-6-7-dc-os-c",
        chart_path="docs/optical-specs/sigma-16-300mm-f3-5-6-7-dc-os-c/sigma-16-300mm-f3-5-6-7-dc-os-c-mtf-diffraction-wide.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=("f/3.5",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="Tier 2 (ADR-041) — #793. Image 2991x1964 matches 56mm template; 56mm plot box transferred unchanged. Wide + tele panels share one digitization-log.md.",
        plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=83, y_bottom=1700),
        additional_views=(
            ChartView(
                chart_path="docs/optical-specs/sigma-16-300mm-f3-5-6-7-dc-os-c/sigma-16-300mm-f3-5-6-7-dc-os-c-mtf-diffraction-tele.png",
                plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=83, y_bottom=1700),
            ),
        ),
    ),
    ReferenceChart(
        slug="sigma-18-50mm-f2-8-dc-dn-c",
        chart_path="docs/optical-specs/sigma-18-50mm-f2-8-dc-dn-c/sigma-18-50mm-f2-8-dc-dn-c-mtf-diffraction-wide.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=("f/2.8",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="Tier 2 (ADR-041) — #793. Image 2991x1964 matches 56mm template; 56mm plot box transferred unchanged. Wide + tele panels share one digitization-log.md.",
        plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=83, y_bottom=1700),
        additional_views=(
            ChartView(
                chart_path="docs/optical-specs/sigma-18-50mm-f2-8-dc-dn-c/sigma-18-50mm-f2-8-dc-dn-c-mtf-diffraction-tele.png",
                plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=83, y_bottom=1700),
            ),
        ),
    ),
    ReferenceChart(
        slug="sigma-100-400mm-f5-6-3-dg-dn-os-c",
        chart_path="docs/optical-specs/sigma-100-400mm-f5-6-3-dg-dn-os-c/sigma-100-400mm-f5-6-3-dg-dn-os-c-mtf-diffraction-wide.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=("f/5",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="Tier 2 (ADR-041) — #793. Fujifilm X mount edition; source publishes parallel L/Sony FF and TC chart sets (deleted per #1032). Image 2991x1964 matches 56mm template; 56mm plot box transferred unchanged. Wide + tele panels share one digitization-log.md.",
        plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=83, y_bottom=1700),
        additional_views=(
            ChartView(
                chart_path="docs/optical-specs/sigma-100-400mm-f5-6-3-dg-dn-os-c/sigma-100-400mm-f5-6-3-dg-dn-os-c-mtf-diffraction-tele.png",
                plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=83, y_bottom=1700),
            ),
        ),
    ),
    ReferenceChart(
        slug="sigma-17-40mm-f1-8-dc-art",
        chart_path="docs/optical-specs/sigma-17-40mm-f1-8-dc-art/sigma-17-40mm-f1-8-dc-art-mtf-diffraction-wide.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=("f/1.8",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="Tier 2 (ADR-041) — #793. Image 2988x1953 with the wide-end 30 lp/mm curves crossing the right axis frame; required the #1036 detector fix (total ink fraction instead of longest contiguous run). Plot box auto-detected via detect_sigma_plot_box(). Wide + tele panels share one digitization-log.md.",
        plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=75, y_bottom=1693),
        additional_views=(
            ChartView(
                chart_path="docs/optical-specs/sigma-17-40mm-f1-8-dc-art/sigma-17-40mm-f1-8-dc-art-mtf-diffraction-tele.png",
                plot_box=PlotBoxCoords(x_left=309, x_right=2980, y_top=77, y_bottom=1694),
            ),
        ),
    ),
    ReferenceChart(
        slug="samyang-85mm-f1-4-as-if-umc",
        chart_path="docs/optical-specs/samyang-85mm-f1-4-as-if-umc/samyang-85mm-f1-4-as-if-umc-mtf.png",
        style_family="mainstream-4color-all-solid",
        apertures=("MAX", "F8"),
        frequencies_lpmm=(10, 30),
        image_height_mm=21.6,
        notes="two stacked panels; MAX shows S/M divergence at edges, F8 mostly recovers except 30M edge dip",
        # MAX panel only — F8 panel calibration deferred (requires a
        # second plot box; the runnable subset is MAX-only today).
        plot_box=PlotBoxCoords(x_left=31, x_right=461, y_top=43, y_bottom=463),
        ground_truth=_SAMYANG_85_GT,
    ),
    ReferenceChart(
        slug="samyang-300mm-f6-3-ed-umc-cs-reflex",
        chart_path="docs/optical-specs/samyang-300mm-f6-3-ed-umc-cs-reflex/samyang-300mm-f6-3-ed-umc-cs-reflex-mtf.png",
        style_family="idealized-flat",
        apertures=("MAX", "F8"),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="ALL curves pinned at ~1.0 across both apertures; the flat-axis blind-spot probe case",
        # Same layout as the Samyang 85mm (identical template); MAX panel.
        plot_box=PlotBoxCoords(x_left=31, x_right=461, y_top=43, y_bottom=463),
        ground_truth=_SAMYANG_300_GT,
    ),
    ReferenceChart(
        slug="7artisans-50mm-f1-2-mark-ii",
        chart_path="docs/optical-specs/7artisans-50mm-f1-2-mark-ii/mtf-chart.png",
        style_family="samecolor-dashed-sm",
        apertures=("f/1.2",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="blue=T(10), green=S(30); within each color solid/dashed split S/M; green S1 dips to 0.45 at 11mm before recovering",
        # Plot box from vertical-gridline + y-label scan: x-ticks every
        # 1.4mm at ~57.5px spacing (x_left at 0mm tick = 78, x_right at
        # 14mm = 653); y-labels every 0.2 OTF at ~52px (1.0 line at y=75,
        # 0 baseline at y=335). See `probe_three_profiles.py` history.
        plot_box=PlotBoxCoords(x_left=78, x_right=653, y_top=75, y_bottom=335),
        ground_truth=_SEVENARTISANS_50_GT,
    ),
    ReferenceChart(
        slug="ttartisan-50mm-f1-2",
        chart_path="docs/optical-specs/ttartisan-50mm-f1-2/ttartisan-50mm-f1-2-mtf.png",
        style_family="ttartisan-4color-dual-aperture",
        # Aperture order MUST match the profile's
        # `apertures_per_chart=("max", "stopped")` — orchestrator uses
        # the labels positionally (ADR-044, #1074).
        apertures=("f/1.2", "f/5.6"),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes=(
            "Tier 1 anchor for `ttartisan-4color-dual-aperture` style "
            "family (ADR-044). 800x600 dual-aperture template; max "
            "aperture f/1.2 (black/grey curves), stopped aperture f/5.6 "
            "(red/orange curves) — eye-read from the chart legend. "
            "Promoted from Tier 2 for maintainer-anchored calibration; "
            "scaffolder `_TIER1_SKIP_SLUGS` excludes this slug from "
            "regeneration. DRAFT GT pending maintainer eye-read (88 "
            "values: 2 apertures x 2 frequencies x {S,M} x 11 "
            "fractions)."
        ),
        # Plot box (data-edge convention, #954). Detector-detected
        # values from `ttartisan_plotbox.detect_ttartisan_plotbox` for
        # the APS-C scheme; matches the same coordinates the Tier 2
        # scaffolder would write.
        plot_box=PlotBoxCoords(x_left=87, x_right=607, y_top=116, y_bottom=461),
        ground_truth=_TTARTISAN_50_GT,
    ),
    ReferenceChart(
        slug="ttartisan-7-5mm-f2-0-fisheye",
        chart_path="docs/optical-specs/ttartisan-7-5mm-f2-0-fisheye/ttartisan-7-5mm-f2-0-fisheye-mtf.png",
        style_family="ttartisan-4color-dual-aperture",
        # Aperture order MUST match the profile's
        # `apertures_per_chart=("max", "stopped")` — orchestrator uses
        # the labels positionally (ADR-044, #1074).
        apertures=("f/2", "f/8"),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes=(
            "Second Tier 1 anchor for `ttartisan-4color-dual-aperture` "
            "(ADR-041 allows multiple anchors per (brand, style_family); "
            "see the GF 23 / XF 23 pair in `fujifilm-permfreq`). Fisheye "
            "design stresses edge behavior: the 10S right-edge crash and "
            "the 30S dip-and-recover that #1122 traced to the vertical "
            "chrome strip on the y-axis spine. 800x600 dual-aperture "
            "template (same as 50/1.2); max aperture f/2 (black/grey "
            "curves), stopped aperture f/8 (red/orange curves). GT is "
            "transcribed from `eye-read.md` (ADR-048) — currently the "
            "extractor's mechanical predictions; maintainer review "
            "pending. Scaffolder `_TIER1_SKIP_SLUGS` excludes this slug "
            "from regeneration."
        ),
        # Plot box (data-edge convention, #954). Detector-detected
        # values from `ttartisan_plotbox.detect_ttartisan_plotbox` for
        # the APS-C scheme; identical to the 50/1.2 since the template
        # is identical.
        plot_box=PlotBoxCoords(x_left=87, x_right=607, y_top=116, y_bottom=461),
        ground_truth=_TTARTISAN_7_GT,
    ),
    ReferenceChart(
        slug="7artisans-35mm-f1-2-mark-ii",
        chart_path="docs/optical-specs/7artisans-35mm-f1-2-mark-ii/mtf-chart.png",
        style_family="soft-multicurve-promo",
        apertures=("f/1.3",),
        frequencies_lpmm=(5, 10, 20, 30),
        image_height_mm=21.0,
        notes="code-v.com lab plot; 8+ curves of mixed colors; out-of-band — exercises profile fail-loud",
    ),
    ReferenceChart(
        slug="tokina-atx-m-23mm-f1-4-x",
        chart_path="docs/optical-specs/tokina-atx-m-23mm-f1-4-x/tokina-atx-m-23mm-f1-4-x-mtf.png",
        style_family="2color-frequency",
        apertures=("f/1.4",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="red=S solid, blue=M dotted; both 10 and 30 curves share style, separated by y-position; non-Sigma convention",
        # Plot box from gridline scan: vertical lines at x=186 (0mm tick),
        # 607 (5mm), 1030 (10mm) → 84.4 px/mm; x_right at 14mm = 1368.
        # Horizontal gridlines at y=149 (100%), 331 (75%), 513 (50%),
        # 695 (25%) → 728 px per 100% of OTF; y_bottom (0%) = 877.
        plot_box=PlotBoxCoords(x_left=186, x_right=1368, y_top=149, y_bottom=877),
        ground_truth=_TOKINA_23_GT,
    ),
    ReferenceChart(
        slug="tokina-atx-m-33mm-f1-4-x",
        chart_path="docs/optical-specs/tokina-atx-m-33mm-f1-4-x/tokina-atx-m-33mm-f1-4-x-mtf.png",
        style_family="2color-frequency",
        apertures=("f/1.4",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="same press-kit template as 23mm/56mm; 10S/M flat to ~10mm then S drops to 0.76 / M to 0.60; 30S has dip-recovery shape, 30M smooth fall to 0.30 at edge",
        # Plot box from gridline scan: vertical lines at x=182 (0mm tick),
        # 594 (5mm), 1008 (10mm) → 82.6 px/mm; x_right at 14mm = 1338.
        # Horizontal gridlines at y=144 (100%), 322 (75%), 500 (50%),
        # 677 (25%), 855 (0%). Overlay verified the 100% line sits at y=144.
        plot_box=PlotBoxCoords(x_left=182, x_right=1338, y_top=144, y_bottom=855),
        ground_truth=_TOKINA_33_GT,
    ),
    ReferenceChart(
        slug="tokina-atx-m-56mm-f1-4-x",
        chart_path="docs/optical-specs/tokina-atx-m-56mm-f1-4-x/tokina-atx-m-56mm-f1-4-x-mtf.png",
        style_family="2color-frequency",
        apertures=("f/1.4",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="same press-kit template as 23mm/33mm; bumpy 10S with peak near 4mm; 30M plateau ~0.55 across mid-field then crash to 0.18 at edge",
        # Vertical lines at x=338 (0mm), 812 (5mm), 1288 (10mm) → 95.0 px/mm;
        # x_right at 14mm = 1668. Horizontal lines at y=188/393/597/802/1006
        # for 100/75/50/25/0%; full five gridlines visible.
        plot_box=PlotBoxCoords(x_left=338, x_right=1668, y_top=188, y_bottom=1006),
        ground_truth=_TOKINA_56_GT,
    ),
    ReferenceChart(
        slug="tokina-atx-m-11-18mm-f2-8-x-at-11mm",
        chart_path="docs/optical-specs/tokina-atx-m-11-18mm-f2-8-x/tokina-atx-m-11-18mm-f2-8-x-mtf-11mm.png",
        style_family="2color-frequency-cc-rank",
        apertures=("F2.8",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="11mm wide-end panel of the 11-18mm zoom; white bg, red solid = S, blue dashed = M, gridlines every 20%; per-column ridge dispatch handles the curve-overlap that defeated the older y_band_split=0.25 path",
        # X bounds at the data edge (curves drawn from col 333..1670).
        # Y bounds derived from the printed 20%-spaced gridlines (at
        # y=374, 529, 683, 840) — extrapolating one 155-px step above
        # the 80% gridline puts the MTF=100% line at y=219, one step
        # below the 20% gridline puts MTF=0% at y=995. The earlier
        # y_top=235 sat 16 px below the actual 100% line, clipping
        # away the upper red curve where it tracks at 100% in the
        # left half — extractor returned None there. (#795)
        plot_box=PlotBoxCoords(x_left=333, x_right=1670, y_top=219, y_bottom=995),
        ground_truth=_TOKINA_11_18_AT_11_GT,
    ),
    ReferenceChart(
        slug="tokina-atx-m-11-18mm-f2-8-x-at-18mm",
        chart_path="docs/optical-specs/tokina-atx-m-11-18mm-f2-8-x/tokina-atx-m-11-18mm-f2-8-x-mtf-18mm.png",
        style_family="2color-frequency-cc-rank",
        apertures=("F2.8",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="18mm long-end panel of the 11-18mm zoom; same template as the 11mm panel; per-column ridge dispatch",
        # X bounds at the data edge (curves end at col 1673, not 1676).
        # Y bounds from the same gridline-extrapolation as the 11mm panel
        # (identical chart template, identical 155-px gridline spacing).
        plot_box=PlotBoxCoords(x_left=331, x_right=1673, y_top=219, y_bottom=995),
        ground_truth=_TOKINA_11_18_AT_18_GT,
    ),
    ReferenceChart(
        slug="viltrox-af-75mm-f1-2-pro",
        chart_path="docs/optical-specs/viltrox-af-75mm-f1-2-pro/viltrox-af-75mm-f1-2-pro-mtf.png",
        style_family="bw-dashed-promo",
        apertures=("f/1.2", "F8"),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="soft B&W promo; all dashed at different patterns; F8 panel is nearly idealized-flat (border case to idealized-flat)",
        # f/1.2 panel only (top). Vertical axis line at x=287 (0mm tick),
        # plot frame ends at x=653 (14mm). Y-axis calibration measured by
        # gridline scan (#994): full-width horizontal lines sit at y=153
        # (OTF=1.0) and y=393 (OTF=0.0), giving 240 px per 1.0 OTF (24 px
        # per 0.1 step matches the printed minor tick spacing).
        #
        # The pre-#994 calibration used y_top=130, y_bottom=365 — which
        # placed OTF=1.0 at the printed "1" label rather than at the
        # gridline 23 px below it. That mis-calibration was hidden in
        # Run 4 because CC_RANK_BY_MEAN_Y read the y=130 plot-frame
        # border line as 10S, and the border mapped to MTF=1.0 under the
        # wrong y_top — a coincidental match to ground truth. The
        # plot-box and dispatch fixes land together in this PR.
        #
        # F8 panel calibration deferred — single light-blue curve doesn't
        # fit the 4-field extractor.
        plot_box=PlotBoxCoords(x_left=287, x_right=653, y_top=153, y_bottom=393),
        ground_truth=_VILTROX_75_GT,
    ),
    ReferenceChart(
        slug="fujifilm-gf-23mm-f4-r-lm-wr",
        chart_path=(
            "docs/optical-specs/fujifilm-gf-23mm-f4-r-lm-wr/"
            "fujifilm-gf-23mm-f4-r-lm-wr-15lp.png"
        ),
        style_family="fujifilm-permfreq",
        apertures=("f/4",),
        frequencies_lpmm=(15, 20, 40),
        image_height_mm=26.9,
        notes=(
            "Tier 1 anchor for `fujifilm-permfreq` style family (ADR-043). "
            "GF prime, three per-frequency images (15/20/40 lp/mm); blue "
            "solid=S, red dashed=M; single max aperture f/4. 282x212 px per "
            "image. Tick marks at x=58,102,145,189,232 correspond to "
            "5/10/15/20/25 mm (8.7 px/mm); the plot box right edge at x=249 "
            "projects to 26.9 mm — Fujifilm draws ~17 px of data area past "
            "the '25' tick label without an explicit tick there. Plot box "
            "(15, 249, 4, 184): y_bottom=184 (MTF 0.0), y_top=4 (extrapolated "
            "MTF 1.0; spacing 36 px/0.2)."
        ),
        plot_box=PlotBoxCoords(x_left=15, x_right=249, y_top=4, y_bottom=184),
        ground_truth=_FUJI_GF_23_GT,
        additional_views=(
            ChartView(
                chart_path=(
                    "docs/optical-specs/fujifilm-gf-23mm-f4-r-lm-wr/"
                    "fujifilm-gf-23mm-f4-r-lm-wr-20lp.png"
                ),
                plot_box=PlotBoxCoords(
                    x_left=15, x_right=249, y_top=4, y_bottom=184
                ),
            ),
            ChartView(
                chart_path=(
                    "docs/optical-specs/fujifilm-gf-23mm-f4-r-lm-wr/"
                    "fujifilm-gf-23mm-f4-r-lm-wr-40lp.png"
                ),
                plot_box=PlotBoxCoords(
                    x_left=15, x_right=249, y_top=4, y_bottom=184
                ),
            ),
        ),
    ),
    ReferenceChart(
        slug="fujifilm-xf-23mm-f1-4-r-lm-wr",
        chart_path=(
            "docs/optical-specs/fujifilm-xf-23mm-f1-4-r-lm-wr/"
            "fujifilm-xf-23mm-f1-4-r-lm-wr-15lp.png"
        ),
        style_family="fujifilm-permfreq",
        apertures=("f/1.4",),
        frequencies_lpmm=(15, 45),
        image_height_mm=14.2,
        notes=(
            "Second Tier 1 anchor for `fujifilm-permfreq` (ADR-041 allows "
            "multiple anchors per family). XF (APS-C) prime, two "
            "per-frequency images (15/45 lp/mm); blue solid=S, red "
            "dashed=M; single max aperture f/1.4. 376x282 px RGBA "
            "(transparent background; loader composites over white). "
            "Tick label centers at x=16,125,231.5,315 correspond to "
            "0/5/10/14.2 mm; dark x-axis baseline at y=245 runs x=19..319 "
            "(21.13 px/mm). Plot box (19, 319, 40, 245): y_bottom=245 "
            "(dark axis = MTF 0.0), y_top=40 (extrapolated MTF 1.0; "
            "light gridline spacing is 41 px/0.2)."
        ),
        plot_box=PlotBoxCoords(x_left=19, x_right=319, y_top=40, y_bottom=245),
        ground_truth=_FUJI_XF_23_GT,
        additional_views=(
            ChartView(
                chart_path=(
                    "docs/optical-specs/fujifilm-xf-23mm-f1-4-r-lm-wr/"
                    "fujifilm-xf-23mm-f1-4-r-lm-wr-45lp.png"
                ),
                plot_box=PlotBoxCoords(
                    x_left=19, x_right=319, y_top=40, y_bottom=245
                ),
            ),
        ),
    ),
    ReferenceChart(
        slug="zeiss-touit-32mm-f1-8",
        chart_path="docs/optical-specs/zeiss-touit-32mm-f1-8/zeiss-touit-32mm-f1-8-mtf.png",
        style_family="multifreq-press-kit",
        apertures=("k=1.8", "k=4"),
        frequencies_lpmm=(10, 20, 40),
        image_height_mm=15.0,
        notes="German press kit; B&W solid=S, dashed=T; THREE frequencies — must reject as out-of-band for 2-freq profiles",
    ),
)


# Tier 2 production entries (ADR-041) auto-scaffolded by
# `scripts/scaffold_fuji_tier2.py`. Imported here so the extractor
# sees one unified `REFERENCE_CHARTS` tuple. Re-run the scaffolder if
# new Fujifilm lenses or chart files appear under
# `docs/optical-specs/`.
from ._fuji_tier2_charts import FUJI_TIER2_CHARTS  # noqa: E402

# TTartisan Tier 2 production entries (ADR-041, ADR-044) auto-scaffolded
# by `scripts/scaffold_ttartisan_tier2.py`. One ReferenceChart per lens;
# every chart packs two apertures by color encoding and is dispatched
# through the multi-aperture orchestrator (`extract.py:_run_view_passes`).
from ._ttartisan_tier2_charts import TTARTISAN_TIER2_CHARTS  # noqa: E402

REFERENCE_CHARTS = REFERENCE_CHARTS + FUJI_TIER2_CHARTS + TTARTISAN_TIER2_CHARTS


STYLE_FAMILIES: frozenset[str] = frozenset(
    chart.style_family for chart in REFERENCE_CHARTS
)
