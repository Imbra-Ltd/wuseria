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

    `y_top_insets` is a per-hue-name additional inset applied at the
    mask-clip step only (#1271, ADR-067). Each entry trims `n` rows from
    the top of the named hue's mask before skeletonization, leaving the
    plot box's actual `y_top` untouched for every other hue. Used when
    one curve's antialiasing halo lands inside a sister curve's HSV
    band — a global `y_top` shift would clip the contaminator's own
    curve, but a per-hue inset shields the contaminated mask without
    affecting the contaminator's. Sampling, scoring, and rendering all
    use the unmodified `y_top`/`y_bottom` for MTF conversion. None or
    empty means no inset.
    """

    x_left: int
    x_right: int
    y_top: int
    y_bottom: int
    # Per-hue additional y_top inset, as ((hue_name, n), ...) so the
    # field stays hashable and the dataclass stays frozen. Empty tuple
    # means no inset applied. See class docstring.
    y_top_insets: tuple[tuple[str, int], ...] = ()

    @property
    def width(self) -> int:
        return self.x_right - self.x_left

    @property
    def height(self) -> int:
        return self.y_bottom - self.y_top

    def hue_y_top(self, hue_name: str) -> int:
        """Effective `y_top` for the named hue's mask clipping.

        Equals `y_top + n` when `(hue_name, n)` appears in
        `y_top_insets`; falls back to `y_top` otherwise. Use at the
        per-hue mask clip step; MUST NOT be used for sampling or MTF
        conversion (those depend on the chart's unmodified plot
        rectangle).
        """
        for name, n in self.y_top_insets:
            if name == hue_name:
                return self.y_top + n
        return self.y_top


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
    # `coincident_anchor_count[field]` is the number of sister-filled
    # cells overridden by the matching lower-frequency curve's value
    # when the lower curve is pinned at MTF >= 0.95 (#1269). Fires
    # mid-field on chart families where high-freq and low-freq strokes
    # are drawn coincident at chart top.
    coincident_anchor_count: dict[str, int] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        # Frozen dataclass + mutable defaults; resolve None to {} after init.
        if self.sister_fallback_count is None:
            object.__setattr__(self, "sister_fallback_count", {})
        if self.center_anchor_count is None:
            object.__setattr__(self, "center_anchor_count", {})
        if self.coincident_anchor_count is None:
            object.__setattr__(self, "coincident_anchor_count", {})
