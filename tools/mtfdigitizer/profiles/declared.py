"""Declared MTF chart profiles (#934, ADR-038 §1).

Six profile families. The first two (Sigma, Samyang) shipped with #934.
The three families added next (7Artisans, Tokina prime + wide-zoom,
Viltrox) covered the rest of the in-band reference set (epic #932).
Fujifilm per-frequency followed (ADR-043). TTartisan dual-aperture
follows the multi-aperture orchestrator (ADR-044) added in #1071.

The HSV bands were measured from the reference set's actual chart pixels
— never invented. See `probe_three_profiles.py` history (deleted post-merge)
for the sampling script.
"""

from __future__ import annotations

from .types import HueRange, MtfProfile


# Sigma 2-color: red 10 lp/mm, blue 30 lp/mm; solid = sagittal, dashed = meridional.
# Measured peaks on sigma-56mm-f1-4-dc-dn-c-mtf-diffraction.png: h≈6 (red), h≈109 (blue).
SIGMA_2COLOR_SOLID_DASHED: MtfProfile = MtfProfile(
    name="sigma-2color-solid-dashed",
    hues=(
        HueRange(name="red", h_lo=0, h_hi=12, s_min=60, v_min=60),
        HueRange(name="red", h_lo=168, h_hi=179, s_min=60, v_min=60),
        HueRange(name="blue", h_lo=100, h_hi=120, s_min=60, v_min=60),
    ),
    style_axis="SPLIT_BY_DASH",
    hue_meaning="GEODESIC_DP",  # red=10 lp/mm, blue=30 lp/mm; DP bridges dashed-M gaps
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
    # FREQUENCY_PER_HUE_RIDGE (not FREQUENCY) — same shape as TTartisan
    # max-aperture (ADR-045). The 7Artisans chart's morphological close
    # (7 px horizontal) cannot bridge the wider dash gaps in this brand's
    # dashed-line rendering, so split_sm_by_cc_width returns one
    # spatially-confined left-half CC as S and ~30 right-half fragments
    # lumped as M — neither curve covers the field end-to-end. Per-column
    # ridge tracking handles fragmented dashed lines naturally: 7artisans-
    # 50mm-f1-2-mark-ii anchor goes from 5/11 paired (freq10M) to 10/11,
    # p95|Δ| on freq30S from 0.184 to 0.053 (closes #1045).
    hue_meaning="FREQUENCY_PER_HUE_RIDGE",
    frequencies_lpmm=(10, 30),
    dashed_is_sagittal=True,
    # Enable y-band coherence prior in the ridge DP (#1104). 7artisans
    # charts have dashed-line rendering where every column carries at
    # most two ridge centroids (one per curve) and dash gaps regularly
    # leave a single centroid behind. The anchor lets the DP coast past
    # those single-centroid columns instead of swapping curve identity
    # at the corner crossing. See ADR-049 §"Known limitation".
    # Per-hue audit (S155, 2026-06-17): flipping blue or green to False
    # regresses aggregate in-band count and p95 |d|. Scalar True confirmed
    # optimal for both hues.
    ridge_dp_y_anchor=True,
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
    hue_meaning="GEODESIC_DP",
    frequencies_lpmm=(10, 30),
    # Not auto-suggestable: red+blue palette overlaps Sigma's; the current
    # suggest scorer is presence-based and cannot disambiguate them
    # (both score 1.0 on either chart). Sigma wins by default for red+blue
    # autosuggest; Tokina must be explicitly declared.
    auto_suggestable=False,
    notes="Tokina/atx-m convention: red=S solid, blue=M dotted; per-hue Viterbi shortest path through the dilated mask extracts both curves of one color (upper=10, lower=30) with dash-gap bridging baked into the smoothness prior",
)


