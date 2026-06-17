"""Scaffold Tier 2 ReferenceChart entries for every Fujifilm lens that
has MTF chart images, by auto-detecting each chart's plot box.

Walks `docs/optical-specs/fujifilm-*` folders, calls
`fuji_plotbox.detect_fuji_plotbox` on each `-NNlp.png` file, groups
charts by lens, and writes a `_fuji_tier2_charts.py` module that
declares one `ReferenceChart` per lens with:

- `style_family="fujifilm-permfreq"`
- `plot_box` from the primary view (typically the lowest-frequency
  chart — same image dimensions as the rest within a lens)
- `additional_views` for the remaining frequencies (and wide+tele
  for zooms — detected by the `-wide-` / `-tele-` filename suffix)
- `ground_truth=None` (Tier 2 per ADR-041)

Lens-level metadata that the scaffolder cannot infer from the chart
PNG alone — `image_height_mm`, `apertures`, `frequencies_lpmm` — is
populated from the detector output and filename parsing.

Usage::

    cd tools
    py -m mtfdigitizer.scripts.scaffold_fuji_tier2          # preview to stdout
    py -m mtfdigitizer.scripts.scaffold_fuji_tier2 --write   # write to the module

The generated module imports the same `ReferenceChart` /
`PlotBoxCoords` / `ChartView` types as the curated `charts.py`, so the
existing extractor reads it via a small import added to `charts.py`'s
top-level `REFERENCE_CHARTS` concatenation.

Per ADR-041 Tier 2: no per-lens ground truth, no eye-read by the
maintainer for these entries. Production runs gate on render-match +
plausibility priors + the maintainer overlay glance per chart.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from mtfdigitizer.fuji_plotbox import detect_fuji_plotbox, FujiBoxResult


REPO_ROOT = Path(__file__).resolve().parents[3]
OPTICAL_SPECS_DIR = REPO_ROOT / "docs" / "optical-specs"


_LP_FILENAME = re.compile(
    r"^(?P<stem>fujifilm-.+?)(?:-(?P<view>wide|tele))?-(?P<freq>\d+)lp\.png$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class _ChartFile:
    """One detected chart image's metadata."""

    path: Path  # relative to repo root
    view: str | None  # "wide" / "tele" / None for primes
    freq: int
    detected: FujiBoxResult


def _gather_charts(lens_dir: Path) -> list[_ChartFile]:
    """Find every MTF chart image in a lens folder + run the detector."""
    charts: list[_ChartFile] = []
    for p in sorted(lens_dir.glob("*lp.png")):
        m = _LP_FILENAME.match(p.name)
        if m is None:
            continue
        res = detect_fuji_plotbox(p)
        if res is None or res.plot_box == (0, 0, 0, 0):
            # Detector rejected — surface the rejection but skip.
            print(
                f"SKIP {p.relative_to(REPO_ROOT)}: detection failed "
                f"({'; '.join(res.notes) if res else 'unreadable'})",
                file=sys.stderr,
            )
            continue
        charts.append(
            _ChartFile(
                path=p.relative_to(REPO_ROOT),
                view=m.group("view"),
                freq=int(m.group("freq")),
                detected=res,
            )
        )
    return charts


# --- Code emission --------------------------------------------------------


def _box_repr(box: tuple[int, int, int, int]) -> str:
    xl, xr, yt, yb = box
    return f"PlotBoxCoords(x_left={xl}, x_right={xr}, y_top={yt}, y_bottom={yb})"


def _chart_path_literal(rel_path: Path) -> str:
    """Forward-slashed path literal for `chart_path`."""
    return str(rel_path).replace("\\", "/")


def _format_view(c: _ChartFile, indent: str = "            ") -> str:
    return (
        f"{indent}ChartView(\n"
        f'{indent}    chart_path="{_chart_path_literal(c.path)}",\n'
        f"{indent}    plot_box={_box_repr(c.detected.plot_box)},\n"
        f"{indent}),"
    )


