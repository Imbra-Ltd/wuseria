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
#931's B1 fail-loud gate. Two combinations are currently wired:

- `(SPLIT_BY_DASH, FREQUENCY)` — Sigma dialect: each hue is a frequency,
  CC-width split gives S/M per hue.
- `(HUE_IS_CURVE, CURVE_IDENTITY)` — Samyang dialect: each hue uniquely
  identifies one curve; the name encodes both frequency and S/M.
"""

from __future__ import annotations

import re

import cv2
import numpy as np

from ..profiles.types import MtfProfile
from .masks import masks_by_curve_name
from .skeleton import close_and_skeletonize
from .split import split_sm_by_cc_width


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


def field_skeletons(
    bgr: np.ndarray, profile: MtfProfile
) -> dict[str, np.ndarray]:
    """Run hue masking → skeleton → S/M split, keyed by committed field.

    Output: ``{field_name: uint8 skeleton mask}``. Fields with no
    detectable curve in the image are simply absent — callers tolerate
    missing keys (the sampler treats them as missing data, the IoU
    scorer treats them as the "skeleton side empty" case).
    """
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    curve_masks = masks_by_curve_name(hsv, profile)

    out: dict[str, np.ndarray] = {}

    if profile.style_axis == "SPLIT_BY_DASH" and profile.hue_meaning == "FREQUENCY":
        # Each hue = one frequency. After skeletonize+CC-split, S=solid, M=dashed.
        freq_by_color = dict(zip(unique_named_hues(profile), profile.frequencies_lpmm))
        for color_name, mask in curve_masks.items():
            skeleton = close_and_skeletonize(mask)
            split = split_sm_by_cc_width(skeleton)
            freq = freq_by_color[color_name]
            for sm, sk in (("S", split.sagittal), ("M", split.meridional)):
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
    else:
        raise NotImplementedError(
            f"profile dispatch not implemented: style_axis={profile.style_axis!r}, "
            f"hue_meaning={profile.hue_meaning!r}"
        )

    return out
