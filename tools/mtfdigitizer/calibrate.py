"""Reference-set calibration runner (#953, ADR-038 §4).

Runs `extract_chart()` against every reference chart that has both
ground truth and a plot box, and reports the per-position offset (Δ)
distribution against the eye-read values.

This delivers the **offset distribution** half of the calibration
defined in `referenceset/REFERENCE_SET.md` §"What 'calibration against
the set' actually means". The other half — render-match IoU — needs the
confidence signal sub-task to land first; this runner is silent on it.

Usage::

    cd tools
    py -m mtfdigitizer.calibrate
    py -m mtfdigitizer.calibrate --write-readings

The default invocation prints a per-chart Δ table on stdout and an
aggregate summary. ``--write-readings`` additionally writes one
markdown file per chart under ``referenceset/readings/<slug>.md`` with
the full GT-vs-extracted-vs-Δ grid. Diff those files after an
algorithm change to see exactly what moved.
"""

from __future__ import annotations

import argparse
import dataclasses
import re
import statistics
from dataclasses import dataclass
from pathlib import Path

from .family_profile import profile_for_chart
from .pipeline import PlotBox, SampledReading, extract_chart
from .pipeline.sampling import SAMPLE_FRACTIONS
from .referenceset.charts import REFERENCE_CHARTS, PlotBoxCoords, ReferenceChart


REPO_ROOT = Path(__file__).resolve().parents[2]


# Style families whose lenses publish one chart image per spatial
# frequency. The calibration runner extracts every view and merges
# the per-frequency readings into one tuple keyed by sample position.
_PER_FREQUENCY_STYLE_FAMILIES: frozenset[str] = frozenset({"fujifilm-permfreq"})

# Mirror of `extract._FUJI_FREQ_RE`: per-frequency filename suffix.
_FUJI_FREQ_RE = re.compile(r"-(?P<freq>\d+)lp\.png$", re.IGNORECASE)


# Per-aperture result type for multi-aperture charts (ADR-044). When a
# chart's profile declares `apertures_per_chart=(...)`, the calibrator
# runs the extractor once per aperture and returns a dict keyed by the
# orchestrator's aperture label (`"max"` / `"stopped"` for TTartisan).
# Ground-truth lookups are then keyed by the SAME label — the chart's
# `ground_truth` dict for a multi-aperture chart MUST use the
# orchestrator's aperture labels, not f-numbers. Single-aperture charts
# continue to return a single `ExtractedChart` and ground-truth uses
# the lens's f-number label as it always has.


@dataclass(frozen=True)
class FieldDelta:
    """One field's Δ stats across the 11 sample positions of one chart."""

    chart_slug: str
    aperture: str
    field: str
    deltas: tuple[float, ...]  # |extracted - gt| for positions where both exist
    gt_value_count: int  # positions where ground truth is not None
    extracted_none_count: int  # positions where extractor returned None
    paired_count: int  # positions where both sides had a value

    @property
    def median_abs_delta(self) -> float | None:
        return statistics.median(self.deltas) if self.deltas else None

    @property
    def p95_abs_delta(self) -> float | None:
        if not self.deltas:
            return None
        # statistics.quantiles needs ≥ 2 points; for fewer, return the max.
        if len(self.deltas) < 2:
            return self.deltas[0]
        return statistics.quantiles(self.deltas, n=20)[-1]  # 95th percentile


def _to_plotbox(coords: PlotBoxCoords) -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
    )


def _extracted_value(reading: SampledReading, field: str) -> float | None:
    return reading.samples.get(field)


def _compare_field(
    chart: ReferenceChart,
    aperture: str,
    field: str,
    extracted: tuple[SampledReading, ...],
    ground_truth: tuple[float | None, ...],
) -> FieldDelta:
    deltas: list[float] = []
    gt_value_count = 0
    extracted_none_count = 0
    paired_count = 0
    for reading, gt in zip(extracted, ground_truth):
        ext = _extracted_value(reading, field)
        if gt is not None:
            gt_value_count += 1
        if ext is None:
            extracted_none_count += 1
        if gt is not None and ext is not None:
            deltas.append(abs(ext - gt))
            paired_count += 1
    return FieldDelta(
        chart_slug=chart.slug,
        aperture=aperture,
        field=field,
        deltas=tuple(deltas),
        gt_value_count=gt_value_count,
        extracted_none_count=extracted_none_count,
        paired_count=paired_count,
    )


