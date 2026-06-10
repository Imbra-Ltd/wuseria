"""Aperture-pass resolution shared by extract.py and svg.py (#1107).

`aperture_passes_for_view` translates one chart view into one or more
(aperture, profile) extraction passes — the same fan-out the production
extractor uses for ADR-044 multi-aperture-per-chart charts (TTartisan).

Shared module because both the production CLI (`extract.py`) and the
reference-chart SVG emitter (`svg.py`) need the same answer; putting
the function in either creates a circular import.
"""

from __future__ import annotations

import dataclasses
import re
from pathlib import Path

from .family_profile import profile_for_chart
from .profiles.types import MtfProfile
from .referenceset.charts import ReferenceChart


_FUJI_FREQ_RE = re.compile(r"-(?P<freq>\d+)lp\.png$", re.IGNORECASE)
_FUJI_STYLE_FAMILIES: frozenset[str] = frozenset({"fujifilm-permfreq"})


def _parse_filename_frequency(image_path: Path) -> int:
    """Extract the spatial frequency from a per-frequency chart filename."""
    m = _FUJI_FREQ_RE.search(image_path.name)
    if m is None:
        raise ValueError(
            f"per-frequency chart filename must end in `-<N>lp.png`; "
            f"got {image_path.name!r}"
        )
    return int(m.group("freq"))


def _hue_filtered_profile(profile: MtfProfile, aperture: str) -> MtfProfile:
    """Return a profile copy with `hues` filtered to one aperture (ADR-044)."""
    filtered = tuple(h for h in profile.hues if h.name.startswith(f"{aperture}-"))
    return dataclasses.replace(profile, hues=filtered)


def aperture_passes_for_view(
    chart: ReferenceChart, image_path: Path
) -> list[tuple[str, MtfProfile]]:
    """Resolve a view to one or more (aperture, profile) extraction passes.

    - Fujifilm per-frequency (ADR-043): one pass, profile copied with
      `frequencies_lpmm` substituted from the filename.
    - Multi-aperture-per-chart (ADR-044): N passes, one per aperture,
      each with profile hues filtered to that aperture's bucket.
    - Default: one pass with the chart's primary aperture label.
    """
    base = profile_for_chart(chart)
    if chart.style_family in _FUJI_STYLE_FAMILIES:
        freq = _parse_filename_frequency(image_path)
        substituted = dataclasses.replace(base, frequencies_lpmm=(freq,))
        return [(chart.apertures[0], substituted)]
    if base.apertures_per_chart is not None:
        return [
            (ap, _hue_filtered_profile(base, ap)) for ap in base.apertures_per_chart
        ]
    return [(chart.apertures[0] if chart.apertures else "", base)]
