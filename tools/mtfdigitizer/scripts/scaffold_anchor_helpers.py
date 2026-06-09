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


def _render_readhelper(view: HelperView, image_height_mm: float) -> Image.Image:
    """3x upscale of the base image with green vertical sample-position
    lines and per-line mm labels.
    """
    base = Image.open(view.base_image_path).convert("RGB")
    up = base.resize(
        (base.width * UPSCALE_FACTOR, base.height * UPSCALE_FACTOR),
        resample=Image.NEAREST,
    )
    draw = ImageDraw.Draw(up)

    # Scale plot-box x coordinates to the upscaled image.
    plot_left_up = view.plot_box.x_left * UPSCALE_FACTOR
    plot_right_up = view.plot_box.x_right * UPSCALE_FACTOR
    plot_top_up = view.plot_box.y_top * UPSCALE_FACTOR
    plot_bottom_up = view.plot_box.y_bottom * UPSCALE_FACTOR
    plot_width_up = plot_right_up - plot_left_up

    font = _load_label_font()

    for frac in SAMPLE_FRACTIONS:
        x_up = int(plot_left_up + frac * plot_width_up)
        # Vertical line spanning the plot area.
        draw.line(
            [(x_up, plot_top_up), (x_up, plot_bottom_up)],
            fill=GREEN_LINE_RGB,
            width=GREEN_LINE_WIDTH_PX,
        )
        # Label just below the plot in mm.
        mm = frac * image_height_mm
        label = f"{mm:.1f}"
        # Anchor label slightly below the plot bottom; offset so the
        # text is centered on the line.
        label_y = plot_bottom_up + 6 * UPSCALE_FACTOR
        bbox = draw.textbbox((0, 0), label, font=font)
        label_w = bbox[2] - bbox[0]
        draw.text(
            (x_up - label_w // 2, label_y),
            label,
            fill=LABEL_FILL_RGB,
            font=font,
        )
    return up


def _load_label_font() -> ImageFont.ImageFont:
    """Best-effort load of a legible truetype font; fall back to PIL's
    default if no system font is reachable.
    """
    # Pillow ships with a default bitmap font; on most systems a
    # truetype is also reachable. Try a couple of common names then
    # fall back.
    for name in ("DejaVuSans.ttf", "arial.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size=14 * UPSCALE_FACTOR)
        except OSError:
            continue
    return ImageFont.load_default()


# --- Markdown renderers --------------------------------------------------


def _render_eye_read_template(
    chart: ReferenceChart, views: list[HelperView]
) -> str:
    """Markdown body for `eye-read-template.md` — one table per view."""
    fractions_mm = tuple(round(f * chart.image_height_mm, 1) for f in SAMPLE_FRACTIONS)
    fractions_csv = ", ".join(f"{m:.1f}" for m in fractions_mm)

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
        "`tools/mtfdigitizer/referenceset/charts.py` "
        f"(`_<LENS>_GT`). Then run from `tools/`:"
    )
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
    return "\n".join(lines)


def _extractor_readings_for_view(chart: ReferenceChart, view: HelperView):
    """Run the extractor for one helper view and return its 11 readings.

    For multi-aperture profiles, hue-filter the profile to the target
    aperture before running so the readings reflect that aperture's
    curves only. For single-aperture profiles, run the base profile.
    """
    base_profile = profile_for_chart(chart)
    image_path = REPO_ROOT / chart.chart_path
    if view.aperture_label is not None:
        from mtfdigitizer.extract import _hue_filtered_profile  # noqa: PLC0415

        profile = _hue_filtered_profile(base_profile, view.aperture_label)
    else:
        profile = base_profile
    result = extract_chart(
        image_path,
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

    # Readhelper PNGs.
    for view in views:
        helper = _render_readhelper(view, chart.image_height_mm)
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