def _parse_filename_frequency(image_path: Path) -> int:
    """Parse spatial frequency from a per-frequency Fuji filename.

    Mirrors `extract._parse_filename_frequency`. Raises if the filename
    does not match the `-<N>lp.png` convention.
    """
    m = _FUJI_FREQ_RE.search(image_path.name)
    if m is None:
        raise ValueError(
            f"per-frequency chart filename must end in `-<N>lp.png`; "
            f"got {image_path.name!r}"
        )
    return int(m.group("freq"))


def _extract_per_frequency_chart(chart: ReferenceChart):
    """Walk every view of a per-frequency lens; merge per-position readings.

    Each Fujifilm-style chart publishes one image per spatial frequency.
    For each view, we substitute the parsed frequency into the declared
    profile (which carries `frequencies_lpmm=(0,)` as a sentinel), run
    `extract_chart`, then merge the per-view sample dicts at each
    position so one `SampledReading` row carries all frequencies'
    `freq{N}S` / `freq{N}M` keys.
    """
    assert chart.plot_box is not None
    base_profile = profile_for_chart(chart)

    merged_samples: dict[float, dict[str, float | None]] = {}
    last_result = None
    for view in chart.views:
        assert view.plot_box is not None
        image_path = REPO_ROOT / view.chart_path
        freq = _parse_filename_frequency(image_path)
        profile = dataclasses.replace(base_profile, frequencies_lpmm=(freq,))
        plot_box = _to_plotbox(view.plot_box)
        result = extract_chart(
            image_path, profile, plot_box,
            image_height_mm=chart.image_height_mm,
        )
        last_result = result
        for reading in result.readings:
            merged = merged_samples.setdefault(reading.position_mm, {})
            merged.update(reading.samples)

    # Rebuild a single readings tuple with the merged samples per position.
    merged_readings = tuple(
        SampledReading(position_mm=pos, samples=merged_samples[pos])
        for pos in sorted(merged_samples.keys())
    )
    # Reuse the last result's ExtractedChart structure (the source_path
    # and profile_name reflect the final view; the readings are the
    # merged set).
    assert last_result is not None
    return dataclasses.replace(last_result, readings=merged_readings)


def _extract_multi_aperture_chart(chart: ReferenceChart) -> dict[str, "object"]:
    """Run the extractor once per declared aperture and return a per-
    aperture result dict (ADR-044).

    The profile's `apertures_per_chart` lists the orchestrator-side
    aperture labels (`"max"` / `"stopped"` for TTartisan). For each
    label, the profile's hues are filtered to only those whose name
    starts with `f"{label}-"`, then the extractor runs against the
    full chart raster using that filtered profile. The result is
    aperture-tagged so downstream code can compare against
    `chart.ground_truth[label]`.

    Returns ``{aperture_label: ExtractedChart}``. Single-aperture
    charts use the existing single-result path in `_calibrate_chart`
    and never call this.
    """
    from .extract import _hue_filtered_profile  # noqa: PLC0415 — avoid cycle at import
    from .aperture_passes import _apply_sm_swap_override  # noqa: PLC0415 — avoid cycle at import

    assert chart.plot_box is not None
    base_profile = profile_for_chart(chart)
    assert base_profile.apertures_per_chart is not None, (
        f"{chart.slug}: _extract_multi_aperture_chart called on a profile "
        f"without apertures_per_chart declared"
    )
    image_path = REPO_ROOT / chart.chart_path
    plot_box = _to_plotbox(chart.plot_box)

    results: dict[str, object] = {}
    for aperture in base_profile.apertures_per_chart:
        filtered = _hue_filtered_profile(base_profile, aperture)
        # Per-lens S/M swap override (#1199). Same override application
        # as `aperture_passes_for_view` so calibration and production
        # extraction agree on label assignment.
        filtered = _apply_sm_swap_override(filtered, chart.sm_swap_per_hue)
        results[aperture] = extract_chart(
            image_path,
            filtered,
            plot_box,
            image_height_mm=chart.image_height_mm,
        )
    return results