# Tokina 2-color frequency-by-color, wide-zoom variant: same hue palette
# as `TOKINA_2COLOR_FREQUENCY`, identical DP dispatch — the two profiles
# stay separate because they may diverge if a future Tokina prime needs
# a different DP parameterisation. Today they share one algorithm.
#
# Used by the 11-18mm wide-zoom panels where the 10 lp/mm and 30 lp/mm
# pairs sit close in y-space and where the blue dashed lines have wider
# dash gaps than on the prime charts. The DP smoothness prior bridges
# both without skeletonization staircase artefacts.
TOKINA_2COLOR_FREQUENCY_CC_RANK: MtfProfile = MtfProfile(
    name="tokina-2color-frequency-geodesic-dp",
    hues=(
        HueRange(name="S-red", h_lo=0, h_hi=12, s_min=80, v_min=120),
        HueRange(name="S-red", h_lo=168, h_hi=179, s_min=80, v_min=120),
        HueRange(name="M-blue", h_lo=90, h_hi=115, s_min=80, v_min=120),
    ),
    style_axis="HUE_IS_CURVE",
    hue_meaning="GEODESIC_DP",
    frequencies_lpmm=(10, 30),
    auto_suggestable=False,
    notes="Tokina wide-zoom variant: per-hue Viterbi shortest path through the dilated mask; same algorithm as the prime profile but kept separate so a per-profile DP parameterisation can diverge later",
)


# Viltrox B&W all-dashed promo: f/1.2 panel only. No informative hue;
# the four curves are grey/black at different y-positions and dash
# patterns. The four curves are tightly bunched between OTF 0.65 and
# 1.00 with heavy overlap between the 10 and 30 lp/mm pairs.
#
# CC-based dispatches (Y_BAND_IS_FREQUENCY, CC_RANK_BY_MEAN_Y) fail
# here because the dashes of adjacent frequencies sit within
# antialiasing distance in this small 366x235px f/1.2 panel — even the
# raw neutral mask fuses all four curves into one 2012-px component
# spanning the full plot height. The CC_RANK shipped in #992 picked the
# printed top plot-box border (which sits at OTF ~ 1.0 by coincidence)
# as the 10S track, while 10M reported 0/11 paired (#994 probe). The
# Y_BAND_IS_FREQUENCY predecessor yielded 30 lp/mm |d| of 0.258-0.524.
#
# RIDGE_TRACKING (#994) is geometric: per column it finds local mask
# runs as ridge centroids, then clusters across columns into tracks.
# Two curves separated by 2-3 px yield 2 distinct ridges even when
# their masks merge into one CC. See `pipeline/ridge.py`. The F8 panel
# (lower in the source PNG) is idealized-flat single light-blue curve
# — out of scope for the 4-field extractor; not declared.
VILTROX_BW_DASHED_F12: MtfProfile = MtfProfile(
    name="viltrox-bw-dashed-f1.2",
    hues=(
        # Black-to-mid-grey curve pixels; tight V cap rejects axis labels
        # and background. S<60 admits both pure black and anti-aliased grey
        # along curve edges.
        HueRange(name="neutral", h_lo=0, h_hi=179, s_min=0, s_max=60, v_min=0, v_max=110),
    ),
    style_axis="SPLIT_BY_DASH",
    hue_meaning="RIDGE_TRACKING",
    frequencies_lpmm=(10, 30),
    # Not auto-suggestable: the neutral hue range matches axis labels and
    # gridlines on EVERY chart, so leaving it in the suggest pool would
    # poison disambiguation. Must be explicitly declared.
    auto_suggestable=False,
    notes="Viltrox promo, f/1.2 panel only; ridge-tracking dispatch handles four curves that fuse into one CC under skeletonization (#994); per-column ridge centroids clustered into 4 tracks, upper 2 = 10 lp/mm, lower 2 = 30 lp/mm, S/M by coverage within each pair; F8 panel not declared",
)


