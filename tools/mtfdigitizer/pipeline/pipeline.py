"""Top-level pipeline orchestrator (#935, ADR-038 §2-3).

Reads chart → dispatches per profile dialect → samples each curve at the
11 fixed points. The "which curve becomes which committed field" logic
lives in `dispatch.field_skeletons()` so the render-match scorer reuses
the same answer the extractor computes (#963).

Post-extraction the pipeline applies two physics-grounded corrections:

- **Sister fallback.** When a curve has no real ink near a sample
  fraction (the dispatch's skeleton is empty in the bracket window),
  the reading falls back to the sister curve's value — i.e. 10M takes
  10S's value when 10M has no ink, and vice versa; same for 30S/30M.
  Lossy but defensible: at the optical axis sister curves are equal
  (B4), and where one curve drops off near the field edge the other
  often tracks closely. Better than letting the DP path drift onto a
  parallel curve's ink and reporting a misleading value.

- **Center symmetry.** At fraction 0.0 (the optical axis), sagittal
  and meridional MTF are equal by physics (B4). Whatever value each
  frequency reports at center is averaged so S and M match exactly,
  removing any anti-aliasing or pixel-noise asymmetry.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from ..loader import load_chart_bgr
from ..profiles.types import MtfProfile
from .dispatch import curve_field, field_skeletons, unique_named_hues
from .masks import masks_by_curve_name
from .skeleton import close_and_skeletonize
from .split import split_sm_by_cc_width
from .sampling import (
    SAMPLE_FRACTIONS,
    sample_positions_mm,
    sample_skeleton_at_fraction,
)
from .types import ExtractedChart, PlotBox, SampledReading


SAMPLE_POINTS: tuple[float, ...] = SAMPLE_FRACTIONS  # re-export


# Half-width of the column window in which raw ink is required for a
# sample to count as "really there" (i.e. not eligible for sister
# fallback). About half a dash period — small enough that a normal
# dashed curve still passes (dashes are ~10 px wide; even mid-gap
# columns find ink within ~10 px), but big enough to fire when the
# curve is genuinely absent (Tokina 11-18 left edge where 10M
# starts ~25 px right of the plot box). Earlier values of 30 were
# overshooting: single dashes were not enough to trigger fallback,
# but their ~0.01 anti-aliasing biases were inheriting from the
# sister and broadcasting across the curve.
_INK_PRESENCE_HALF_WIDTH: int = 10


# Horizontal kernel width used to bridge a dashed curve's gaps when
# building its sister-fallback presence mask under the
# (SPLIT_BY_DASH, GEODESIC_DP) dispatch. Wide enough (~0.5 mm at Sigma
# plot scale) that a curve whose last dash falls just short of the plot
# edge still reads "present" at the field-edge sample — so the DP path's
# extrapolated value is kept instead of being overwritten by the
# diverging solid (sister) curve. Vertical extent stays 3 px so the mask
# does not pull the raw-centroid snap off the true stroke.
_DASH_PRESENCE_BRIDGE_W: int = 121


# Sister-curve pairs by committed field name. Both directions so the
# fallback works regardless of which member has the missing ink.
_SISTER_OF: dict[str, str] = {
    "contrast10S": "contrast10M",
    "contrast10M": "contrast10S",
    "resolution30S": "resolution30M",
    "resolution30M": "resolution30S",
}


def _sample_curve(
    skeleton, plot_box: PlotBox, raw_mask=None
) -> tuple[float | None, ...]:
    """11-point sample of one skeleton, returns one MTF value per fraction.

    When ``raw_mask`` is supplied, each sample is snapped to the raw
    ink centroid in a tight window around the skeleton's predicted y —
    restores pixel-accuracy on solid strokes without losing DP
    interpolation across dash gaps.
    """
    return tuple(
        sample_skeleton_at_fraction(skeleton, f, plot_box, raw_mask=raw_mask)
        for f in SAMPLE_FRACTIONS
    )


def _ink_presence_per_field(
    skeletons: dict[str, np.ndarray], plot_box: PlotBox
) -> dict[str, tuple[bool, ...]]:
    """For each field, return whether real ink exists in a wide window
    of each sample fraction.

    True means the skeleton has at least one pixel within
    ``_INK_PRESENCE_HALF_WIDTH`` columns of the sample target —
    proxy for "this curve really exists at this fraction." False
    means the sample is a candidate for sister fallback.
    """
    out: dict[str, tuple[bool, ...]] = {}
    for field, skel in skeletons.items():
        presence: list[bool] = []
        for f in SAMPLE_FRACTIONS:
            target_x = int(round(plot_box.x_left + f * plot_box.width))
            x_lo = max(plot_box.x_left, target_x - _INK_PRESENCE_HALF_WIDTH)
            x_hi = min(plot_box.x_right, target_x + _INK_PRESENCE_HALF_WIDTH)
            window = skel[plot_box.y_top : plot_box.y_bottom + 1, x_lo : x_hi + 1]
            presence.append(bool(window.any()))
        out[field] = tuple(presence)
    return out


def _apply_sister_fallback(
    samples: dict[str, tuple[float | None, ...]],
    presence: dict[str, tuple[bool, ...]],
) -> tuple[dict[str, tuple[float | None, ...]], dict[str, int]]:
    """Replace samples where ink is absent with the sister curve's value.

    Returns ``(samples, fallback_count_by_field)``. The counter
    records how many of a field's 11 samples were filled from the
    sister curve (i.e. the field's own raw ink was absent and the
    sister's was present); samples that stayed `None` because both
    curves lacked ink do not count as fallbacks.
    """
    out: dict[str, tuple[float | None, ...]] = {}
    fallback_count: dict[str, int] = {}
    for field, values in samples.items():
        sister = _SISTER_OF.get(field)
        sister_values = samples.get(sister, (None,) * len(SAMPLE_FRACTIONS)) if sister else (None,) * len(SAMPLE_FRACTIONS)
        field_presence = presence.get(field, (False,) * len(SAMPLE_FRACTIONS))
        sister_presence = presence.get(sister, (False,) * len(SAMPLE_FRACTIONS)) if sister else (False,) * len(SAMPLE_FRACTIONS)
        fixed: list[float | None] = []
        count = 0
        for i, v in enumerate(values):
            if field_presence[i]:
                fixed.append(v)
            elif sister_presence[i]:
                # Sister has real ink here; trust it over our drifted value.
                fixed.append(sister_values[i])
                count += 1
            else:
                # Neither curve has ink — keep whatever the DP path
                # interpolated (or None if the curve was missing entirely).
                fixed.append(v)
        out[field] = tuple(fixed)
        fallback_count[field] = count
    return out, fallback_count


def _apply_center_symmetry(
    samples: dict[str, tuple[float | None, ...]],
) -> dict[str, tuple[float | None, ...]]:
    """Force S = M at the optical axis (fraction 0.0) by copying S to M.

    At position 0 sagittal and meridional MTF are equal by physics
    (B4). Take S as the source of truth and override M with it (not
    the average): on charts where the DP path for the M curve has
    drifted near center (Tokina 11-18, where 10M's ink doesn't
    quite reach frac 0.0 and the path lands on a nearby curve's
    stripe), averaging would split the difference between the right
    value and the drifted value. The S curve is solid-line, less
    susceptible to drift, and almost always the cleaner anchor.
    """
    out = {field: list(values) for field, values in samples.items()}
    for s_field, m_field in (
        ("contrast10S", "contrast10M"),
        ("resolution30S", "resolution30M"),
    ):
        if s_field not in out or m_field not in out:
            continue
        s_val = out[s_field][0]
        m_val = out[m_field][0]
        if s_val is None and m_val is None:
            continue
        if s_val is None:
            out[s_field][0] = m_val
        else:
            # B4: at the optical axis, S=M. Use S for both — solid
            # strokes are less prone to centroid drift than dashed.
            out[m_field][0] = s_val
    return {field: tuple(values) for field, values in out.items()}


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


def _hue_masks_for_presence(
    bgr: np.ndarray, profile: MtfProfile, plot_box: PlotBox
) -> dict[str, np.ndarray]:
    """Build per-field RAW-ink masks for the ink-presence check.

    The skeleton coming out of the dispatch is the DP path rasterised
    everywhere, so it always says "ink present" — useless as a
    presence signal. We need the raw per-hue mask the dispatch
    consumed. Re-extract it here (cheap: HSV + range threshold) and
    map each hue's mask to both committed fields under that hue.
    """
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    curve_masks = masks_by_curve_name(hsv, profile)
    if plot_box is not None:
        clip = np.zeros_like(next(iter(curve_masks.values())))
        clip[
            plot_box.y_top : plot_box.y_bottom + 1,
            plot_box.x_left : plot_box.x_right + 1,
        ] = 1
        curve_masks = {name: (m & clip) for name, m in curve_masks.items()}
    # Map per-hue raw mask to the two fields that share that hue.
    # The mapping depends on the profile; we read it from the hue
    # name convention ("S-red" → contrast10S + resolution30S, etc).
    out: dict[str, np.ndarray] = {}
    if profile.style_axis == "SPLIT_BY_DASH" and profile.hue_meaning == "GEODESIC_DP":
        # Color-named hues (one per frequency); each splits into a solid
        # (S) and dashed (M) sub-skeleton. The dashed sub-skeleton is
        # horizontally dilated to bridge dash gaps before it becomes the
        # presence signal: a raw gappy dashed skeleton makes the
        # ink-presence check read "absent" mid-gap and triggers a
        # spurious sister fallback (M←S), which is wrong precisely where
        # the dashed curve diverges from the solid one (the field edge).
        # Dilating leaves presence False only past the curve's true
        # extent, where sister fallback is genuinely warranted.
        solid_sm, dashed_sm = ("M", "S") if profile.dashed_is_sagittal else ("S", "M")
        freq_by_color = dict(zip(unique_named_hues(profile), profile.frequencies_lpmm))
        bridge = cv2.getStructuringElement(
            cv2.MORPH_RECT, (_DASH_PRESENCE_BRIDGE_W, 3)
        )
        for color_name, mask in curve_masks.items():
            split = split_sm_by_cc_width(close_and_skeletonize(mask))
            freq = freq_by_color[color_name]
            # Solid line is continuous — its own skeleton is the presence
            # signal. Dashed line is bridged so a dash within ~half a mm
            # of the field edge still marks the edge sample present; the
            # DP path holds the curve's real value there, whereas sister
            # fallback would wrongly copy the (diverging) solid value.
            for sm, sub in (
                (solid_sm, split.sagittal),
                (dashed_sm, cv2.dilate(split.meridional.astype(np.uint8), bridge)),
            ):
                field = curve_field(freq, sm)
                if field is not None:
                    out[field] = sub
    elif profile.style_axis == "HUE_IS_CURVE" and profile.hue_meaning in (
        "SAGITTAL_MERIDIONAL", "PER_COLUMN_RIDGE",
        "SKELETON_CONTINUOUS_PICK", "GEODESIC_DP",
    ):
        for hue_name, mask in curve_masks.items():
            sm = hue_name[0]  # "S" or "M"
            out[f"contrast10{sm}"] = mask
            out[f"resolution30{sm}"] = mask
    # Other dialects: presence check falls back to the skeleton itself
    # (legacy behaviour). The caller treats missing keys as "no
    # presence info — trust whatever value the sampler returned."
    return out


def extract_chart(
    image_path: str | Path,
    profile: MtfProfile,
    plot_box: PlotBox,
    image_height_mm: float,
) -> ExtractedChart:
    """End-to-end MTF extraction for one chart image.

    Returns 11 `SampledReading` rows (one per fixed sample point).
    Two post-extraction corrections are applied: sister fallback when
    a curve has no ink at a fraction, and center symmetry forcing S=M
    at fraction 0.0 by physics.

    Raises `NotImplementedError` for profile (style_axis, hue_meaning)
    combinations not yet wired by `dispatch.field_skeletons()`.
    """
    bgr = load_chart_bgr(image_path)
    skeletons = field_skeletons(bgr, profile, plot_box)

    # Re-derive per-field raw masks for two uses: (1) tight-window
    # raw-centroid snapping at sample time (restores pixel-accuracy
    # on solid strokes), (2) wider-window ink-presence check for the
    # sister fallback. Cheap — HSV + range threshold on the chart.
    presence_masks = _hue_masks_for_presence(bgr, profile, plot_box)

    samples_per_field: dict[str, tuple[float | None, ...]] = {
        field: _sample_curve(skel, plot_box, raw_mask=presence_masks.get(field))
        for field, skel in skeletons.items()
    }

    # Sister fallback: replace samples where the raw ink is absent
    # with the sister curve's value. Use the raw per-hue mask, not
    # the DP-rasterised skeleton (which has ink everywhere).
    presence = (
        _ink_presence_per_field(presence_masks, plot_box) if presence_masks else {}
    )
    fallback_count: dict[str, int] = {}
    if presence:
        samples_per_field, fallback_count = _apply_sister_fallback(
            samples_per_field, presence
        )
    samples_per_field = _apply_center_symmetry(samples_per_field)

    return ExtractedChart(
        source_path=str(image_path),
        profile_name=profile.name,
        plot_box=plot_box,
        image_height_mm=image_height_mm,
        readings=_readings_to_dict(samples_per_field, plot_box, image_height_mm),
        sister_fallback_count=fallback_count,
    )
