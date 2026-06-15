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
- `(SPLIT_BY_DASH, FREQUENCY_PER_HUE_RIDGE)` — TTartisan max-aperture
  dialect: same hue→frequency convention, but the S and T curves run
  within ~5 px of each other so their antialiased halos fuse into one
  CC. Per-column ridge centroids preserve both curves; the
  higher-coverage track is solid (S unless `dashed_is_sagittal`).
- `(HUE_IS_CURVE, CURVE_IDENTITY)` — Samyang dialect: each hue uniquely
  identifies one curve; the name encodes both frequency and S/M.
- `(HUE_IS_CURVE, SAGITTAL_MERIDIONAL)` — Tokina prime dialect: hue carries
  S/M (named "S-*"/"M-*"); within each hue, `y_band_split` separates the
  upper frequency from the lower. Works when the two frequencies sit in
  cleanly separable y-bands.
- `(HUE_IS_CURVE, PER_COLUMN_RIDGE)` — Tokina wide-zoom variant where the
  two frequencies overlap in y near center (30 lp/mm starts at OTF ~0.90
  while 10 lp/mm starts at 1.00; their y-bands intersect AND dashed-line
  fragments of the two curves interleave in y across the field, so any
  CC-based partition misclassifies). Per-column ridge tracking handles
  arbitrary curve overlap as long as the two curves of one color never
  cross within a column: the upper run per column = upper frequency,
  the lower run = lower frequency. Uses `ridge.ridge_tracks_for_hue`.
- `(HUE_IS_CURVE, SKELETON_CONTINUOUS_PICK)` — robust per-hue variant
  ported from the retired mtf-extract-skeleton.py. Dilate + skeletonize
  per hue, split into connected components by mean-y (top = upper
  freq, bottom = lower freq), then walk each CC column-by-column
  picking the branch closest to the previous y (greedy y-continuity).
  Replaces per-column ridge for the Tokina wide-zoom case: the per-
  CC continuity walk handles fragmented dashed curves AND curve
  coincidence cleanly. See `pipeline/continuous_pick.py`.
- `(HUE_IS_CURVE, GEODESIC_DP)` — per-hue Viterbi shortest path
  through the dilated mask. Replaces skeletonization with a global-
  optimum DP whose smoothness prior bridges dashed-line gaps without
  the staircase coverage holes that defeat sampling, and refuses to
  hop to a parallel curve at near-touching regions. Default for the
  Tokina family (5 charts). See `pipeline/dp_extract.py`.
- `(SPLIT_BY_DASH, Y_BAND_IS_FREQUENCY)` — Viltrox B&W dialect: a single
  neutral mask is split by `y_band_split` into frequency groups, then by
  CC-width within each group for S/M.
- `(SPLIT_BY_DASH, CC_RANK_BY_MEAN_Y)` — Viltrox B&W tightly-clustered
  variant. Skeletonize the single neutral mask once, then rank connected
  components by mean y-position and split at the largest y-gap into
  upper-frequency and lower-frequency clusters. Within each cluster,
  CC-width split picks solid (S by default; M if `dashed_is_sagittal`)
  from dashed. Adapts to fragmented dashed lines (more than 4 CCs total)
  without depending on a fixed `y_band_split` fraction.
- `(SPLIT_BY_DASH, RIDGE_TRACKING)` — geometric per-column ridge
  extraction for charts where CC-based dispatches fuse curves into one
  component (Viltrox AF 75mm f/1.2). See `pipeline/ridge.py` for the
  full algorithm.
