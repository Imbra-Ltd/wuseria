"""Machine-readable MTF reference set (#933).

Eight eye-verified charts spanning the chart-style families found in
`docs/optical-specs/`. Used to calibrate the render-match threshold and
offset tolerance band of the digitizer (ADR-038 §4).

Field semantics:

- `slug`              — lens slug; matches `docs/optical-specs/<slug>/`
- `chart_path`        — relative path from repo root
- `style_family`      — one of the declared families (see notes below)
- `apertures`         — list of apertures plotted in the chart
- `frequencies_lpmm`  — spatial frequencies plotted (lp/mm)
- `image_height_mm`   — chart x-axis extent in mm
- `notes`             — one-line shape summary; full verification in REFERENCE_SET.md

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
class ReferenceChart:
    """One eye-verified reference chart entry."""

    slug: str
    chart_path: str
    style_family: str
    apertures: tuple[str, ...]
    frequencies_lpmm: tuple[int, ...]
    image_height_mm: float
    notes: str


REFERENCE_CHARTS: tuple[ReferenceChart, ...] = (
    ReferenceChart(
        slug="sigma-56mm-f1-4-dc-dn-c",
        chart_path="docs/optical-specs/sigma-56mm-f1-4-dc-dn-c/sigma-56mm-f1-4-dc-dn-c-mtf-1.png",
        style_family="mainstream-2color-solid-dashed",
        apertures=("f/1.4",),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="canonical clean chart; 10S/M flat ~0.97 to 10mm then dips; 30S falls 0.86→0.3 at edge",
    ),
    ReferenceChart(
        slug="samyang-85mm-f1-4-as-if-umc",
        chart_path="docs/optical-specs/samyang-85mm-f1-4-as-if-umc/samyang-85mm-f1-4-as-if-umc-mtf.png",
        style_family="mainstream-4color-all-solid",
        apertures=("MAX", "F8"),
        frequencies_lpmm=(10, 30),
        image_height_mm=21.6,
        notes="two stacked panels; MAX shows S/M divergence at edges, F8 mostly recovers except 30M edge dip",
    ),
    ReferenceChart(
        slug="samyang-300mm-f6-3-ed-umc-cs-reflex",
        chart_path="docs/optical-specs/samyang-300mm-f6-3-ed-umc-cs-reflex/samyang-300mm-f6-3-ed-umc-cs-reflex-mtf.png",
        style_family="idealized-flat",
        apertures=("MAX", "F8"),
        frequencies_lpmm=(10, 30),
        image_height_mm=14.0,
        notes="ALL curves pinned at ~1.0 across both apertures; the flat-axis blind-spot probe case",
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
