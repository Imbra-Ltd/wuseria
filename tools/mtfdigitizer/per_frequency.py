"""Per-frequency chart family helpers (ADR-043).

Fujifilm publishes MTF as one chart image per spatial frequency. The
extractor's single-image pipeline gives one ExtractedChart per image;
this module merges the per-frequency views back into one ExtractedChart
whose readings carry all frequencies as `freq{N}S` / `freq{N}M` keys
on each `SampledReading.samples` dict.

Three callers use this:

- `calibrate.py` — compares merged per-frequency readings to the
  per-lens ground-truth tuples.
- `extract.py` — runs each view as its own production-tier extraction,
  with the merged result used only by the orchestrator's verdict
  aggregation.
- `emit.py` — produces the merged readings for `mtf-readings.ts`
  emission.

The orchestration is identical across callers: parse the spatial
frequency from each view's filename, substitute it onto a profile copy,
extract each view, merge per-position sample dicts.
"""

from __future__ import annotations

import dataclasses
import re
from pathlib import Path

from .family_profile import profile_for_chart
from .pipeline import extract_chart
from .pipeline.types import ExtractedChart, PlotBox, SampledReading
from .referenceset.charts import PlotBoxCoords, ReferenceChart


# Style families that publish one chart image per spatial frequency.
# Callers branch on this set to choose between the single-image path
# (the existing reference-set workflow for Sigma / Samyang / Tokina /
# etc.) and the per-frequency multipath here.
PER_FREQUENCY_STYLE_FAMILIES: frozenset[str] = frozenset({"fujifilm-permfreq"})


# Per-frequency Fujifilm filenames carry the frequency as a trailing
# suffix: `<stem>-15lp.png`, `<stem>-45lp.png`, etc.
_FUJI_FREQ_RE = re.compile(r"-(?P<freq>\d+)lp\.png$", re.IGNORECASE)


def parse_filename_frequency(image_path: Path) -> int:
    """Extract the spatial frequency from a per-frequency chart filename.

    Raises `ValueError` when the suffix is missing — the orchestrator's
    contract per ADR-043 is to refuse non-conforming filenames rather
    than guess.
    """
    m = _FUJI_FREQ_RE.search(image_path.name)
    if m is None:
        raise ValueError(
            f"per-frequency chart filename must end in `-<N>lp.png`; "
            f"got {image_path.name!r}"
        )
    return int(m.group("freq"))


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


def extract_per_frequency_chart(
    chart: ReferenceChart, repo_root: Path
) -> ExtractedChart:
    """Walk every view of a per-frequency lens; merge per-position readings.

    Each Fujifilm-style chart publishes one image per spatial frequency.
    For each view: parse the frequency from the filename, substitute it
    onto a copy of the declared profile (which carries
    `frequencies_lpmm=(0,)` as a sentinel), run `extract_chart`. Then
    merge the per-view sample dicts at each position so one
    `SampledReading` row carries all frequencies' `freq{N}S` /
    `freq{N}M` keys.

    The returned `ExtractedChart` borrows the structure of the last view
    extracted; `source_path` and `profile_name` reflect that final view,
    while `readings` is the merged tuple.
    """
    assert chart.plot_box is not None, (
        f"chart {chart.slug!r} has no plot_box — "
        "per-frequency extraction requires a calibrated box"
    )
    base_profile = profile_for_chart(chart)

    merged_samples: dict[float, dict[str, float | None]] = {}
    last_result: ExtractedChart | None = None
    for view in chart.views:
        assert view.plot_box is not None, (
            f"view {view.chart_path!r} on chart {chart.slug!r} has no plot_box"
        )
        image_path = repo_root / view.chart_path
        freq = parse_filename_frequency(image_path)
        profile = dataclasses.replace(base_profile, frequencies_lpmm=(freq,))
        plot_box = _to_plotbox(view.plot_box, view.y_top_insets)
        result = extract_chart(
            image_path,
            profile,
            plot_box,
            image_height_mm=chart.image_height_mm,
        )
        last_result = result
        for reading in result.readings:
            merged = merged_samples.setdefault(reading.position_mm, {})
            merged.update(reading.samples)

    merged_readings = tuple(
        SampledReading(position_mm=pos, samples=merged_samples[pos])
        for pos in sorted(merged_samples.keys())
    )
    assert last_result is not None
    return dataclasses.replace(last_result, readings=merged_readings)
