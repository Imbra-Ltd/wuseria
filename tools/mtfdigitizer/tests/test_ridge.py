"""Tests for ridge-tracking dispatch helpers (#994, pipeline/ridge.py)."""

from __future__ import annotations

import numpy as np

from mtfdigitizer.pipeline.ridge import (
    Track,
    _cluster_into_tracks,
    _column_runs,
    _extract_ridge_points,
    _merge_near_duplicate_tracks,
    _select_top_n_tracks,
    _strip_chrome,
    ridge_tracks_for_hue_freq_split,
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


def test_strip_chrome_zeros_plot_box_border_rows_unconditionally() -> None:
    """Regression for #1090. The X-axis border lines at y_top / y_bottom
    must always be stripped — the TTartisan 100mm-macro chart's bottom
    border had only 87% coverage (under the 90% threshold) and was
    selected as a high-coverage 'curve' at MTF=0, hijacking the
    freq30S slot from the real grey S30_F2.8 curve at MTF~0.78.

    Border rows are chrome by construction: a curve cannot legitimately
    sit exactly at MTF=0 or MTF=1 — those y coordinates are the plot
    frame, not data.
    """
    mask = np.zeros((100, 100), dtype=np.uint8)
    # Sub-threshold ink on both border rows (87% coverage like #1090).
    mask[20, 0:87] = 1  # y_top border, 87% width — would slip 90% gate
    mask[80, 0:87] = 1  # y_bottom border, same
    cleaned = _strip_chrome(mask, _box(y_top=20, y_bottom=80))
    assert cleaned[20, :].sum() == 0, "y_top border row not stripped"
    assert cleaned[80, :].sum() == 0, "y_bottom border row not stripped"


def test_strip_chrome_keeps_curve_ink_just_inside_borders() -> None:
    """A curve sample one pixel inside the y_top / y_bottom borders is
    real data and MUST survive the border-strip. Distinguishes border
    chrome from a curve that happens to peak/trough near the frame.
    """
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[21, 10:30] = 1  # one pixel inside y_top — real curve ink
    mask[79, 10:30] = 1  # one pixel inside y_bottom — real curve ink
    cleaned = _strip_chrome(mask, _box(y_top=20, y_bottom=80))
    assert cleaned[21, 10:30].sum() == 20
    assert cleaned[79, 10:30].sum() == 20


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


# --- _select_top_n_tracks (fusion-before-floor, #1097) -------------------


def test_select_top_n_tracks_fuses_subfloor_fragments_before_applying_floor() -> None:
    """Regression for #1097. A real curve can split into multiple
    sub-floor fragments where its ridge intersects another curve's.
    Fragment fusion MUST run before the coverage floor — otherwise the
    fragments are dropped and the real curve never enters track
    selection.

    Mirrors the TTartisan T10 dive shape: three disjoint, contiguous
    fragments individually below the 10% floor (on plot_width=600 the
    floor is 60), endpoint y's matching within _FRAGMENT_MERGE_MAX_DY=6.
    """
    plot_width = 600
    floor = int(0.10 * plot_width)  # 60
    background = Track(points=tuple((x, 150.0) for x in range(100, 400)))
    # Three sub-floor fragments of a diving curve with matching endpoint y's.
    dive_left = Track(points=tuple((x, 200.0 + (x - 445) * 0.2) for x in range(445, 480)))
    dive_mid = Track(points=tuple((x, 207.0 + (x - 480) * 0.3) for x in range(480, 510)))
    dive_right = Track(points=tuple((x, 216.0 + (x - 510) * 0.4) for x in range(510, 560)))
    assert dive_left.coverage < floor
    assert dive_mid.coverage < floor
    assert dive_right.coverage < floor
    selected = _select_top_n_tracks(
        [background, dive_left, dive_mid, dive_right],
        n=2,
        plot_width=plot_width,
    )
    assert len(selected) == 2, (
        "fusion should stitch the dive fragments into one >floor track"
    )
    # The fused dive track must include points from all three fragments
    dive = [t for t in selected if t is not background][0]
    dive_xs = {x for x, _ in dive.points}
    assert dive_xs & set(range(445, 480)), "missing left dive fragment"
    assert dive_xs & set(range(480, 510)), "missing middle dive fragment"
    assert dive_xs & set(range(510, 560)), "missing right dive fragment"


def test_select_top_n_tracks_does_not_admit_sub_floor_noise() -> None:
    """The floor still rejects isolated sub-floor noise tracks that
    DON'T fuse into anything. Guards against the regression where the
    fusion-first reorder turns the algorithm into "always pass" by
    dropping the noise filter.
    """
    plot_width = 600
    floor = int(0.10 * plot_width)  # 60
    # Two real curves clearly above floor
    upper = Track(points=tuple((x, 100.0) for x in range(0, 200)))
    lower = Track(points=tuple((x, 300.0) for x in range(0, 200)))
    # A noise track far from both, sub-floor coverage, no continuity link
    noise = Track(points=tuple((x, 500.0) for x in range(0, 30)))
    assert noise.coverage < floor
    selected = _select_top_n_tracks(
        [upper, lower, noise],
        n=3,
        plot_width=plot_width,
    )
    selected_ys = sorted(t.mean_y for t in selected)
    assert 500.0 not in selected_ys, "sub-floor noise should still be filtered"
    assert len(selected) == 2


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


# --- ridge_tracks_for_hue_freq_split (TTartisan dispatch) ----------------


def test_ridge_tracks_for_hue_freq_split_labels_higher_coverage_as_S() -> None:
    """One hue carries one frequency with both S (solid, full coverage)
    and T (dashed, partial coverage). The solid track should land in
    freq10S; the dashed in freq10M, by the default Sigma convention
    (`dashed_is_sagittal=False`)."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    # Solid line: every column in [5, 85)
    mask[20, 5:85] = 1
    # Dashed line: alternating 6-px-on / 6-px-off pattern at y=40
    for x in range(5, 85, 12):
        mask[40, x : x + 6] = 1
    out = ridge_tracks_for_hue_freq_split(
        mask, _box(), freq=10, dashed_is_sagittal=False,
    )
    assert "freq10S" in out
    assert "freq10M" in out
    # The dense (solid) track has higher coverage and goes to S.
    assert int(out["freq10S"].sum()) > int(out["freq10M"].sum())
    # Y positions: solid at 20, dashed at 40.
    s_y = np.nonzero(out["freq10S"])[0].mean()
    t_y = np.nonzero(out["freq10M"])[0].mean()
    assert s_y == 20
    assert t_y == 40


def test_ridge_tracks_for_hue_freq_split_honors_dashed_is_sagittal() -> None:
    """7Artisans-style convention: dashed = S, solid = T. The
    higher-coverage track should land in freq10M instead of freq10S."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[20, 5:85] = 1
    for x in range(5, 85, 12):
        mask[40, x : x + 6] = 1
    out = ridge_tracks_for_hue_freq_split(
        mask, _box(), freq=10, dashed_is_sagittal=True,
    )
    # Solid track (higher coverage) now labels as M; dashed labels as S.
    assert int(out["freq10M"].sum()) > int(out["freq10S"].sum())
    m_y = np.nonzero(out["freq10M"])[0].mean()
    s_y = np.nonzero(out["freq10S"])[0].mean()
    assert m_y == 20  # solid (high-coverage) at y=20
    assert s_y == 40  # dashed at y=40


def test_ridge_tracks_for_hue_freq_split_shares_value_at_whole_curve_coincidence() -> None:
    """When only one track survives (the two curves visually coincide
    across the entire field), both fields share its value — same B4
    physics generalization as `ridge_tracks_for_hue`."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    # Single curve at y=30; second curve is absent entirely.
    mask[30, 5:85] = 1
    out = ridge_tracks_for_hue_freq_split(
        mask, _box(), freq=10, dashed_is_sagittal=False,
    )
    assert "freq10S" in out
    assert "freq10M" in out
    # Both fields rasterize the same track.
    assert int(out["freq10S"].sum()) == int(out["freq10M"].sum())
    assert (out["freq10S"] == out["freq10M"]).all()


def test_ridge_tracks_for_hue_freq_split_returns_empty_when_mask_blank() -> None:
    out = ridge_tracks_for_hue_freq_split(
        np.zeros((100, 100), dtype=np.uint8),
        _box(),
        freq=10,
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
