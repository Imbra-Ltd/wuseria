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
    """One sample point along the image-height axis (ADR-042).

    `samples` is a dict of synthetic field-name strings to MTF values,
    one entry per (frequency, S|M) pair the chart publishes. Field-name
    convention is ``f"freq{freq_lpmm}{S|M}"`` — e.g. ``"freq10S"``,
    ``"freq30M"``, ``"freq15S"``, ``"freq45M"``. Use `curve_field()`
    in `dispatch.py` to construct the name from `(freq, sm)`.

    A value is `None` when no usable curve data exists at that point
    (B2: never fabricate). A field-name MAY be absent from the dict
    entirely when the chart does not publish that (frequency, S|M)
    pair — Fujifilm primes publish at 15/20/40 lp/mm, so a Fuji
    reading carries `{"freq15S", "freq15M", "freq20S", "freq20M",
    "freq40S", "freq40M"}` and never references `freq10*` or
    `freq30*`.
    """

    position_mm: float
    samples: dict[str, float | None]

    def get(self, field: str) -> float | None:
        """Return the value for `field`, or `None` if absent."""
        return self.samples.get(field)


@dataclass(frozen=True)
class ExtractedChart:
    """Result of `extract_chart()` for one chart image."""

    source_path: str
    profile_name: str
    plot_box: PlotBox
    image_height_mm: float
    readings: tuple[SampledReading, ...]  # length 11
    # Per-field diagnostic counters surfaced for the digitization log.
    # `sister_fallback_count[field]` is the number of the 11 sample
    # fractions whose value was filled from the sister curve because
    # the raw ink mask of this field was empty there. 0 means every
    # sample came from direct extraction. Default empty dict means
    # diagnostics weren't tracked (e.g. legacy callers).
    sister_fallback_count: dict[str, int] = None  # type: ignore[assignment]
    # `center_anchor_count[field]` is the number of cells anchored to
    # MTF=1.0 by the B4 physics rule (S=M=1.0 at the optical axis) —
    # fires at frac=0.0 only, and only when both S and M of a
    # frequency pair are None after sister-fallback (#1267). 0 or 1
    # per field in practice; tracked per-field to make the rare
    # firing visible in the digitization log.
    center_anchor_count: dict[str, int] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        # Frozen dataclass + mutable defaults; resolve None to {} after init.
        if self.sister_fallback_count is None:
            object.__setattr__(self, "sister_fallback_count", {})
        if self.center_anchor_count is None:
            object.__setattr__(self, "center_anchor_count", {})
