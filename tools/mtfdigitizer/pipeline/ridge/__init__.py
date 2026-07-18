"""Ridge tracking for tightly-clustered curves (#994, ADR-038, ADR-083).

Decomposed by data-flow stage (ADR-083):

- `foundation` — mask chrome-strip, per-column ridge extraction, track
  clustering/merge/select, rasterize/densify/coincidence.
- `dp` — per-column Viterbi DP passes and crossing detection/swap.
- `hue` — `ridge_tracks_for_hue_freq_split` (FREQUENCY_PER_HUE_RIDGE).
- `fields` — `ridge_tracks_to_fields_multifreq` / `ridge_tracks_to_fields`
  (RIDGE_TRACKING).

Re-exports the public entry points plus the private helpers that
`tests/test_ridge.py` imports directly, so `from .pipeline.ridge import X`
is unchanged.
"""

from .dp import (
    _compute_y_anchors,
    _detect_and_swap_at_crossings,
    _path_mask_continuity,
    _path_to_track,
    _ridge_dp_one_pass,
    _ridge_dp_two_paths,
    _ridges_by_column,
)
from .fields import (
    _order_band_sm,
    ridge_tracks_to_fields,
    ridge_tracks_to_fields_multifreq,
)
from .foundation import (
    Track,
    _cluster_into_tracks,
    _column_runs,
    _densify_track,
    _extend_track_to_plot_edges,
    _extract_ridge_points,
    _filter_isolated_ridge_points,
    _merge_near_duplicate_tracks,
    _select_top_n_tracks,
    _strip_chrome,
)
from .hue import ridge_tracks_for_hue_freq_split

__all__ = [
    "Track",
    "ridge_tracks_for_hue_freq_split",
    "ridge_tracks_to_fields",
    "ridge_tracks_to_fields_multifreq",
    "_cluster_into_tracks",
    "_column_runs",
    "_compute_y_anchors",
    "_densify_track",
    "_detect_and_swap_at_crossings",
    "_extend_track_to_plot_edges",
    "_extract_ridge_points",
    "_filter_isolated_ridge_points",
    "_merge_near_duplicate_tracks",
    "_order_band_sm",
    "_path_mask_continuity",
    "_path_to_track",
    "_ridge_dp_one_pass",
    "_ridge_dp_two_paths",
    "_ridges_by_column",
    "_select_top_n_tracks",
    "_strip_chrome",
]
