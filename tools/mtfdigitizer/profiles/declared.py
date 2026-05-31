"""Declared MTF chart profiles (#934, ADR-038 §1).

Five profiles. The first two (Sigma, Samyang) shipped with #934. The
three families added here cover the rest of the in-band reference set
(epic #932): same-color dashed-S/M (7Artisans), color-carries-frequency
with sagittal/meridional-by-color (Tokina), and pure B&W dashed (Viltrox).

The HSV bands were measured from the reference set's actual chart pixels
— never invented. See `probe_three_profiles.py` history (deleted post-merge)
for the sampling script.
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


# 7Artisans 2-color same-color-dashed: blue 10 lp/mm, green 30 lp/mm.
# Within each color, solid = T (meridional), dashed = S (sagittal). The
# legend in `7artisans-50mm-f1-2-mark-ii/mtf-chart.png` labels them T1/T2
# (blue meridional pair) and S1/S2 (green sagittal pair) — Chinese MTFs
# label the meridional curve "T" (tangential) by convention, the inverse
# of the Sigma "S=solid" convention. Dispatch-wise: same path as Sigma
# (one hue per frequency, CC-split for S/M). The S<->M label swap is a
# semantic concern handled in dispatch.
#
# Measured peaks on `mtf-chart.png` (730x435 dark background):
#   blue   h~105-115 S~80-170  V~80-200  → 10 lp/mm pair
#   green  h~40-55   S~80-200  V~80-220  → 30 lp/mm pair
# Lower s_min than Sigma — the curves are mid-saturation, not vivid.
SEVENARTISANS_2COLOR_SAMECOLOR_DASHED: MtfProfile = MtfProfile(
    name="7artisans-2color-samecolor-dashed",
    hues=(
        HueRange(name="blue", h_lo=95, h_hi=120, s_min=60, v_min=70),
        HueRange(name="green", h_lo=35, h_hi=60, s_min=60, v_min=70),
    ),
    style_axis="SPLIT_BY_DASH",
    hue_meaning="FREQUENCY",
    frequencies_lpmm=(10, 30),
    dashed_is_sagittal=True,
    notes="7Artisans/Chinese convention: blue=10, green=30; T1/T2 (blue) = M pair, S1/S2 (green) = S pair; dashed=S within hue",
)


# Tokina 2-color frequency-by-color: red = S, blue = M (dotted). Frequency
# is carried by y-position — upper pair (10 lp/mm) sits ~OTF 0.62-0.97 and
# the lower pair (30 lp/mm) sits ~OTF 0.32-0.73. The pairs overlap in OTF
# but a visual gap centered around OTF ≈ 0.75 (y_fraction ≈ 0.25 of plot
# box) separates them cleanly. The first version of this profile used
# y_band_split=0.50, which put the split deep into the 30 lp/mm region and
# left 30S almost empty; 0.25 was measured from the curve clusters seen on
# the calibration chart.
#
# Measured peaks on `tokina-atx-m-23mm-f1-4-x-mtf.png` (1541x1028):
#   red   h~0 + h~170-179 S~120-250 V~160-255 → S (solid)
#   blue  h~95-105        S~140-250 V~160-255 → M (dotted)
TOKINA_2COLOR_FREQUENCY: MtfProfile = MtfProfile(
    name="tokina-2color-frequency",
    hues=(
        HueRange(name="S-red", h_lo=0, h_hi=12, s_min=80, v_min=120),
        HueRange(name="S-red", h_lo=168, h_hi=179, s_min=80, v_min=120),
        HueRange(name="M-blue", h_lo=90, h_hi=115, s_min=80, v_min=120),
    ),
    style_axis="HUE_IS_CURVE",
    hue_meaning="SAGITTAL_MERIDIONAL",
    frequencies_lpmm=(10, 30),
    y_band_split=0.25,
    # Not auto-suggestable: red+blue palette overlaps Sigma's; the current
    # suggest scorer is presence-based and cannot disambiguate them
    # (both score 1.0 on either chart). Sigma wins by default for red+blue
    # autosuggest; Tokina must be explicitly declared.
    auto_suggestable=False,
    notes="Tokina/atx-m convention: red=S solid, blue=M dotted; frequency by y-band (upper=10, lower=30); both hues split by y_band_split",
)


# Viltrox B&W all-dashed promo: f/1.2 panel only. No informative hue;
# the four curves are grey/black at different y-positions and dash
# patterns. The four curves are tightly bunched between OTF 0.65 and
# 1.00 with heavy overlap between the 10 and 30 lp/mm pairs — there is
# no clean y-band gap separating them at any fixed fraction. The
# previous Y_BAND_IS_FREQUENCY dispatch with y_band_split=0.30 yielded
# 30 lp/mm |d| of 0.258–0.524 (Run 3 baseline).
#
# CC_RANK_BY_MEAN_Y skeletonizes the neutral mask first, then ranks the
# resulting connected components by mean y-position and splits at the
# largest y-gap. This adapts to wherever the natural break between the
# 10 and 30 lp/mm clusters lands on a given chart, rather than relying
# on a hand-tuned fraction. The F8 panel (lower in the source PNG) is
# idealized-flat single light-blue curve — out of scope for the 4-field
# extractor; not declared.
VILTROX_BW_DASHED_F12: MtfProfile = MtfProfile(
    name="viltrox-bw-dashed-f1.2",
    hues=(
        # Black-to-mid-grey curve pixels; tight V cap rejects axis labels
        # and background. S<60 admits both pure black and anti-aliased grey
        # along curve edges.
        HueRange(name="neutral", h_lo=0, h_hi=179, s_min=0, s_max=60, v_min=0, v_max=110),
    ),
    style_axis="SPLIT_BY_DASH",
    hue_meaning="CC_RANK_BY_MEAN_Y",
    frequencies_lpmm=(10, 30),
    # Not auto-suggestable: the neutral hue range matches axis labels and
    # gridlines on EVERY chart, so leaving it in the suggest pool would
    # poison disambiguation. Must be explicitly declared.
    auto_suggestable=False,
    notes="Viltrox promo, f/1.2 panel only; single neutral mask skeletonized, components ranked by mean-y and split at the largest gap into 10 (upper) / 30 (lower); within each cluster longest CC = S, rest = M; F8 panel not declared",
)


DECLARED_PROFILES: tuple[MtfProfile, ...] = (
    SIGMA_2COLOR_SOLID_DASHED,
    SAMYANG_4COLOR_ALL_SOLID,
    SEVENARTISANS_2COLOR_SAMECOLOR_DASHED,
    TOKINA_2COLOR_FREQUENCY,
    VILTROX_BW_DASHED_F12,
)
