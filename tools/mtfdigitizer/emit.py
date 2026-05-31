"""Emit extractor readings as a TypeScript literal for src/data/mtf-readings.ts.

The mtfdigitizer pipeline returns `ExtractedChart` Python objects; the
Astro lens page consumes the same data as TypeScript records keyed by
lens slug. This module bridges the two: it serializes one or more
`ExtractedChart` results into a TS `MtfData` object literal that can be
pasted into `src/data/mtf-readings.ts`.

Closes the loop the ADR-038 design called for: digitized readings
become the site's display source of truth, while the committed SVG
under `docs/optical-specs/<slug>/` remains a provenance artifact.

## Null readings

`MtfReading` in `src/types/mtf.ts` declares each OTF field as
`number | null`. The digitizer's `SampledReading` returns `None` for
fields where no usable curve data exists at that column (B2 contract
— never fabricate). The emitter passes those through as TypeScript
`null` literals; the chart renderer breaks its polyline at nulls and
the lens-page table shows an em-dash for null cells.

A position with all four fields null is dropped entirely (no row to
emit). Per-field null counts are reported on stderr so the operator
can see chart-coverage gaps without staring at the diff.

## Usage

    cd tools
    py -m mtfdigitizer.emit <slug>                 # one slug, print to stdout
    py -m mtfdigitizer.emit <slug> <slug> ...      # multiple slugs

Each slug must be present in `referenceset/charts.py` with a populated
`plot_box`. The output prints the lens entry in `mtf-readings.ts` order
— copy-paste into the file, then `npm run check && npm run build` to
verify.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from .pipeline import PlotBox, extract_chart
from .pipeline.types import ExtractedChart, SampledReading
from .profiles import (
    SAMYANG_4COLOR_ALL_SOLID,
    SEVENARTISANS_2COLOR_SAMECOLOR_DASHED,
    SIGMA_2COLOR_SOLID_DASHED,
    TOKINA_2COLOR_FREQUENCY,
    VILTROX_BW_DASHED_F12,
)
from .profiles.types import MtfProfile
from .referenceset.charts import REFERENCE_CHARTS, PlotBoxCoords, ReferenceChart


# Map style_family declared on each reference chart to the runtime
# profile. Centralised so we don't sprinkle per-family lookups across
# the codebase. Kept here rather than `referenceset/` because the
# binding is profile-side, not reference-side.
_FAMILY_TO_PROFILE: dict[str, MtfProfile] = {
    "mainstream-2color-solid-dashed": SIGMA_2COLOR_SOLID_DASHED,
    "mainstream-4color-all-solid": SAMYANG_4COLOR_ALL_SOLID,
    "idealized-flat": SAMYANG_4COLOR_ALL_SOLID,
    "samecolor-dashed-sm": SEVENARTISANS_2COLOR_SAMECOLOR_DASHED,
    "2color-frequency": TOKINA_2COLOR_FREQUENCY,
    "bw-dashed-promo": VILTROX_BW_DASHED_F12,
}


def _to_plotbox(coords: PlotBoxCoords) -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
    )


@dataclass(frozen=True)
class EmitResult:
    """What `emit_lens()` produced for one slug."""

    slug: str
    ts_literal: str
    positions_emitted: int
    null_counts: dict[str, int]


_FIELDS: tuple[str, ...] = (
    "contrast10S",
    "contrast10M",
    "resolution30S",
    "resolution30M",
)


def _has_any_data(r: SampledReading) -> bool:
    return any(getattr(r, field) is not None for field in _FIELDS)


def _format_value(value: float | None) -> str:
    """Render `0.92` not `0.92000000000001`, or `null` for None."""
    if value is None:
        return "null"
    return f"{round(value, 2):.2f}"


def _format_reading(r: SampledReading) -> str:
    return (
        "          {\n"
        f"            position: {r.position_mm:g},\n"
        f"            contrast10S: {_format_value(r.contrast10S)},\n"
        f"            contrast10M: {_format_value(r.contrast10M)},\n"
        f"            resolution30S: {_format_value(r.resolution30S)},\n"
        f"            resolution30M: {_format_value(r.resolution30M)},\n"
        "          },"
    )


def _format_chart(
    aperture: str, paired: tuple[SampledReading, ...]
) -> str:
    readings_block = "\n".join(_format_reading(r) for r in paired)
    return (
        "      {\n"
        f"        aperture: \"{aperture}\",\n"
        "        readings: [\n"
        f"{readings_block}\n"
        "        ],\n"
        "      },"
    )


def _format_entry(
    slug: str,
    source: str,
    aperture: str,
    paired: tuple[SampledReading, ...],
) -> str:
    chart_block = _format_chart(aperture, paired)
    return (
        f"  \"{slug}\": {{\n"
        f"    source: \"{source}\",\n"
        "    mtfType: \"measured\",\n"
        "    charts: [\n"
        f"{chart_block}\n"
        "    ],\n"
        "  },"
    )


def emit_lens(
    chart: ReferenceChart,
    source_url: str,
    aperture: str | None = None,
    repo_root: Path | None = None,
) -> EmitResult:
    """Extract one reference chart and serialize to a TS object literal.

    `source_url` becomes the `source` field on the emitted entry — the
    canonical attribution URL that the lens page renders below the chart.
    `aperture` overrides the chart's first declared aperture (useful when
    the reference chart declares multiple panels but only the first is
    extracted by the current pipeline).
    """
    if chart.plot_box is None or chart.ground_truth is None:
        raise ValueError(
            f"reference chart {chart.slug!r} has no plot_box or ground_truth — "
            f"emit only supports charts that calibrate"
        )
    profile = _FAMILY_TO_PROFILE.get(chart.style_family)
    if profile is None:
        raise ValueError(
            f"no runtime profile mapped for style_family {chart.style_family!r}"
        )

    root = repo_root or Path(__file__).resolve().parents[2]
    extracted: ExtractedChart = extract_chart(
        root / chart.chart_path,
        profile,
        _to_plotbox(chart.plot_box),
        image_height_mm=chart.image_height_mm,
    )

    rows = tuple(r for r in extracted.readings if _has_any_data(r))
    null_counts = {
        field: sum(1 for r in extracted.readings if getattr(r, field) is None)
        for field in _FIELDS
    }

    return EmitResult(
        slug=chart.slug,
        ts_literal=_format_entry(
            slug=chart.slug,
            source=source_url,
            aperture=aperture or chart.apertures[0],
            paired=rows,
        ),
        positions_emitted=len(rows),
        null_counts=null_counts,
    )


# Mapping from reference chart slug to the source URL the lens page
# should cite. Kept here rather than on ReferenceChart because
# attribution is an emit-step concern, not a calibration concern.
_DEFAULT_SOURCES: dict[str, str] = {
    "sigma-56mm-f1-4-dc-dn-c": (
        "https://www.sigma-global.com/en/lenses/c018_56_14/"
    ),
    "samyang-85mm-f1-4-as-if-umc": (
        "https://www.lksamyang.com/en/product/product-view.php?seq=311"
    ),
    "samyang-300mm-f6-3-ed-umc-cs-reflex": (
        "https://www.lksamyang.com/en/product/product-view.php?seq=355"
    ),
    "viltrox-af-75mm-f1-2-pro": (
        "https://viltrox.com/products/75mm-f12-xf-lens"
    ),
    "tokina-atx-m-23mm-f1-4-x": (
        "https://www.lenstip.com/665.1-Lens_review-Tokina_atx-m_23_mm_f_1.4_X-Introduction.html"
    ),
    "tokina-atx-m-33mm-f1-4-x": (
        "https://tokinalens.com/product/atx_m_33mm_f1_4_x/"
    ),
    "tokina-atx-m-56mm-f1-4-x": (
        "https://tokinalens.com/product/atx_m_56mm_f1_4_x/"
    ),
    "tokina-atx-m-11-18mm-f2-8-x-at-11mm": (
        "https://tokinalens.com/product/atx_m_11_18mm_f2_8_x/"
    ),
    "tokina-atx-m-11-18mm-f2-8-x-at-18mm": (
        "https://tokinalens.com/product/atx_m_11_18mm_f2_8_x/"
    ),
    "7artisans-50mm-f1-2-mark-ii": (
        "https://7artisans.store/products/7artisans-50mm-f-1-2-mark-ii-prime-lens"
    ),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "slugs",
        nargs="+",
        help="reference-set lens slug(s) to emit",
    )
    args = parser.parse_args(argv)

    chart_by_slug = {c.slug: c for c in REFERENCE_CHARTS}

    for slug in args.slugs:
        chart = chart_by_slug.get(slug)
        if chart is None:
            print(f"ERROR: unknown slug {slug!r}", file=sys.stderr)
            return 1
        source = _DEFAULT_SOURCES.get(slug)
        if source is None:
            print(
                f"ERROR: no default source URL for {slug!r}; "
                f"add to _DEFAULT_SOURCES",
                file=sys.stderr,
            )
            return 1
        result = emit_lens(chart, source_url=source)
        print(result.ts_literal)
        nulls = ", ".join(
            f"{field}={count}" for field, count in result.null_counts.items()
        )
        print(
            f"\n# {slug}: emitted {result.positions_emitted}/11 positions; "
            f"nulls per field: {nulls}",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
