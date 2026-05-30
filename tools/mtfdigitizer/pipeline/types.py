"""Pipeline data types (#935)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlotBox:
    """The plot area in pixel coordinates.

    Image coordinates are (0, 0) at top-left; y increases downward.
    The y-axis of the chart (MTF value) increases upward, so:

        mtf_value = (y_bottom - y_pixel) / (y_bottom - y_top)

    All four fields are inclusive pixel indices.
    """

    x_left: int
    x_right: int
    y_top: int
    y_bottom: int

    @property
    def width(self) -> int:
        return self.x_right - self.x_left

    @property
    def height(self) -> int:
        return self.y_bottom - self.y_top


@dataclass(frozen=True)
class SampledReading:
    """One sample point along the image-height axis.

    Each MTF curve reading is `None` when no usable curve data exists
    at that point (B2: never fabricate). The committed serializer
    (a later task) decides whether to interpolate or hold the None.
    """

    position_mm: float
    contrast10S: float | None
    contrast10M: float | None
    resolution30S: float | None
    resolution30M: float | None


@dataclass(frozen=True)
class ExtractedChart:
    """Result of `extract_chart()` for one chart image."""

    source_path: str
    profile_name: str
    plot_box: PlotBox
    image_height_mm: float
    readings: tuple[SampledReading, ...]  # length 11