def _calibrate_chart(chart: ReferenceChart):
    """Run extract_chart on one reference chart and return per-field stats.

    The chart must carry both `plot_box` and `ground_truth`; the caller
    filters runnable charts.

    Three dispatch shapes:

    - **Per-frequency** (Fujifilm; ADR-043): walk every chart view,
      substitute the filename frequency into the profile per call, and
      merge per-position readings into one tuple before the GT
      comparison. Result is a single `ExtractedChart`.
    - **Multi-aperture** (TTartisan; ADR-044): run the extractor once
      per declared aperture with the profile's hues filtered to that
      aperture's bucket. Result is a `dict[aperture_label, ExtractedChart]`
      so GT comparison can index per aperture without colliding
      `freq{N}S/M` field names across passes.
    - **Standard** (everything else): single `extract_chart` call on
      the primary view.

    Returns ``(field_deltas, result)`` where ``result`` is the shape
    appropriate to the chart — single `ExtractedChart` for standard +
    per-frequency dispatches, dict for multi-aperture.
    """
    assert chart.plot_box is not None
    assert chart.ground_truth is not None

    base_profile = profile_for_chart(chart)
    if base_profile.apertures_per_chart is not None:
        results_by_aperture = _extract_multi_aperture_chart(chart)
        out: list[FieldDelta] = []
        for aperture, gt_by_field in chart.ground_truth.items():
            if aperture not in results_by_aperture:
                # GT carries an aperture key the profile didn't declare.
                # Fail-loud: a typo here masks a missing extractor pass.
                raise KeyError(
                    f"{chart.slug}: ground_truth aperture {aperture!r} not "
                    f"in profile.apertures_per_chart "
                    f"{base_profile.apertures_per_chart!r}"
                )
            result = results_by_aperture[aperture]
            for field, gt_values in gt_by_field.items():
                out.append(
                    _compare_field(
                        chart, aperture, field, result.readings, gt_values
                    )
                )
        return out, results_by_aperture

    if chart.style_family in _PER_FREQUENCY_STYLE_FAMILIES:
        result = _extract_per_frequency_chart(chart)
    else:
        from .aperture_passes import _apply_sm_swap_override  # noqa: PLC0415
        profile = _apply_sm_swap_override(base_profile, chart.sm_swap_per_hue)
        image_path = REPO_ROOT / chart.chart_path
        plot_box = _to_plotbox(chart.plot_box)
        result = extract_chart(
            image_path, profile, plot_box,
            image_height_mm=chart.image_height_mm,
        )

    out = []
    # The ground truth dict may carry multiple apertures; the extractor
    # was given a single plot box (MAX panel today), so only compare the
    # apertures that match. In practice a single key today.
    for aperture, fields in chart.ground_truth.items():
        for field, gt_values in fields.items():
            out.append(_compare_field(chart, aperture, field, result.readings, gt_values))
    return out, result


def _format_field_row(delta: FieldDelta) -> str:
    med = delta.median_abs_delta
    p95 = delta.p95_abs_delta
    med_s = f"{med:.3f}" if med is not None else "  -  "
    p95_s = f"{p95:.3f}" if p95 is not None else "  -  "
    return (
        f"  {delta.field:<14}  med |d| {med_s}  p95 |d| {p95_s}  "
        f"paired {delta.paired_count:2d}/11  "
        f"ext-None {delta.extracted_none_count:2d}"
    )


READINGS_DIR = REPO_ROOT / "tools" / "mtfdigitizer" / "referenceset" / "readings"


def _readings_for_aperture(result, aperture: str):
    """Resolve the readings tuple to use when comparing one aperture.

    For multi-aperture charts (ADR-044) the result is a
    ``dict[aperture_label, ExtractedChart]`` and we pick the matching
    entry. For single-aperture charts the result is a single
    ``ExtractedChart`` and we use its readings regardless of aperture
    — the chart's `ground_truth` carries one aperture key.
    """
    if isinstance(result, dict):
        return result[aperture].readings
    return result.readings


