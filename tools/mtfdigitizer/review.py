"""3-panel review-file generator (#973, ADR-038 §4).

For each chart, emits a static HTML file that lays out three panels:

- **Left**  — the original chart raster.
- **Right** — the regenerated SVG from #971 (linked, browser renders it
  natively — no rasterization, no new heavy dependency).
- **Bottom** — an overlay PNG: the original chart with the extractor's
  11-point polylines drawn over its plot box, registered against the
  same ``PlotBox`` the extractor used. Deterministic registration
  replaces the hand-tuned calibration of the deprecated
  ``tools/mtf-overlay.html``.

The composite is the entry point the ADR §"Workflow" calls out: "for a
flagged chart the maintainer opens its 3-panel review file, sees what is
wrong, and gives feedback in conversation." Charts that auto-triage HIGH
do not need a review file — they are explicitly **not** generated for
those, per ADR-038 §"Workflow: confidence log + chat summary" ("the
maintainer is never asked to eyeball a chart the tool already verified
two independent ways").

Standalone use::

    cd tools
    py -m mtfdigitizer.review              # emit review files for the 3 runnable charts
    py -m mtfdigitizer.review --check      # render only, don't write

Hooked into ``autotriage.py``: after the verdict prints, this module is
called once per LOW chart so the run leaves the review files in place.

Output paths::

    docs/optical-specs/<slug>/<chart-stem>-review.html
    docs/optical-specs/<slug>/<chart-stem>-overlay.png
"""

from __future__ import annotations

import argparse
import html
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .loader import load_chart_bgr
from .pipeline import ExtractedChart, SampledReading, extract_chart
from .pipeline.dispatch import parse_field_name
from .pipeline.plotbox import image_height_mm_to_x_pixel
from .pipeline.rendermatch import fields_in
from .pipeline.types import PlotBox
from .family_profile import profile_for_chart
from .referenceset import REFERENCE_CHARTS
from .referenceset.charts import PlotBoxCoords, ReferenceChart


REPO_ROOT = Path(__file__).resolve().parents[2]


# --- overlay drawing -------------------------------------------------
#
# The overlay reuses the SVG emitter's palette so a maintainer reads the
# same field as the same color in the right panel and the bottom panel.
# Colors are BGR (OpenCV convention).

# BGR convention (OpenCV). Mirrors `svg.py:_FREQUENCY_COLOR` (RGB hex
# → BGR tuple); kept here as concrete tuples so the overlay renders the
# same color the SVG legend swatches do, on the same maintainer screen.
_OVERLAY_FREQ_COLOR: dict[int, tuple[int, int, int]] = {
    10: (60, 155, 200),   # #c89b3c warm gold
    15: (74, 161, 212),   # #d4a14a
    20: (111, 168, 95),   # #5fa86f teal-green
    30: (210, 155, 107),  # #6b9bd2 cool blue
    40: (181, 123, 93),   # #5d7bb5
    45: (181, 123, 93),   # #5d7bb5
}
_OVERLAY_NEUTRAL = (136, 136, 136)  # neutral grey fallback
# Backwards-compat: kept for tests that referenced the 10/30 colors
# explicitly. The frequency-color map is the new source of truth.
_OVERLAY_COLOR_10 = _OVERLAY_FREQ_COLOR[10]
_OVERLAY_COLOR_30 = _OVERLAY_FREQ_COLOR[30]
_OVERLAY_THICKNESS = 3
_OVERLAY_DASH_LENGTH_PX = 6  # length of each dash segment for M fields
_OVERLAY_GAP_LENGTH_PX = 4   # gap between dashes for M fields


def _field_color(field: str) -> tuple[int, int, int]:
    freq, _sm = parse_field_name(field)
    return _OVERLAY_FREQ_COLOR.get(freq, _OVERLAY_NEUTRAL)


def _is_meridional(field: str) -> bool:
    return field.endswith("M")


def _mtf_to_y_pixel(mtf: float, plot_box: PlotBox) -> int:
    """Inverse of ``plotbox.y_pixel_to_mtf``. Clamps before mapping so
    out-of-band readings still land on the plot edge instead of falling
    off the canvas."""
    clamped = max(0.0, min(1.0, mtf))
    return int(round(plot_box.y_bottom - clamped * plot_box.height))


