"""Tests for ridge-tracking dispatch helpers (#994, pipeline/ridge.py)."""

from __future__ import annotations

import numpy as np

from mtfdigitizer.pipeline.ridge import (
    Track,
    _cluster_into_tracks,
    _column_runs,
    _extract_ridge_points,
    _merge_near_duplicate_tracks,
    _strip_chrome,
    ridge_tracks_to_fields,
)
from mtfdigitizer.pipeline.types import PlotBox


def _box(x_left=0, x_right=99, y_top=0, y_bottom=99) -> PlotBox:
    return PlotBox(x_left=x_left, x_right=x_right, y_top=y_top, y_bottom=y_bottom)


# --- _column_runs --------------------------------------------------------


def test_column_runs_groups_adjacent_pixels_into_one_run() -> None:
    col = np.zeros(20, dtype=np.uint8)
    col[5:9] = 1  # one continuous run of 4 pixels
    runs = _column_runs(col)
    assert len(runs) == 1
    centroid, length = runs[0]
    assert centroid == 6.5
    assert length == 4


def test_column_runs_splits_at_gap_larger_than_tolerance() -> None:
    col = np.zeros(20, dtype=np.uint8)
    col[5] = 1
    col[6] = 1
    col[10] = 1  # gap of 4 — splits the run (tolerance default 1)
    col[11] = 1
    runs = _column_runs(col)
    assert len(runs) == 2


def test_column_runs_returns_empty_for_blank_column() -> None:
    col = np.zeros(20, dtype=np.uint8)
    assert _column_runs(col) == []


# --- _strip_chrome -------------------------------------------------------


def test_strip_chrome_removes_full_width_horizontal_line() -> None:
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[50, :] = 1  # full-width line at y=50
    cleaned = _strip_chrome(mask, _box())
    assert cleaned[50, :].sum() == 0


def test_strip_chrome_preserves_short_horizontal_segments() -> None:
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[50, 10:30] = 1  # 20% of width — well below the 90% threshold
    cleaned = _strip_chrome(mask, _box())
    assert cleaned[50, 10:30].sum() == 20


def test_strip_chrome_ignores_pixels_outside_plot_box() -> None:
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[50, :] = 1  # full-width chrome
    cleaned = _strip_chrome(mask, _box(x_left=0, x_right=99, y_top=60, y_bottom=99))
    # y=50 is above plot_box.y_top=60 — outside the strip window
    assert cleaned[50, :].sum() == 100


# --- _cluster_into_tracks ------------------------------------------------


def test_cluster_joins_points_in_same_y_band_into_one_track() -> None:
    points = [(x, 10.0) for x in range(0, 100, 2)]  # straight horizontal
    tracks = _cluster_into_tracks(points)
    assert len(tracks) == 1
    assert tracks[0].coverage == 50


def test_cluster_separates_points_in_distant_y_bands() -> None:
    # Two horizontal tracks 20px apart, well outside max_dy=5
    points = [(x, 10.0) for x in range(0, 100, 2)] + [
        (x, 50.0) for x in range(0, 100, 2)
    ]
    tracks = _cluster_into_tracks(points)
    assert len(tracks) == 2
    ys = sorted(t.mean_y for t in tracks)
    assert ys == [10.0, 50.0]


def test_cluster_bridges_x_gaps_within_max_dx() -> None:
    # Two points 30 columns apart on the same y — joined because
    # max_dx=40 default
    points = [(10, 25.0), (40, 25.0)]
    tracks = _cluster_into_tracks(points)
    assert len(tracks) == 1


def test_cluster_does_not_bridge_x_gaps_beyond_max_dx() -> None:
    # 50 columns apart with max_dx=40 default → separate tracks
    points = [(10, 25.0), (60, 25.0)]
    tracks = _cluster_into_tracks(points)
    assert len(tracks) == 2


# --- _merge_near_duplicate_tracks ----------------------------------------


def test_dedup_drops_short_track_within_window_of_longer() -> None:
    long_track = Track(points=tuple((x, 10.0) for x in range(100)))
    near_track = Track(points=tuple((x, 12.0) for x in range(0, 30)))  # 2px away
    kept = _merge_near_duplicate_tracks([long_track, near_track])
    assert kept == [long_track]


def test_dedup_keeps_both_when_outside_window() -> None:
    track_a = Track(points=tuple((x, 10.0) for x in range(100)))
    track_b = Track(points=tuple((x, 50.0) for x in range(100)))  # well outside
    kept = _merge_near_duplicate_tracks([track_a, track_b])
    assert len(kept) == 2


# --- ridge_tracks_to_fields end-to-end -----------------------------------


def test_ridge_tracks_to_fields_separates_two_curves_at_distinct_y() -> None:
    """Two horizontal curves at y=20 and y=40 inside a 100x100 plot box —
    upper goes to freq10S, lower to freq30S (the SAGITTAL slot
    of each frequency pair)."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    # Curves cover 80% of plot width — below the 90% chrome threshold so
    # they survive the strip pass. (Realistic curves rarely span every
    # column; the chrome strip is meant for printed full-width gridlines.)
    mask[20, 5:85] = 1
    mask[40, 5:85] = 1
    out = ridge_tracks_to_fields(
        mask,
        _box(),
        upper_freq=10,
        lower_freq=30,
        dashed_is_sagittal=False,
    )
    assert "freq10S" in out
    assert "freq30S" in out
    # The upper-band track ended up in 10S
    upper_y = np.nonzero(out["freq10S"])[0].mean()
    lower_y = np.nonzero(out["freq30S"])[0].mean()
    assert upper_y == 20
    assert lower_y == 40


def test_ridge_tracks_to_fields_returns_empty_when_mask_blank() -> None:
    out = ridge_tracks_to_fields(
        np.zeros((100, 100), dtype=np.uint8),
        _box(),
        upper_freq=10,
        lower_freq=30,
        dashed_is_sagittal=False,
    )
    assert out == {}


def test_extract_ridge_points_walks_only_inside_plot_box() -> None:
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[20, 5] = 1  # inside box
    mask[20, 95] = 1  # outside box (box right=49)
    points = _extract_ridge_points(mask, _box(x_left=0, x_right=49))
    xs = sorted(x for x, _ in points)
    assert xs == [5]
