"""Profile dispatch: hue masks → committed-field skeletons (#963).

Both the extractor (`pipeline.py`) and the render-match scorer
(`rendermatch.py`) need the same answer to the same question: given a
declared profile and a chart image, which of the four committed fields
({10S, 10M, 30S, 30M}) does each curve in the image map to, and where
does the skeleton for that field sit?

`field_skeletons()` is that single answer. It dispatches on
`(style_axis, hue_meaning)` exactly once, runs the hue mask + skeleton +
S/M split pipeline, and returns a `dict[field_name, skeleton_mask]`.

Out-of-band combinations raise `NotImplementedError` — generalizing PR
#931's B1 fail-loud gate. Four combinations are currently wired:

- `(SPLIT_BY_DASH, FREQUENCY)` — Sigma + 7Artisans dialects: each hue is
  a frequency, CC-width split gives S/M per hue. (7Artisans inverts the
  S/M labels: dashed = S, solid = M; opt in via `profile.dashed_is_sagittal`.)
- `(HUE_IS_CURVE, CURVE_IDENTITY)` — Samyang dialect: each hue uniquely
  identifies one curve; the name encodes both frequency and S/M.
- `(HUE_IS_CURVE, SAGITTAL_MERIDIONAL)` — Tokina dialect: hue carries S/M
  (named "S-*"/"M-*"); within each hue, `y_band_split` separates the
  upper frequency from the lower.
- `(SPLIT_BY_DASH, Y_BAND_IS_FREQUENCY)` — Viltrox B&W dialect: a single
  neutral mask is split by `y_band_split` into frequency groups, then by
  CC-width within each group for S/M.
"""

from __future__ import annotations

import re

import cv2
import numpy as np

from ..profiles.types import MtfProfile
from .masks import masks_by_curve_name
from .skeleton import close_and_skeletonize
from .split import split_sm_by_cc_width
from .types import PlotBox


# Curve-identity hue names follow `<freq><sm>-<color-tag>` (e.g.
# "10S-red", "30M-light-grey"). The regex is anchored to enforce the
# convention — a typo in `declared.py` should fail loud here, not
# silently mis-map.
_CURVE_IDENTITY_NAME = re.compile(r"^(?P<freq>\d{2})(?P<sm>[SM])(?:-.+)?$")


# Map (frequency, S/M) → committed-data field name. None when the
# combination is not part of the canonical (10S, 10M, 30S, 30M) set
# (the schema in `src/types/mtf.ts`).
_FIELD_BY_KEY: dict[tuple[int, str], str] = {
    (10, "S"): "contrast10S",
    (10, "M"): "contrast10M",
    (30, "S"): "resolution30S",
    (30, "M"): "resolution30M",
}


def curve_field(freq_lpmm: int, sm: str) -> str | None:
    """Map (frequency, S/M) → committed-data field name, or None when
    the combination is not part of the canonical (10S, 10M, 30S, 30M) set."""
    return _FIELD_BY_KEY.get((freq_lpmm, sm))


def parse_curve_identity_name(name: str) -> tuple[int, str]:
    """Parse a `CURVE_IDENTITY` hue name like '10S-red' → (10, 'S')."""
    m = _CURVE_IDENTITY_NAME.match(name)
    if not m:
        raise ValueError(
            f"profile uses hue_meaning='CURVE_IDENTITY' but hue name {name!r} "
            f"does not follow the '<freq><sm>-<color>' convention "
            f"(e.g. '10S-red', '30M-light-grey')"
        )
    return int(m.group("freq")), m.group("sm")


def unique_named_hues(profile: MtfProfile) -> tuple[str, ...]:
    """Distinct hue names in declaration order (wrap-around collapsed)."""
    seen: list[str] = []
    for hue in profile.hues:
        if hue.name not in seen:
            seen.append(hue.name)
    return tuple(seen)


# Sagittal/meridional hue names follow `<sm>-<color-tag>` (e.g. "S-red",
# "M-blue"). The regex enforces the convention so a typo in `declared.py`
# fails loud here, not silently mis-maps.
_SAGITTAL_MERIDIONAL_NAME = re.compile(r"^(?P<sm>[SM])(?:-.+)?$")


def parse_sagittal_meridional_name(name: str) -> str:
    """Parse a `SAGITTAL_MERIDIONAL` hue name like 'S-red' → 'S'."""
    m = _SAGITTAL_MERIDIONAL_NAME.match(name)
    if not m:
        raise ValueError(
            f"profile uses hue_meaning='SAGITTAL_MERIDIONAL' but hue name "
            f"{name!r} does not follow the '<S|M>-<color>' convention "
            f"(e.g. 'S-red', 'M-blue')"
        )
    return m.group("sm")


def split_by_y_band(
    mask: np.ndarray, plot_box: PlotBox, split_fraction: float
) -> tuple[np.ndarray, np.ndarray]:
    """Slice a binary mask into upper and lower halves at a fraction of plot height.

    Pixels strictly above (smaller y) the split line go into `upper`;
    pixels at or below the line go into `lower`. Both outputs are full-size
    masks (the unused half is zeros) so downstream code can keep working
    in image coordinates.
    """
    if not 0.0 < split_fraction < 1.0:
        raise ValueError(f"split_fraction must be in (0, 1): {split_fraction}")
    split_y = int(round(plot_box.y_top + split_fraction * plot_box.height))
    upper = np.zeros_like(mask)
    lower = np.zeros_like(mask)
    upper[:split_y, :] = mask[:split_y, :]
    lower[split_y:, :] = mask[split_y:, :]
    return upper, lower