def _dashed_line(
    image: np.ndarray,
    p0: tuple[int, int],
    p1: tuple[int, int],
    color: tuple[int, int, int],
    thickness: int,
) -> None:
    """Draw a dashed segment between two pixel points.

    OpenCV has no built-in dash style; we walk the segment in fixed
    dash/gap lengths so the dash density is independent of slope. Pure
    side-effect on ``image``.
    """
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    length = float(np.hypot(dx, dy))
    if length == 0.0:
        return
    ux, uy = dx / length, dy / length
    step = _OVERLAY_DASH_LENGTH_PX + _OVERLAY_GAP_LENGTH_PX
    distance = 0.0
    while distance < length:
        seg_end = min(distance + _OVERLAY_DASH_LENGTH_PX, length)
        sx = int(round(x0 + ux * distance))
        sy = int(round(y0 + uy * distance))
        ex = int(round(x0 + ux * seg_end))
        ey = int(round(y0 + uy * seg_end))
        cv2.line(image, (sx, sy), (ex, ey), color, thickness)
        distance += step


def render_overlay(
    image_bgr: np.ndarray,
    readings: tuple[SampledReading, ...],
    plot_box: PlotBox,
    image_height_mm: float,
) -> np.ndarray:
    """Draw the extractor's polylines over the original chart.

    The original is copied — the input is not mutated. Each segment
    draws only when both endpoints carry a value (B2 contract, matches
    ``rasterize_readings`` in ``pipeline/rendermatch.py``). S fields
    use solid strokes; M fields are dashed to match the SVG emitter.
    """
    out = image_bgr.copy()
    x_pixels = tuple(
        int(round(image_height_mm_to_x_pixel(r.position_mm, plot_box, image_height_mm)))
        for r in readings
    )
    for field in fields_in(readings):
        color = _field_color(field)
        dashed = _is_meridional(field)
        for i in range(len(readings) - 1):
            a = readings[i].samples.get(field)
            b = readings[i + 1].samples.get(field)
            if a is None or b is None:
                continue
            x0, x1 = x_pixels[i], x_pixels[i + 1]
            y0 = _mtf_to_y_pixel(a, plot_box)
            y1 = _mtf_to_y_pixel(b, plot_box)
            if dashed:
                _dashed_line(out, (x0, y0), (x1, y1), color, _OVERLAY_THICKNESS)
            else:
                cv2.line(out, (x0, y0), (x1, y1), color, _OVERLAY_THICKNESS)
    return out


# --- HTML composition ------------------------------------------------


@dataclass(frozen=True)
class ReviewPaths:
    """The three artifacts a review file references.

    ``original_filename`` and ``svg_filename`` are relative to the
    review file's directory — they live next to it in
    ``docs/optical-specs/<slug>/``. Same for ``overlay_filename``.
    """

    original_filename: str
    svg_filename: str
    overlay_filename: str


def render_review_html(*, title: str, paths: ReviewPaths) -> str:
    """Compose the static 3-panel HTML.

    No JS, no external assets, no remote stylesheets — the review file
    works opened off-disk via ``file://``. The grid is two columns on
    the top row (original + SVG) and one full-width row at the bottom
    (overlay), per ADR-038 §4.
    """
    safe_title = html.escape(title)
    return _HTML_TEMPLATE.format(
        title=safe_title,
        original=html.escape(paths.original_filename, quote=True),
        svg=html.escape(paths.svg_filename, quote=True),
        overlay=html.escape(paths.overlay_filename, quote=True),
    )


_HTML_TEMPLATE = """\
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>{title} - MTF review</title>
    <style>
      body {{
        font-family: ui-monospace, "Cascadia Code", monospace;
        background: #1a1a2e;
        color: #e0e0e0;
        margin: 0;
        padding: 1.5rem;
      }}
      h1 {{
        font-size: 1.1rem;
        margin: 0 0 1rem 0;
        color: #d4a853;
        font-weight: normal;
      }}
      .grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: auto auto;
        gap: 1rem;
        max-width: 1400px;
      }}
      .panel {{
        background: #fff;
        border: 1px solid #333;
        padding: 0.75rem;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
      }}
      .panel.bottom {{ grid-column: 1 / span 2; }}
      .panel h2 {{
        font-size: 0.75rem;
        margin: 0;
        color: #666;
        font-weight: normal;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }}
      .panel img,
      .panel object {{
        display: block;
        width: 100%;
        height: auto;
        max-height: 60vh;
        object-fit: contain;
      }}
    </style>
  </head>
  <body>
    <h1>{title}</h1>
    <div class="grid">
      <div class="panel">
        <h2>Original</h2>
        <img src="{original}" alt="Original MTF chart" />
      </div>
      <div class="panel">
        <h2>Regenerated SVG</h2>
        <img src="{svg}" alt="Regenerated MTF SVG from extracted readings" />
      </div>
      <div class="panel bottom">
        <h2>Overlay (extractor curves over original)</h2>
        <img src="{overlay}" alt="Extractor polylines overlaid on the original chart" />
      </div>
    </div>
  </body>
</html>
"""


