"""Unified MTF chart digitizer (ADR-038).

One adaptive tool that digitizes MTF charts across all brands into uniform,
confidence-scored readings + SVG, superseding the per-brand scrapers and the
legacy `mtf-extract-skeleton.py`.

The package is scaffolded incrementally as epic #932 lands:

- `referenceset/`   — eye-verified ground-truth charts (#933)
- `profiles/`       — declared chart profiles + advisory auto-suggest (#934)
- `pipeline/`       — adaptive extraction pipeline (#935)
- `pipeline/rendermatch.py` — round-trip IoU + precision scorer (#963)
- `priors.py`       — physical-plausibility priors (#966)
- `triage.py`       — auto-triage gate combining both signals (#968)
- `svg.py`          — SVG emitter from readings (#971)
- `review.py`       — 3-panel review file generator
"""