# Fujifilm per-frequency images (ADR-043). One frequency per chart image
# (filename suffix `-NNlp.png`), blue solid = sagittal, red dashed =
# meridional. The profile carries `frequencies_lpmm=(0,)` as a sentinel —
# the multipath orchestrator (`extract.py:extract_lens_multipath`) reads
# the frequency from the filename and constructs a per-image profile copy
# with `frequencies_lpmm=(parsed_freq,)` before calling `extract_chart`.
#
# Measured peaks across GF (gf-23mm 15/20/40, xf-23mm 15) and XF
# (xf-14mm 45) charts: blue centered at hue 100-110, red at 170-180.
# Both saturated (S>=80) and bright (60<=V<250 to exclude white BG and
# pure black grid).
FUJIFILM_PERMFREQ_2COLOR_SOLID_DASHED: MtfProfile = MtfProfile(
    name="fujifilm-permfreq-2color-solid-dashed",
    hues=(
        HueRange(name="S-blue", h_lo=95, h_hi=115, s_min=80, v_min=60, v_max=250),
        HueRange(name="M-red", h_lo=168, h_hi=179, s_min=80, v_min=60, v_max=250),
        HueRange(name="M-red", h_lo=0, h_hi=8, s_min=80, v_min=60, v_max=250),
    ),
    style_axis="HUE_IS_CURVE",
    hue_meaning="SAGITTAL_MERIDIONAL_SINGLE_FREQ",
    frequencies_lpmm=(0,),
    # Not auto-suggestable: small images (282x212) and the same blue+red
    # palette overlap with Sigma's; matching by hue alone would mis-route
    # Sigma charts here. Explicit declaration via the
    # `fujifilm-permfreq` style family is required.
    auto_suggestable=False,
    notes=(
        "Fujifilm per-frequency MTF: one chart image per spatial frequency "
        "(filename `-NNlp.png`); blue solid = S, red dashed = M. The "
        "multipath orchestrator parses the frequency from the filename "
        "and passes it via `frequencies_lpmm=(N,)` on a per-image profile "
        "copy. See ADR-043."
    ),
)


