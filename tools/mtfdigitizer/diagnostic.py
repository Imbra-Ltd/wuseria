"""Per-stage diagnostic bundle (ADR-050).

When `extract_chart` runs with a `DiagnosticSink`, every pipeline stage
records its output to the sink. A `FileDiagnosticSink` writes one PNG
per stage to disk, plus a `manifest.json` capturing scalar state. The
bundle is gitignored — it's an on-demand debugging artifact, not a
committed record.

The sink protocol lets the diagnostic concern live outside
`pipeline.py`: the pipeline calls `sink.record_*` if a sink is given,
or does nothing if not. Extraction values are identical with or
without the sink (ADR-050 contract).

CLI surface: `python -m mtfdigitizer.diagnose <slug>` — see
`diagnose.py`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import cv2
import numpy as np

from .pipeline.types import PlotBox, SampledReading


class DiagnosticSink(Protocol):
    """Receives per-stage artifacts during one `extract_chart` call.

    A sink is opt-in — `extract_chart` only calls these methods if a
    sink is supplied. Each method takes the artifact produced by one
    pipeline stage; the sink decides how to persist it. The methods
    are no-ops by default in concrete sinks for stages that don't
    apply (e.g. a chart without sister-fallback corrections).
    """

    def record_source(self, bgr: np.ndarray) -> None: ...
    def record_plotbox(self, bgr: np.ndarray, plot_box: PlotBox) -> None: ...
    def record_hue_mask(self, hue_name: str, mask: np.ndarray) -> None: ...
    def record_skeleton(
        self, field: str, skeleton: np.ndarray, bgr: np.ndarray
    ) -> None: ...
    def record_presence_mask(self, field: str, mask: np.ndarray) -> None: ...
    def record_sampling(
        self,
        readings: tuple[SampledReading, ...],
        bgr: np.ndarray,
        plot_box: PlotBox,
        image_height_mm: float,
    ) -> None: ...
    def record_fallback(
        self,
        before: dict[str, tuple[float | None, ...]],
        after: dict[str, tuple[float | None, ...]],
        fallback_count: dict[str, int],
    ) -> None: ...
    def record_symmetry(
        self,
        before: dict[str, tuple[float | None, ...]],
        after: dict[str, tuple[float | None, ...]],
    ) -> None: ...
    def record_emit(self, svg_text: str) -> None: ...
    def record_manifest(self, manifest: dict) -> None: ...


# Color palette for skeleton/mask overlays. Same per-frequency map as
# `svg.py` so a reader sees the same colors across all diagnostic
# artifacts.
_OVERLAY_COLOR_BGR: dict[int, tuple[int, int, int]] = {
    10: (60, 155, 200),   # warm gold (BGR for hex c89b3c)
    15: (74, 161, 212),
    20: (111, 168, 95),
    30: (210, 155, 107),  # cool blue (BGR for hex 6b9bd2)
    40: (181, 123, 93),
    45: (181, 123, 93),
}
_FADED_ALPHA = 0.35  # blend factor for the source PNG underlay


def _faded_bgr(bgr: np.ndarray) -> np.ndarray:
    """Faded copy of the source for use as an underlay."""
    white = np.full_like(bgr, 255)
    return cv2.addWeighted(bgr, _FADED_ALPHA, white, 1.0 - _FADED_ALPHA, 0)


def _color_for_field(field: str) -> tuple[int, int, int]:
    """BGR overlay color for a field name (`freq{N}{S|M}`)."""
    if not field.startswith("freq"):
        return (128, 128, 128)
    digits = "".join(c for c in field[4:] if c.isdigit())
    try:
        freq = int(digits)
    except ValueError:
        return (128, 128, 128)
    return _OVERLAY_COLOR_BGR.get(freq, (128, 128, 128))


def _draw_plotbox(bgr: np.ndarray, plot_box: PlotBox) -> np.ndarray:
    """Source PNG with the plot box outlined in red."""
    out = bgr.copy()
    cv2.rectangle(
        out,
        (plot_box.x_left, plot_box.y_top),
        (plot_box.x_right, plot_box.y_bottom),
        (0, 0, 255),
        2,
    )
    return out


def _mask_overlay(bgr: np.ndarray, mask: np.ndarray, color: tuple[int, int, int]) -> np.ndarray:
    """Faded source with the mask filled in `color`."""
    out = _faded_bgr(bgr)
    out[mask.astype(bool)] = color
    return out


def _sampling_overlay(
    bgr: np.ndarray,
    readings: tuple[SampledReading, ...],
    plot_box: PlotBox,
    image_height_mm: float,
) -> np.ndarray:
    """Source PNG with the 11 sample columns drawn as vertical lines.

    Each column is labeled with the position in mm. Color is neutral
    grey to avoid conflict with the per-field overlay colors used in
    other stages.
    """
    out = bgr.copy()
    for r in readings:
        if image_height_mm <= 0:
            continue
        frac = r.position_mm / image_height_mm
        x = int(round(plot_box.x_left + frac * plot_box.width))
        cv2.line(out, (x, plot_box.y_top), (x, plot_box.y_bottom), (180, 180, 180), 1)
        label = f"{r.position_mm:.1f}"
        cv2.putText(
            out, label, (x - 12, plot_box.y_top - 4),
            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (80, 80, 80), 1,
        )
    return out


def _samples_diff_overlay(
    before: dict[str, tuple[float | None, ...]],
    after: dict[str, tuple[float | None, ...]],
    bgr: np.ndarray,
    plot_box: PlotBox,
    image_height_mm: float,
) -> np.ndarray:
    """Visual diff between two sample dicts.

    Per field, draws a small marker at every sample position whose
    before-vs-after value changed. Marker color is the field color;
    a vertical tick connects before-y to after-y so direction is
    obvious. Unchanged samples are not drawn — an empty overlay means
    "no correction fired here," which is itself useful signal.
    """
    out = _faded_bgr(bgr)
    fields = sorted(set(before) | set(after))
    for field in fields:
        color = _color_for_field(field)
        before_vals = before.get(field, ())
        after_vals = after.get(field, ())
        n = max(len(before_vals), len(after_vals))
        for i in range(n):
            b = before_vals[i] if i < len(before_vals) else None
            a = after_vals[i] if i < len(after_vals) else None
            if b == a:
                continue
            if image_height_mm <= 0:
                continue
            frac = i / max(n - 1, 1)
            x = int(round(plot_box.x_left + frac * plot_box.width))
            for v, marker in ((b, "before"), (a, "after")):
                if v is None:
                    continue
                y = int(round(plot_box.y_bottom - v * plot_box.height))
                radius = 4 if marker == "after" else 2
                cv2.circle(out, (x, y), radius, color, -1 if marker == "after" else 1)
            if b is not None and a is not None:
                y0 = int(round(plot_box.y_bottom - b * plot_box.height))
                y1 = int(round(plot_box.y_bottom - a * plot_box.height))
                cv2.line(out, (x, y0), (x, y1), color, 1)
    return out


@dataclass
class FileDiagnosticSink:
    """Sink that writes each stage's artifact to disk under `out_dir`.

    Filenames are numbered by stage so file managers and PR diffs show
    them in pipeline order. Multi-aperture charts use one sink per
    aperture pass, each pointing to its own subdirectory.
    """

    out_dir: Path
    _hue_count: int = 0
    _skeleton_count: int = 0
    _presence_count: int = 0

    def __post_init__(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def record_source(self, bgr: np.ndarray) -> None:
        cv2.imwrite(str(self.out_dir / "01-source.png"), bgr)

    def record_plotbox(self, bgr: np.ndarray, plot_box: PlotBox) -> None:
        cv2.imwrite(str(self.out_dir / "02-plotbox.png"), _draw_plotbox(bgr, plot_box))

    def record_hue_mask(self, hue_name: str, mask: np.ndarray) -> None:
        # Visualise as faded source + the mask pixels in solid yellow,
        # so the mask's coverage is obvious against the underlying chart.
        # The bgr underlay is recorded later via `record_skeleton`; for
        # hue masks alone we render the mask on a white background.
        h, w = mask.shape[:2]
        canvas = np.full((h, w, 3), 255, dtype=np.uint8)
        canvas[mask.astype(bool)] = (0, 165, 255)  # solid orange
        safe = hue_name.replace("/", "-").replace(" ", "-")
        cv2.imwrite(str(self.out_dir / f"03-hue-{safe}.png"), canvas)
        self._hue_count += 1

    def record_skeleton(
        self, field: str, skeleton: np.ndarray, bgr: np.ndarray
    ) -> None:
        color = _color_for_field(field)
        out = _mask_overlay(bgr, skeleton, color)
        cv2.imwrite(str(self.out_dir / f"04-skeleton-{field}.png"), out)
        self._skeleton_count += 1

    def record_presence_mask(self, field: str, mask: np.ndarray) -> None:
        h, w = mask.shape[:2]
        canvas = np.full((h, w, 3), 255, dtype=np.uint8)
        canvas[mask.astype(bool)] = (180, 180, 180)
        cv2.imwrite(str(self.out_dir / f"05-presence-{field}.png"), canvas)
        self._presence_count += 1

    def record_sampling(
        self,
        readings: tuple[SampledReading, ...],
        bgr: np.ndarray,
        plot_box: PlotBox,
        image_height_mm: float,
    ) -> None:
        out = _sampling_overlay(bgr, readings, plot_box, image_height_mm)
        cv2.imwrite(str(self.out_dir / "06-sampling.png"), out)

    def record_fallback(
        self,
        before: dict[str, tuple[float | None, ...]],
        after: dict[str, tuple[float | None, ...]],
        fallback_count: dict[str, int],
    ) -> None:
        # Need plot_box + bgr for the overlay; cached by the sink at the
        # source-recording stage isn't ideal — instead, the diff overlay
        # is generated by the pipeline caller that knows both. The sink
        # itself records only the scalar count map; the visual diff is
        # written by `record_fallback_visual` from the caller.
        path = self.out_dir / "07-fallback-counts.json"
        path.write_text(json.dumps(fallback_count, indent=2), encoding="utf-8")

    def record_fallback_visual(
        self,
        before: dict[str, tuple[float | None, ...]],
        after: dict[str, tuple[float | None, ...]],
        bgr: np.ndarray,
        plot_box: PlotBox,
        image_height_mm: float,
    ) -> None:
        out = _samples_diff_overlay(before, after, bgr, plot_box, image_height_mm)
        cv2.imwrite(str(self.out_dir / "07-fallback.png"), out)

    def record_symmetry(
        self,
        before: dict[str, tuple[float | None, ...]],
        after: dict[str, tuple[float | None, ...]],
    ) -> None:
        # Same pattern as fallback — see `record_symmetry_visual`.
        # No scalar artifact for symmetry; it always touches at most
        # one sample (fraction 0.0) per S/M pair.
        pass

    def record_symmetry_visual(
        self,
        before: dict[str, tuple[float | None, ...]],
        after: dict[str, tuple[float | None, ...]],
        bgr: np.ndarray,
        plot_box: PlotBox,
        image_height_mm: float,
    ) -> None:
        out = _samples_diff_overlay(before, after, bgr, plot_box, image_height_mm)
        cv2.imwrite(str(self.out_dir / "08-center-symmetry.png"), out)

    def record_emit(self, svg_text: str) -> None:
        (self.out_dir / "09-emit.svg").write_text(svg_text, encoding="utf-8")

    def record_manifest(self, manifest: dict) -> None:
        (self.out_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, default=str), encoding="utf-8"
        )