def _format_lens_entry(slug: str, charts: list[_ChartFile]) -> str:
    """Emit one ReferenceChart literal for one Fujifilm lens."""
    primary = charts[0]
    extras = charts[1:]
    frequencies = sorted({c.freq for c in charts})

    notes = (
        f"Tier 2 production entry (ADR-041) scaffolded by "
        f"`scaffold_fuji_tier2`; plot box auto-detected by "
        f"`fuji_plotbox.detect_fuji_plotbox`. Per-image image_height_mm "
        f"is constant within a lens; calibration via the "
        f"{_mount_label(slug)} mount default."
    )
    additional = "".join(
        f"\n{_format_view(c)}" for c in extras
    )
    return (
        "    ReferenceChart(\n"
        f'        slug="{slug}",\n'
        f'        chart_path="{_chart_path_literal(primary.path)}",\n'
        '        style_family="fujifilm-permfreq",\n'
        '        apertures=("max",),\n'
        f"        frequencies_lpmm={tuple(frequencies)},\n"
        f"        image_height_mm={primary.detected.image_height_mm},\n"
        f'        notes=(\n            "{notes}"\n        ),\n'
        f"        plot_box={_box_repr(primary.detected.plot_box)},\n"
        "        ground_truth=None,\n"
        "        additional_views=("
        + (additional + "\n        " if extras else "")
        + "),\n"
        "    ),"
    )


def _mount_label(slug: str) -> str:
    if slug.startswith("fujifilm-gf-"):
        return "GF"
    if slug.startswith("fujifilm-xf-"):
        return "XF"
    if slug.startswith("fujifilm-mkx-"):
        return "MKX"
    if slug.startswith("fujifilm-xc-"):
        return "XC"
    return "Fujifilm"


# --- Top-level emitter ----------------------------------------------------


def collect_lens_groups() -> dict[str, list[_ChartFile]]:
    """Walk every Fujifilm lens folder; map slug → detected chart files."""
    groups: dict[str, list[_ChartFile]] = {}
    skip_slugs = {
        # Tier 1 anchors live in `charts.py` proper; the scaffolder
        # never emits a duplicate entry for them.
        "fujifilm-gf-23mm-f4-r-lm-wr",
        "fujifilm-xf-23mm-f1-4-r-lm-wr",
    }
    for lens_dir in sorted(OPTICAL_SPECS_DIR.iterdir()):
        if not lens_dir.is_dir():
            continue
        if not lens_dir.name.startswith("fujifilm-"):
            continue
        if lens_dir.name in skip_slugs:
            continue
        charts = _gather_charts(lens_dir)
        if not charts:
            continue
        groups[lens_dir.name] = charts
    return groups


def emit_module(groups: dict[str, list[_ChartFile]]) -> str:
    """Render the full _fuji_tier2_charts.py module body."""
    body_entries = "\n".join(
        _format_lens_entry(slug, charts) for slug, charts in groups.items()
    )
    lens_count = len(groups)
    chart_count = sum(len(v) for v in groups.values())
    header = (
        '"""Tier 2 ReferenceChart entries for Fujifilm lenses.\n\n'
        "Generated by `tools/mtfdigitizer/scripts/scaffold_fuji_tier2.py`.\n"
        "Plot boxes auto-detected by `fuji_plotbox.detect_fuji_plotbox`.\n"
        "Do not hand-edit; re-run the scaffolder to update.\n\n"
        f"At time of generation: {lens_count} lenses, {chart_count} chart images.\n"
        '"""\n\n'
        "from __future__ import annotations\n\n"
        "from .charts import ChartView, PlotBoxCoords, ReferenceChart\n\n\n"
        "FUJI_TIER2_CHARTS: tuple[ReferenceChart, ...] = (\n"
    )
    footer = "\n)\n"
    # Strip the trailing comma's outer indentation and re-indent each
    # literal under the tuple.
    indented = body_entries
    return header + indented + footer


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the scaffolded module to "
        "tools/mtfdigitizer/referenceset/_fuji_tier2_charts.py. "
        "Without this flag, the output is printed to stdout for review.",
    )
    args = parser.parse_args(argv)

    groups = collect_lens_groups()
    if not groups:
        print("No Fujifilm Tier 2 lenses found.", file=sys.stderr)
        return 1

    module_source = emit_module(groups)

    target = (
        REPO_ROOT / "tools" / "mtfdigitizer" / "referenceset"
        / "_fuji_tier2_charts.py"
    )
    if args.write:
        target.write_text(module_source, encoding="utf-8", newline="\n")
        chart_count = sum(len(v) for v in groups.values())
        print(
            f"Wrote {target.relative_to(REPO_ROOT)} "
            f"({len(groups)} lenses, {chart_count} charts).",
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
