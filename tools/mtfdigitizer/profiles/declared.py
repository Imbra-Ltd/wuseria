"""Declared MTF chart profiles (#934, ADR-038 §1).

Two profiles to start, matching the brands we have reference data for
(the YAGNI hint in #934 — "Sigma, Samyang to start"). Other brands'
profiles get declared as the digitizer encounters them in #935 and
onwards.

The HSV bands were measured from the reference set's actual chart
pixels — not invented. The sampling script logs are in commit
message; rerun by stepping a histogram over each reference chart and
reading the dominant saturated-hue peaks plus any achromatic grey
bands.
"""

from __future__ import annotations

from .types import HueRange, MtfProfile


# Sigma 2-color: red 10 lp/mm, blue 30 lp/mm; solid = sagittal, dashed = meridional.
# Measured peaks on sigma-56mm-f1-4-dc-dn-c-mtf-1.png: h≈6 (red), h≈109 (blue).
SIGMA_2COLOR_SOLID_DASHED: MtfProfile = MtfProfile(
    name="sigma-2color-solid-dashed",
    hues=(
        HueRange(name="red", h_lo=0, h_hi=12, s_min=60, v_min=60),
        HueRange(name="red", h_lo=168, h_hi=179, s_min=60, v_min=60),
        HueRange(name="blue", h_lo=100, h_hi=120, s_min=60, v_min=60),
    ),
    style_axis="SPLIT_BY_DASH",
    hue_meaning="FREQUENCY",  # red=10 lp/mm, blue=30 lp/mm
    frequencies_lpmm=(10, 30),
    notes="Sigma global product pages; red solid=S, red dashed=M, blue solid=S, blue dashed=M",
)


# Samyang 4-color: 2 reds (saturated + pink) for 10 lp/mm, 2 greys (dark + light)
# for 30 lp/mm; each curve has its own color, no within-color split.
# Measured peaks on samyang-85mm-f1-4-as-if-umc-mtf.png:
#   saturated red h≈172 S>=180 V≈170-220   → 10S
#   pink          h≈172 S 40-180 V>=180   → 10M
#   dark grey     S<40 V≈94-103            → 30S
#   light grey    S<40 V≈166-184            → 30M
SAMYANG_4COLOR_ALL_SOLID: MtfProfile = MtfProfile(
    name="samyang-4color-all-solid",
    hues=(
        HueRange(name="10S-red", h_lo=0, h_hi=10, s_min=140, v_min=60),
        HueRange(name="10S-red", h_lo=168, h_hi=179, s_min=140, v_min=60),
        HueRange(name="10M-pink", h_lo=0, h_hi=10, s_min=40, s_max=140, v_min=140),
        HueRange(name="10M-pink", h_lo=168, h_hi=179, s_min=40, s_max=140, v_min=140),
        # Samyang's greys sit in narrow V bands measured from real pixels —
        # tight ranges prevent matching neutral midtones in unrelated charts'
        # gridlines or anti-aliased backgrounds.
        HueRange(name="30S-dark-grey", h_lo=0, h_hi=179, s_min=0, s_max=40, v_min=85, v_max=115),
        HueRange(name="30M-light-grey", h_lo=0, h_hi=179, s_min=0, s_max=40, v_min=160, v_max=195),
    ),
    style_axis="HUE_IS_CURVE",
    hue_meaning="CURVE_IDENTITY",
    frequencies_lpmm=(10, 30),
    notes="Samyang product page MTF; each curve identified by (hue, saturation, brightness)",
)


DECLARED_PROFILES: tuple[MtfProfile, ...] = (
    SIGMA_2COLOR_SOLID_DASHED,
    SAMYANG_4COLOR_ALL_SOLID,
)
