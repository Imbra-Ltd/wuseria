"""Unified MTF chart digitizer (ADR-038).

One adaptive tool that digitizes MTF charts across all brands into uniform,
confidence-scored readings + SVG, superseding the per-brand scrapers and the
legacy `mtf-extract-skeleton.py`.

The package is scaffolded incrementally as epic #932 lands:

- `referenceset/`   — eye-verified ground-truth charts (#933, this PR)
- `profiles/`       — declared chart profiles (#934)
- `pipeline.py`     — adaptive extraction pipeline (#935)
- `confidence.py`   — render-match + plausibility priors
- `svg.py`          — SVG emitter (from numbers)
- `review.py`       — 3-panel review file generator
"""
