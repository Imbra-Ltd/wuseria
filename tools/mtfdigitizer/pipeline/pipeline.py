"""Top-level pipeline orchestrator (#935, ADR-038 §2-3).

Composes the small stages from `masks.py`, `skeleton.py`, `split.py`,
and `sampling.py` into one extraction. Dispatch on `profile.style_axis`
and `profile.hue_meaning` to wire stages correctly per dialect.

Curve-name → output-field mapping:

- `style_axis == "SPLIT_BY_DASH"` and `hue_meaning == "FREQUENCY"`
  (Sigma dialect): each hue is a frequency; CC-split gives S/M per
  hue. So {red→10, blue→30} × {S, M} = {10S, 10M, 30S, 30M}.
- `style_axis == "HUE_IS_CURVE"` and `hue_meaning == "CURVE_IDENTITY"`
  (Samyang dialect): the hue name already encodes both frequency and
  S/M, e.g. "10S-red" or "30M-light-grey". The name is parsed to map
  directly.

Other combinations are not yet declared and raise `NotImplementedError`
(fail loud, per the ADR-038 §1 spirit).
"""

from __future__ import annotations

import re
from pathlib import Path

from ..loader import load_chart_bgr
import cv2

from ..profiles.types import MtfProfile
from .masks import masks_by_curve_name
from .sampling import (
    SAMPLE_FRACTIONS,
    sample_positions_mm,
    sample_skeleton_at_fraction,
)
from .skeleton import close_and_skeletonize
from .split import split_sm_by_cc_width
from .types import ExtractedChart, PlotBox, SampledReading


SAMPLE_POINTS: tuple[float, ...] = SAMPLE_FRACTIONS  # re-export


# Curve-identity hue names follow `<freq><sm>-<color-tag>` (e.g. "10S-red",
# "30M-light-grey"). The freq prefix is one of `10`, `20`, `30`, `40`; the
# sm letter is `S` or `M`. The regex is anchored to enforce the convention
# — a typo in `declared.py` should fail loud here, not silently mis-map.
_CURVE_IDENTITY_NAME = re.compile(r"^(?P<freq>\d{2})(?P<sm>[SM])(?:-.+)?$")


_FIELD_BY_KEY: dict[tuple[int, str], str] = {
    (10, "S"): "contrast10S",
    (10, "M"): "contrast10M",
    (30, "S"): "resolution30S",
    (30, "M"): "resolution30M",
}


def _curve_field(freq_lpmm: int, sm: str) -> str | None:
    """Map (frequency, S/M) → committed-data field name, or None when
    the combination is not part of the canonical (10S, 10M, 30S, 30M) set
    (the schema in `src/types/mtf.ts`)."""
    return _FIELD_BY_KEY.get((freq_lpmm, sm))


def _parse_curve_identity_name(name: str) -> tuple[int, str]:
    """Parse a `CURVE_IDENTITY` hue name like '10S-red' → (10, 'S')."""
    m = _CURVE_IDENTITY_NAME.match(name)
    if not m:
        raise ValueError(
            f"profile uses hue_meaning='CURVE_IDENTITY' but hue name {name!r} "
            f"does not follow the '<freq><sm>-<color>' convention "
            f"(e.g. '10S-red', '30M-light-grey')"
        )
    return int(m.group("freq")), m.group("sm")


def _sample_curve(
    skeleton, plot_box: PlotBox, image_height_mm: float
) -> tuple[float | None, ...]:
    """11-point sample of one skeleton, returns one MTF value per fraction."""
    return tuple(
        sample_skeleton_at_fraction(skeleton, f, plot_box) for f in SAMPLE_FRACTIONS
    )


def _readings_to_dict(
    samples_per_field: dict[str, tuple[float | None, ...]],
    plot_box: PlotBox,
    image_height_mm: float,
) -> tuple[SampledReading, ...]:
    """Build the 11 SampledReading rows from per-field column samples."""
    positions = sample_positions_mm(plot_box, image_height_mm)
    rows: list[SampledReading] = []
    for i, pos in enumerate(positions):
        rows.append(
            SampledReading(
                position_mm=pos,
                contrast10S=samples_per_field.get("contrast10S", (None,) * 11)[i],
                contrast10M=samples_per_field.get("contrast10M", (None,) * 11)[i],
                resolution30S=samples_per_field.get("resolution30S", (None,) * 11)[i],
                resolution30M=samples_per_field.get("resolution30M", (None,) * 11)[i],
            )
        )
    return tuple(rows)


def extract_chart(
    image_path: str | Path,
    profile: MtfProfile,
    plot_box: PlotBox,
    image_height_mm: float,
) -> ExtractedChart:
    """End-to-end MTF extraction for one chart image.

    Returns 11 `SampledReading` rows (one per fixed sample point), with
    `None` for any field whose curve has no usable data at that point
    (B2 contract — never fabricated).

    Raises `NotImplementedError` for profile (style_axis, hue_meaning)
    combinations not yet wired. Two combinations are currently wired:

    - (SPLIT_BY_DASH, FREQUENCY) → Sigma dialect
    - (HUE_IS_CURVE, CURVE_IDENTITY) → Samyang dialect
    """
    bgr = load_chart_bgr(image_path)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    curve_masks = masks_by_curve_name(hsv, profile)

    samples_per_field: dict[str, tuple[float | None, ...]] = {}

    if profile.style_axis == "SPLIT_BY_DASH" and profile.hue_meaning == "FREQUENCY":
        # Each hue = one frequency. After skeletonize+CC-split, S=solid, M=dashed.
        freq_by_color = dict(zip(_unique_named_hues(profile), profile.frequencies_lpmm))
        for color_name, mask in curve_masks.items():
            skeleton = close_and_skeletonize(mask)
            split = split_sm_by_cc_width(skeleton)
            freq = freq_by_color[color_name]
            for sm, sk in (("S", split.sagittal), ("M", split.meridional)):
                field = _curve_field(freq, sm)
                if field is not None:
                    samples_per_field[field] = _sample_curve(sk, plot_box, image_height_mm)
    elif (
        profile.style_axis == "HUE_IS_CURVE"
        and profile.hue_meaning == "CURVE_IDENTITY"
    ):
        for hue_name, mask in curve_masks.items():
            freq, sm = _parse_curve_identity_name(hue_name)
            skeleton = close_and_skeletonize(mask)
            field = _curve_field(freq, sm)
            if field is not None:
                samples_per_field[field] = _sample_curve(skeleton, plot_box, image_height_mm)
    else:
        raise NotImplementedError(
            f"profile dispatch not implemented: style_axis={profile.style_axis!r}, "
            f"hue_meaning={profile.hue_meaning!r}"
        )

    return ExtractedChart(
        source_path=str(image_path),
        profile_name=profile.name,
        plot_box=plot_box,
        image_height_mm=image_height_mm,
        readings=_readings_to_dict(samples_per_field, plot_box, image_height_mm),
    )


def _unique_named_hues(profile: MtfProfile) -> tuple[str, ...]:
    """Distinct hue names in declaration order (wrap-around collapsed)."""
    seen: list[str] = []
    for hue in profile.hues:
        if hue.name not in seen:
            seen.append(hue.name)
    return tuple(seen)