"""

from __future__ import annotations

import re

import cv2
import numpy as np

from ..profiles.types import MtfProfile
from .continuous_pick import extract_two_curves_per_hue
from .dp_extract import (
    curve_to_field_skeleton,
    curves_to_field_skeletons,
    extract_one_curve_dp,
    extract_two_curves_dp,
)
from .masks import masks_by_curve_name
from .ridge import (
    ridge_tracks_for_hue,
    ridge_tracks_for_hue_freq_split,
    ridge_tracks_to_fields,
)
from .skeleton import close_and_skeletonize
from .split import split_sm_by_cc_width
from .types import PlotBox


# Curve-identity hue names follow `<freq><sm>-<color-tag>` (e.g.
# "10S-red", "30M-light-grey"). The regex is anchored to enforce the
# convention — a typo in `declared.py` should fail loud here, not
# silently mis-map.
_CURVE_IDENTITY_NAME = re.compile(r"^(?P<freq>\d{2})(?P<sm>[SM])(?:-.+)?$")


# Synthetic field-name convention (ADR-042). Every (frequency, S/M)
# pair maps to a deterministic string: `freq{N}{S|M}`. The names are
# dict keys carried through the pipeline (skeleton dicts, rendermatch
# masks, sampler output, `SampledReading.samples`) and translated to
# the TS schema's frequency-keyed shape at the `emit.py` boundary.
def curve_field(freq_lpmm: int, sm: str) -> str:
    """Synthetic field name for one (frequency, S|M) pair.

    Always returns a name — there is no longer a "not part of the
    canonical set" exclusion now that the schema accepts arbitrary
    frequencies. Caller previously checked `is not None`; that check
    is now a no-op but kept where it appears for readability.
    """
    if sm not in ("S", "M"):
        raise ValueError(f"sm must be 'S' or 'M', got {sm!r}")
    return f"freq{freq_lpmm}{sm}"


def parse_field_name(field: str) -> tuple[int, str]:
    """Inverse of `curve_field`: 'freq10S' → (10, 'S').

    Raises `ValueError` on names that don't follow the convention —
    a sanity check for callers that introspect field names emitted
    by the pipeline.
    """
    import re as _re

    m = _re.match(r"^freq(\d+)([SM])$", field)
    if not m:
        raise ValueError(
            f"field name {field!r} does not follow freq{{N}}{{S|M}} convention"
        )
    return int(m.group(1)), m.group(2)


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


def _component_masks_with_mean_y(
    skeleton: np.ndarray, min_area: int = 5
) -> list[tuple[np.ndarray, float]]:
    """Return (component_mask, mean_y) for each connected component above
    the area floor.

    The area floor rejects single-pixel skeleton noise without dropping
    short dashed fragments — Viltrox's dashes skeletonize to ~10-40
    pixels each.
    """
    sk = skeleton.astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        sk, connectivity=8
    )
    out: list[tuple[np.ndarray, float]] = []
    for label in range(1, num_labels):
        if int(stats[label, cv2.CC_STAT_AREA]) < min_area:
            continue
        component = (labels == label).astype(np.uint8)
        ys = np.nonzero(component)[0]
        if ys.size == 0:
            continue
        out.append((component, float(ys.mean())))
    return out


def _split_components_at_largest_y_gap(
    components: list[tuple[np.ndarray, float]],
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Sort components by mean-y and split at the largest gap into upper
    (smaller y) and lower (larger y) clusters.

    With 4 ideal CCs (2 solid + 2 solid-bridged-dashed) this returns 2+2.
    With more (fragmented dashed lines), the largest-gap heuristic still
    picks the band boundary — within each band the longest CC is the
    solid line; the remainder is dashed. Returns ([], []) when fewer than
    two components are present (caller treats as missing data).
    """
    if len(components) < 2:
        return [], []
    components_sorted = sorted(components, key=lambda c: c[1])
    mean_ys = [c[1] for c in components_sorted]
    gaps = [mean_ys[i + 1] - mean_ys[i] for i in range(len(mean_ys) - 1)]
    split_idx = int(np.argmax(gaps)) + 1
    upper = [c[0] for c in components_sorted[:split_idx]]
    lower = [c[0] for c in components_sorted[split_idx:]]
    return upper, lower


