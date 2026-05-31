"""Render-match IoU scorer (#963, ADR-038 §4 confidence signal).

Round-trip check: take the extractor's own 11-point readings, redraw
them as 1px polylines in plot-box coordinates, dilate both sides by a
small symmetric radius, and compute Intersection-over-Union against the
extractor's own skeleton. High IoU means "what we extracted, when
redrawn, lands on the original curve" — sound calibration. Low IoU
flags shape/scale errors for review.

The de-risking probe summarized in epic #932 separated good extractions
(IoU 0.64–0.87) from mis-calibrated ones (0.03–0.49). The Samyang 300mm
"idealized-flat" case scores well for the wrong reason (no horizontal
structure to disagree on) — render-match cannot catch it. That blind
spot is left to the plausibility prior, a separate confidence
sub-task; this module is honest about what it can see.

Pipeline:

```
ExtractedChart.readings ─┐
                         ├─ rasterize_readings ──┐
                         │                       │
                         └─ dilate_for_iou ──────┤
                                                 ├─ iou ──► per-field IoU ─► aggregate
chart PNG ─ field_skeletons (shared dispatch) ───┤
                         └─ dilate_for_iou ──────┘
```

The skeleton side reuses the exact dispatch `extract_chart()` runs — so
the comparison really is round-trip, not "compare to a second
rendering." That's a deliberate choice over hue-mask comparison: the
skeleton is what the extractor sampled, so IoU against it is a direct
calibration signal, not a measure of mask-construction noise.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from ..loader import load_chart_bgr
from ..profiles.types import MtfProfile
from .dispatch import field_skeletons
from .plotbox import image_height_mm_to_x_pixel
from .sampling import SAMPLE_FRACTIONS
from .types import PlotBox, SampledReading


# Symmetric dilation radius applied to both the rasterized polyline and
# the extractor's skeleton before IoU. Matched to the sampling stage's
# `_BRACKET_HALF_WIDTH = 3` — IoU is meant to confirm "agrees within the
# same tolerance the sampler reads with," not pixel-perfect alignment
# that anti-aliasing and rounding would crater anyway.
DEFAULT_DILATION_RADIUS_PX: int = 3


# Field-name → which 11-point tuple to draw. Order matches the schema
# in `src/types/mtf.ts` and `SampledReading`'s field order.
CURVE_FIELDS: tuple[str, ...] = (
    "contrast10S",
    "contrast10M",
    "resolution30S",
    "resolution30M",
)


@dataclass(frozen=True)
class FieldIou:
    """IoU for one (chart, field) pair.

    `score` is `None` when neither side carries any pixels — there is no
    surface to compare and treating it as 0.0 would be a misleading
    failure signal. `score` is 0.0 when one side has pixels and the
    other does not (a genuine disagreement).
    """

    field: str
    score: float | None
    rasterized_px: int  # non-zero pixel count after dilation, redraw side
    skeleton_px: int  # non-zero pixel count after dilation, original side
    intersection_px: int
    union_px: int


@dataclass(frozen=True)
class RenderMatchScore:
    """Result of `score_chart()` for one chart image.

    `aggregate` is the mean IoU across fields that have a defined score
    (both sides non-empty). `None` when no field is comparable.
    """

    source_path: str
    profile_name: str
    field_scores: tuple[FieldIou, ...]
    aggregate: float | None


# --- rasterize -------------------------------------------------------


def rasterize_readings(
    readings: tuple[SampledReading, ...],
    plot_box: PlotBox,
    image_shape: tuple[int, int],
    image_height_mm: float,
) -> dict[str, np.ndarray]:
    """Redraw 11-point readings as 1px polylines, one mask per field.

    Output masks are the same height × width as the source image so they
    align with the extractor's skeleton without resizing. `None` gaps
    are honest: segments draw only between adjacent positions where both
    endpoints carry a value (B2 contract — never bridge a None).

    The y-axis is the plot box's: MTF=1 at `y_top`, MTF=0 at `y_bottom`.
    """
    if len(readings) != len(SAMPLE_FRACTIONS):
        raise ValueError(
            f"expected {len(SAMPLE_FRACTIONS)} readings, got {len(readings)}"
        )
    h, w = image_shape
    masks: dict[str, np.ndarray] = {
        field: np.zeros((h, w), dtype=np.uint8) for field in CURVE_FIELDS
    }

    # Precompute the x pixel of each sample once — same x grid for every field.
    x_pixels = tuple(
        int(round(image_height_mm_to_x_pixel(r.position_mm, plot_box, image_height_mm)))
        for r in readings
    )

    for field in CURVE_FIELDS:
        for i in range(len(readings) - 1):
            a = getattr(readings[i], field)
            b = getattr(readings[i + 1], field)
            if a is None or b is None:
                continue
            x0, x1 = x_pixels[i], x_pixels[i + 1]
            y0 = _mtf_to_y_pixel(a, plot_box)
            y1 = _mtf_to_y_pixel(b, plot_box)
            cv2.line(masks[field], (x0, y0), (x1, y1), color=1, thickness=1)

    return masks


def _mtf_to_y_pixel(mtf: float, plot_box: PlotBox) -> int:
    """Inverse of `plotbox.y_pixel_to_mtf` — MTF value to y pixel index."""
    mtf_clamped = max(0.0, min(1.0, mtf))
    return int(round(plot_box.y_bottom - mtf_clamped * plot_box.height))


# --- dilate + IoU ----------------------------------------------------


def dilate_for_iou(
    mask: np.ndarray, radius_px: int = DEFAULT_DILATION_RADIUS_PX
) -> np.ndarray:
    """Symmetric dilation by an elliptical kernel of `radius_px`.

    Both the rasterized polyline and the extractor's skeleton are
    dilated with the *same* radius before IoU. A radius of 0 is a no-op
    that just normalizes to uint8 binary.
    """
    if radius_px < 0:
        raise ValueError(f"radius_px must be non-negative, got {radius_px}")
    binary = (mask > 0).astype(np.uint8)
    if radius_px == 0:
        return binary
    size = 2 * radius_px + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
    return cv2.dilate(binary, kernel)


def iou(a: np.ndarray, b: np.ndarray) -> float | None:
    """Intersection-over-Union of two binary masks.

    Returns `None` when both masks are empty — there's nothing to
    compare. Returns 0.0 when one is empty and the other is not (a
    genuine disagreement). Otherwise returns `|A ∩ B| / |A ∪ B|`.
    """
    if a.shape != b.shape:
        raise ValueError(f"mask shape mismatch: {a.shape} vs {b.shape}")
    a_bool = a > 0
    b_bool = b > 0
    if not a_bool.any() and not b_bool.any():
        return None
    inter = int(np.logical_and(a_bool, b_bool).sum())
    union = int(np.logical_or(a_bool, b_bool).sum())
    return inter / union


# --- orchestrator ---------------------------------------------------


def score_chart(
    image_path: str | Path,
    profile: MtfProfile,
    plot_box: PlotBox,
    image_height_mm: float,
    readings: tuple[SampledReading, ...],
    dilation_radius_px: int = DEFAULT_DILATION_RADIUS_PX,
) -> RenderMatchScore:
    """Render-match IoU score for one chart.

    Takes pre-extracted `readings` rather than re-running the extractor —
    keeps this module pure and lets the caller (the scorer CLI) decide
    whether to extract fresh or reuse a cached `ExtractedChart`.
    """
    bgr = load_chart_bgr(image_path)
    h, w = bgr.shape[:2]
    rasterized = rasterize_readings(
        readings, plot_box, image_shape=(h, w), image_height_mm=image_height_mm
    )
    skeletons = field_skeletons(bgr, profile, plot_box)

    field_scores: list[FieldIou] = []
    defined_scores: list[float] = []
    for field in CURVE_FIELDS:
        raster_mask = dilate_for_iou(rasterized[field], dilation_radius_px)
        skel_raw = skeletons.get(field, np.zeros((h, w), dtype=np.uint8))
        skel_mask = dilate_for_iou(skel_raw, dilation_radius_px)
        score = iou(raster_mask, skel_mask)

        a_bool = raster_mask > 0
        b_bool = skel_mask > 0
        field_scores.append(
            FieldIou(
                field=field,
                score=score,
                rasterized_px=int(a_bool.sum()),
                skeleton_px=int(b_bool.sum()),
                intersection_px=int(np.logical_and(a_bool, b_bool).sum()),
                union_px=int(np.logical_or(a_bool, b_bool).sum()),
            )
        )
        if score is not None:
            defined_scores.append(score)

    aggregate = statistics.mean(defined_scores) if defined_scores else None
    return RenderMatchScore(
        source_path=str(image_path),
        profile_name=profile.name,
        field_scores=tuple(field_scores),
        aggregate=aggregate,
    )
