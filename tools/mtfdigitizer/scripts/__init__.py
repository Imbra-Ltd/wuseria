"""One-shot scripts that scaffold or maintain reference-set entries.

These modules are not part of the runtime pipeline — they are
maintainer tooling. The current entries:

- `scaffold_fuji_tier2` — auto-detect plot boxes for every Fujifilm
  lens with MTF charts and emit a `_fuji_tier2_charts.py` module of
  Tier 2 ReferenceChart entries.
"""
