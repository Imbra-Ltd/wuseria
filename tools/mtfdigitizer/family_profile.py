"""Style family → runtime profile mapping (single source of truth).

Every CLI that runs the extractor (calibrate, scorer, plausibility,
autotriage, emit, svg, review) needs the same `style_family ->
MtfProfile` lookup. Before this module each CLI carried its own copy
of the table — when the Tokina / 7Artisans / Viltrox profiles
shipped in #988, four of the six copies were updated and two
(svg.py, review.py) were silently missed, so those CLIs failed loudly
on the first non-Sigma / non-Samyang chart and the missing artifacts
went unnoticed until #795.

The map lives here so adding a new style family means editing one
file. Calibration concerns (which charts run today) are still on
the `ReferenceChart` itself (a chart without `plot_box` /
`ground_truth` is skipped before the lookup happens).
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from .profiles import (
    SAMYANG_4COLOR_ALL_SOLID,
    SEVENARTISANS_2COLOR_SAMECOLOR_DASHED,
    SIGMA_2COLOR_SOLID_DASHED,
    TOKINA_2COLOR_FREQUENCY,
    VILTROX_BW_DASHED_F12,
)
from .profiles.types import MtfProfile

if TYPE_CHECKING:
    from .referenceset.charts import ReferenceChart


# Five declared profiles wired today. The two absent style families
# (`soft-multicurve-promo`, `multifreq-press-kit`) are deliberately
# out-of-band fail-loud cases (7Artisans 35mm promo, Zeiss Touit
# press kit) and have no profile.
PROFILE_BY_STYLE: dict[str, MtfProfile] = {
    "mainstream-2color-solid-dashed": SIGMA_2COLOR_SOLID_DASHED,
    "mainstream-4color-all-solid": SAMYANG_4COLOR_ALL_SOLID,
    "idealized-flat": SAMYANG_4COLOR_ALL_SOLID,  # same 4-color template
    "samecolor-dashed-sm": SEVENARTISANS_2COLOR_SAMECOLOR_DASHED,
    "2color-frequency": TOKINA_2COLOR_FREQUENCY,
    "bw-dashed-promo": VILTROX_BW_DASHED_F12,
}


def profile_for(style_family: str, slug: str) -> MtfProfile:
    """Look up the runtime profile for one chart's style family.

    Raises ValueError with the chart slug in the message so failures
    are debuggable without a stack trace alone.

    For callers that have a ReferenceChart available, prefer
    `profile_for_chart()` — it also applies any per-chart override
    (e.g. y_band_split for wide-zoom variants).
    """
    profile = PROFILE_BY_STYLE.get(style_family)
    if profile is None:
        raise ValueError(
            f"{slug}: no declared profile for style_family={style_family!r}"
        )
    return profile


def profile_for_chart(chart: "ReferenceChart") -> MtfProfile:
    """Look up the runtime profile and apply any per-chart overrides.

    Currently the only override is `y_band_split_override` — used when
    a chart's curve geometry differs enough from the profile's defaults
    that the profile's `y_band_split` would misclassify curves (e.g.
    the 11-18mm wide-zoom Tokina panels where 30 lp/mm sits much higher
    in y than on the prime charts the default was measured against).
    """
    profile = profile_for(chart.style_family, chart.slug)
    if chart.y_band_split_override is not None:
        profile = replace(profile, y_band_split=chart.y_band_split_override)
    return profile