# TTartisan 4-color dual-aperture (ADR-044). One chart image packs TWO
# apertures by color encoding:
#   max aperture     — black (10 lp/mm) + grey (30 lp/mm)
#   stopped aperture — red   (10 lp/mm) + orange (30 lp/mm)
# Within each color the solid line is the sagittal (S) curve and the
# dashed line is the tangential (T) curve — same convention as Sigma
# (`dashed_is_sagittal=False`). The legend names every curve with its
# aperture explicitly (`S10_F1.2`, `T10_F5.6`, ...); the stopped
# f-number varies per lens and is read from the chart legend at
# scaffold time, not from the slug.
#
# Hue names MUST start with `max-` or `stopped-` per ADR-044 — the
# orchestrator's `_hue_filtered_profile` splits on the prefix to fan
# out one extractor pass per aperture, each pass seeing only its own
# color bucket.
#
# Measured peaks on `ttartisan-50mm-f1-2/ttartisan-50mm-f1-2-mtf.png`
# (Tier 1 anchor; 800x600; plot region x=85..608, y=115..462). Pixel
# counts inside the plot region:
#   max-10S-black:    2865 px (V<80, S<60)
#   max-30S-grey:     2223 px (V∈[90,160], S<35)
#   stopped-10S-red:  1669 px (h≈0 or h≈179, S≥80, V∈[80,220])
#   stopped-30S-orange: 1417 px (h≈17, S≥80, V∈[80,220])
TTARTISAN_4COLOR_DUAL_APERTURE: MtfProfile = MtfProfile(
    name="ttartisan-4color-dual-aperture",
    # Per-hue `dp_y_anchor` audit (S155, 2026-06-17): four candidate hues
    # toggled against the 14-anchor reference set. Findings:
    #   max-10-black  False->True: median 0.0079->0.0083, p95 unchanged.
    #   max-30-grey   False->True: ttartisan-50 freq30S p95 0.024->0.146
    #                              (anchor punishes the legitimate corner
    #                              dive — ADR-049 known limitation confirmed).
    #   stopped-10-red False->True: median 0.0079->0.0084, p95 unchanged.
    #   stopped-30-orange True->False: tilt-50 freq30S p95 0.011->0.188,
    #                              freq30M 0.011->0.193 (confirms #1168 fix).
    # No flips warranted; current settings are locally optimal.
    hues=(
        # Black — 10 lp/mm at max aperture. Low V, low S; the S<60 cap
        # admits anti-aliased curve edges, V<80 rejects mid-grey gridlines.
        HueRange(name="max-10-black", h_lo=0, h_hi=179, s_min=0, s_max=60, v_min=0, v_max=80),
        # Black overlap recovery (#1159): where the f/2 black solid line
        # physically overlaps the f/8 red solid/dashed lines on the
        # right-edge crossing, the PNG renderer blends the colors and
        # produces pixels with V<55 but S=255 (low-V red). These are
        # genuinely black ink stained red by the overlap. Admit them
        # unconditionally on V<55. Same name as above; masks_by_curve_name
        # ORs same-name entries (same pattern as stopped-10-red wrap-around).
        # Risk check: V<55 is below the grey mask's v_min=90 by a wide
        # margin, so no collision. Probe (S149) found 492 new pixels
        # recovered, 0 grey-mask collisions.
        HueRange(name="max-10-black", h_lo=0, h_hi=179, s_min=0, s_max=255, v_min=0, v_max=55),
        # Grey — 30 lp/mm at max aperture. Mid V band, very low S; the
        # tight V∈[90,160] window separates from the light-grey
        # background gridlines (V>200) and the dark black curves (V<80).
        HueRange(name="max-30-grey", h_lo=0, h_hi=179, s_min=0, s_max=35, v_min=90, v_max=160),
        # Red — 10 lp/mm at the stopped aperture. Hue wraps around the
        # 0/179 boundary; both ends listed flat per the existing
        # wrap-around convention (Sigma, Samyang).
        HueRange(name="stopped-10-red", h_lo=0, h_hi=5, s_min=80, v_min=80, v_max=220),
        HueRange(name="stopped-10-red", h_lo=175, h_hi=179, s_min=80, v_min=80, v_max=220),
        # Orange — 30 lp/mm at the stopped aperture. Centered on hue 17;
        # high S to reject the brown/tan legend text background.
        # `dp_y_anchor=True` (#1168): on tilt-50 stopped pass the
        # solid S30 and dashed T30 cross near MTF 0.71 mid-field, and
        # the unanchored DP swaps curve identity per column at dash
        # gaps. The anchor pulls each pass toward its band so neither
        # swaps. Safe on stopped 30 (no legitimate large dives like the
        # max 30 grey case the profile-level scalar avoids).
        HueRange(name="stopped-30-orange", h_lo=12, h_hi=22, s_min=80, v_min=80, v_max=220, dp_y_anchor=True),
    ),
    style_axis="SPLIT_BY_DASH",
    # The S (solid) and T (dashed) curves of one frequency run within
    # ~5 px of each other on the TTartisan template, fusing their
    # antialiased halos into one CC and defeating CC-width split. Per-
    # column ridge tracking preserves both curves at coincidence. See
    # `ridge.ridge_tracks_for_hue_freq_split` and the FREQUENCY_PER_HUE_
    # RIDGE branch in `dispatch.field_skeletons`.
    hue_meaning="FREQUENCY_PER_HUE_RIDGE",
    frequencies_lpmm=(10, 30),
    apertures_per_chart=("max", "stopped"),
    # TTartisan legend: S = solid, T = dashed — same as Sigma's
    # `S=solid` convention. `dashed_is_sagittal=False` (default).
    # Not auto-suggestable: the black + grey palette would false-match
    # any chart with prominent text or gridlines (same hazard as the
    # Viltrox neutral-greys profile). Must be declared explicitly via
    # the `ttartisan-4color-dual-aperture` style family.
    auto_suggestable=False,
    notes=(
        "TTartisan convention (ADR-044): one chart image, two apertures "
        "packed by color. black=max-10, grey=max-30, red=stopped-10, "
        "orange=stopped-30. Solid=S, dashed=T (Sigma convention). "
        "Stopped aperture f-number varies per lens and is read from the "
        "chart legend at scaffold time."
    ),
)


DECLARED_PROFILES: tuple[MtfProfile, ...] = (
    SIGMA_2COLOR_SOLID_DASHED,
    SAMYANG_4COLOR_ALL_SOLID,
    SEVENARTISANS_2COLOR_SAMECOLOR_DASHED,
    TOKINA_2COLOR_FREQUENCY,
    TOKINA_2COLOR_FREQUENCY_CC_RANK,
    VILTROX_BW_DASHED_F12,
    FUJIFILM_PERMFREQ_2COLOR_SOLID_DASHED,
    TTARTISAN_4COLOR_DUAL_APERTURE,
)
