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

from .family_profile import profile_for_chart
from .per_frequency import (
    PER_FREQUENCY_STYLE_FAMILIES,
    extract_per_frequency_chart,
)
from .pipeline import PlotBox, extract_chart, score_chart
from .pipeline.dispatch import parse_field_name
from .pipeline.rendermatch import DEFAULT_DILATION_RADIUS_PX, fields_in
from .pipeline.types import ExtractedChart, SampledReading
from .priors import check_all
from .referenceset.charts import REFERENCE_CHARTS, PlotBoxCoords, ReferenceChart
from .triage import triage


def _to_plotbox(
    coords: PlotBoxCoords,
    y_top_insets: tuple[tuple[str, int], ...] = (),
) -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
        y_top_insets=y_top_insets,
    )


@dataclass(frozen=True)
class EmitResult:
    """What `emit_lens()` produced for one slug.

    For multi-panel zooms (one chart per published focal length per
    ADR-033), `positions_emitted` and `null_counts` aggregate across
    every panel — the totals an operator wants to see when deciding
    whether the emission is healthy.
    """

    slug: str
    ts_literal: str
    positions_emitted: int
    null_counts: dict[str, int]


# Backwards-compat: the canonical-frequency field set, kept for tests
# and callers that referenced the legacy 4-tuple. New code should derive
# the field set from `SampledReading.samples` keys via `fields_in()`.
_FIELDS: tuple[str, ...] = ("freq10S", "freq10M", "freq30S", "freq30M")


def _has_any_data(r: SampledReading) -> bool:
    return any(v is not None for v in r.samples.values())


def _format_value(value: float | None) -> str:
    """Render `0.92` not `0.92000000000001`, or `null` for None.

    Drops trailing zeros after the decimal point so a rounded `0.9` is
    emitted as `0.9`, not `0.90` — `unicorn/no-zero-fractions` lints
    against the latter. A whole-number value renders as `1`.
    """
    if value is None:
        return "null"
    rounded = round(value, 2)
    text = f"{rounded:.2f}".rstrip("0").rstrip(".")
    return text or "0"


def _frequencies_in_reading(r: SampledReading) -> tuple[int, ...]:
    """Sorted (low → high) frequencies referenced by this reading's keys."""
    freqs: set[int] = set()
    for field in r.samples:
        try:
            freq, _sm = parse_field_name(field)
        except ValueError:
            continue
        freqs.add(freq)
    return tuple(sorted(freqs))


def _format_reading(r: SampledReading) -> str:
    """Emit one `MtfReading` row in the ADR-042 samples-record shape.

    Per ADR-042:
    ```
    {
        position: <pos>,
        samples: {
            10: { S: <v>, M: <v> },
            30: { S: <v>, M: <v> },
        },
    }
    ```
    Frequencies are sorted low → high so the output is stable across runs.
    """
    inner: list[str] = []
    for freq in _frequencies_in_reading(r):
        s_val = r.samples.get(f"freq{freq}S")
        m_val = r.samples.get(f"freq{freq}M")
        inner.append(
            f"              {freq}: {{ S: {_format_value(s_val)}, "
            f"M: {_format_value(m_val)} }},"
        )
    samples_block = "\n".join(inner)
    return (
        "          {\n"
        f"            position: {r.position_mm:g},\n"
        "            samples: {\n"
        f"{samples_block}\n"
        "            },\n"
        "          },"
    )


def _format_chart(
    aperture: str,
    paired: tuple[SampledReading, ...],
    focal_length: int | None = None,
    confidence: str = "HIGH",
    confidence_reason: str | None = None,
) -> str:
    readings_block = "\n".join(_format_reading(r) for r in paired)
    focal_line = (
        f"        focalLength: {focal_length},\n"
        if focal_length is not None
        else ""
    )
    # ADR-053 + #1134: per-pass confidence. `confidence` is required on
    # the TS type; `confidenceReason` is set only when LOW (ADR-052
    # reason code from `ChartVerdict.reasons[0]`).
    reason_line = (
        f"        confidenceReason: \"{confidence_reason}\",\n"
        if confidence == "LOW" and confidence_reason
        else ""
    )
    return (
        "      {\n"
        f"        aperture: \"{aperture}\",\n"
        f"{focal_line}"
        f"        confidence: \"{confidence}\",\n"
        f"{reason_line}"
        "        readings: [\n"
        f"{readings_block}\n"
        "        ],\n"
        "      },"
    )


# One emitted chart panel: aperture, optional focal length, readings, and
# per-pass confidence with optional reason code (ADR-053 + #1134).
ChartPanel = tuple[
    str,
    int | None,
    tuple[SampledReading, ...],
    str,
    str | None,
]


