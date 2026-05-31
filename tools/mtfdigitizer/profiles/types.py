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
# - `SAGITTAL_MERIDIONAL`   — hue = S vs M (red=S, blue=M in the Tokina
#                             dialect); frequency is then carried by
#                             curve y-position, declared via
#                             `MtfProfile.y_band_split`
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
HueMeaning = Literal[
    "FREQUENCY",
    "SAGITTAL_MERIDIONAL",
    "CURVE_IDENTITY",
    "Y_BAND_IS_FREQUENCY",
    "CC_RANK_BY_MEAN_Y",
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
