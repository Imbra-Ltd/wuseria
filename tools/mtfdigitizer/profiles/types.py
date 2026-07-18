"""MTF chart profile types (#934, ADR-038 §1).

Frozen dataclasses + literal enums; no behavior. The matching logic lives
in `suggest.py`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


# Style axis: how S and M are separated within a single hue.
#
# - `SPLIT_BY_DASH`  — one hue carries both S and M; tell them apart by
#                      line style (solid vs dashed). The extractor must
#                      skeletonize and split by fragment width.
# - `HUE_IS_CURVE`   — each curve has its own hue; no within-hue split.
#                      The extractor masks one curve per hue and reads
#                      the line directly.
StyleAxis = Literal["SPLIT_BY_DASH", "HUE_IS_CURVE"]


# What a hue identifies on the chart.
#
# - `FREQUENCY`             — hue = spatial frequency (red=10 lp/mm,
#                             blue=30 lp/mm in the Sigma dialect)
# - `FREQUENCY_PER_HUE_RIDGE` — same as FREQUENCY but per-hue dispatch
#                             runs ridge tracking instead of skeleton
#                             + CC-width split. Used by SPLIT_BY_DASH
#                             charts where the solid and dashed curves
#                             of one hue run within a few px of each
#                             other (TTartisan max-aperture pass): the
#                             raw mask fuses both curves' antialiased
#                             halos into one connected component, so
#                             `split_sm_by_cc_width` can't separate
#                             them. Per-column ridge centroids preserve
#                             two distinct tracks even at coincidence.
#                             Higher-coverage track = solid (S by
#                             default; M when dashed_is_sagittal).
# - `SAGITTAL_MERIDIONAL`   — hue = S vs M (red=S, blue=M in the Tokina
#                             dialect); frequency is then carried by
#                             curve y-position, declared via
#                             `MtfProfile.y_band_split`
# - `SAGITTAL_MERIDIONAL_SINGLE_FREQ` — hue = S vs M (blue solid=S,
#                             red dashed=M in the Fujifilm dialect);
#                             the chart image carries one frequency
#                             only. The frequency is read from the
#                             filename (`-15lp.png` → 15) and passed
#                             to the extractor via a per-call profile
#                             copy with `frequencies_lpmm=(N,)`. No
#                             y_band_split — each hue is the whole
#                             curve. See ADR-043.
# - `CURVE_IDENTITY`        — hue uniquely identifies one curve out of
#                             {10S, 10M, 30S, 30M} (the Samyang 4-color
#                             dialect)
# - `Y_BAND_IS_FREQUENCY`   — there is no informative hue (B&W chart);
#                             a single neutral mask carries all curves
#                             and they're separated into frequency
#                             groups by y-position, then into S/M by
#                             dash pattern within each band (Viltrox).
# - `CC_RANK_BY_MEAN_Y`     — variant of the above for tightly-clustered
#                             B&W charts where the four curves overlap in
#                             OTF space too much for a fixed y_band_split
#                             to separate them. Skeletonize the single
#                             neutral mask, then rank connected components
#                             by mean y: top two = upper frequency (10),
#                             bottom two = lower frequency (30). Within
#                             each band, the wider CC is solid (S) and
#                             the rest is dashed (M). No y_band_split.
# - `RIDGE_TRACKING`        — geometric (not topological) extraction for
#                             charts where curves visually overlap or sit
#                             within antialiasing distance, fusing into
#                             one CC. Per-column ridge centroids are
#                             clustered into 4 tracks; top two by mean-y
#                             = upper frequency, bottom two = lower
#                             frequency; within each pair the higher-
#                             coverage track is solid (S by default).
#                             See `pipeline/ridge.py`.
# - `GEODESIC_DP`           — per-hue Viterbi shortest path through the
#                             dilated mask. The smoothness prior bridges
#                             dash gaps without skeletonization staircase
#                             artefacts and refuses to switch to a
#                             parallel curve at near-touching regions.
#                             Each hue carries S or M (named "S-*"/"M-*").
#                             See `pipeline/dp_extract.py`.
HueMeaning = Literal[
    "FREQUENCY",
    "FREQUENCY_PER_HUE_RIDGE",
    "SAGITTAL_MERIDIONAL",
    "SAGITTAL_MERIDIONAL_SINGLE_FREQ",
    "CURVE_IDENTITY",
    "Y_BAND_IS_FREQUENCY",
    "CC_RANK_BY_MEAN_Y",
    "RIDGE_TRACKING",
    "GEODESIC_DP",
]


@dataclass(frozen=True)
class HueRange:
    """An HSV band a profile expects to find in the chart.

    Hue is in OpenCV's 0..179 range. The S and V bounds turn this into
    a full HSV box, which is what's needed to separate curves that share
    a hue but differ in saturation or brightness — the Samyang dialect
    distinguishes pink (low S) from red (high S) and light grey (high V,
    low S) from dark grey (low V, low S).

    A red curve typically spans both ends of the hue circle (both low
    and high hue values read as red), so a profile may list two
    `HueRange` entries with the same `name`; they count as one curve
    for matching, and the extractor ORs their masks. Keeping the
    wrap-around flat avoids special-casing in the masker.
    """

    name: str  # e.g. "red" or "10S-saturated-red"
    h_lo: int  # 0..179
    h_hi: int  # 0..179
    s_min: int = 60  # reject pale pixels (white background, anti-aliased edges)
    s_max: int = 255
    v_min: int = 60  # reject dark gridlines and text
    v_max: int = 255
    # Per-hue override for the FREQUENCY_PER_HUE_RIDGE dispatch's
    # `use_y_anchor` flag (see MtfProfile.ridge_dp_y_anchor). None falls
    # back to the profile's scalar setting. Set True to stabilize S/M
    # labels at curve crossings where the two curves of one hue are
    # close (TTartisan stopped-30-orange on tilt-50: the solid S30 and
    # dashed T30 cross near MTF 0.71 mid-field, and the unanchored DP
    # swaps curve identity per column at dash gaps, producing alternating
    # 0.71/0.55 readings). The anchor pulls each pass toward its band so
    # neither swaps. Use cautiously: on freq30 curves with legitimate
    # large dives (TTartisan max-30-grey on 7.5 fisheye), the anchor can
    # punish the dive — keep that case at False. See #1168 / #1159.
    dp_y_anchor: bool | None = None
    # Per-hue post-discriminator override for FREQUENCY_PER_HUE_RIDGE:
    # after the coverage/continuity discriminator picks solid/dashed,
    # swap them when True. Applies only on lenses where every available
    # signal (coverage, continuity, divergent-band presence, mask-CC
    # count under band) picks the wrong track because the physical
    # solid line is fragmented enough by its own shape that the DP
    # path can't trace it, while the dashed line is smooth enough that
    # the DP locks every dash centroid (af-35 stopped-30-orange:
    # #1199). Set per-lens by `ReferenceChart.sm_swap_per_hue` — the
    # field stays False on the shared profile so other lenses sharing
    # the profile are unaffected. Default False.
    force_sm_swap: bool = False


@dataclass(frozen=True)
class MtfProfile:
    """A declared MTF chart profile (ADR-038 §1).

    `y_band_split` is set when a profile needs to separate curves into
    frequency groups by vertical position (Tokina, Viltrox). The value
    is the y-fraction of the plot box at which the upper and lower bands
    are split — pixels above the line group as the first frequency, below
    as the second. None for profiles where hue or curve identity alone
    determines the (frequency, S/M) mapping.
    """

    name: str  # stable identifier, e.g. "sigma-2color-solid-dashed"
    hues: tuple[HueRange, ...]
    style_axis: StyleAxis
    hue_meaning: HueMeaning
    frequencies_lpmm: tuple[int, ...]  # e.g. (10, 30)
    notes: str = ""
    y_band_split: float | None = None  # 0.0..1.0 fraction of plot height
    # Convention for SPLIT_BY_DASH dispatch: True means dashed lines are
    # the sagittal (S) curve and solid lines are meridional (M). 7Artisans
    # labels the meridional pair "T1/T2" and sagittal pair "S1/S2", which
    # is the inverse of Sigma's "S=solid". Default matches Sigma.
    dashed_is_sagittal: bool = False
    # When False, this profile is excluded from `suggest_profile()` and
    # may only be used by explicit declaration in `resolve()`. Required
    # for profiles whose hue band is so broad that it false-matches every
    # chart (Viltrox's neutral-greys mask matches any image with text or
    # gridlines, so it can never be auto-suggested without poisoning the
    # disambiguation of every other profile).
    auto_suggestable: bool = True
    # Per-profile override for the horizontal close-kernel width used by
    # `close_and_skeletonize` when bridging dashed-line gaps. None falls
    # back to the module-level default (7 px). Override when a profile's
    # chart family has wider dash gaps than the default can bridge —
    # raising this value bridges longer gaps but risks merging adjacent
    # parallel curves of the same hue (so far always safe, since per-hue
    # masks only contain one color and within-color curves don't run
    # parallel for these chart styles).
    close_kernel_width: int | None = None
    # When set, the chart image packs multiple apertures per panel via
    # color encoding (TTartisan-style: black+grey curves at max aperture,
    # red+orange at the stopped aperture). The orchestrator runs the
    # extractor once per aperture in this tuple, each time with `hues`
    # filtered to those whose `HueRange.name` starts with `f"{aperture}-"`.
    # None for single-aperture charts (every profile shipped before this
    # extension). See ADR-044 (multi-aperture orchestrator).
    apertures_per_chart: tuple[str, ...] | None = None
    # When True, the FREQUENCY_PER_HUE_RIDGE dispatch runs its per-column
    # ridge DP with a y-band coherence prior (#1104): the upper and lower
    # paths each follow a precomputed anchor curve so the DP can break
    # smoothness-cost ties through dash gaps without swapping curve
    # identity. Only safe on charts where 1- and 2-ridge columns dominate
    # (7Artisans samecolor-dashed-sm). Defaults False because the option
    # can drag a path off a legitimate dive on noisier charts (TTartisan
    # max-aperture grey freq30 — see ADR-049's "Known limitation").
    ridge_dp_y_anchor: bool = False
    # Cross-hue AA-halo subtractions to apply before skeletonization
    # (#1216). Each tuple is `(contaminator_hue_name, contaminated_hue_name)`
    # — the contaminated hue's mask gets the dilated contaminator mask
    # subtracted before the dispatch branch runs. Used when two hues'
    # HueRanges share an HSV boundary so the contaminated mask catches
    # the AA gradient ring around the contaminator's curves (e.g. Samyang
    # `10S-red` AA halo bleeds into `10M-pink` because pink's `s_max=140`
    # equals red's `s_min=140`). Distinct from the TTartisan
    # `_build_halo_exclusion_map` (which auto-derives pairs from
    # aperture prefix + frequency on the FREQUENCY_PER_HUE_RIDGE branch);
    # this field declares pairs explicitly and applies to any dispatch
    # branch that honours it. Default empty.
    halo_pairs: tuple[tuple[str, str], ...] = ()
    # Profile-declared spurious-CC filter for masks that should consist of
    # one dominant connected component near the top of the panel (ADR-074).
    # Each tuple is `(curve_name, min_area, max_y_delta)`. The pipeline
    # drops any CC in `curve_masks[curve_name]` whose y-centroid is more
    # than `max_y_delta` rows below the dominant CC's y-centroid AND whose
    # area is less than `min_area` pixels. Both conditions must hold.
    # Distinct from `halo_pairs`: that subtracts a contaminator's AA ring
    # from a contaminated mask, requiring the contaminator to be present
    # in the same row neighbourhood. This filter targets the orthogonal
    # case where the contaminated mass exists without a co-located
    # contaminator (e.g. Samyang 20mm stopped 10S, where pink crosses
    # through a darker shade that lands in the 10S-red HSV box at a
    # column where pink itself has no mask pixels). Default empty.
    small_below_top_cc_filters: tuple[tuple[str, int, int], ...] = ()
    # When True, `ridge_tracks_to_fields_multifreq` assigns the kept
    # tracks to frequency bands by clustering their INTERIOR y-position
    # (an optimal 1-D k-means over the left field region) instead of the
    # global-mean-y equal-size split (#1347). The equal split collapses
    # to 1/1/3 when a sparse dashed curve is lost to the coverage floor
    # and mis-files the middle frequency under the highest; on
    # press-kit panels whose curves crash and converge near the APS-C
    # corner, the interior region is where the frequency bands still
    # separate cleanly, so clustering there recovers the correct
    # frequency assignment. Opt-in per ADR: only the multifreq-press-kit
    # Touit family sets it; 2-freq RIDGE_TRACKING (Viltrox) keeps the
    # equal-split path unchanged. Default False.
    interior_anchored_bands: bool = False

    # When True, `ridge_tracks_to_fields_multifreq` assigns S/M within
    # each 2-track frequency band by ridge-coverage dashedness (the
    # solid curve has ink at nearly every ridge column; a dashed curve
    # leaves gaps) instead of y-order, honoring `dashed_is_sagittal`
    # (#1374). The default top-track-is-S assumption is refuted on the
    # Zeiss Touit 32mm f/1.8 panel, where the maintainer eye-read GT
    # (#1332) shows the dashed M running ABOVE solid S from ~3 mm
    # outward at 10/20 lp/mm. Coverage falls back to y-order when the
    # two tracks' coverages sit within the calibrated margin (coincident
    # pairs, #791 cluster-collapse bands). Opt-in: only families whose
    # S/M axis is solid-vs-dashed can use it — all-dashed families
    # (Viltrox) carry no coverage signal. Default False.
    band_sm_by_coverage: bool = False

    # When True, build sister-fallback presence masks for this
    # SPLIT_BY_DASH + RIDGE_TRACKING profile by splitting its single
    # neutral mask into solid (S) and dashed (M) sub-skeletons and
    # broadcasting each across every frequency. The dialect otherwise
    # falls through to "no presence info", so the M<-S sister fallback
    # never fires; a dashed curve that merges into its solid sibling in
    # the interior and is lost to the coverage floor then reads all-None.
    # With presence wired the fallback recovers it from the solid sibling
    # where they coincide (the interior) and leaves an honest None at the
    # diverging corner, where the sibling's own sample is also None so no
    # wrong value is copied (#1347). Opt-in: only the multifreq-press-kit
    # Touit family sets it; 2-freq RIDGE_TRACKING (Viltrox) stays on the
    # legacy no-presence path. Default False.
    dashed_split_presence: bool = False

    @property
    def hue_count(self) -> int:
        """How many distinct colors the profile expects in the chart.

        A profile may list multiple `HueRange` entries that map to the
        same perceived color (red wraps around the hue circle); those
        share a name and count as one. Used by the auto-suggest's
        hue-peak signal.
        """
        return len({hue.name for hue in self.hues})


@dataclass(frozen=True)
class ProfileMatch:
    """Result of `suggest_profile()` — advisory only."""

    profile: MtfProfile | None
    confidence: float  # 0..1
    reason: str
    detected_hue_peaks: int


class ProfileMismatch(Exception):
    """Raised when a declared profile disagrees with an image, or when
    an undeclared image cannot be matched to any candidate profile.

    Generalizes PR #931's B1 fail-loud gate: an unrecognized or
    mismatched chart is refused, not guessed (ADR-038 §1).
    """