def _format_entry(
    slug: str,
    source: str,
    mtf_type: str,
    panels: tuple[ChartPanel, ...],
) -> str:
    chart_blocks = "\n".join(
        _format_chart(
            aperture,
            paired,
            focal_length=focal,
            confidence=confidence,
            confidence_reason=reason,
        )
        for aperture, focal, paired, confidence, reason in panels
    )
    return (
        f"  \"{slug}\": {{\n"
        f"    source: \"{source}\",\n"
        f"    mtfType: \"{mtf_type}\",\n"
        "    charts: [\n"
        f"{chart_blocks}\n"
        "    ],\n"
        "  },"
    )


def _verdict_for_panel(
    image_path: Path,
    profile: object,
    plot_box: PlotBox,
    image_height_mm: float,
    extracted: ExtractedChart,
) -> tuple[str, str | None]:
    """Compute (confidence, reason) for one emitted panel via ADR-052.

    Runs the same render-match + priors as `autotriage._run_pipeline` so
    emit's verdict and the autotriage CLI agree on every panel. Returns
    `("HIGH", None)` when the panel passes the gate, or
    `("LOW", "<first_reason_code>")` when it fails. The first reason is
    the primary one (matches the autotriage CLI display); a panel that
    trips multiple priors collapses to its first reason for the emit
    output. The autotriage CLI run remains the authoritative report
    when the maintainer needs the full reason list.
    """
    score = score_chart(
        image_path,
        profile,  # type: ignore[arg-type]
        plot_box,
        image_height_mm=image_height_mm,
        readings=extracted.readings,
        dilation_radius_px=DEFAULT_DILATION_RADIUS_PX,
    )
    violations = check_all(extracted.readings)
    verdict = triage(score, violations)
    if verdict.verdict == "HIGH":
        return "HIGH", None
    reason_code = verdict.reasons[0].value if verdict.reasons else "unknown"
    return "LOW", reason_code


def emit_lens(
    chart: ReferenceChart,
    source_url: str,
    mtf_type: str = "measured",
    aperture: str | None = None,
    focal_lengths: tuple[int, ...] | None = None,
    repo_root: Path | None = None,
) -> EmitResult:
    """Extract one reference chart and serialize to a TS object literal.

    `source_url` becomes the `source` field on the emitted entry — the
    canonical attribution URL that the lens page renders below the chart.
    `mtf_type` becomes the `mtfType` field — "computed" for manufacturer
    charts derived from optical design (Sigma, Fujifilm, Nikon), "measured"
    for review-lab charts from a tested sample (LensTip, Optical Limits).
    `aperture` overrides the chart's first declared aperture (useful when
    the reference chart declares multiple panels but only the first is
    extracted by the current pipeline).
    `focal_lengths` supplies the mm value to stamp on each emitted chart
    panel — required for zooms (ADR-033 mandates one panel per published
    focal length), omitted for primes. When supplied, its length must
    match `chart.views`; values are zipped in primary-then-additional
    order.
    """
    if chart.plot_box is None:
        raise ValueError(
            f"reference chart {chart.slug!r} has no plot_box — "
            f"emit requires a calibrated or measured plot box"
        )
    if mtf_type not in ("computed", "measured"):
        raise ValueError(
            f"mtf_type must be 'computed' or 'measured', got {mtf_type!r}"
        )
    views = chart.views
    if focal_lengths is not None and len(focal_lengths) != len(views):
        raise ValueError(
            f"focal_lengths length {len(focal_lengths)} does not match "
            f"view count {len(views)} for {chart.slug!r}"
        )
    if len(views) > 1 and focal_lengths is None:
        raise ValueError(
            f"reference chart {chart.slug!r} has {len(views)} views — "
            f"focal_lengths is required to disambiguate panels per ADR-033"
        )
    profile = profile_for_chart(chart)

    root = repo_root or Path(__file__).resolve().parents[2]
    aperture_string = aperture or chart.apertures[0]

    panels: list[ChartPanel] = []
    total_positions = 0
    null_counts: dict[str, int] = {}

    for index, view in enumerate(views):
        if view.plot_box is None:
            raise ValueError(
                f"view {index} of {chart.slug!r} has no plot_box — "
                f"emit requires a calibrated plot box on every view"
            )
        view_plot_box = _to_plotbox(view.plot_box, view.y_top_insets)
        view_image_path = root / view.chart_path
        extracted = extract_chart(
            view_image_path,
            profile,
            view_plot_box,
            image_height_mm=chart.image_height_mm,
        )
        # ADR-053 + #1134: per-pass confidence verdict. emit shares the
        # autotriage gate (ADR-052) — same render-match + priors as
        # `autotriage._run_pipeline`, no new thresholds.
        confidence, reason = _verdict_for_panel(
            view_image_path,
            profile,
            view_plot_box,
            chart.image_height_mm,
            extracted,
        )
        rows = tuple(r for r in extracted.readings if _has_any_data(r))
        focal = focal_lengths[index] if focal_lengths is not None else None
        panels.append((aperture_string, focal, rows, confidence, reason))
        total_positions += len(rows)
        for field in fields_in(extracted.readings):
            null_counts.setdefault(field, 0)
            null_counts[field] += sum(
                1 for r in extracted.readings if r.samples.get(field) is None
            )

    return EmitResult(
        slug=chart.slug,
        ts_literal=_format_entry(
            slug=chart.slug,
            source=source_url,
            mtf_type=mtf_type,
            panels=tuple(panels),
        ),
        positions_emitted=total_positions,
        null_counts=null_counts,
    )


