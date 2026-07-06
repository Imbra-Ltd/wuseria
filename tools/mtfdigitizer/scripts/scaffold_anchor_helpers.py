"""Scaffold maintainer eye-read helpers for a Tier 1 anchor.

For a given anchor slug, generates two artifacts in the lens's
`docs/optical-specs/<slug>/` folder:

1. **`<view-stem>-readhelper.png`** — 3x upscale of the view's base
   image with green vertical lines at the 11 sample positions and
   each line labelled with its image-height mm value. One file per
   view (per frequency for `fujifilm-permfreq`, per aperture for
   `ttartisan-4color-dual-aperture`).

2. **`eye-read.md`** — single document (per ADR-048) holding both
   the legend / reading procedure AND the per-cell values. Cells are
   pre-populated with the extractor's predictions. The maintainer
   reviews each cell against the source PNG and:

   - leaves cells they judge correct as-is (silent verification);
   - overwrites wrong cells and appends `!` (e.g. `0.45!`);
   - appends `?` to cells they couldn't read (becomes `None` in GT).

   Then the agent transcribes the file into the `_<LENS>_GT` tuple
   via ``py -m mtfdigitizer.eyeread <slug> --apply``.

On re-run (after an extractor change, for example), the scaffolder
PRESERVES `!` and `?` marks and refreshes unmarked cells from the
new extractor predictions. The header text and legend are always
regenerated.

The agent does NOT propose cell values of its own — that is the
maintainer's job (`feedback_agent_no_gt_eye_read`). The scaffolder
publishes the extractor's predictions as a starting point for the
maintainer to verify or correct.

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
# Grey dashed major gridlines — mid-weight anchors between the chart's
# printed lines on dense grids (e.g. Touit's 0.01 grid gets grey lines
# at every 0.1) so the eye can localize without counting orange lines.
MAJOR_STEP_LINE_RGB = (110, 110, 110)


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
    if chart.style_family == "multifreq-press-kit":
        return _multifreq_press_kit_views(chart)
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
    """TTartisan dual-aperture: one PNG per aperture, sample-position
    lines drawn over the **clean source chart** (never the extractor
    overlay).

    The readhelper's purpose is unbiased maintainer eye-reading. Layering
    the extractor's traced curves underneath nudges the eye toward the
    extractor's answer — exactly the bias the eye-read is meant to
    catch. The clean chart stays the source of truth here; the overlay
    PNG is used elsewhere (`*-overlay.png` + the review HTML) when the
    maintainer specifically wants to compare extractor output against
    the chart.
    """
    assert chart.plot_box is not None
    profile = profile_for_chart(chart)
    assert profile.apertures_per_chart is not None, (
        f"{chart.slug}: profile has no apertures_per_chart but style "
        f"family is ttartisan-4color-dual-aperture"
    )
    source_path = REPO_ROOT / chart.chart_path
    source_stem = source_path.stem
    freqs = chart.frequencies_lpmm

    views: list[HelperView] = []
    for ap_label, f_number in zip(profile.apertures_per_chart, chart.apertures):
        views.append(
            HelperView(
                title=f"{f_number} ({ap_label})",
                base_image_path=source_path,
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


def _multifreq_press_kit_views(chart: ReferenceChart) -> list[HelperView]:
    """Zeiss Touit press-kit: B&W chart with N spatial frequencies stacked
    in one plot panel, two apertures split across two plot panels of one
    PNG (ADR-063 per-view aperture override, ADR-075 N-frequency
    RIDGE_TRACKING).

    Differs from TTartisan dual-aperture in two ways: (1) panels are
    split by plot-box y-coordinates, not by color hue — no hue filtering
    needed; (2) frequencies span the chart's column set (3 freqs × {S,M}
    = 6 columns per panel), where TTartisan uses 2 freqs × {S,M} = 4.
    """
    assert chart.plot_box is not None
    source_path = REPO_ROOT / chart.chart_path
    source_stem = source_path.stem
    freqs = chart.frequencies_lpmm

    views: list[HelperView] = []
    for chart_view, f_number in zip(chart.views, chart.apertures):
        assert chart_view.plot_box is not None
        ap_label = chart_view.aperture
        assert ap_label is not None, (
            f"{chart.slug}: multifreq-press-kit view {chart_view.chart_path!r} "
            f"has no aperture role label (ADR-063); expected one of "
            f"{chart.apertures}"
        )
        views.append(
            HelperView(
                title=f"{f_number} ({ap_label})",
                base_image_path=source_path,
                readhelper_filename=f"{source_stem}-{ap_label}-readhelper.png",
                field_columns=tuple(
                    f"freq{f}{sm}" for f in freqs for sm in ("S", "M")
                ),
                column_headers=tuple(
                    f"{f}{sm}" for f in freqs for sm in ("S", "M")
                ),
                plot_box=_to_plotbox(chart_view.plot_box),
                # Both panels live on one PNG — extractor uses the shared
                # raster with each view's plot_box. No hue/aperture
                # profile transformation needed (panels are positionally
                # separated, unlike TTartisan's color encoding).
                extractor_chart_path=source_path,
                aperture_label=None,
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
    - **Orange dashed horizontal gridlines** (controlled by
      `extras.readhelper_extra_otf`) fill in 0.05-step ticks the
      source chart doesn't print natively, letting the maintainer
      eye-read at ±0.02 precision (half a 0.05 tick) regardless of
      the chart's native gridline density.
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

    # Extra horizontal gridlines (filling out the source chart's
    # native grid). Drawn FIRST so the green sample lines render on
    # top of them. Labels are emitted only for entries in
    # `readhelper_label_otf` (when empty, every line is labelled —
    # historical default for the 0.05-grid families).
    labelled = (
        set(extras.readhelper_label_otf)
        if extras.readhelper_label_otf
        else set(extras.readhelper_extra_otf)
    )
    major = set(extras.readhelper_major_otf)
    for otf in extras.readhelper_extra_otf:
        y = int(plot_bottom_up - otf * plot_height_up)
        line_rgb = MAJOR_STEP_LINE_RGB if otf in major else HALF_STEP_LINE_RGB
        _draw_dashed_hline(
            draw,
            x_left=plot_left_up,
            x_right=plot_right_up,
            y=y,
            color=line_rgb,
            width=HALF_STEP_LINE_WIDTH_PX,
            dash_len=HALF_STEP_DASH_LEN_PX * UPSCALE_FACTOR,
        )
        if otf not in labelled:
            continue
        # Label the OTF value just right of the plot, in the line's own
        # color. Use 2 decimals so 0.05 / 0.15 / 0.25 / ... show their
        # hundredths digit cleanly.
        label = f"{otf:.2f}"
        bbox = draw.textbbox((0, 0), label, font=font)
        draw.text(
            (plot_right_up + 4 * UPSCALE_FACTOR, y - (bbox[3] - bbox[1]) // 2),
            label,
            fill=line_rgb,
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
    # OTF fractions (0..1) at which to draw an orange dashed horizontal
    # gridline on the readhelper PNG, on top of the chart's own printed
    # gridlines. The eye-read target grid is family-specific: Fuji and
    # TTartisan use a 0.05 grid (Fuji prints every 0.2, TTartisan every
    # 0.1, so each fills the gap to 0.05); Zeiss Touit uses a 0.01 grid
    # for higher-precision reads. Empty tuple = no extra gridlines.
    readhelper_extra_otf: tuple[float, ...] = ()
    # OTF fractions in `readhelper_extra_otf` that should be labelled
    # with their value next to the plot. Empty tuple = label every
    # line (default — fine when the grid is coarse). Used when the
    # grid is denser than the label column can fit readably: lines
    # are still drawn at every entry in `readhelper_extra_otf`, but
    # only entries in this tuple get a text label.
    readhelper_label_otf: tuple[float, ...] = ()
    # OTF fractions in `readhelper_extra_otf` to draw as grey MAJOR
    # anchors instead of orange minors. On dense grids the eye needs a
    # mid-weight tier between the chart's printed lines and the minor
    # fill — e.g. Touit draws grey at every 0.1 the chart does not
    # print, so no read starts more than 0.05 from a grey or printed
    # line. Empty tuple = no major tier (all lines orange).
    readhelper_major_otf: tuple[float, ...] = ()
    # Sentence stating the maintainer's read precision against the
    # rendered grid. Half a tick spacing on `readhelper_extra_otf`:
    # 0.05 grid → ±0.02, 0.01 grid → ±0.005. Default reads ±0.02 to
    # match the historical default for 0.05-grid families.
    eye_precision_text: str = "±0.02 (half a gridline tick)"


def _extras_for(chart: ReferenceChart) -> StyleFamilyExtras:
    if chart.style_family == "fujifilm-permfreq":
        return _fuji_permfreq_extras(chart)
    if chart.style_family == "ttartisan-4color-dual-aperture":
        return _ttartisan_dual_aperture_extras(chart)
    if chart.style_family == "multifreq-press-kit":
        return _multifreq_press_kit_extras(chart)
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
        "Orange dashed lines fill in every 0.05 between the printed gridlines",
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
        # Fuji prints every 0.2 OTF; add lines at every 0.05 in
        # between so the readhelper supports a uniform 0.05 grid
        # (and ±0.02 eye-precision per ADR-046's eye-read scope).
        readhelper_extra_otf=tuple(
            round(0.05 * i, 2)
            for i in range(1, 20)
            if round(0.05 * i, 2) not in (0.2, 0.4, 0.6, 0.8)
        ),
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
    f_max, f_stopped = chart.apertures[0], chart.apertures[1]
    sample_line_warning = (
        f"**Important:** both apertures are packed into one chart by color "
        f"encoding — black/grey curves are the max-aperture pass ({f_max}), "
        f"red/orange curves are the stopped-aperture pass ({f_stopped}). "
        f"Per ADR-046 the helper PNG shows the **clean source chart** "
        f"(no extractor overlay) so the eye-read is unbiased; read each "
        f"aperture's curves directly off the chart's own printed lines. "
        f"The green sample lines span the full plot regardless of aperture."
    )

    mtf_axis_legend = (
        "Top of plot area → MTF 1.0",
        "Each printed gridline → 0.1 OTF spacing (every line carries a y-axis label)",
        "Bottom gridline → MTF 0.0",
        "Orange dashed lines fill in every 0.05 between the printed gridlines",
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
    # GT variable name: e.g. _TTARTISAN_50_GT. AF lenses
    # (`ttartisan-af-NNmm-...`) and tilt lenses get a prefix segment to
    # keep their var names unique — must match `eyeread.gt_var_for_chart`.
    parts = chart.slug.split("-")
    if parts[1] in {"af", "tilt"}:
        variant = parts[1].upper()
        focal = parts[2].replace("mm", "")
        gt_var = f"_TTARTISAN_{variant}_{focal}_GT"
    else:
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
        # TTartisan prints every 0.1 OTF natively; add the missing
        # 0.05-step lines so the maintainer can eye-read at ±0.02
        # precision against a uniform 0.05 grid.
        readhelper_extra_otf=(0.05, 0.15, 0.25, 0.35, 0.45,
                              0.55, 0.65, 0.75, 0.85, 0.95),
    )


def _multifreq_press_kit_extras(chart: ReferenceChart) -> StyleFamilyExtras:
    """Curated wording for the Zeiss Touit press-kit template:
    monochrome, solid=S dashed=T (dotted on 50mm macro), 3 frequencies
    stacked vertically per panel (10 lp/mm highest, 40 lp/mm lowest at
    center), two apertures across two stacked panels of one PNG.
    """
    f_max, f_stopped = chart.apertures[0], chart.apertures[1]
    sample_line_warning = (
        f"**Important:** both apertures are packed into one chart as "
        f"two stacked panels — top panel is the max-aperture pass "
        f"({f_max}), bottom panel is the stopped-aperture pass "
        f"({f_stopped}). All curves are monochrome black; solid lines "
        f"are sagittal (S), dashed (or dotted, on the 50mm macro) are "
        f"tangential (M). Within each panel the three frequencies stack "
        f"vertically: 10 lp/mm highest, 20 lp/mm middle, 40 lp/mm "
        f"lowest at the optical centre. Per ADR-046 the helper PNG "
        f"shows the **clean source chart** (no extractor overlay) so "
        f"the eye-read is unbiased. The green sample lines span the "
        f"full plot regardless of panel."
    )

    mtf_axis_legend = (
        "Top of plot area → MTF 1.0",
        "Each printed gridline below it → 0.8, 0.6, 0.4, 0.2",
        "Bottom gridline → MTF 0.0",
        "Grey dashed lines anchor every 0.1 between the printed gridlines",
        "Orange dashed lines fill in every 0.01 between them",
    )

    # GT-snippet for Zeiss Touit: aperture KEYS are profile role labels
    # ("max"/"stopped") per ADR-063 — calibrate.py keys results on the
    # view's aperture role, not the f-number.
    field_lines_per_aperture = "\n        ".join(
        f'"freq{f}{sm}": (...11 values from the {f}{sm} column...),'
        for f in chart.frequencies_lpmm for sm in ("S", "M")
    )
    ap_blocks = []
    for ap_label, f_number in zip(("max", "stopped"), chart.apertures):
        ap_blocks.append(
            f'    "{ap_label}": {{  # {f_number}\n'
            f"        {field_lines_per_aperture}\n"
            f"    }},"
        )
    gt_var = _zeiss_touit_gt_var(chart)
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
        # Zeiss prints every 0.20 OTF natively; add lines at every 0.01
        # in between so the maintainer can eye-read at ±0.005 precision
        # against a uniform 0.01 grid. Touit gets the dense grid because
        # the 3-frequency stopped-panel calibration (#1332, ADR-075)
        # needs sub-0.02 resolution to distinguish ridge-cluster
        # coincidence regressions from true measurement error.
        readhelper_extra_otf=tuple(
            round(0.01 * i, 2)
            for i in range(1, 100)
            if round(0.01 * i, 2) not in (0.2, 0.4, 0.6, 0.8)
        ),
        # 99 lines is too many to label individually next to the plot.
        # Label only the major 0.05 ticks (0.05, 0.10, ..., 0.95) so
        # the right margin stays readable; minor 0.01 lines are still
        # drawn for the read.
        readhelper_label_otf=tuple(
            round(0.05 * i, 2)
            for i in range(1, 20)
            if round(0.05 * i, 2) not in (0.2, 0.4, 0.6, 0.8)
        ),
        # Grey major anchors at every 0.1 the chart does not print
        # (0.1, 0.3, 0.5, 0.7, 0.9) — with the printed 0.2-step lines
        # this gives the eye a strong line at every 0.1.
        readhelper_major_otf=tuple(
            round(0.1 * i, 2)
            for i in range(1, 10)
            if round(0.1 * i, 2) not in (0.2, 0.4, 0.6, 0.8)
        ),
        eye_precision_text="±0.005 (half a gridline tick)",
    )


def _zeiss_touit_gt_var(chart: ReferenceChart) -> str:
    """Return the `_ZEISS_TOUIT_<FOCAL>_GT` variable name for a Zeiss
    Touit anchor. Must match `eyeread.gt_var_for_chart`.

    Slug shape: `zeiss-touit-<focal>mm-f<ap>-...` (e.g.
    `zeiss-touit-12mm-f2-8`, `zeiss-touit-50mm-f2-8-macro`). Focal
    lives at parts[2] — strip the trailing `mm`.
    """
    parts = chart.slug.split("-")
    focal = parts[2].replace("mm", "")
    return f"_ZEISS_TOUIT_{focal}_GT"


# --- Markdown renderers --------------------------------------------------


def _render_eye_read(
    chart: ReferenceChart,
    views: list[HelperView],
    existing_marks: dict[tuple[str, str, int], "Cell"] | None = None,
) -> str:
    """Markdown body for `eye-read.md` — legend + one table per view.

    Tables are pre-populated with the extractor's predictions. If
    `existing_marks` is provided (from parsing the prior eye-read.md),
    each `!` or `?`-marked cell keeps its previous value and mark,
    overriding the fresh extractor prediction. The mapping key is
    ``(view_heading, column_header, row_index)`` — stable identifiers
    that survive header rewording when the lens display name changes.
    """
    from mtfdigitizer.eyeread import Cell as ParsedCell, format_cell  # noqa: PLC0415
    fractions_mm = tuple(round(f * chart.image_height_mm, 1) for f in SAMPLE_FRACTIONS)
    fractions_csv = ", ".join(f"{m:.1f}" for m in fractions_mm)
    extras = _extras_for(chart)

    lines: list[str] = []
    lines.append(f"# Eye-read — {_lens_display_name(chart)}")
    lines.append("")
    lines.append(
        f"Tier 1 anchor for the `{chart.style_family}` style family. "
        f"Cells below are pre-populated with the extractor's predictions. "
        f"The maintainer reads each cell against the source PNG; per "
        f"ADR-048 each cell has one of three states:"
    )
    lines.append("")
    lines.append(
        "- bare number (`0.43`) — extractor's prediction, maintainer "
        "judged it fine (silent verification)"
    )
    lines.append(
        "- number with `!` (`0.45!`) — maintainer-corrected; overrides "
        "the extractor's value"
    )
    lines.append(
        "- number with `?` (`0.43?`) or bare `?` — maintainer hasn't "
        "read this cell; becomes `None` in the GT tuple"
    )
    lines.append("")
    lines.append(
        "When the extractor is re-run and predictions change, this file "
        "preserves `!` and `?` marks and refreshes unmarked cells. The "
        "header text and legend are regenerated from the scaffolder."
    )
    lines.append("")
    lines.append(
        "Per [[feedback_agent_no_gt_eye_read]] the agent does NOT propose "
        "cell values of its own — the extractor predictions you see are "
        "mechanical readings, not eye-reads."
    )
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
        f"gridlines. Eye precision is {extras.eye_precision_text}. "
        "Read to two decimals. Use `?` only when the curve genuinely "
        "does not extend to that x position."
    )
    if extras.mtf_axis_legend:
        lines.append("")
        for bullet in extras.mtf_axis_legend:
            lines.append(f"- {bullet}")
    lines.append("")

    for view in views:
        lines.append(f"## {view.title}")
        lines.append("")
        header = "| Position (mm) | " + " | ".join(
            h.ljust(5) for h in view.column_headers
        ) + " |"
        sep = "| ------------- | " + " | ".join(
            ["-----"] * len(view.column_headers)
        ) + " |"
        lines.append(header)
        lines.append(sep)
        readings = _extractor_readings_for_view(chart, view)
        for i, mm in enumerate(fractions_mm):
            rendered_cells: list[str] = []
            for col_idx, (field, header_text) in enumerate(
                zip(view.field_columns, view.column_headers)
            ):
                key = (view.title, header_text, i)
                cell = (existing_marks or {}).get(key)
                if cell is not None and cell.mark in ("!", "?"):
                    # Preserve marked cell.
                    pass
                else:
                    extractor_val = readings[i].get(field)
                    cell = ParsedCell(value=extractor_val, mark="")
                rendered_cells.append(format_cell(cell, width=5))
            lines.append(f"| {mm:<13.1f} | " + " | ".join(rendered_cells) + " |")
        lines.append("")

    lines.append("## Transcribing to GT")
    lines.append("")
    lines.append(
        "After updating the cells above, ask the agent to transcribe — "
        "or run from `tools/`:"
    )
    lines.append("")
    lines.append("```")
    lines.append(f"py -m mtfdigitizer.eyeread {chart.slug} --apply")
    lines.append("py -m mtfdigitizer.calibrate")
    lines.append("```")
    lines.append("")
    lines.append(
        "The first command rewrites `_<LENS>_GT` in "
        "`tools/mtfdigitizer/referenceset/charts.py`. The second reports "
        "per-field median |Δ| and p95 |Δ| against the extractor's output. "
        "Median |Δ| under ~0.04 means the dispatch is calibrated; higher "
        "means an adjustment is needed."
    )
    lines.append("")
    if extras.gt_snippet:
        lines.append("The resulting GT tuple shape:")
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


def _load_existing_marks(path: Path):
    """Read the prior eye-read.md (if any) and return a map of
    (view_heading, column_header, row_index) → Cell for cells that
    carry a `!` or `?` mark.

    Returns ``None`` if the file doesn't exist (first scaffold) or
    can't be parsed; the renderer falls back to fresh extractor
    predictions everywhere.
    """
    if not path.exists():
        return None
    from mtfdigitizer.eyeread import parse_eye_read  # noqa: PLC0415
    try:
        views = parse_eye_read(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    marks = {}
    for view in views:
        for i, (_position, fields) in enumerate(view.cells):
            for header, cell in fields.items():
                if cell.mark in ("!", "?"):
                    marks[(view.heading, header, i)] = cell
    return marks


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

    # Eye-read.md — preserve `!` and `?` marks from the prior version.
    eye_read_path = lens_dir / "eye-read.md"
    existing_marks = _load_existing_marks(eye_read_path)
    eye_read = _render_eye_read(chart, views, existing_marks).encode("utf-8")
    if _write_or_check(eye_read_path, eye_read, write=args.write, check=args.check):
        any_changed = True

    # Clean up the pre-ADR-048 split files (extractor-prediction.md +
    # eye-read-template.md). Removing them is part of the unification.
    for legacy in ("extractor-prediction.md", "eye-read-template.md"):
        legacy_path = lens_dir / legacy
        if legacy_path.exists():
            if args.check:
                print(
                    f"  legacy file present: {legacy_path.relative_to(REPO_ROOT)}",
                    file=sys.stderr,
                )
                any_changed = True
            elif args.write:
                legacy_path.unlink()
                print(
                    f"  deleted: {legacy_path.relative_to(REPO_ROOT)}",
                    file=sys.stderr,
                )

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