# --- top-level writer ------------------------------------------------


@dataclass(frozen=True)
class ReviewOutputs:
    """Paths to the two files this module writes per chart."""

    html_path: Path
    overlay_path: Path


def write_review(
    extracted: ExtractedChart,
    image_path: Path,
    *,
    plot_box: PlotBox,
    image_height_mm: float,
    svg_path: Path,
    out_dir: Path | None = None,
) -> ReviewOutputs:
    """Write the HTML composite and the overlay PNG for one chart.

    ``image_path`` is the source raster, ``svg_path`` is the SVG emitter's
    output (#971), both expected to live in ``docs/optical-specs/<slug>/``.
    Output paths default to the same folder; the HTML references the
    three artifacts by their basenames, so the directory must contain
    all four files for the HTML to render correctly off-disk.
    """
    target_dir = out_dir if out_dir is not None else image_path.parent
    overlay_path = target_dir / f"{image_path.stem}-overlay.png"
    html_path = target_dir / f"{image_path.stem}-review.html"

    original_bgr = load_chart_bgr(image_path)
    overlay = render_overlay(
        original_bgr, extracted.readings, plot_box, image_height_mm
    )
    cv2.imwrite(str(overlay_path), overlay)

    paths = ReviewPaths(
        original_filename=image_path.name,
        svg_filename=svg_path.name,
        overlay_filename=overlay_path.name,
    )
    html_content = render_review_html(
        title=image_path.stem, paths=paths
    )
    html_path.write_text(html_content, encoding="utf-8")
    return ReviewOutputs(html_path=html_path, overlay_path=overlay_path)


# --- CLI -------------------------------------------------------------


def _to_plotbox(coords: PlotBoxCoords) -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
    )


def _svg_path_for(image_path: Path) -> Path:
    """Convention from #971: the SVG sits next to the PNG with the same stem."""
    return image_path.with_suffix(".svg")


def _emit_chart(chart: ReferenceChart, *, check_only: bool) -> ReviewOutputs | None:
    """Render one reference chart's review file. Returns ``None`` in
    ``--check`` mode after rendering everything in memory."""
    assert chart.plot_box is not None
    profile = profile_for_chart(chart)
    image_path = REPO_ROOT / chart.chart_path
    plot_box = _to_plotbox(chart.plot_box)
    extracted = extract_chart(
        image_path, profile, plot_box, image_height_mm=chart.image_height_mm
    )

    if check_only:
        # Exercise the overlay + HTML paths without touching disk so
        # --check still catches regressions in either code path.
        bgr = load_chart_bgr(image_path)
        _ = render_overlay(bgr, extracted.readings, plot_box, chart.image_height_mm)
        _ = render_review_html(
            title=image_path.stem,
            paths=ReviewPaths(
                original_filename=image_path.name,
                svg_filename=_svg_path_for(image_path).name,
                overlay_filename=f"{image_path.stem}-overlay.png",
            ),
        )
        return None

    return write_review(
        extracted,
        image_path,
        plot_box=plot_box,
        image_height_mm=chart.image_height_mm,
        svg_path=_svg_path_for(image_path),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="Render to memory only, don't write files. Used in CI/tests.",
    )
    args = parser.parse_args()

    runnable = [c for c in REFERENCE_CHARTS if c.plot_box and c.ground_truth]
    print(f"Emitting review file for {len(runnable)} of {len(REFERENCE_CHARTS)} reference charts.")
    if args.check:
        print("(--check: rendering only, no files written)")
    print()

    for chart in runnable:
        outputs = _emit_chart(chart, check_only=args.check)
        if outputs is None:
            print(f"  {chart.slug:<40}  rendered (--check)")
            continue
        rel_html = outputs.html_path.relative_to(REPO_ROOT)
        rel_overlay = outputs.overlay_path.relative_to(REPO_ROOT)
        print(f"  {chart.slug:<40}  wrote  {rel_html}")
        print(f"  {'':<40}  wrote  {rel_overlay}")


if __name__ == "__main__":
    main()
