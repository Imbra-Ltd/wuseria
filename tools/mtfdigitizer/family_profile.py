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

from typing import TYPE_CHECKING

from .profiles import (
    FUJIFILM_PERMFREQ_2COLOR_SOLID_DASHED,
    MITAKON_2COLOR_STANDM,
    SAMYANG_4COLOR_ALL_SOLID,
    SEVENARTISANS_2COLOR_SAMECOLOR_DASHED,
    SIGMA_2COLOR_SOLID_DASHED,
    TOKINA_2COLOR_FREQUENCY,
    TOKINA_2COLOR_FREQUENCY_CC_RANK,
    TTARTISAN_4COLOR_DUAL_APERTURE,
    VILTROX_BW_DASHED_F12,
    ZEISS_TOUIT_BW_3FREQ,
)
from .profiles.types import MtfProfile

if TYPE_CHECKING:
    from .referenceset.charts import ReferenceChart


# The remaining absent style family (`soft-multicurve-promo`) is the
# 7Artisans 35mm promo chart — deliberately out-of-band as a fail-loud
# anchor for the suggest scorer, no profile declared.
#
# `multifreq-press-kit` (Zeiss Touit) was previously absent; ADR-075 /
# #791 promoted it to an extracted family via the N-frequency
# RIDGE_TRACKING pipeline.
PROFILE_BY_STYLE: dict[str, MtfProfile] = {
    "mainstream-2color-solid-dashed": SIGMA_2COLOR_SOLID_DASHED,
    "mainstream-4color-all-solid": SAMYANG_4COLOR_ALL_SOLID,
    "idealized-flat": SAMYANG_4COLOR_ALL_SOLID,  # same 4-color template
    "samecolor-dashed-sm": SEVENARTISANS_2COLOR_SAMECOLOR_DASHED,
    "2color-frequency": TOKINA_2COLOR_FREQUENCY,
    "2color-frequency-cc-rank": TOKINA_2COLOR_FREQUENCY_CC_RANK,
    # Mitakon/Zhongyi GFX house style: red=S, green=M; two curves per hue
    # (10 lp/mm upper, 30 lp/mm lower) via per-hue Viterbi DP. Same dispatch
    # as Tokina with green swapped for blue.
    "mitakon-2color-standm": MITAKON_2COLOR_STANDM,
    "bw-dashed-promo": VILTROX_BW_DASHED_F12,
    # Fujifilm: one chart image per spatial frequency (ADR-043). Frequency
    # is read from the filename suffix at extraction time; the declared
    # profile carries a sentinel `frequencies_lpmm=(0,)`. Routed via the
    # multipath orchestrator (`extract.py:extract_lens_multipath`).
    "fujifilm-permfreq": FUJIFILM_PERMFREQ_2COLOR_SOLID_DASHED,
    # TTartisan: one chart image, two apertures packed by color (ADR-044).
    # The orchestrator fans out one extractor pass per aperture; the
    # profile's hues are filtered by name prefix (`max-` vs `stopped-`)
    # on each pass.
    "ttartisan-4color-dual-aperture": TTARTISAN_4COLOR_DUAL_APERTURE,
    # Zeiss Touit: B&W, 3 frequencies (10/20/40 lp/mm) separated by
    # y-band, S/M split by dash; dual-aperture stacked panels (Samyang
    # style). Routed via the N-frequency RIDGE_TRACKING pipeline
    # (`ridge_tracks_to_fields_multifreq`). See ADR-075.
    "multifreq-press-kit": ZEISS_TOUIT_BW_3FREQ,
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
    """Look up the runtime profile for one reference chart.

    Thin wrapper over `profile_for` that takes a `ReferenceChart`
    directly. Reserved for future per-chart overrides; today it just
    routes through the style-family lookup.
    """
    return profile_for(chart.style_family, chart.slug)