# Mapping from reference chart slug to the source URL the lens page
# should cite. Kept here rather than on ReferenceChart because
# attribution is an emit-step concern, not a calibration concern.
_DEFAULT_SOURCES: dict[str, str] = {
    "sigma-12mm-f1-4-dc-dn-c": (
        "https://www.sigma-global.com/en/lenses/c025_12_14/"
    ),
    "sigma-15mm-f1-4-dc-dn-c": (
        "https://www.sigma-global.com/en/lenses/c026_15_14/"
    ),
    "sigma-23mm-f1-4-dc-dn-c": (
        "https://www.sigma-global.com/en/lenses/c023_23_14/"
    ),
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
    # Sigma zooms — #793. Two-panel diffraction MTF (wide + tele) per
    # ADR-033; see _DEFAULT_FOCAL_LENGTHS below for the mm values.
    "sigma-10-18mm-f2-8-dc-dn-c": (
        "https://www.sigma-global.com/en/lenses/c023_10_28/"
    ),
    "sigma-16-300mm-f3-5-6-7-dc-os-c": (
        "https://www.sigma-global.com/en/lenses/c025_16_300/"
    ),
    "sigma-17-40mm-f1-8-dc-art": (
        "https://www.sigma-global.com/en/lenses/a025_17_40/"
    ),
    "sigma-18-50mm-f2-8-dc-dn-c": (
        "https://www.sigma-global.com/en/lenses/c021_18_50/"
    ),
    "sigma-100-400mm-f5-6-3-dg-dn-os-c": (
        "https://www.sigma-global.com/en/lenses/c020_100_400/"
    ),
}


# Focal length (mm) per emitted panel, in primary-then-additional view
# order. Required for any reference chart with more than one view
# (ADR-033). Primes are not listed here — emit_lens passes
# `focal_lengths=None` for them.
_DEFAULT_FOCAL_LENGTHS: dict[str, tuple[int, ...]] = {
    "sigma-10-18mm-f2-8-dc-dn-c": (10, 18),
    "sigma-16-300mm-f3-5-6-7-dc-os-c": (16, 300),
    "sigma-17-40mm-f1-8-dc-art": (17, 40),
    "sigma-18-50mm-f2-8-dc-dn-c": (18, 50),
    "sigma-100-400mm-f5-6-3-dg-dn-os-c": (100, 400),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "slugs",
        nargs="+",
        help="reference-set lens slug(s) to emit",
    )
    parser.add_argument(
        "--mtf-type",
        choices=("computed", "measured"),
        default="measured",
        help=(
            "MTF provenance for the emitted entries: 'computed' for "
            "manufacturer optical-design charts (Sigma, Fujifilm), "
            "'measured' for review-lab charts (LensTip). Default: measured."
        ),
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
        focal_lengths = _DEFAULT_FOCAL_LENGTHS.get(slug)
        if len(chart.views) > 1 and focal_lengths is None:
            print(
                f"ERROR: {slug!r} has {len(chart.views)} views but no "
                f"_DEFAULT_FOCAL_LENGTHS entry; add one (mm per panel, "
                f"primary first)",
                file=sys.stderr,
            )
            return 1
        result = emit_lens(
            chart,
            source_url=source,
            mtf_type=args.mtf_type,
            focal_lengths=focal_lengths,
        )
        print(result.ts_literal)
        nulls = ", ".join(
            f"{field}={count}" for field, count in result.null_counts.items()
        )
        panel_count = len(chart.views)
        per_panel = 11 * panel_count
        print(
            f"\n# {slug}: emitted {result.positions_emitted}/{per_panel} "
            f"positions across {panel_count} panel(s); "
            f"nulls per field: {nulls}",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
