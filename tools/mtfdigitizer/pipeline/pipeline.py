"""Top-level pipeline orchestrator (#935, ADR-038 §2-3).

Reads chart → dispatches per profile dialect → samples each curve at the
11 fixed points. The "which curve becomes which committed field" logic
lives in `dispatch.field_skeletons()` so the render-match scorer reuses
the same answer the extractor computes (#963).
"""

from __future__ import annotations

from pathlib import Path

from ..loader import load_chart_bgr
from ..profiles.types import MtfProfile
from .dispatch import field_skeletons
from .sampling import (
    SAMPLE_FRACTIONS,
    sample_positions_mm,
    sample_skeleton_at_fraction,
)
from .types import ExtractedChart, PlotBox, SampledReading


SAMPLE_POINTS: tuple[float, ...] = SAMPLE_FRACTIONS  # re-export


def _sample_curve(
    skeleton, plot_box: PlotBox
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
    combinations not yet wired by `dispatch.field_skeletons()`.
    """
    bgr = load_chart_bgr(image_path)
    skeletons = field_skeletons(bgr, profile)

    samples_per_field: dict[str, tuple[float | None, ...]] = {
        field: _sample_curve(skel, plot_box) for field, skel in skeletons.items()
    }

    return ExtractedChart(
        source_path=str(image_path),
        profile_name=profile.name,
        plot_box=plot_box,
        image_height_mm=image_height_mm,
        readings=_readings_to_dict(samples_per_field, plot_box, image_height_mm),
    )