def _solid_dashed_from_components(
    component_masks: list[np.ndarray],
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """Pick the largest CC as solid; OR the rest as dashed.

    Returns (None, None) for an empty cluster; (solid, None) when only
    one CC is present (no dashed pixels to bundle).
    """
    if not component_masks:
        return None, None
    areas = [int(m.sum()) for m in component_masks]
    largest_idx = int(np.argmax(areas))
    solid = component_masks[largest_idx]
    remainder = [m for i, m in enumerate(component_masks) if i != largest_idx]
    if not remainder:
        return solid, None
    dashed = np.zeros_like(solid)
    for m in remainder:
        dashed = dashed | m
    return solid, dashed


# Vertical dilation kernel half-width for cross-hue halo exclusion. A
# line drawn in pure ink (V≈0) surrounded by ±N rows of anti-aliased
# gradient pixels (V rising to 255 over N rows) emits halo pixels in
# the grey hue range out to ~N rows from the line center. Sized for the
# TTartisan press-kit raster where the black line's AA gradient extends
# ~5 px on each side of the 2-px-wide line center.
_HALO_DILATE_DY: int = 5


def _aperture_prefix(hue_name: str) -> str | None:
    """Split a TTartisan-style hue name into its aperture prefix.

    The ADR-044 convention is `<aperture>-<freq>-<color>` (e.g.
    `max-10-black`, `stopped-30-orange`). The aperture prefix is
    everything before the first `-NN-` segment, where `NN` is a
    decimal-digit frequency. Returns `None` when the hue name does
    not match the convention — non-TTartisan profiles using
    `FREQUENCY_PER_HUE_RIDGE` would have to declare their own
    convention if/when they're added.
    """
    parts = hue_name.split("-")
    for i, segment in enumerate(parts):
        if segment.isdigit():
            return "-".join(parts[:i]) if i > 0 else None
    return None


def _build_halo_exclusion_map(
    curve_masks: dict[str, np.ndarray],
    freq_by_color: dict[str, int],
    lower_freq: int,
) -> dict[str, tuple[np.ndarray, ...]]:
    """Build a mapping `{hue_name: (dilated halo masks to subtract, ...)}`.

    For every lower-frequency hue (e.g. `max-10-black`), compute the
    vertically-dilated mask and queue it for subtraction from every
    higher-frequency hue (`max-30-grey`) that shares its aperture
    prefix. Hues with no aperture prefix (non-TTartisan convention)
    contribute no exclusions.
    """
    kernel = np.ones((2 * _HALO_DILATE_DY + 1, 1), np.uint8)
    halo_by_prefix: dict[str, np.ndarray] = {}
    for color_name, mask in curve_masks.items():
        if freq_by_color.get(color_name) != lower_freq:
            continue
        prefix = _aperture_prefix(color_name)
        if prefix is None:
            continue
        halo_by_prefix[prefix] = cv2.dilate(mask.astype(np.uint8), kernel)
    out: dict[str, tuple[np.ndarray, ...]] = {}
    for color_name in curve_masks:
        if freq_by_color.get(color_name) == lower_freq:
            continue  # the lower-freq hue is not contaminated by itself
        prefix = _aperture_prefix(color_name)
        if prefix is None or prefix not in halo_by_prefix:
            continue
        out[color_name] = (halo_by_prefix[prefix],)
    return out


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
                out[curve_field(freq, sm)] = sk
    elif (
        profile.style_axis == "SPLIT_BY_DASH"
        and profile.hue_meaning == "GEODESIC_DP"
    ):
        # Same dash split as (SPLIT_BY_DASH, FREQUENCY): each hue is one
        # frequency, the longest CC is the solid line and the remainder
        # is the dashed line. The difference is the dashed line — its
        # fragments leave the legacy skeleton gappy, so the sampler
        # returns None at any sample column that lands in a dash gap.
        # Here the dashed curve gets a single Viterbi DP pass that
        # bridges the gaps (the smoothness prior IS the interpolation),
        # while the solid line keeps its already-continuous skeleton
        # unchanged. See `pipeline/dp_extract.py::extract_one_curve_dp`.
        if plot_box is None:
            raise ValueError("(SPLIT_BY_DASH, GEODESIC_DP) requires plot_box")
        solid_sm, dashed_sm = ("M", "S") if profile.dashed_is_sagittal else ("S", "M")
        freq_by_color = dict(zip(unique_named_hues(profile), profile.frequencies_lpmm))
        for color_name, mask in curve_masks.items():
            skeleton = close_and_skeletonize(mask)
            split = split_sm_by_cc_width(skeleton)
            freq = freq_by_color[color_name]
            out[curve_field(freq, solid_sm)] = split.sagittal
            dashed_field = curve_field(freq, dashed_sm)
            if split.meridional.any():
                curve = extract_one_curve_dp(split.meridional, plot_box)
                out[dashed_field] = curve_to_field_skeleton(curve, mask)
            else:
                out[dashed_field] = split.meridional
    elif (
        profile.style_axis == "SPLIT_BY_DASH"
        and profile.hue_meaning == "FREQUENCY_PER_HUE_RIDGE"
    ):
        # Each hue carries one frequency with both S (solid) and T
        # (dashed) curves. The raw mask fuses both curves into one CC
        # at coincidence regions (TTartisan max-aperture: S10 and T10
        # halos touch where they run within ~5 px), so the CC-width
        # split used by FREQUENCY can't separate them. Per-column ridge
        # centroids preserve two distinct tracks even at coincidence;
        # higher-coverage track is solid (S by default; M when
        # `dashed_is_sagittal`). See `ridge.ridge_tracks_for_hue_freq_split`.
        if plot_box is None:
            raise ValueError(
                "FREQUENCY_PER_HUE_RIDGE profile requires plot_box for "
                "per-column ridge extraction"
            )
        freq_by_color = dict(
            zip(unique_named_hues(profile), profile.frequencies_lpmm)
        )
        # Cross-hue halo exclusion (#1095): the higher-frequency hue's
        # mask is contaminated by the lower-frequency hue's anti-aliased
        # halo. Concretely on TTartisan max-aperture the grey mask
        # (V∈[90,160]) catches mid-grey pixels along the black line's
        # AA gradient (V=131 lies inside that gradient). Those halo
        # pixels form full-width tracks that out-rank the real T30 dashed
        # curve in top-2-by-coverage selection. For every hue that maps
        # to the lower frequency of the pair (e.g. 10 lp/mm), dilate the
        # mask by `_HALO_DILATE_DY` vertically and subtract it from the
        # higher-frequency hues that share its aperture prefix. The
        # aperture prefix is the part of the hue name before the first
        # `-<freq>-` segment (e.g. `max-10-black` → `max`, per ADR-044).
        lower_freq = min(profile.frequencies_lpmm)
        halo_pairs = _build_halo_exclusion_map(
            curve_masks, freq_by_color, lower_freq
        )
        # Per-hue `dp_y_anchor` override: pick the first HueRange entry
        # whose name matches and use its `dp_y_anchor` when not None.
        # Multiple entries with the same name share the same override
        # (red wrap-around case).
        per_hue_anchor: dict[str, bool] = {}
        for hue in profile.hues:
            if hue.name in per_hue_anchor:
                continue
            if hue.dp_y_anchor is not None:
                per_hue_anchor[hue.name] = hue.dp_y_anchor
        for color_name, mask in curve_masks.items():
            cleaned_mask = mask
            for halo_mask in halo_pairs.get(color_name, ()):
                cleaned_mask = cleaned_mask & ~halo_mask
            freq = freq_by_color[color_name]
            anchor = per_hue_anchor.get(color_name, profile.ridge_dp_y_anchor)
            hue_fields = ridge_tracks_for_hue_freq_split(
                cleaned_mask, plot_box, freq=freq,
                dashed_is_sagittal=profile.dashed_is_sagittal,
                use_y_anchor=anchor,
            )
            out.update(hue_fields)
    elif (
        profile.style_axis == "HUE_IS_CURVE"
        and profile.hue_meaning == "CURVE_IDENTITY"
    ):
        for hue_name, mask in curve_masks.items():
            freq, sm = parse_curve_identity_name(hue_name)
            skeleton = close_and_skeletonize(mask)
            out[curve_field(freq, sm)] = skeleton
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
                if band_mask.any():
                    out[curve_field(freq, sm)] = close_and_skeletonize(band_mask)
    elif (
        profile.style_axis == "HUE_IS_CURVE"
        and profile.hue_meaning == "SAGITTAL_MERIDIONAL_SINGLE_FREQ"
    ):
        # Each hue carries one curve (S or M); the chart image carries one
        # frequency only. Used by Fujifilm per-frequency images (ADR-043).
        # The frequency is the single entry in `profile.frequencies_lpmm`,
        # supplied by the caller per image (the declared base profile
        # carries `frequencies_lpmm=(0,)` as a placeholder; the multipath
        # orchestrator copies the profile with the parsed-from-filename
        # frequency before calling `extract_chart`).
        if len(profile.frequencies_lpmm) != 1:
            raise ValueError(
                "SAGITTAL_MERIDIONAL_SINGLE_FREQ requires exactly one entry "
                f"in frequencies_lpmm; got {profile.frequencies_lpmm!r}"
            )
        freq = profile.frequencies_lpmm[0]
        for hue_name, mask in curve_masks.items():
            sm = parse_sagittal_meridional_name(hue_name)
            if not mask.any():
                continue
            out[curve_field(freq, sm)] = close_and_skeletonize(
                mask, close_kernel_width=profile.close_kernel_width
            )
    elif (
        profile.style_axis == "HUE_IS_CURVE"
        and profile.hue_meaning == "PER_COLUMN_RIDGE"
    ):
        # Each hue carries S or M (same naming as SAGITTAL_MERIDIONAL).
        # Within each hue, run per-column ridge tracking: for every x
        # column the topmost run is the upper-frequency point, the
        # bottommost run is the lower-frequency point. The greedy
        # cluster-by-tracks step in `ridge.py` then assembles per-column
        # points into two coherent tracks per hue. Works for charts where
        # the two curves of one color never cross spatially, regardless
        # of whether their dashed fragments interleave in y-space.
        if plot_box is None:
            raise ValueError(
                "PER_COLUMN_RIDGE profile requires plot_box for per-column scanning"
            )
        upper_freq, lower_freq = profile.frequencies_lpmm[0], profile.frequencies_lpmm[1]
        for hue_name, mask in curve_masks.items():
            sm = parse_sagittal_meridional_name(hue_name)
            hue_fields = ridge_tracks_for_hue(
                mask, plot_box, sm, upper_freq=upper_freq, lower_freq=lower_freq
            )
            out.update(hue_fields)
    elif (
        profile.style_axis == "HUE_IS_CURVE"
        and profile.hue_meaning == "SKELETON_CONTINUOUS_PICK"
    ):
        # Each hue carries S or M. Per hue: dilate+skeletonize, split
        # CCs by mean-y (top = upper-freq, bottom = lower-freq), then
        # per CC walk columns picking the branch closest to the
        # previous y. Ports the legacy mtf-extract-skeleton.py approach
        # for robust extraction of dashed-line curves and coincident-
        # curve regions. See `pipeline/continuous_pick.py`.
        if plot_box is None:
            raise ValueError(
                "SKELETON_CONTINUOUS_PICK profile requires plot_box"
            )
        upper_freq, lower_freq = profile.frequencies_lpmm[0], profile.frequencies_lpmm[1]
        for hue_name, mask in curve_masks.items():
            sm = parse_sagittal_meridional_name(hue_name)
            upper_curve, lower_curve = extract_two_curves_per_hue(mask, plot_box)
            for freq, curve in (
                (upper_freq, upper_curve),
                (lower_freq, lower_curve),
            ):
                if not curve.points:
                    continue
                sk = np.zeros(mask.shape, dtype=np.uint8)
                for x, y in curve.points:
                    sk[int(round(y)), x] = 1
                out[curve_field(freq, sm)] = sk
    elif (
        profile.style_axis == "HUE_IS_CURVE"
        and profile.hue_meaning == "GEODESIC_DP"
    ):
        # Each hue carries S or M. Per hue: Viterbi shortest path through
        # the dilated mask finds the two curves; the smoothness prior
        # bridges dashed-line gaps and refuses to hop to a parallel
        # curve at near-touching regions. The B2-honest rasterizer
        # only emits skeleton pixels where the dilated mask had ink
        # near the predicted point — DP extrapolation through pure
        # white sections does not fabricate samples.
        # See `pipeline/dp_extract.py`.
        if plot_box is None:
            raise ValueError("GEODESIC_DP profile requires plot_box")
        upper_freq, lower_freq = profile.frequencies_lpmm[0], profile.frequencies_lpmm[1]
        for hue_name, mask in curve_masks.items():
            sm = parse_sagittal_meridional_name(hue_name)
            upper_curve, lower_curve = extract_two_curves_dp(mask, plot_box)
            upper_sk, lower_sk = curves_to_field_skeletons(
                upper_curve, lower_curve, mask, plot_box
            )
            for freq, sk in ((upper_freq, upper_sk), (lower_freq, lower_sk)):
                if sk is None or not sk.any():
                    continue
                out[curve_field(freq, sm)] = sk
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
                out[curve_field(freq, sm)] = sk
    elif (
        profile.style_axis == "SPLIT_BY_DASH"
        and profile.hue_meaning == "RIDGE_TRACKING"
    ):
        if len(curve_masks) != 1:
            raise ValueError(
                f"RIDGE_TRACKING expects one neutral hue; "
                f"profile {profile.name!r} declares {len(curve_masks)}"
            )
        if plot_box is None:
            raise ValueError("RIDGE_TRACKING requires plot_box")
        single_mask = next(iter(curve_masks.values()))
        upper_freq, lower_freq = (
            profile.frequencies_lpmm[0],
            profile.frequencies_lpmm[1],
        )
        out = ridge_tracks_to_fields(
            single_mask,
            plot_box,
            upper_freq=upper_freq,
            lower_freq=lower_freq,
            dashed_is_sagittal=profile.dashed_is_sagittal,
        )
    elif (
        profile.style_axis == "SPLIT_BY_DASH"
        and profile.hue_meaning == "CC_RANK_BY_MEAN_Y"
    ):
        # Single neutral mask, no informative hue. Skeletonize once,
        # rank connected components by mean y, then split at the largest
        # y-gap into upper- and lower-frequency clusters. Within each
        # cluster the longest CC is the solid line (S by default, M when
        # dashed_is_sagittal); the rest are dashed fragments.
        if len(curve_masks) != 1:
            raise ValueError(
                f"CC_RANK_BY_MEAN_Y expects one neutral hue; "
                f"profile {profile.name!r} declares {len(curve_masks)}"
            )
        upper_freq, lower_freq = profile.frequencies_lpmm[0], profile.frequencies_lpmm[1]
        solid_sm, dashed_sm = ("M", "S") if profile.dashed_is_sagittal else ("S", "M")
        single_mask = next(iter(curve_masks.values()))
        skeleton = close_and_skeletonize(single_mask)
        components = _component_masks_with_mean_y(skeleton)
        upper_cluster, lower_cluster = _split_components_at_largest_y_gap(components)
        for freq, cluster in (
            (upper_freq, upper_cluster),
            (lower_freq, lower_cluster),
        ):
            solid, dashed = _solid_dashed_from_components(cluster)
            for sm, sk in ((solid_sm, solid), (dashed_sm, dashed)):
                if sk is not None:
                    out[curve_field(freq, sm)] = sk
    else:
        raise NotImplementedError(
            f"profile dispatch not implemented: style_axis={profile.style_axis!r}, "
            f"hue_meaning={profile.hue_meaning!r}"
        )

    return out
