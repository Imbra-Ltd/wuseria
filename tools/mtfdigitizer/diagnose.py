"""Per-stage diagnostic bundle CLI (ADR-050).

Runs the extractor on one slug or a brand cohort, writing one
per-pipeline-stage artifact per chart to `<slug>/diagnostic/` (or
`<slug>/diagnostic/<aperture>/` for multi-aperture charts).

The diagnostic bundle is gitignored — regenerate on demand when a
chart looks wrong. The artifacts identify *which* stage broke; they
do not fix the failure (ADR-050 "What this does not do").

Usage::

    cd tools
    py -m mtfdigitizer.diagnose <slug>                 # one chart
    py -m mtfdigitizer.diagnose --brand ttartisan      # whole brand cohort
    py -m mtfdigitizer.diagnose --all                  # whole corpus (slow)

Output layout::

    docs/optical-specs/<slug>/diagnostic/
        # single-aperture:
        01-source.png ... 09-emit.svg + manifest.json
        # multi-aperture (per ADR-044):
        max/01-source.png ... 09-emit.svg + manifest.json
        stopped/01-source.png ...
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .aperture_passes import aperture_passes_for_view
from .diagnostic import FileDiagnosticSink
from .pipeline import extract_chart
from .pipeline.types import PlotBox
from .referenceset import REFERENCE_CHARTS
from .referenceset.charts import PlotBoxCoords, ReferenceChart
from .svg import render_svg


REPO_ROOT = Path(__file__).resolve().parents[2]


def _to_plotbox(coords: PlotBoxCoords) -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
    )


def _diagnose_chart(chart: ReferenceChart) -> list[Path]:
    """Write the diagnostic bundle for one reference chart.

    Multi-aperture charts get one subdirectory per aperture pass;
    single-aperture charts write directly to `diagnostic/`. Returns
    the list of bundle directories written.
    """
    if chart.plot_box is None:
        return []
    image_path = REPO_ROOT / chart.chart_path
    if not image_path.exists():
        return []
    plot_box = _to_plotbox(chart.plot_box)
    passes = aperture_passes_for_view(chart, image_path)
    multi = len(passes) > 1
    lens_dir = (REPO_ROOT / "docs" / "optical-specs" / chart.slug / "diagnostic")
    written: list[Path] = []
    for aperture, profile in passes:
        # Aperture labels contain `/` (e.g. `f/2.8`) — replace for path safety.
        safe_aperture = aperture.replace("/", "-").replace(" ", "")
        out_dir = lens_dir / safe_aperture if multi else lens_dir
        sink = FileDiagnosticSink(out_dir=out_dir)
        extracted = extract_chart(
            image_path,
            profile,
            plot_box,
            image_height_mm=chart.image_height_mm,
            diagnostic_sink=sink,
        )
        svg = render_svg(extracted)
        sink.record_emit(svg)
        sink.record_manifest(
            {
                "slug": chart.slug,
                "chart_path": chart.chart_path,
                "aperture": aperture,
                "profile": profile.name,
                "style_family": chart.style_family,
                "plot_box": {
                    "x_left": plot_box.x_left,
                    "x_right": plot_box.x_right,
                    "y_top": plot_box.y_top,
                    "y_bottom": plot_box.y_bottom,
                },
                "image_height_mm": chart.image_height_mm,
                "frequencies_lpmm": list(chart.frequencies_lpmm),
                "sister_fallback_count": extracted.sister_fallback_count,
                "samples": {
                    field: [r.samples.get(field) for r in extracted.readings]
                    for field in sorted(
                        {f for r in extracted.readings for f in r.samples}
                    )
                },
            }
        )
        written.append(out_dir)
    return written


def _charts_for_brand(brand: str) -> list[ReferenceChart]:
    prefix = f"{brand}-"
    return [c for c in REFERENCE_CHARTS if c.slug.startswith(prefix)]


def _chart_by_slug(slug: str) -> ReferenceChart | None:
    for c in REFERENCE_CHARTS:
        if c.slug == slug:
            return c
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("slug", nargs="?", help="Lens slug to diagnose.")
    group.add_argument("--brand", help="Diagnose every chart whose slug starts with `<brand>-`.")
    group.add_argument("--all", action="store_true", help="Diagnose every runnable chart.")
    args = parser.parse_args(argv)

    if args.slug:
        chart = _chart_by_slug(args.slug)
        if chart is None:
            print(f"No reference chart for slug {args.slug!r}.")
            return 1
        charts = [chart]
    elif args.brand:
        charts = _charts_for_brand(args.brand)
        if not charts:
            print(f"No reference charts for brand {args.brand!r}.")
            return 1
    else:
        charts = [c for c in REFERENCE_CHARTS if c.plot_box]

    print(f"Diagnosing {len(charts)} chart(s).")
    total = 0
    for chart in charts:
        written = _diagnose_chart(chart)
        for out_dir in written:
            relative = out_dir.relative_to(REPO_ROOT)
            print(f"  {chart.slug:<40}  -> {relative}")
            total += 1
    print(f"\nWrote {total} bundle(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
