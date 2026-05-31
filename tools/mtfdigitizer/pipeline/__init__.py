"""Adaptive MTF extraction pipeline (#935, ADR-038 §2-3).

```
chart PNG
  -> profile (declared/resolved)
  -> plot-box detection            (plotbox.py)
  -> mask per declared hue         (masks.py)
  -> morphological close + skel    (skeleton.py)
  -> S/M split for SPLIT_BY_DASH   (split.py)
  -> 11-point sampling + interp    (sampling.py)
  -> {position_mm: {10S, 10M, 30S, 30M}}
```

Each stage is a small composable function with frozen-dataclass IO so
the pipeline can be tested stage-by-stage and orchestrated through one
top-level `extract_chart()` entry point.

The pipeline retains the three sound parts of the legacy skeleton-trace
approach that ADR-038 §2 explicitly keeps:

- axis/grid detection
- `interpolate_at` semantics (returns None outside bracketing data — B2)
- connected-components S/M split by fragment width (the only thing
  that separates two same-colored curves, ADR-038 §2)

Public surface:

- `extract_chart(image_path, profile, image_height_mm) -> ExtractedChart`
- `score_chart(image_path, profile, plot_box, image_height_mm, readings)
   -> RenderMatchScore` — round-trip IoU confidence signal (#963)
- `SAMPLE_POINTS` — the 11 fractional sample heights (0.0, 0.1, ..., 1.0)
- `PlotBox`, `ExtractedChart`, `SampledReading` (types)
- `FieldIou`, `RenderMatchScore` (render-match types)
"""

from .pipeline import extract_chart, SAMPLE_POINTS
from .rendermatch import FieldIou, RenderMatchScore, score_chart
from .types import ExtractedChart, PlotBox, SampledReading

__all__ = [
    "ExtractedChart",
    "FieldIou",
    "PlotBox",
    "RenderMatchScore",
    "SAMPLE_POINTS",
    "SampledReading",
    "extract_chart",
    "score_chart",
]