def field_skeletons(
    bgr: np.ndarray,
    profile: MtfProfile,
    plot_box: PlotBox | None = None,
) -> dict[str, np.ndarray]:
    """Run hue masking → skeleton → S/M split, keyed by committed field.

    Output: ``{field_name: uint8 skeleton mask}``. Fields with no
    detectable curve in the image are simply absent — callers tolerate
    missing keys (the sampler treats them as missing data, the IoU
    scorer treats them as the "skeleton side empty" case).

    `plot_box` is required for profiles that declare `y_band_split`
    (Tokina, Viltrox) since the y-band classifier needs to know where
    the plot area sits in pixel coordinates.
    """
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    curve_masks = masks_by_curve_name(hsv, profile)

    # Clip masks to the plot box when supplied. Required for profiles whose
    # hue range catches off-plot pixels (Viltrox's neutral mask captures
    # title text, axis labels, gridlines, and the F8 panel below). The Sigma
    # and Samyang dialects don't need this — their hue ranges are color-
    # specific enough that off-plot pixels never qualify — but applying
    # uniformly is harmless when plot_box is given.
    if plot_box is not None:
        clip = np.zeros_like(next(iter(curve_masks.values())))
        clip[plot_box.y_top : plot_box.y_bottom + 1,
             plot_box.x_left : plot_box.x_right + 1] = 1
        curve_masks = {name: (m & clip) for name, m in curve_masks.items()}

    out: dict[str, np.ndarray] = {}

    if profile.style_axis == "SPLIT_BY_DASH" and profile.hue_meaning == "FREQUENCY":
        # Each hue = one frequency. After skeletonize+CC-split, the longest
        # CC is the solid line; remainder is dashed. Which one is S vs M
        # depends on `dashed_is_sagittal` (Sigma: False, 7Artisans: True).
        solid_sm, dashed_sm = ("M", "S") if profile.dashed_is_sagittal else ("S", "M")
        freq_by_color = dict(zip(unique_named_hues(profile), profile.frequencies_lpmm))
        for color_name, mask in curve_masks.items():
            skeleton = close_and_skeletonize(mask)
            split = split_sm_by_cc_width(skeleton)
            freq = freq_by_color[color_name]
            for sm, sk in ((solid_sm, split.sagittal), (dashed_sm, split.meridional)):
                field = curve_field(freq, sm)
                if field is not None:
                    out[field] = sk
    elif (
        profile.style_axis == "HUE_IS_CURVE"
        and profile.hue_meaning == "CURVE_IDENTITY"
    ):
        for hue_name, mask in curve_masks.items():
            freq, sm = parse_curve_identity_name(hue_name)
            skeleton = close_and_skeletonize(mask)
            field = curve_field(freq, sm)
            if field is not None:
                out[field] = skeleton
    elif (
        profile.style_axis == "HUE_IS_CURVE"
        and profile.hue_meaning == "SAGITTAL_MERIDIONAL"
    ):
        # Each hue carries S or M; y-band splits each hue into upper
        # frequency (first in frequencies_lpmm) and lower frequency.
        if plot_box is None or profile.y_band_split is None:
            raise ValueError(
                "SAGITTAL_MERIDIONAL profile requires plot_box and "
                "y_band_split — both are needed for y-band dispatch"
            )
        upper_freq, lower_freq = profile.frequencies_lpmm[0], profile.frequencies_lpmm[1]
        for hue_name, mask in curve_masks.items():
            sm = parse_sagittal_meridional_name(hue_name)
            upper_mask, lower_mask = split_by_y_band(
                mask, plot_box, profile.y_band_split
            )
            for freq, band_mask in (
                (upper_freq, upper_mask),
                (lower_freq, lower_mask),
            ):
                field = curve_field(freq, sm)
                if field is not None and band_mask.any():
                    out[field] = close_and_skeletonize(band_mask)
    elif (
        profile.style_axis == "SPLIT_BY_DASH"
        and profile.hue_meaning == "Y_BAND_IS_FREQUENCY"
    ):
        # Single neutral mask, no informative hue. Split by y-band into
        # frequency groups, then CC-split within each band for S/M.
        if plot_box is None or profile.y_band_split is None:
            raise ValueError(
                "Y_BAND_IS_FREQUENCY profile requires plot_box and "
                "y_band_split — both are needed for y-band dispatch"
            )
        if len(curve_masks) != 1:
            raise ValueError(
                f"Y_BAND_IS_FREQUENCY expects one neutral hue; "
                f"profile {profile.name!r} declares {len(curve_masks)}"
            )
        upper_freq, lower_freq = profile.frequencies_lpmm[0], profile.frequencies_lpmm[1]
        solid_sm, dashed_sm = ("M", "S") if profile.dashed_is_sagittal else ("S", "M")
        single_mask = next(iter(curve_masks.values()))
        upper_mask, lower_mask = split_by_y_band(
            single_mask, plot_box, profile.y_band_split
        )
        for freq, band_mask in (
            (upper_freq, upper_mask),
            (lower_freq, lower_mask),
        ):
            if not band_mask.any():
                continue
            skeleton = close_and_skeletonize(band_mask)
            split = split_sm_by_cc_width(skeleton)
            for sm, sk in ((solid_sm, split.sagittal), (dashed_sm, split.meridional)):
                field = curve_field(freq, sm)
                if field is not None:
                    out[field] = sk
    else:
        raise NotImplementedError(
            f"profile dispatch not implemented: style_axis={profile.style_axis!r}, "
            f"hue_meaning={profile.hue_meaning!r}"
        )

    return out
