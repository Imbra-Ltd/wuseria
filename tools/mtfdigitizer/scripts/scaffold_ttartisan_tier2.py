"""Scaffold Tier 2 ReferenceChart entries for every TTartisan lens that
has an MTF chart image.

Walks ``docs/optical-specs/ttartisan-*`` folders, classifies each
chart's scheme via ``ttartisan_plotbox.detect_ttartisan_plotbox``, and
writes ``_ttartisan_tier2_charts.py`` declaring one ``ReferenceChart``
per lens with:

- ``style_family="ttartisan-4color-dual-aperture"``
- ``plot_box`` per scheme (APS-C vs GFX/full-frame template constant)
- ``apertures`` = (max, stopped) — read from the per-lens table below
- ``frequencies_lpmm=(10, 30)``
- ``ground_truth=None`` (Tier 2 per ADR-041)

Per ADR-044 the orchestrator fans out one extractor pass per aperture;
``chart.apertures`` MUST list the apertures in the same order as the
profile's ``apertures_per_chart=("max", "stopped")``.

The **stopped aperture** lives only in the chart legend — pixel-OCR
of the legend text was attempted and abandoned (text-width overlap
across f/8 / f/11 / f/5.6 on the 800x600 template). The maintainer
eye-read every legend during the PR that introduced this scaffolder
and ships the per-lens table below as the single source of truth. A
chart whose slug is not in the table fails the scaffolder loud at
generation time.

Usage::

    cd tools
    py -m mtfdigitizer.scripts.scaffold_ttartisan_tier2          # preview
    py -m mtfdigitizer.scripts.scaffold_ttartisan_tier2 --write   # commit
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from mtfdigitizer.ttartisan_plotbox import (
    TTartisanBoxResult,
    detect_ttartisan_plotbox,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
OPTICAL_SPECS_DIR = REPO_ROOT / "docs" / "optical-specs"


# Per-lens (max, stopped) apertures eye-read from each chart's legend.
# The agent did NOT auto-derive these — pixel-OCR was too unreliable
# (see ttartisan_plotbox.py header). Source of truth: the legend on
# each chart in docs/optical-specs/<slug>/<slug>-mtf.png.
_APERTURES_BY_SLUG: dict[str, tuple[str, str]] = {
    "ttartisan-100mm-f2-8-macro-2x-gfx": ("f/2.8", "f/8"),
    "ttartisan-100mm-f2-8-macro-2x": ("f/2.8", "f/8"),
    "ttartisan-11mm-f2-8-fisheye-gfx": ("f/2.8", "f/5.6"),
    "ttartisan-23mm-f1-4": ("f/1.4", "f/5.6"),
    "ttartisan-25mm-f2-0": ("f/2", "f/8"),
    "ttartisan-35mm-f1-4": ("f/1.4", "f/8"),
    "ttartisan-40mm-f2-8-macro": ("f/2.8", "f/8"),
    "ttartisan-500mm-f6-3": ("f/6.3", "f/11"),
    "ttartisan-500mm-f6-3-gfx": ("f/6.3", "f/11"),
    "ttartisan-50mm-f1-2": ("f/1.2", "f/5.6"),
    "ttartisan-50mm-f2-0": ("f/2", "f/8"),
    "ttartisan-7-5mm-f2-0-fisheye": ("f/2", "f/8"),
    "ttartisan-90mm-f1-25-gfx": ("f/1.25", "f/5.6"),
    "ttartisan-af-27mm-f2-8": ("f/2.8", "f/8"),
    "ttartisan-af-35mm-f1-8": ("f/1.8", "f/5.6"),
    "ttartisan-af-56mm-f1-8": ("f/1.8", "f/5.6"),
    "ttartisan-af-75mm-f2-0": ("f/2", "f/5.6"),
    "ttartisan-tilt-35mm-f1-4": ("f/1.4", "f/8"),
    "ttartisan-tilt-50mm-f1-4": ("f/1.4", "f/8"),
}


@dataclass(frozen=True)
class _ChartFile:
    """One detected chart image's metadata."""

    slug: str
    path: Path  # relative to repo root
    max_aperture: str
    stopped_aperture: str
    detected: TTartisanBoxResult


# Tier 1 anchors live in `charts.py` proper with maintainer-read
# ground truth; the scaffolder never emits a duplicate entry for them
# (the `test_no_duplicate_slugs` assertion would fail).
_TIER1_SKIP_SLUGS: frozenset[str] = frozenset({
    "ttartisan-50mm-f1-2",
    "ttartisan-7-5mm-f2-0-fisheye",
    "ttartisan-af-35mm-f1-8",
})


