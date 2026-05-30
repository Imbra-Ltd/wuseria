"""Machine-readable MTF reference set (#933, extended in #953).

Eight eye-verified charts spanning the chart-style families found in
`docs/optical-specs/`. Used to calibrate the render-match threshold and
offset tolerance band of the digitizer (ADR-038 §4).

Three of the eight charts carry ground-truth values + a hand-measured
plot box — the subset `extract_chart()` can run today (Sigma 2-color
and Samyang 4-color profiles, the two declared in `profiles/declared.py`).
The other five are tracked for shape coverage; calibration on them
unblocks once their profile lands.

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
- `2color-frequency`                — Tokina-style: colors carry frequency, S/M = solid/dotted
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
class ReferenceChart:
    """One eye-verified reference chart entry."""

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
        "contrast10S": (0.97, 0.97, 0.97, 0.97, 0.97, 0.97, 0.97, 0.97, 0.94, 0.86, 0.68),
        # Red dashed — 10M — sits slightly above 10S until edge
        "contrast10M": (0.97, 0.97, 0.97, 0.97, 0.97, 0.97, 0.97, 0.97, 0.96, 0.93, 0.87),
        # Blue solid — 30S — starts ~0.86, slow sag, steep edge drop
        "resolution30S": (0.86, 0.86, 0.86, 0.85, 0.84, 0.82, 0.81, 0.80, 0.74, 0.60, 0.33),
        # Blue dashed — 30M — sits above 30S, gentler edge drop
        "resolution30M": (0.87, 0.87, 0.87, 0.88, 0.87, 0.86, 0.86, 0.85, 0.83, 0.68, 0.60),
    },
}

# Samyang 85mm MAX panel — x positions: 0, 2.16, 4.32, 6.48, 8.64, 10.8, 12.96, 15.12, 17.28, 19.44, 21.6
_SAMYANG_85_GT: GroundTruthCurves = {
    "MAX": {
        # Dark red — 10S — flat near top, sharp knee past 17mm
        "contrast10S": (0.91, 0.92, 0.93, 0.94, 0.94, 0.94, 0.94, 0.93, 0.91, 0.86, 0.78),
        # Pink — 10M — similar to 10S but holds at edge
        "contrast10M": (0.91, 0.92, 0.93, 0.93, 0.94, 0.94, 0.94, 0.94, 0.94, 0.93, 0.93),
        # Dark grey — 30S — gradual drop with a slight uptick at edge
        "resolution30S": (0.70, 0.68, 0.66, 0.63, 0.62, 0.60, 0.58, 0.57, 0.57, 0.54, 0.52),
        # Light grey — 30M — near-linear drop
        "resolution30M": (0.70, 0.67, 0.66, 0.64, 0.62, 0.61, 0.60, 0.59, 0.58, 0.57, 0.57),
    },
}

# Samyang 300mm reflex — x positions: 0, 1.4, 2.8, ..., 14.0
# All four curves pinned at 1.0 across the entire field (idealized-flat).
# This chart's value in the set is the plausibility prior, not a render-match
# test — every extractor scores this chart well by IoU and that's the bug
# the prior catches. Ground truth here is "what the chart literally shows."
_SAMYANG_300_GT: GroundTruthCurves = {
    "MAX": {
        "contrast10S": (1.0,) * 11,
        "contrast10M": (1.0,) * 11,
        "resolution30S": (1.0,) * 11,
        "resolution30M": (1.0,) * 11,
    },
}


REFERENCE_CHARTS: tuple[ReferenceChart, ...] = (
    ReferenceChart(
        slug="sigma-56mm-f1-4-dc-dn-c",
        chart_path="docs/optical-specs/sigma-56mm-f1-4-dc-dn-c/sigma-56mm-f1-4-dc-dn-c-mtf-1.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=("f/1.4",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="canonical clean chart; 10S/M flat ~0.97 to 10mm then dips; 30S falls 0.86→0.3 at edge",
        plot_box=PlotBoxCoords(x_left=186, x_right=2987, y_top=83, y_bottom=1700),
        ground_truth=_SIGMA_56_GT,
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
    ),
    ReferenceChart(
        slug="viltrox-af-75mm-f1-2-pro",
        chart_path="docs/optical-specs/viltrox-af-75mm-f1-2-pro/viltrox-af-75mm-f1-2-pro-mtf.png",
        style_family="bw-dashed-promo",
        apertures=("f/1.2", "F8"),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="soft B&W promo; all dashed at different patterns; F8 panel is nearly idealized-flat (border case to idealized-flat)",
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


STYLE_FAMILIES: frozenset[str] = frozenset(
    chart.style_family for chart in REFERENCE_CHARTS
)