def _write_readings_log(chart: ReferenceChart, result, field_deltas: list[FieldDelta]) -> Path:
    """Write a markdown grid of GT vs extracted vs Δ for one chart.

    The file lives at ``referenceset/readings/<slug>.md`` and is meant
    to be diffed across algorithm changes — every row is a single
    sample fraction, every column is a curve/field, and the Δ column
    shows the per-position error against the eye-read ground truth.

    For multi-aperture charts the result is a per-aperture dict; this
    function picks the matching aperture's readings when filling each
    section's grid (per ADR-044).
    """
    READINGS_DIR.mkdir(parents=True, exist_ok=True)
    path = READINGS_DIR / f"{chart.slug}.md"
    fields = ("freq10S", "freq10M", "freq30S", "freq30M")
    lines: list[str] = []
    lines.append(f"# {chart.slug}")
    lines.append("")
    lines.append(f"- **Style family:** `{chart.style_family}`")
    lines.append(f"- **Chart path:** `{chart.chart_path}`")
    lines.append(
        f"- **Plot box:** x=[{chart.plot_box.x_left}, {chart.plot_box.x_right}], "
        f"y=[{chart.plot_box.y_top}, {chart.plot_box.y_bottom}]"
    )
    lines.append(f"- **Image height:** {chart.image_height_mm} mm")
    lines.append("")

    # Per-aperture grids. Single-aperture charts hit this loop once;
    # multi-aperture charts (ADR-044) hit it once per declared aperture
    # and index `result` per aperture to pull the right pass's readings.
    for aperture, gt_by_field in chart.ground_truth.items():
        readings = _readings_for_aperture(result, aperture)
        lines.append(f"## Aperture {aperture}")
        lines.append("")
        # Per-field stats table
        lines.append("| Field          | paired | med \\|Δ\\| | p95 \\|Δ\\| |")
        lines.append("| -------------- | ------ | --------- | --------- |")
        for fd in field_deltas:
            if fd.aperture != aperture:
                continue
            med = (
                f"{fd.median_abs_delta:.3f}"
                if fd.median_abs_delta is not None
                else "—"
            )
            p95 = (
                f"{fd.p95_abs_delta:.3f}"
                if fd.p95_abs_delta is not None
                else "—"
            )
            lines.append(
                f"| {fd.field:<14} | {fd.paired_count:>2}/11  | {med:>9} | {p95:>9} |"
            )
        lines.append("")

        # Grid: rows = sample fractions, columns = (GT, EX, Δ) per field
        header_parts = ["frac"]
        for f in fields:
            header_parts.extend([f"{f} GT", f"{f} EX", f"{f} Δ"])
        lines.append("| " + " | ".join(header_parts) + " |")
        lines.append("| " + " | ".join(["---"] * len(header_parts)) + " |")
        for i, frac in enumerate(SAMPLE_FRACTIONS):
            row = [f"{frac:.1f}"]
            for f in fields:
                gt_vals = gt_by_field.get(f, (None,) * 11)
                gt = gt_vals[i] if i < len(gt_vals) else None
                ex = _extracted_value(readings[i], f)
                if gt is not None and ex is not None:
                    delta = f"{abs(ex - gt):.3f}"
                else:
                    delta = "—"
                row.extend([
                    f"{gt:.2f}" if gt is not None else "—",
                    f"{ex:.2f}" if ex is not None else "—",
                    delta,
                ])
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--write-readings",
        action="store_true",
        help="Additionally write per-chart markdown grids to "
        "referenceset/readings/<slug>.md",
    )
    args = parser.parse_args()

    runnable = [
        c for c in REFERENCE_CHARTS if c.plot_box and c.ground_truth
    ]
    print(f"Calibrating {len(runnable)} of {len(REFERENCE_CHARTS)} reference charts.")
    print(f"Sample fractions: {SAMPLE_FRACTIONS}")
    if args.write_readings:
        print(f"Writing per-chart readings to {READINGS_DIR.relative_to(REPO_ROOT)}/")
    print()

    all_deltas: list[float] = []
    for chart in runnable:
        print(f"## {chart.slug} ({chart.style_family})")
        field_deltas, result = _calibrate_chart(chart)
        for fd in field_deltas:
            print(_format_field_row(fd))
            all_deltas.extend(fd.deltas)
        if args.write_readings:
            _write_readings_log(chart, result, field_deltas)
        print()

    if not all_deltas:
        print("No paired comparisons — nothing to summarize.")
        return

    median = statistics.median(all_deltas)
    p95 = (
        statistics.quantiles(all_deltas, n=20)[-1]
        if len(all_deltas) >= 2
        else all_deltas[0]
    )
    print("## Aggregate (all charts, all fields)")
    print(f"  paired comparisons:    {len(all_deltas)}")
    print(f"  median |d|:           {median:.4f}")
    print(f"  p95 |d|:              {p95:.4f}")
    print(f"  max |d|:              {max(all_deltas):.4f}")
    print()
    print("  Reference offset tolerance band proposed by REFERENCE_SET.md: +/-0.05.")
    in_band = sum(1 for d in all_deltas if d <= 0.05)
    print(f"  Comparisons within +/-0.05: {in_band}/{len(all_deltas)} "
          f"({100 * in_band / len(all_deltas):.1f}%)")


if __name__ == "__main__":
    main()