def _gather_charts() -> list[_ChartFile]:
    """Find every TTartisan MTF chart image and run the detector."""
    charts: list[_ChartFile] = []
    for lens_dir in sorted(OPTICAL_SPECS_DIR.iterdir()):
        if not lens_dir.is_dir():
            continue
        if not lens_dir.name.startswith("ttartisan-"):
            continue
        if lens_dir.name in _TIER1_SKIP_SLUGS:
            continue
        slug = lens_dir.name
        chart_path = lens_dir / f"{slug}-mtf.png"
        if not chart_path.exists():
            print(
                f"SKIP {lens_dir.name}: no <slug>-mtf.png file",
                file=sys.stderr,
            )
            continue
        if slug not in _APERTURES_BY_SLUG:
            raise KeyError(
                f"{slug}: no entry in _APERTURES_BY_SLUG. Add the lens's "
                f"(max, stopped) aperture tuple to the table at the top of "
                f"scaffold_ttartisan_tier2.py — eye-read from the chart's "
                f"legend (e.g. `('f/1.4', 'f/5.6')` for an F1.4/F5.6 legend)."
            )
        max_ap, stopped_ap = _APERTURES_BY_SLUG[slug]
        detected = detect_ttartisan_plotbox(chart_path)
        charts.append(
            _ChartFile(
                slug=slug,
                path=chart_path.relative_to(REPO_ROOT),
                max_aperture=max_ap,
                stopped_aperture=stopped_ap,
                detected=detected,
            )
        )
    return charts


# --- Code emission --------------------------------------------------------


def _box_repr(box: tuple[int, int, int, int]) -> str:
    xl, xr, yt, yb = box
    return f"PlotBoxCoords(x_left={xl}, x_right={xr}, y_top={yt}, y_bottom={yb})"


def _chart_path_literal(rel_path: Path) -> str:
    """Forward-slashed path literal for ``chart_path``."""
    return str(rel_path).replace("\\", "/")


def _format_lens_entry(c: _ChartFile) -> str:
    """Emit one ReferenceChart literal for one TTartisan lens."""
    notes = (
        f"Tier 2 production entry (ADR-041, ADR-044). TTartisan publishes "
        f"this chart as the standard 800x600 dual-aperture template; the "
        f"scaffolder classified it as {c.detected.scheme!r} (image height "
        f"{c.detected.image_height_mm} mm). Max aperture {c.max_aperture}, "
        f"stopped aperture {c.stopped_aperture} — eye-read from the chart "
        f"legend per `scaffold_ttartisan_tier2._APERTURES_BY_SLUG`."
    )
    return (
        "    ReferenceChart(\n"
        f'        slug="{c.slug}",\n'
        f'        chart_path="{_chart_path_literal(c.path)}",\n'
        '        style_family="ttartisan-4color-dual-aperture",\n'
        # The aperture tuple positions MUST align with the profile's
        # `apertures_per_chart=("max", "stopped")` — the orchestrator
        # uses the labels positionally.
        f'        apertures=("{c.max_aperture}", "{c.stopped_aperture}"),\n'
        f"        frequencies_lpmm=(10, 30),\n"
        f"        image_height_mm={c.detected.image_height_mm},\n"
        f'        notes=(\n            "{notes}"\n        ),\n'
        f"        plot_box={_box_repr(c.detected.plot_box)},\n"
        "        ground_truth=None,\n"
        "    ),"
    )


def emit_module(charts: list[_ChartFile]) -> str:
    """Render the full ``_ttartisan_tier2_charts.py`` module body."""
    body = "\n".join(_format_lens_entry(c) for c in charts)
    header = (
        '"""Tier 2 ReferenceChart entries for TTartisan lenses (ADR-044).\n\n'
        "Generated by `tools/mtfdigitizer/scripts/scaffold_ttartisan_tier2.py`.\n"
        "Plot box and image-height scheme auto-detected by\n"
        "`ttartisan_plotbox.detect_ttartisan_plotbox`. Per-lens aperture\n"
        "pair (max, stopped) eye-read from each chart's legend and held\n"
        "in `_APERTURES_BY_SLUG` in the scaffolder.\n\n"
        "Do not hand-edit; re-run the scaffolder to update.\n\n"
        f"At time of generation: {len(charts)} lenses, "
        f"{len(charts)} chart images (one per lens).\n"
        '"""\n\n'
        "from __future__ import annotations\n\n"
        "from .charts import PlotBoxCoords, ReferenceChart\n\n\n"
        "TTARTISAN_TIER2_CHARTS: tuple[ReferenceChart, ...] = (\n"
    )
    footer = "\n)\n"
    return header + body + footer


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the scaffolded module to "
        "tools/mtfdigitizer/referenceset/_ttartisan_tier2_charts.py. "
        "Without this flag, the output is printed to stdout for review.",
    )
    args = parser.parse_args(argv)

    charts = _gather_charts()
    if not charts:
        print("No TTartisan lenses found.", file=sys.stderr)
        return 1

    module_source = emit_module(charts)
    target = (
        REPO_ROOT
        / "tools"
        / "mtfdigitizer"
        / "referenceset"
        / "_ttartisan_tier2_charts.py"
    )
    if args.write:
        target.write_text(module_source, encoding="utf-8", newline="\n")
        print(
            f"Wrote {target.relative_to(REPO_ROOT)} ({len(charts)} lenses).",
            file=sys.stderr,
        )
    else:
        print(module_source)
        print(
            f"\n# Preview only — pass --write to update "
            f"{target.relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
