"""Scaffold maintainer eye-read helpers for a Tier 1 anchor.

For a given anchor slug, generates three artifacts in the lens's
`docs/optical-specs/<slug>/` folder:

1. **`<view-stem>-readhelper.png`** — 3x upscale of the view's base
   image with green vertical lines at the 11 sample positions and
   each line labelled with its image-height mm value. One file per
   view (per frequency for `fujifilm-permfreq`, per aperture for
   `ttartisan-4color-dual-aperture`).

2. **`eye-read-template.md`** — fill-in table the maintainer
   completes by eye-reading the source PNG against the printed
   gridlines. One table per view, columns per (frequency, S|M)
   pair.

3. **`extractor-prediction.md`** — extractor's reading of each
   sample position. NOT ground truth — a starting point for
   maintainer validation. The maintainer scans against the source
   PNG, accepts cells that look right, overwrites cells that look
   wrong, then copies the validated values into the `_<LENS>_GT`
   tuple in `referenceset/charts.py`.

The agent does NOT eye-read these values — that is the maintainer's
job (`feedback_agent_no_gt_eye_read`). This script only scaffolds
the artifacts the maintainer reads.

Supported style families:

- `fujifilm-permfreq` — one PNG per spatial frequency (e.g. 15lp,
  20lp, 40lp); one helper PNG per frequency.
- `ttartisan-4color-dual-aperture` — one PNG packing both apertures
  by color encoding; one helper PNG per aperture (uses the existing
  per-aperture overlay PNG from `extract.py` as the base when
  available so the target aperture's curves are pre-marked).

Usage::

    cd tools

    # Preview: list the artifacts that would be written.
    py -m mtfdigitizer.scripts.scaffold_anchor_helpers <slug>

    # Write: materialize the artifacts on disk.
    py -m mtfdigitizer.scripts.scaffold_anchor_helpers <slug> --write

    # Check: exit non-zero if any artifact would change on disk.
    py -m mtfdigitizer.scripts.scaffold_anchor_helpers <slug> --check
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from mtfdigitizer.pipeline import extract_chart
from mtfdigitizer.pipeline.sampling import SAMPLE_FRACTIONS
from mtfdigitizer.pipeline.types import PlotBox
from mtfdigitizer.family_profile import profile_for_chart
from mtfdigitizer.referenceset.charts import REFERENCE_CHARTS, ReferenceChart


REPO_ROOT = Path(__file__).resolve().parents[3]

UPSCALE_FACTOR = 3
GREEN_LINE_RGB = (0, 180, 0)
GREEN_LINE_WIDTH_PX = 2
LABEL_FILL_RGB = (0, 120, 0)
# Orange dashed half-step gridlines (Fuji style — fills the 0.1 gap
# between Fuji's printed 0.2-step MTF lines so eye-read precision
# improves from 0.2 to 0.1 ticks).
HALF_STEP_LINE_RGB = (240, 130, 0)
HALF_STEP_LINE_WIDTH_PX = 1
HALF_STEP_DASH_LEN_PX = 6


@dataclass(frozen=True)
class HelperView:
    """One view of an anchor that needs its own readhelper PNG and
    eye-read column-group. For Fuji this is a spatial frequency; for
    TTartisan this is an aperture.
    """

    # Short label used in markdown headings (e.g. "15 lp/mm", "f/1.2 (max)").
    title: str
    # The base PNG to overlay sample-position lines on. For
    # multi-aperture, prefer the existing per-aperture overlay so the
    # target aperture's traced curves are visible.
    base_image_path: Path
    # Output filename for the readhelper (lens_dir-relative).
    readhelper_filename: str
    # Field names to extract for this view (e.g. ("freq15S", "freq15M")
    # for Fuji 15lp; ("freq10S", "freq10M", "freq30S", "freq30M") for
    # one TTartisan aperture).
    field_columns: tuple[str, ...]
    # Column headers for the markdown tables (e.g. ("15S", "15M")).
    column_headers: tuple[str, ...]
    # Plot box for this view (drives where the green sample lines land).
    plot_box: PlotBox
    # Path to the chart image the EXTRACTOR runs on for this view.
    # For Fuji permfreq, this is the per-frequency PNG (different per
    # view). For TTartisan, this is the primary chart shared across
    # views (both apertures live on one PNG).
    extractor_chart_path: Path
    # Aperture label to filter the extractor pass on; None for
    # single-aperture views.
    aperture_label: str | None


def _resolve_helper_views(chart: ReferenceChart) -> list[HelperView]:
    """Translate one anchor into the list of views the helpers cover."""
    if chart.style_family == "fujifilm-permfreq":
        return _fuji_permfreq_views(chart)
    if chart.style_family == "ttartisan-4color-dual-aperture":
        return _ttartisan_dual_aperture_views(chart)
    raise ValueError(
        f"{chart.slug}: style_family {chart.style_family!r} not "
        f"supported by scaffold_anchor_helpers. Add a new "
        f"`_resolve_helper_views` branch."
    )


def _fuji_permfreq_views(chart: ReferenceChart) -> list[HelperView]:
    """Fujifilm permfreq: one PNG per spatial frequency."""
    assert chart.plot_box is not None
    views: list[HelperView] = []
    for view in chart.views:
        # The frequency is encoded in the filename suffix, e.g.
        # `*-15lp.png`. Parse it back out.
        stem = Path(view.chart_path).stem
        freq_lpmm = _parse_frequency_from_stem(stem)
        source_path = REPO_ROOT / view.chart_path
        plot_box = view.plot_box if view.plot_box is not None else chart.plot_box
        views.append(
            HelperView(
                title=f"{freq_lpmm} lp/mm",
                base_image_path=source_path,
                readhelper_filename=f"{stem}-readhelper.png",
                field_columns=(f"freq{freq_lpmm}S", f"freq{freq_lpmm}M"),
                column_headers=(f"{freq_lpmm}S", f"{freq_lpmm}M"),
                plot_box=_to_plotbox(plot_box),
                extractor_chart_path=source_path,
                aperture_label=None,
            )
        )
    return views


def _ttartisan_dual_aperture_views(chart: ReferenceChart) -> list[HelperView]:
    """TTartisan dual-aperture: one PNG per aperture; the base image
    is the existing per-aperture overlay PNG when it exists, so the
    target aperture's traced curves are visible.
    """
    assert chart.plot_box is not None
    profile = profile_for_chart(chart)
    assert profile.apertures_per_chart is not None, (
        f"{chart.slug}: profile has no apertures_per_chart but style "
        f"family is ttartisan-4color-dual-aperture"
    )
    source_path = REPO_ROOT / chart.chart_path
    source_stem = source_path.stem
    lens_dir = source_path.parent
    freqs = chart.frequencies_lpmm

    views: list[HelperView] = []
    for ap_label, f_number in zip(profile.apertures_per_chart, chart.apertures):
        # Per-aperture overlay PNG from extract.py:_write_inspection_artifacts.
        # Filename convention: `<source_stem>-<ap_label>-overlay.png`.
        overlay_path = lens_dir / f"{source_stem}-{ap_label}-overlay.png"
        base = overlay_path if overlay_path.exists() else source_path
        views.append(
            HelperView(
                title=f"{f_number} ({ap_label})",
                base_image_path=base,
                readhelper_filename=f"{source_stem}-{ap_label}-readhelper.png",
                field_columns=tuple(
                    f"freq{f}{sm}" for f in freqs for sm in ("S", "M")
                ),
                column_headers=tuple(
                    f"{f}{sm}" for f in freqs for sm in ("S", "M")
                ),
                plot_box=_to_plotbox(chart.plot_box),
                # Both apertures live on one PNG — extractor runs on
                # the primary chart for every view, filtered by aperture.
                extractor_chart_path=source_path,
                aperture_label=ap_label,
            )
        )
    return views


def _parse_frequency_from_stem(stem: str) -> int:
    """Extract the lp/mm frequency from a Fuji permfreq filename stem.

    The Fuji convention is `<lens-slug>-<freq>lp` (e.g.
    `fujifilm-gf-23mm-f4-r-lm-wr-15lp`). Returns the integer
    frequency or raises if the suffix is missing.
    """
    parts = stem.split("-")
    last = parts[-1]
    if not last.endswith("lp"):
        raise ValueError(
            f"stem {stem!r}: cannot parse frequency — expected `-<N>lp` suffix"
        )
    return int(last[:-2])


def _to_plotbox(coords) -> PlotBox:
    """Lift PlotBoxCoords from the reference set to the pipeline type."""
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
    )


# --- Readhelper PNG renderer ---------------------------------------------


def _render_readhelper(
    view: HelperView,
    image_height_mm: float,
    extras: StyleFamilyExtras,
) -> Image.Image:
    """3x upscale of the base image with sample-position lines + labels.

    Per the design carried over from #1058:

    - **Green vertical sample lines** span the plot area at each of the
      11 sample fractions; **mm labels sit at the TOP** of each line
      (just above y_top) so they don't collide with the chart's own
      printed x-tick labels at the bottom of the plot.
    - **Orange dashed half-step horizontal gridlines** (Fuji only —
      controlled by `extras.readhelper_half_step_otf`) fill in the
      0.1-step ticks Fuji's source chart doesn't print, letting the
      maintainer eye-read at ~0.05 precision instead of ~0.10.
    """
    base = Image.open(view.base_image_path).convert("RGB")
    up = base.resize(
        (base.width * UPSCALE_FACTOR, base.height * UPSCALE_FACTOR),
        resample=Image.NEAREST,
    )
    draw = ImageDraw.Draw(up)

    # Scale plot-box coordinates to the upscaled image.
    plot_left_up = view.plot_box.x_left * UPSCALE_FACTOR
    plot_right_up = view.plot_box.x_right * UPSCALE_FACTOR
    plot_top_up = view.plot_box.y_top * UPSCALE_FACTOR
    plot_bottom_up = view.plot_box.y_bottom * UPSCALE_FACTOR
    plot_width_up = plot_right_up - plot_left_up
    plot_height_up = plot_bottom_up - plot_top_up

    # Scale font to the upscaled plot WIDTH so labels stay legible on
    # small charts (Fuji 282x212) and don't overwhelm big charts
    # (TTartisan 800x600). Cap to avoid runaway sizes on giant Sigma
    # 2991x1964 charts.
    target_label_h = max(8, min(plot_width_up // 60, 40))
    font = _load_label_font(target_label_h)

    # Half-step horizontal gridlines (Fuji-only today). Drawn FIRST so
    # the green sample lines render on top of them.
    for otf in extras.readhelper_half_step_otf:
        y = int(plot_bottom_up - otf * plot_height_up)
        _draw_dashed_hline(
            draw,
            x_left=plot_left_up,
            x_right=plot_right_up,
            y=y,
            color=HALF_STEP_LINE_RGB,
            width=HALF_STEP_LINE_WIDTH_PX,
            dash_len=HALF_STEP_DASH_LEN_PX * UPSCALE_FACTOR,
        )
        # Label the OTF value just right of the plot.
        label = f"{otf:.1f}"
        bbox = draw.textbbox((0, 0), label, font=font)
        draw.text(
            (plot_right_up + 4 * UPSCALE_FACTOR, y - (bbox[3] - bbox[1]) // 2),
            label,
            fill=HALF_STEP_LINE_RGB,
            font=font,
        )

    # Green vertical sample lines + mm labels at the TOP of each line.
    for frac in SAMPLE_FRACTIONS:
        x_up = int(plot_left_up + frac * plot_width_up)
        draw.line(
            [(x_up, plot_top_up), (x_up, plot_bottom_up)],
            fill=GREEN_LINE_RGB,
            width=GREEN_LINE_WIDTH_PX,
        )
        mm = frac * image_height_mm
        label = f"{mm:.1f}"
        bbox = draw.textbbox((0, 0), label, font=font)
        label_w = bbox[2] - bbox[0]
        label_h = bbox[3] - bbox[1]
        # Anchor label ABOVE the plot's top edge so it doesn't collide
        # with the chart's own printed x-tick labels at the bottom.
        label_y = plot_top_up - label_h - 2 * UPSCALE_FACTOR
        # If the label would clip the top of the canvas, drop it just
        # below the plot's top edge (rare: most charts have margin above).
        if label_y < 0:
            label_y = plot_top_up + 2 * UPSCALE_FACTOR
        draw.text(
            (x_up - label_w // 2, label_y),
            label,
            fill=LABEL_FILL_RGB,
            font=font,
        )
    return up


def _draw_dashed_hline(
    draw: ImageDraw.ImageDraw,
    *,
    x_left: int,
    x_right: int,
    y: int,
    color: tuple[int, int, int],
    width: int,
    dash_len: int,
) -> None:
    """Draw a horizontal dashed line: `dash_len` on, `dash_len` off."""
    x = x_left
    while x < x_right:
        x_end = min(x + dash_len, x_right)
        draw.line([(x, y), (x_end, y)], fill=color, width=width)
        x = x_end + dash_len


def _load_label_font(target_pixel_height: int) -> ImageFont.ImageFont:
    """Best-effort load of a legible truetype font at the target size;
    fall back to PIL's default if no system font is reachable.
    """
    for name in ("DejaVuSans.ttf", "arial.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size=target_pixel_height)
        except OSError:
            continue
    return ImageFont.load_default()


# --- Style-family extras --------------------------------------------------
#
# Per-style-family wording that the agent does not invent: warnings,
# axis legends, and the literal Python snippet showing the GT tuple
# the maintainer copies into. Originally curated by hand in
# eye-read-template.md for each Fuji anchor (#1058); folded into this
# script when the helpers were codified so all anchors emit the same
# structure but each style family keeps its specific guidance.


@dataclass(frozen=True)
class StyleFamilyExtras:
    """Per-style-family wording blocks for the eye-read template."""

    # Inline paragraph warning the maintainer about anything specific
    # to this chart family that the green sample lines or the printed
    # ticks might mislead them about. Rendered after the generic
    # "sample positions are spaced by image-height fraction" paragraph.
    sample_line_warning: str | None
    # Bulleted list of MTF axis landmarks (e.g. "Top of plot area →
    # MTF 1.0"). Rendered as a sub-list under the generic
    # "read each cell against the printed gridlines" paragraph.
    mtf_axis_legend: tuple[str, ...]
    # Literal Python snippet showing the GT-tuple skeleton with the
    # exact `_<LENS>_GT` variable name and field names this family
    # uses. Maintainer pastes filled values into this shape.
    gt_snippet: str
    # Half-step OTF fractions (0..1) at which to draw an orange dashed
    # horizontal gridline on the readhelper PNG. Use for families
    # whose source chart only prints every 0.2 OTF (Fuji) so the
    # maintainer can eye-read at 0.1 precision. Empty tuple = no
    # extra gridlines (families like TTartisan that already print
    # every 0.1 OTF).
    readhelper_half_step_otf: tuple[float, ...] = ()


def _extras_for(chart: ReferenceChart) -> StyleFamilyExtras:
    if chart.style_family == "fujifilm-permfreq":
        return _fuji_permfreq_extras(chart)
    if chart.style_family == "ttartisan-4color-dual-aperture":
        return _ttartisan_dual_aperture_extras(chart)
    return StyleFamilyExtras(
        sample_line_warning=None, mtf_axis_legend=(), gt_snippet="",
    )


def _fuji_permfreq_extras(chart: ReferenceChart) -> StyleFamilyExtras:
    """Curated wording carried over from the original hand-authored
    Fuji eye-read templates (#1058). Tick-label warning + plot-area
    MTF axis legend + per-cohort GT snippet skeleton.
    """
    # Tick labels printed on the source PNG, derived from the GF (5/10/15/20/25)
    # vs XF (0/5/10/14.2) chart conventions. The right-edge note is
    # cohort-specific (GF goes past "25 mm" by ~17 px; XF lines up at "14.2").
    if "gf-" in chart.slug:
        tick_labels = "5/10/15/20/25"
        right_edge_note = (
            f"the right gridline edge corresponds to ~{chart.image_height_mm} mm "
            f"— past Fujifilm's '25 mm' tick label by ~17 px"
        )
    else:
        tick_labels = "0, 5, 10, 14.2"
        right_edge_note = (
            f"the right gridline edge corresponds to {chart.image_height_mm} mm, "
            f"matching the APS-C 23.5x15.6 mm sensor half-diagonal"
        )

    sample_line_warning = (
        f"**Important:** the green vertical lines do NOT match the printed "
        f"black tick labels ({tick_labels}). The chart's plot area spans "
        f"0..{chart.image_height_mm} mm ({right_edge_note}); each green "
        f"vertical line in the helper PNG is labelled with its mm value."
    )

    mtf_axis_legend = (
        "Top of plot area → MTF 1.0",
        "Each printed gridline below it → 0.8, 0.6, 0.4, 0.2",
        "Bottom gridline → MTF 0.0",
    )

    # GT-snippet variable name: chart-slug-derived would be wrong; the
    # GT variable in charts.py uses the lens shorthand (e.g.
    # `_FUJI_GF_23_GT`). Derive it from the slug by uppercasing the
    # brand + key cohort tokens.
    gt_var, aperture_label = _fuji_gt_var(chart)
    field_lines = "\n        ".join(
        f'"freq{f}{sm}": (...11 values from the {f}{sm} column...),'
        for f in chart.frequencies_lpmm for sm in ("S", "M")
    )
    gt_snippet = (
        f"```python\n"
        f"{gt_var}: GroundTruthCurves = {{\n"
        f'    "{aperture_label}": {{\n'
        f"        {field_lines}\n"
        f"    }},\n"
        f"}}\n"
        f"```"
    )

    return StyleFamilyExtras(
        sample_line_warning=sample_line_warning,
        mtf_axis_legend=mtf_axis_legend,
        gt_snippet=gt_snippet,
        # Fuji prints every 0.2 OTF; add half-step lines at 0.1/0.3/0.5/0.7/0.9
        # so the readhelper supports 0.1-precision eye-reads.
        readhelper_half_step_otf=(0.1, 0.3, 0.5, 0.7, 0.9),
    )


def _fuji_gt_var(chart: ReferenceChart) -> tuple[str, str]:
    """Return the `_FUJI_<COHORT>_<FL>_GT` variable name and the single
    aperture label (e.g. `"f/4"`, `"f/1.4"`) for a Fuji anchor.
    """
    # slug shape: fujifilm-(gf|xf)-<focal>-<aperture-tag>-...
    parts = chart.slug.split("-")
    cohort = parts[1].upper()  # GF / XF
    focal = parts[2].replace("mm", "")  # 23
    gt_var = f"_FUJI_{cohort}_{focal}_GT"
    aperture_label = chart.apertures[0]
    return gt_var, aperture_label


def _ttartisan_dual_aperture_extras(chart: ReferenceChart) -> StyleFamilyExtras:
    """Curated wording for the TTartisan dual-aperture template:
    gridlines every 0.1 OTF, two apertures pack into one PNG by color
    encoding, and the GT keys are profile labels not f-numbers.
    """
    sample_line_warning = (
        "**Important:** both apertures are packed into one chart by color "
        "encoding — black/grey curves are the max-aperture pass (f/1.2), "
        "red/orange curves are the stopped-aperture pass (f/5.6). One "
        "helper PNG per aperture has the target aperture's traced curves "
        "marked by the extractor; read against those, not the other "
        "aperture's curves. The green sample lines span the full plot "
        "regardless of aperture."
    )

    mtf_axis_legend = (
        "Top of plot area → MTF 1.0",
        "Each printed gridline → 0.1 OTF spacing (every line carries a y-axis label)",
        "Bottom gridline → MTF 0.0",
    )

    # GT-snippet for TTartisan: aperture KEYS are profile labels
    # ("max"/"stopped"), NOT f-numbers — orchestrator keys
    # results_by_aperture on the profile's apertures_per_chart tuple.
    field_lines_per_aperture = "\n        ".join(
        f'"freq{f}{sm}": (...11 values from the {f}{sm} column...),'
        for f in chart.frequencies_lpmm for sm in ("S", "M")
    )
    profile = profile_for_chart(chart)
    assert profile.apertures_per_chart is not None
    ap_blocks = []
    for ap_label, f_number in zip(profile.apertures_per_chart, chart.apertures):
        ap_blocks.append(
            f'    "{ap_label}": {{  # {f_number}\n'
            f"        {field_lines_per_aperture}\n"
            f"    }},"
        )
    # GT variable name: e.g. _TTARTISAN_50_GT.
    parts = chart.slug.split("-")
    focal = parts[1].replace("mm", "")  # 50
    gt_var = f"_TTARTISAN_{focal}_GT"
    gt_snippet = (
        f"```python\n"
        f"{gt_var}: GroundTruthCurves = {{\n"
        + "\n".join(ap_blocks) + "\n"
        f"}}\n"
        f"```"
    )

    return StyleFamilyExtras(
        sample_line_warning=sample_line_warning,
        mtf_axis_legend=mtf_axis_legend,
        gt_snippet=gt_snippet,
    )


# --- Markdown renderers --------------------------------------------------


def _render_eye_read_template(
    chart: ReferenceChart, views: list[HelperView]
) -> str:
    """Markdown body for `eye-read-template.md` — one table per view."""
    fractions_mm = tuple(round(f * chart.image_height_mm, 1) for f in SAMPLE_FRACTIONS)
    fractions_csv = ", ".join(f"{m:.1f}" for m in fractions_mm)
    extras = _extras_for(chart)

    lines: list[str] = []
    lines.append(f"# Eye-read template — {_lens_display_name(chart)}")
    lines.append("")
    lines.append(
        f"Tier 1 anchor for the `{chart.style_family}` style family. "
        f"Maintainer fills in the MTF values below by reading the source "
        f"PNG(s) against the printed gridlines, then copies the tuples "
        f"into `_<LENS>_GT` in `tools/mtfdigitizer/referenceset/charts.py`."
    )
    lines.append("")
    lines.append("Per [[feedback_agent_no_gt_eye_read]] the agent does NOT fill these in.")
    lines.append("")
    lines.append("## Reading procedure")
    lines.append("")
    lines.append("A helper rendering for each view with the 11 sample-position lines overlaid:")
    lines.append("")
    for view in views:
        lines.append(f"- `{view.readhelper_filename}` — {view.title}")
    lines.append("")
    lines.append(
        f"The green vertical lines are spaced by image-height fraction, "
        f"not by the chart's printed x-tick labels. Each line is "
        f"labelled with its image-height mm value (image_height_mm = "
        f"{chart.image_height_mm})."
    )
    lines.append("")
    if extras.sample_line_warning:
        lines.append(extras.sample_line_warning)
        lines.append("")
    lines.append(
        f"Sample positions (mm, image_height_mm = {chart.image_height_mm}): "
        f"{fractions_csv}."
    )
    lines.append("")
    lines.append(
        "Read each cell at the intersection of the green vertical "
        "sample line and the curve, against the printed horizontal "
        "gridlines. Eye precision is ±0.02 (half a gridline tick). "
        "Read to two decimals. Use `None` only when the curve "
        "genuinely does not extend to that x position."
    )
    if extras.mtf_axis_legend:
        lines.append("")
        for bullet in extras.mtf_axis_legend:
            lines.append(f"- {bullet}")
    lines.append("")
    lines.append("## Fill-in tables")
    lines.append("")

    for view in views:
        lines.append(f"### {view.title}")
        lines.append("")
        header = "| Position (mm) | " + " | ".join(view.column_headers) + " |"
        sep = "| ------------- | " + " | ".join(
            ["---"] * len(view.column_headers)
        ) + " |"
        lines.append(header)
        lines.append(sep)
        for mm in fractions_mm:
            row = f"| {mm:<13.1f} | " + " | ".join(
                ["   "] * len(view.column_headers)
            ) + " |"
            lines.append(row)
        lines.append("")

    lines.append("## After filling in")
    lines.append("")
    lines.append(
        "Copy each column into the matching tuple in "
        "`tools/mtfdigitizer/referenceset/charts.py`:"
    )
    lines.append("")
    if extras.gt_snippet:
        lines.append(extras.gt_snippet)
        lines.append("")
    lines.append("Then run from `tools/`:")
    lines.append("")
    lines.append("```")
    lines.append("py -m mtfdigitizer.calibrate")
    lines.append("```")
    lines.append("")
    lines.append(
        "The runner reports per-field median |Δ| and p95 |Δ| against "
        "the extractor's output. Median |Δ| under ~0.04 means the "
        "dispatch is calibrated; higher means an adjustment is needed."
    )
    lines.append("")
    return "\n".join(lines)


def _render_extractor_prediction(
    chart: ReferenceChart, views: list[HelperView]
) -> str:
    """Markdown body for `extractor-prediction.md` — extractor's reading
    of each cell, as a starting point for maintainer validation.
    """
    fractions_mm = tuple(round(f * chart.image_height_mm, 1) for f in SAMPLE_FRACTIONS)
    fractions_csv = ", ".join(f"{m:.1f}" for m in fractions_mm)

    lines: list[str] = []
    lines.append(f"# Extractor prediction — {_lens_display_name(chart)}")
    lines.append("")
    lines.append(
        "**NOT GROUND TRUTH.** This file holds the digitizer's reading "
        "of each sample position. It exists to save eye-read time for "
        "the maintainer: scan each cell against the source PNG, accept "
        "what looks right (no edit), overwrite what looks wrong."
    )
    lines.append("")
    lines.append(
        "Per [[feedback_agent_no_gt_eye_read]] only maintainer-validated "
        "values may land in `_<LENS>_GT` in `referenceset/charts.py`. "
        "After scanning this table, transcribe the validated values "
        "(adjusting any that disagree with the source) into the GT tuple."
    )
    lines.append("")
    lines.append(
        f"Sample positions (mm, image_height_mm = {chart.image_height_mm}): "
        f"{fractions_csv}."
    )
    lines.append("")

    for view in views:
        lines.append(f"## {view.title}")
        lines.append("")
        header = "| Position (mm) | " + " | ".join(view.column_headers) + " |"
        sep = "| ------------- | " + " | ".join(
            ["----"] * len(view.column_headers)
        ) + " |"
        lines.append(header)
        lines.append(sep)
        readings = _extractor_readings_for_view(chart, view)
        for i, mm in enumerate(fractions_mm):
            cells = []
            for field in view.field_columns:
                val = readings[i].get(field)
                cells.append(f"{val:.2f}" if val is not None else "—   ")
            lines.append(f"| {mm:<13.1f} | " + " | ".join(cells) + " |")
        lines.append("")

    extras = _extras_for(chart)
    if extras.gt_snippet:
        lines.append("## After validation")
        lines.append("")
        lines.append(
            "Copy each column into the matching tuple in "
            "`tools/mtfdigitizer/referenceset/charts.py`:"
        )
        lines.append("")
        lines.append(extras.gt_snippet)
        lines.append("")
    return "\n".join(lines)


def _extractor_readings_for_view(chart: ReferenceChart, view: HelperView):
    """Run the extractor for one helper view and return its 11 readings.

    Three dispatch paths mirror calibrate.py:

    - **Per-frequency** (`fujifilm-permfreq`): substitute the parsed
      frequency onto a copy of the base profile so the extractor
      labels its readings as `freq{N}S/M` rather than the placeholder
      `freq0S/M`. One view per PNG.
    - **Multi-aperture** (TTartisan): hue-filter the base profile to
      the target aperture before extracting. Both views share the
      primary chart raster.
    - **Standard** (no special-casing today, included for completeness).
    """
    import dataclasses  # noqa: PLC0415
    base_profile = profile_for_chart(chart)
    if view.aperture_label is not None:
        from mtfdigitizer.extract import _hue_filtered_profile  # noqa: PLC0415

        profile = _hue_filtered_profile(base_profile, view.aperture_label)
    elif chart.style_family == "fujifilm-permfreq":
        from mtfdigitizer.per_frequency import (  # noqa: PLC0415
            parse_filename_frequency,
        )

        freq = parse_filename_frequency(view.extractor_chart_path)
        profile = dataclasses.replace(base_profile, frequencies_lpmm=(freq,))
    else:
        profile = base_profile
    result = extract_chart(
        view.extractor_chart_path,
        profile,
        view.plot_box,
        image_height_mm=chart.image_height_mm,
    )
    return result.readings


def _lens_display_name(chart: ReferenceChart) -> str:
    """Resolve the official lens display name from `src/data/lenses.ts`.

    Falls back to the slug if no matching entry is found — the helpers
    still scaffold cleanly for anchors of lenses not yet in lenses.ts,
    just with a less polished header.
    """
    import re  # noqa: PLC0415 — local import to keep top-level lean
    lenses_path = REPO_ROOT / "src" / "data" / "lenses.ts"
    content = lenses_path.read_text(encoding="utf-8")
    # Each entry is a block; match `brand: "X"` then the first `model: "Y"`
    # within the same block, and synthesise the slug to compare. The slug
    # convention is `toSlug(brand + " " + model)` — lowercase, alphanum,
    # hyphens for separators, slashes/periods collapsed.
    for brand_m in re.finditer(r'brand:\s*"([^"]+)"', content):
        brand = brand_m.group(1)
        # Search for the model in the block immediately after.
        rest = content[brand_m.end():brand_m.end() + 800]
        model_m = re.search(r'model:\s*"([^"]+)"', rest)
        if not model_m:
            continue
        model = model_m.group(1)
        if _to_slug(f"{brand} {model}") == chart.slug:
            return f"{brand} {model}"
    return chart.slug


def _to_slug(text: str) -> str:
    """Port of the project's `toSlug` (see `src/utils/slug.ts`).

    Lowercase, strip slashes outright, then replace any run of
    non-alphanumeric characters with a single hyphen, strip
    leading/trailing hyphens. Slashes are stripped (not hyphenated)
    so `f/1.4` → `f1-4` not `f-1-4`.
    """
    import re  # noqa: PLC0415
    cleaned = text.lower().replace("/", "")
    return re.sub(r"[^a-z0-9]+", "-", cleaned).strip("-")


# --- Main ----------------------------------------------------------------


def _find_anchor(slug: str) -> ReferenceChart:
    for chart in REFERENCE_CHARTS:
        if chart.slug == slug:
            if chart.ground_truth is None:
                raise SystemExit(
                    f"{slug}: not a Tier 1 anchor — ground_truth is None. "
                    f"Anchor helpers only scaffold for charts that hold "
                    f"(or will hold) maintainer-read GT."
                )
            return chart
    raise SystemExit(f"{slug}: not found in REFERENCE_CHARTS")


def _write_or_check(path: Path, payload: bytes, *, write: bool, check: bool) -> bool:
    """Write `payload` to `path`, or in --check mode return whether the
    file would change. Returns True if the file would change (or did).
    """
    existing = path.read_bytes() if path.exists() else None
    changed = existing != payload
    if check:
        if changed:
            kind = "differ" if existing is not None else "missing"
            print(f"  {kind}: {path.relative_to(REPO_ROOT)}", file=sys.stderr)
        return changed
    if write and changed:
        path.write_bytes(payload)
        print(f"  wrote: {path.relative_to(REPO_ROOT)}", file=sys.stderr)
    elif not write:
        print(f"  preview: {path.relative_to(REPO_ROOT)}", file=sys.stderr)
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("slug", help="anchor slug to scaffold helpers for")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--write", action="store_true",
        help="materialize artifacts on disk",
    )
    group.add_argument(
        "--check", action="store_true",
        help="exit 1 if any artifact would change on disk",
    )
    args = parser.parse_args(argv)

    chart = _find_anchor(args.slug)
    views = _resolve_helper_views(chart)
    lens_dir = (REPO_ROOT / chart.chart_path).parent

    any_changed = False
    print(f"{args.slug}: {len(views)} view(s)", file=sys.stderr)

    extras = _extras_for(chart)

    # Readhelper PNGs.
    for view in views:
        helper = _render_readhelper(view, chart.image_height_mm, extras)
        import io
        buf = io.BytesIO()
        helper.save(buf, format="PNG")
        out_path = lens_dir / view.readhelper_filename
        if _write_or_check(out_path, buf.getvalue(), write=args.write, check=args.check):
            any_changed = True

    # Markdown templates.
    eye_read = _render_eye_read_template(chart, views).encode("utf-8")
    pred = _render_extractor_prediction(chart, views).encode("utf-8")
    eye_read_path = lens_dir / "eye-read-template.md"
    pred_path = lens_dir / "extractor-prediction.md"
    if _write_or_check(eye_read_path, eye_read, write=args.write, check=args.check):
        any_changed = True
    if _write_or_check(pred_path, pred, write=args.write, check=args.check):
        any_changed = True

    if args.check:
        if any_changed:
            print("FAIL: anchor helpers out of date — re-run without --check.", file=sys.stderr)
            return 1
        print("OK: anchor helpers up to date.", file=sys.stderr)
    elif not args.write:
        print("\nPreview only — pass --write to materialize.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
