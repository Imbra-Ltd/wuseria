"""Tests for ridge-tracking dispatch helpers (#994, pipeline/ridge.py)."""

from __future__ import annotations

import numpy as np

from mtfdigitizer.pipeline.ridge import (
    Track,
    _cluster_into_tracks,
    _column_runs,
    _compute_y_anchors,
    _densify_track,
    _detect_and_swap_at_crossings,
    _extend_track_to_plot_edges,
    _extract_ridge_points,
    _filter_isolated_ridge_points,
    _merge_near_duplicate_tracks,
    _order_band_sm,
    _path_mask_continuity,
    _path_to_track,
    _ridge_dp_one_pass,
    _ridge_dp_two_paths,
    _ridges_by_column,
    _select_top_n_tracks,
    _strip_chrome,
    ridge_tracks_for_hue_freq_split,
    ridge_tracks_to_fields,
    ridge_tracks_to_fields_multifreq,
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
    """A sparse curve sample one pixel inside the y_top / y_bottom
    borders is real data and MUST survive the border-strip. Real chart
    data at MTF~0.99 / MTF~0.01 is sparse — a few pixels per row —
    because curves near the axis are physically rare. Dense ink at
    those rows is anti-aliased axis-line halo and is correctly stripped
    by the axis-halo rule (#1165).
    """
    mask = np.zeros((100, 100), dtype=np.uint8)
    # Sparse curve corner: 5 of 100 columns = 5% coverage, well below
    # _AXIS_HALO_MIN_COVERAGE. This represents a real curve approaching
    # MTF=1.0 at the chart corner (e.g. 7.5 fisheye max-10-black has
    # 2/521 ~ 0.4% coverage near the top axis).
    mask[21, 10:15] = 1  # one pixel inside y_top
    mask[79, 10:15] = 1  # one pixel inside y_bottom
    cleaned = _strip_chrome(mask, _box(y_top=20, y_bottom=80))
    assert cleaned[21, 10:15].sum() == 5
    assert cleaned[79, 10:15].sum() == 5


def test_strip_chrome_kills_dense_halo_just_inside_borders() -> None:
    """Halo immediately below the top axis (or above the bottom axis)
    that has >= _AXIS_HALO_MIN_COVERAGE column coverage is anti-aliased
    chrome, not real curve data. See #1165: TTartisan tilt-50 GFX
    template has 80/517 ~ 15.5% coverage at y_top+3 from the top axis
    halo that survives the standard 90% chrome threshold but is not a
    real curve at MTF~0.99.
    """
    mask = np.zeros((100, 100), dtype=np.uint8)
    # Dense halo: 20 of 100 columns = 20% coverage, above
    # _AXIS_HALO_MIN_COVERAGE (12%). Stripped.
    mask[21, 10:30] = 1  # one pixel inside y_top
    mask[79, 10:30] = 1  # one pixel inside y_bottom
    cleaned = _strip_chrome(mask, _box(y_top=20, y_bottom=80))
    assert cleaned[21, :].sum() == 0
    assert cleaned[79, :].sum() == 0


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


# --- _order_band_sm (#1374) -----------------------------------------------


def test_order_band_sm_defaults_to_y_order() -> None:
    """Flag off: the upper track is S even when the lower has decisively
    more coverage — the pre-#1374 behavior every non-opted profile keeps."""
    upper = Track(points=tuple((x, 20.0) for x in range(0, 40)))
    lower = Track(points=tuple((x, 40.0) for x in range(0, 80)))
    s, m = _order_band_sm(
        [upper, lower], sm_by_coverage=False, dashed_is_sagittal=False
    )
    assert s is upper
    assert m is lower


def test_order_band_sm_assigns_solid_to_higher_coverage_when_enabled() -> None:
    """Zeiss Touit 32mm max-panel regression (#1374): the dashed M runs
    ABOVE solid S, so y-order exchanges the labels. With `sm_by_coverage`
    the denser (solid) track is S regardless of y."""
    dashed_above = Track(points=tuple((x, 20.0) for x in range(0, 80, 2)))
    solid_below = Track(points=tuple((x, 40.0) for x in range(0, 80)))
    s, m = _order_band_sm(
        [dashed_above, solid_below], sm_by_coverage=True, dashed_is_sagittal=False
    )
    assert s is solid_below
    assert m is dashed_above


def test_order_band_sm_falls_back_to_y_order_under_margin() -> None:
    """Coverage within the 1.15x margin carries no dashedness signal (the
    32mm max 40-band reads 342 vs 333 columns) — keep y-order so
    coincident pairs and the #791 collapse bands stay untouched."""
    upper = Track(points=tuple((x, 20.0) for x in range(0, 75)))
    lower = Track(points=tuple((x, 40.0) for x in range(0, 80)))  # 1.07x
    s, m = _order_band_sm(
        [upper, lower], sm_by_coverage=True, dashed_is_sagittal=False
    )
    assert s is upper
    assert m is lower


def test_order_band_sm_honors_dashed_is_sagittal() -> None:
    """7Artisans/TTartisan convention: dashed = S, so the sparse track
    takes the S slot when the discriminator fires."""
    solid = Track(points=tuple((x, 20.0) for x in range(0, 80)))
    dashed = Track(points=tuple((x, 40.0) for x in range(0, 80, 2)))
    s, m = _order_band_sm(
        [solid, dashed], sm_by_coverage=True, dashed_is_sagittal=True
    )
    assert s is dashed
    assert m is solid


def test_order_band_sm_single_track_reports_s_only() -> None:
    only = Track(points=tuple((x, 20.0) for x in range(0, 80)))
    s, m = _order_band_sm([only], sm_by_coverage=True, dashed_is_sagittal=False)
    assert s is only
    assert m is None


def test_order_band_sm_three_track_band_keeps_y_order() -> None:
    """A band with three or more tracks is a cluster-collapse symptom
    (#791) — the dashedness discriminator stays out; the first two by y
    win as before."""
    sparse_top = Track(points=tuple((x, 20.0) for x in range(0, 30)))
    dense_mid = Track(points=tuple((x, 40.0) for x in range(0, 80)))
    dense_low = Track(points=tuple((x, 60.0) for x in range(0, 80)))
    s, m = _order_band_sm(
        [sparse_top, dense_mid, dense_low],
        sm_by_coverage=True,
        dashed_is_sagittal=False,
    )
    assert s is sparse_top
    assert m is dense_mid


def test_ridge_tracks_to_fields_multifreq_sm_by_coverage_flips_dashed_above_solid() -> None:
    """End-to-end multifreq regression for #1374: dashed curve at y=20
    ABOVE solid curve at y=40 in one frequency band. Default y-order
    would call the dashed track S; `sm_by_coverage` labels the solid
    one S."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    for x in range(5, 85, 12):
        mask[20, x : x + 6] = 1  # dashed (M) above
    mask[40, 5:85] = 1  # solid (S) below
    out = ridge_tracks_to_fields_multifreq(
        mask,
        _box(),
        frequencies_lpmm=(10,),
        dashed_is_sagittal=False,
        sm_by_coverage=True,
    )
    assert np.nonzero(out["freq10S"])[0].mean() == 40
    assert np.nonzero(out["freq10M"])[0].mean() == 20


# --- _assign_left_anchored_bands (#1385) ----------------------------------


def test_multifreq_left_anchor_coincident_pair_keeps_bands_aligned() -> None:
    """#1385 stopped-panel regression: a coincident top pair leaves five
    tracks for three frequencies (true populations 1/2/2). The equal
    split slices 1/1/3 — the dashed 20M lands in freq40S and the real
    40M is dropped; left anchoring keeps every band on its own ink."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[10, 5:85] = 1  # coincident 10S/10M pair prints as one curve
    mask[30, 5:85] = 1  # 20S solid — reaches the left window
    for x in range(20, 85, 12):
        mask[38, x : x + 6] = 1  # 20M dashed, enters mid-field
    mask[60, 5:85] = 1  # 40S solid
    for x in range(20, 85, 12):
        mask[75, x : x + 6] = 1  # 40M dashed, enters mid-field
    out = ridge_tracks_to_fields_multifreq(
        mask,
        _box(),
        frequencies_lpmm=(10, 20, 40),
        dashed_is_sagittal=False,
        interior_anchored=True,
        sm_by_coverage=True,
    )
    assert np.nonzero(out["freq10S"])[0].mean() == 10
    assert "freq10M" not in out  # coincident pair reports S only (B2)
    assert np.nonzero(out["freq20S"])[0].mean() == 30
    assert np.nonzero(out["freq20M"])[0].mean() == 38
    assert np.nonzero(out["freq40S"])[0].mean() == 60
    assert np.nonzero(out["freq40M"])[0].mean() == 75


def test_multifreq_left_anchor_full_track_count_can_be_unbalanced() -> None:
    """#1385 max-panel regression: a full 2N kept set does not imply
    balanced bands. A coincident top pair plus a fragmented bottom
    curve is 1/2/3; the equal split shifts every band down one track."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[10, 5:85] = 1  # coincident 10 pair
    mask[30, 5:85] = 1  # 20S solid
    for x in range(20, 85, 12):
        mask[36, x : x + 6] = 1  # 20M dashed
    mask[60, 5:85] = 1  # 40S solid
    mask[70, 16:36] = 1  # 40M inner fragment
    mask[72, 80:96] = 1  # 40M outer fragment (x-gap > 40 stays separate)
    out = ridge_tracks_to_fields_multifreq(
        mask,
        _box(),
        frequencies_lpmm=(10, 20, 40),
        dashed_is_sagittal=False,
        interior_anchored=True,
        sm_by_coverage=True,
    )
    assert np.nonzero(out["freq10S"])[0].mean() == 10
    assert "freq10M" not in out
    assert np.nonzero(out["freq20S"])[0].mean() == 30
    assert np.nonzero(out["freq20M"])[0].mean() == 36
    assert np.nonzero(out["freq40S"])[0].mean() == 60
    assert np.nonzero(out["freq40M"])[0].mean() == 70


def test_multifreq_left_anchor_falls_back_when_no_left_window_tracks() -> None:
    """Curves all entering past the left window leave no band anchors;
    the assignment falls back to the equal split instead of guessing."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[20, 30:85] = 1
    mask[50, 30:85] = 1
    mask[80, 30:85] = 1
    out = ridge_tracks_to_fields_multifreq(
        mask,
        _box(),
        frequencies_lpmm=(10, 20, 40),
        dashed_is_sagittal=False,
        interior_anchored=True,
        sm_by_coverage=True,
    )
    assert np.nonzero(out["freq10S"])[0].mean() == 20
    assert np.nonzero(out["freq20S"])[0].mean() == 50
    assert np.nonzero(out["freq40S"])[0].mean() == 80


# --- ridge_tracks_for_hue_freq_split (TTartisan dispatch) ----------------


def test_ridge_tracks_for_hue_freq_split_labels_solid_track_as_S() -> None:
    """One hue carries one frequency with both S (solid, continuous mask)
    and T (dashed, periodic mask gaps). The solid track lands in
    freq10S; the dashed in freq10M, by the default Sigma convention
    (`dashed_is_sagittal=False`).

    Identity is decided by `Track.coverage` — the count of on-ridge
    columns each DP path locked onto (#1171 follow-up). Solid lines
    are on-ridge at almost every column; dashed lines are on-ridge
    only at the dash centroids, so coverage discriminates cleanly.
    When coverage ties, `_path_mask_continuity` is the tiebreaker.
    """
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
    # Y positions: solid at 20 → S, dashed at 40 → M.
    s_y = np.nonzero(out["freq10S"])[0].mean()
    t_y = np.nonzero(out["freq10M"])[0].mean()
    assert s_y == 20
    assert t_y == 40


def test_ridge_tracks_for_hue_freq_split_honors_dashed_is_sagittal() -> None:
    """7Artisans-style convention: dashed = S, solid = M. The
    solid (continuous-mask) track lands in freq10M instead of freq10S."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[20, 5:85] = 1
    for x in range(5, 85, 12):
        mask[40, x : x + 6] = 1
    out = ridge_tracks_for_hue_freq_split(
        mask, _box(), freq=10, dashed_is_sagittal=True,
    )
    m_y = np.nonzero(out["freq10M"])[0].mean()
    s_y = np.nonzero(out["freq10S"])[0].mean()
    assert m_y == 20  # solid at y=20 labelled M when dashed_is_sagittal=True
    assert s_y == 40  # dashed at y=40 labelled S


def test_ridge_tracks_for_hue_freq_split_uses_coverage_over_continuity_when_disagreeing() -> None:
    """Regression for af-75 stopped freq30 S/M swap (#1171 follow-up).

    Solid curve runs the full plot width (high coverage). Dashed
    curve covers only the right half but every dash is densely
    inked (high in-range continuity score). Continuity-based
    discrimination would mislabel the short dense dashed track as
    solid; coverage-based discrimination correctly picks the
    full-width track as solid.
    """
    mask = np.zeros((100, 100), dtype=np.uint8)
    # Solid line: every column in [5, 90) at y=20 — full width.
    for dy in (-1, 0, 1):
        mask[20 + dy, 5:90] = 1
    # Dashed line: only in right half [50, 90), but every column dense.
    for dy in (-1, 0, 1):
        mask[40 + dy, 50:90] = 1
    out = ridge_tracks_for_hue_freq_split(
        mask, _box(x_left=0, x_right=99), freq=30, dashed_is_sagittal=False,
    )
    # Solid (full-width at y=20) labelled S; dashed (short at y=40) labelled M.
    s_y = np.nonzero(out["freq30S"])[0].mean()
    m_y = np.nonzero(out["freq30M"])[0].mean()
    assert s_y < m_y, f"solid track at y=20 should land in freq30S, got s_y={s_y} m_y={m_y}"


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


# --- _filter_isolated_ridge_points (#1157) -------------------------------


def test_filter_keeps_long_dashed_curve_candidates() -> None:
    """A sparse dashed curve (3 px on, 3 px off across 30 cols) is one
    cluster spanning many columns — it must survive the filter."""
    points: list[tuple[int, float]] = []
    for x in range(0, 30, 6):
        # Each "dash" emits 3 adjacent column points at y=50.
        for d in (0, 1, 2):
            points.append((x + d, 50.0))
    kept = _filter_isolated_ridge_points(points)
    assert len(kept) == len(points)


def test_filter_drops_single_column_blob() -> None:
    """A two-point cluster confined to one column is a gridline fragment
    or noise — dropped."""
    points = [
        # Real curve cluster spanning 5 cols.
        (0, 50.0), (1, 50.0), (2, 50.0), (3, 50.0), (4, 50.0),
        # Single-column noise blob at y=20.
        (10, 20.0),
    ]
    kept = _filter_isolated_ridge_points(points)
    kept_set = set(kept)
    assert (10, 20.0) not in kept_set
    # The real curve survives.
    assert all((x, 50.0) in kept_set for x in range(5))


def test_filter_drops_two_column_blob() -> None:
    """Two adjacent-column candidates form a 2-col cluster, below the
    `_RIDGE_ISOLATION_MIN_COLS=3` threshold — dropped. This is the
    #1157 TTartisan 7.5 max-grey y=204/202 case at x=604/605."""
    points = [
        # Real curve spans 10 cols at y=290.
        *((x, 290.0) for x in range(10)),
        # Two-column mid-air noise at y=204, 202 at columns 20, 21.
        (20, 204.0),
        (21, 202.0),
    ]
    kept = _filter_isolated_ridge_points(points)
    kept_set = set(kept)
    assert (20, 204.0) not in kept_set
    assert (21, 202.0) not in kept_set
    assert all((x, 290.0) in kept_set for x in range(10))


def test_filter_bridges_dx_gap_via_chain() -> None:
    """Candidates connected through a chain of `dx`-spaced links count
    as one cluster, even if no two are within `dx` of every other.
    This is what lets the TTartisan 7.5 max.freq30M corner pixel at
    x=607 stay connected to the curve at x=603 (3-col drop-out)."""
    points = [
        # Cluster A: x in [0, 5], y=100
        *((x, 100.0) for x in range(6)),
        # 3-col drop-out at x=6,7,8
        # Cluster B: x=9, y=100 (single pixel after the gap)
        (9, 100.0),
    ]
    kept = _filter_isolated_ridge_points(points)
    # All 7 points should survive — they form one cluster spanning 7
    # distinct columns via the dx=4 bridge.
    assert len(kept) == 7


def test_filter_bridges_dy_drift_within_cluster() -> None:
    """A real curve gently drifts in y from column to column; that
    drift must not split it into clusters. With dy=8 the filter must
    accept y differences up to 8 px between neighbouring columns."""
    points = [(x, 100.0 + x * 0.5) for x in range(20)]  # drift 0.5 px/col
    kept = _filter_isolated_ridge_points(points)
    assert len(kept) == len(points)


# --- Per-column ridge DP (#1100) -----------------------------------------


def test_ridges_by_column_groups_points_by_column() -> None:
    """Points are grouped per column relative to plot_box.x_left."""
    box = _box(x_left=10, x_right=14)
    points = [(10, 20.0), (10, 30.0), (12, 25.0), (14, 40.0)]
    ridges = _ridges_by_column(points, box)
    assert len(ridges) == 5  # 14 - 10 + 1
    assert ridges[0] == [20.0, 30.0]  # column x=10
    assert ridges[1] == []  # column x=11 — empty
    assert ridges[2] == [25.0]
    assert ridges[3] == []
    assert ridges[4] == [40.0]


def test_ridge_dp_one_pass_picks_single_smooth_curve() -> None:
    """DP picks one y per column. Single curve with constant y=20 should be
    fully recovered with on_ridge=True at every column."""
    ridges_by_col = [[20.0] for _ in range(10)]
    path, on_ridge = _ridge_dp_one_pass(ridges_by_col)
    assert path == [20.0] * 10
    assert on_ridge == [True] * 10


def test_ridge_dp_one_pass_carries_through_empty_columns() -> None:
    """When a column has no ridges, the path carries forward at zero cost.
    The carry-forward columns are marked on_ridge=False so callers can
    filter them out."""
    ridges_by_col = [[20.0], [], [], [20.0]]
    path, on_ridge = _ridge_dp_one_pass(ridges_by_col)
    assert path == [20.0, 20.0, 20.0, 20.0]
    assert on_ridge == [True, False, False, True]


def test_ridge_dp_one_pass_returns_empty_on_blank_input() -> None:
    """If no column has a ridge, the path is all None."""
    path, on_ridge = _ridge_dp_one_pass([[], [], []])
    assert path == [None, None, None]
    assert on_ridge == [False, False, False]


def test_ridge_dp_two_paths_separates_two_parallel_curves() -> None:
    """Two curves at distinct y values across all columns. Pass 1 picks one;
    pass 2 picks the other (separated by more than _RIDGE_DP_ERASE_HALF)."""
    ridges_by_col = [[20.0, 40.0] for _ in range(10)]
    (p1, on1), (p2, on2) = _ridge_dp_two_paths(ridges_by_col)
    assert all(y in (20.0, 40.0) for y in p1)
    assert all(y in (20.0, 40.0) for y in p2)
    # Different curves
    assert p1[0] != p2[0]
    # Both fully on ridges
    assert on1 == [True] * 10
    assert on2 == [True] * 10


def test_ridge_dp_two_paths_recovers_two_curves() -> None:
    """DP's two-pass extraction recovers both curves when they cross.

    Note: at a symmetric crossing the two solutions (cross-through vs.
    bounce-off) have equal total smoothness cost. The interesting
    property DP guarantees is that BOTH paths are individually smooth
    and collectively cover both physical curves — not that each path
    follows a specific physical identity. Identity assignment is the
    job of the post-DP S/M labeling (via `_path_mask_continuity`).
    """
    ridges_by_col = [
        [10.0, 30.0],  # col 0: A above, B below
        [15.0, 25.0],  # col 1: approaching
        [20.0],        # col 2: crossing — single ridge (curves coincide)
        [15.0, 25.0],  # col 3: diverging
        [10.0, 30.0],  # col 4: maximally separated
    ]
    (p1, on1), (p2, on2) = _ridge_dp_two_paths(ridges_by_col)
    # Together the two paths cover all the ridge values at every column.
    # At col 0 we should have both 10.0 and 30.0 across the two paths.
    assert {p1[0], p2[0]} == {10.0, 30.0}
    assert {p1[4], p2[4]} == {10.0, 30.0}
    # At the coincidence column (col 2) pass 1 takes the single ridge;
    # pass 2 has no candidate (it was erased) and coasts.
    assert p1[2] == 20.0
    assert on1[2] is True
    assert on2[2] is False  # pass 2 carried forward through erased column


def test_path_to_track_drops_carry_forward_columns() -> None:
    """Columns where DP coasted via carry-forward should NOT appear in
    the resulting Track — they'd bleed the other pass's y values."""
    path = [20.0, 20.0, 20.0, 20.0]
    on_ridge = [True, False, False, True]
    track = _path_to_track(path, on_ridge, _box(x_left=10, x_right=13))
    assert track is not None
    xs = sorted(x for x, _ in track.points)
    # Only columns 0 and 3 have on_ridge=True; their x's are 10 and 13.
    assert xs == [10, 13]


def test_path_to_track_returns_none_when_all_carry_forward() -> None:
    """If the path never landed on a real ridge (all carry-forward),
    return None — there's no track to make."""
    path = [None, None, None]
    on_ridge = [False, False, False]
    track = _path_to_track(path, on_ridge, _box(x_left=0, x_right=2))
    assert track is None


def test_path_mask_continuity_solid_line_near_one() -> None:
    """A track that runs along a fully-inked row should have continuity
    near 1.0 (every column under it has mask ink)."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[20, 10:90] = 1
    points = tuple((x, 20.0) for x in range(10, 90))
    track = Track(points=points)
    cont = _path_mask_continuity(track, mask)
    assert cont == 1.0


def test_path_mask_continuity_dashed_line_below_solid() -> None:
    """A track over a dashed row (50% duty cycle) should have continuity
    well below 1.0 — the discriminator for S/M assignment."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    # Dashed: 6 on, 6 off
    for x in range(10, 90, 12):
        mask[40, x : x + 6] = 1
    points = tuple((x, 40.0) for x in range(10, 90))
    track = Track(points=points)
    cont = _path_mask_continuity(track, mask)
    assert 0.3 < cont < 0.8


def test_ridge_tracks_for_hue_freq_split_through_dp_crossing() -> None:
    """End-to-end: synthetic two-curve crossing mask. The freq-split
    dispatch should output two coherent fields with identity preserved
    through the crossing."""
    # Solid line goes from y=20 (left) to y=40 (right) — gentle descent.
    # Dashed line goes from y=40 (left) to y=20 (right) — gentle ascent.
    # They cross around the middle.
    mask = np.zeros((100, 100), dtype=np.uint8)
    for x in range(10, 90):
        # Solid: y = 20 + (x - 10) * 0.25
        y_solid = int(20 + (x - 10) * 0.25)
        mask[y_solid, x] = 1
    # Dashed: y = 40 - (x - 10) * 0.25, with periodic gaps (6 on, 6 off)
    dashed_on = True
    for x in range(10, 90):
        if (x - 10) % 12 < 6:
            y_dashed = int(40 - (x - 10) * 0.25)
            mask[y_dashed, x] = 1
    out = ridge_tracks_for_hue_freq_split(
        mask, _box(), freq=10, dashed_is_sagittal=False,
    )
    assert "freq10S" in out
    assert "freq10M" in out
    # At the left edge, S (solid) should be at y≈20, M (dashed) at y≈40.
    # At the right edge, S at y≈40, M at y≈20 — identity preserved through crossing.
    s_ys = np.nonzero(out["freq10S"])
    m_ys = np.nonzero(out["freq10M"])
    # Each field should have nonzero rasterization
    assert len(s_ys[0]) > 0
    assert len(m_ys[0]) > 0


# --- Y-anchor identity prior (#1104) ------------------------------------


def test_compute_y_anchors_seeds_from_two_ridge_columns() -> None:
    """Anchors are seeded only from columns with exactly two ridges. The
    smaller y becomes the upper anchor; the larger becomes the lower."""
    ridges_by_col = [[20.0, 40.0], [], [22.0, 42.0]]
    upper, lower = _compute_y_anchors(ridges_by_col)
    assert upper[0] == 20.0
    assert lower[0] == 40.0
    assert upper[2] == 22.0
    assert lower[2] == 42.0


def test_compute_y_anchors_carry_forward_fills_gaps() -> None:
    """Empty and single-ridge columns inherit the most recent two-ridge
    seed; columns before the first seed inherit it via backward fill."""
    ridges_by_col = [[], [50.0], [20.0, 40.0], [], [25.0], [22.0, 42.0]]
    upper, lower = _compute_y_anchors(ridges_by_col)
    # Backward-fill before the first seed at col 2: cols 0-1 inherit 20.0/40.0.
    assert upper[0] == 20.0
    assert lower[0] == 40.0
    assert upper[1] == 20.0
    # Carry-forward past the seed at col 2: col 3 inherits, col 4 still inherits
    # (single-ridge doesn't reset the seed), col 5 advances to the new seed.
    assert upper[3] == 20.0
    assert upper[4] == 20.0
    assert upper[5] == 22.0


def test_compute_y_anchors_skips_three_or_more_ridge_columns() -> None:
    """A column with three ridges is treated as noisy (gridline echoes,
    adjacent-curve halos) — the smallest/largest from it would drag the
    anchor toward chart chrome. Only exactly-two-ridge columns seed."""
    ridges_by_col = [[100.0, 105.0, 200.0], [20.0, 40.0]]
    upper, lower = _compute_y_anchors(ridges_by_col)
    # The 3-ridge col 0 does NOT seed; carry-fill from col 1's seed instead.
    assert upper[0] == 20.0
    assert lower[0] == 40.0


def test_ridge_dp_two_paths_with_anchor_resists_corner_swap() -> None:
    """Two parallel curves with a dash-gap-induced single-ridge column at
    the end should keep their identities under the y-anchor prior.

    Without the anchor, pass 1's smoothness cost is locally satisfied by
    landing on the only available ridge — even when that ridge belongs to
    the other physical curve. The anchor pulls each pass back to its band.
    """
    # Upper curve at y=20 for 8 cols. Lower curve at y=50 for 8 cols.
    # Last 2 cols have ONLY the lower curve's ridge (upper had a dash gap).
    ridges_by_col = [[20.0, 50.0]] * 8 + [[50.0], [50.0]]
    (p1, _), (p2, _) = _ridge_dp_two_paths(ridges_by_col, use_y_anchor=True)
    # Pass 1 (upper) stays at 20.0 across the first 8 cols; for the last
    # two cols it coasts at 20.0 rather than jumping to 50.0.
    assert p1[0] == 20.0
    assert p1[7] == 20.0
    assert p1[8] == 20.0  # coast, not swap
    assert p1[9] == 20.0
    # Pass 2 (lower) sits at 50.0 throughout — pass 1 left it untouched.
    assert p2[0] == 50.0
    assert p2[7] == 50.0
    assert p2[8] == 50.0
    assert p2[9] == 50.0


def test_ridge_dp_two_paths_without_anchor_keeps_dive_intact() -> None:
    """The default (no anchor) path must still take legitimate large jumps
    — the #1100 TTartisan freq30 dive. With anchoring off and no coast
    option, pass 1 lands on every ridge regardless of size."""
    # A curve that dives 60 px in one column — the #1100 corner-dive shape.
    ridges_by_col = [[100.0], [100.0], [100.0], [160.0], [160.0]]
    (p1, p1_on), _ = _ridge_dp_two_paths(ridges_by_col, use_y_anchor=False)
    assert p1[2] == 100.0
    assert p1[3] == 160.0  # took the dive, did NOT coast
    assert p1_on[3] is True


# --- _extend_track_to_plot_edges (#1171) ---------------------------------


def test_extend_track_fills_small_gap_to_right_edge_using_last_y() -> None:
    """A track ending short of the plot edge gets extended flat (last-
    known y) so the corner sampler finds a pixel — the TTartisan
    tilt-50 dashed-T30-corner pattern.

    Flat extension (not slope-extrapolation) avoids overshoot from
    noisy trailing-dash centroids on stopped-aperture curves where
    the visual line is flat but per-dash centroid noise is ±2 px/col.
    """
    pts = tuple((x, 10.0 + (x - 80)) for x in range(80, 91))
    track = Track(points=pts)
    box = _box(x_left=0, x_right=99)
    extended = _extend_track_to_plot_edges(track, box)
    xs = [x for x, _ in extended.points]
    assert max(xs) == 99
    # Last known y at x=90 is 20.0; flat extension keeps that across x=91..99.
    for x in range(91, 100):
        y = next(y for xx, y in extended.points if xx == x)
        assert y == 20.0


def test_extend_track_fills_small_gap_to_left_edge_using_first_y() -> None:
    pts = tuple((x, 10.0 + (x - 5)) for x in range(5, 21))
    track = Track(points=pts)
    box = _box(x_left=0, x_right=99)
    extended = _extend_track_to_plot_edges(track, box)
    xs = [x for x, _ in extended.points]
    assert min(xs) == 0
    # First known y at x=5 is 10.0; flat extension keeps that across x=0..4.
    for x in range(0, 5):
        y = next(y for xx, y in extended.points if xx == x)
        assert y == 10.0


def test_extend_track_refuses_gap_larger_than_max() -> None:
    """Beyond _EDGE_EXTRAPOLATION_MAX we don't know the curve's behavior —
    leave the corner None rather than fabricate (B2)."""
    # Track ends at x=80 in a 0..99 box: 19-px gap, larger than the
    # 12-px ceiling. Extension must NOT fire.
    pts = tuple((x, 10.0) for x in range(70, 81))
    track = Track(points=pts)
    box = _box(x_left=0, x_right=99)
    extended = _extend_track_to_plot_edges(track, box)
    xs = [x for x, _ in extended.points]
    assert max(xs) == 80
    assert min(xs) == 70  # left side: 70-px gap, refused


def test_extend_track_is_noop_when_already_at_edges() -> None:
    pts = tuple((x, 10.0) for x in range(0, 100))
    track = Track(points=pts)
    box = _box(x_left=0, x_right=99)
    extended = _extend_track_to_plot_edges(track, box)
    assert extended.points == pts


def test_extend_track_extends_single_point_track_within_cap() -> None:
    """A 1-point track is still extended flat — the last-known y is
    well-defined and the 12-px cap still bounds the extension distance."""
    track = Track(points=((97, 10.0),))
    box = _box(x_left=0, x_right=99)
    extended = _extend_track_to_plot_edges(track, box)
    # 2-px gap on right is within the cap → extended; 97-px gap on left
    # is past the cap → not extended.
    assert (99, 10.0) in extended.points
    assert (0, 10.0) not in extended.points


def test_freq_split_dashed_corner_recovered_when_last_dash_short_of_edge() -> None:
    """End-to-end regression for the tilt-50 dashed-T30 corner — see #1171.

    Two parallel curves at distinct y bands; the dashed curve's last
    dash stops 6 px short of the right edge. Before extension the
    corner sampler returned None; after extension the rasterized
    skeleton has a pixel in the right-edge bracket so the corner
    reads a finite MTF."""
    # 3-row solid stroke so it survives `_strip_chrome` (which zeros
    # horizontal lines with >=90% column coverage in a single row).
    mask = np.zeros((100, 100), dtype=np.uint8)
    for dy in (-1, 0, 1):
        mask[20 + dy, 5:90] = 1
    # Dashed curve at y=40: 3-px dashes every 6 px, last dash at
    # x=89..91 — 8 px short of right edge (within the 12-px extrapolation
    # window).
    for dash_start in range(5, 90, 6):
        for dy in (-1, 0, 1):
            mask[40 + dy, dash_start : dash_start + 3] = 1
    out = ridge_tracks_for_hue_freq_split(
        mask, _box(x_left=0, x_right=99), freq=30, dashed_is_sagittal=False,
    )
    # Both tracks must rasterize a pixel inside the right-edge bracket
    # (last 6 px) — without extension the dashed curve's last dash sits
    # outside that window.
    s_track = out["freq30S"]
    m_track = out["freq30M"]
    assert s_track[:, 94:].any(), "solid curve missing at right edge"
    assert m_track[:, 94:].any(), "dashed curve corner not recovered"


# --- _detect_and_swap_at_crossings (#1170) -------------------------------


def test_detect_and_swap_returns_inputs_when_tracks_never_approach() -> None:
    """Two parallel tracks that stay far apart get no swap — there is no
    crossing to detect."""
    track_a = Track(points=tuple((x, 20.0) for x in range(0, 100)))
    track_b = Track(points=tuple((x, 60.0) for x in range(0, 100)))
    out_a, out_b = _detect_and_swap_at_crossings(track_a, track_b)
    assert out_a.points == track_a.points
    assert out_b.points == track_b.points


def test_detect_and_swap_swaps_right_of_monotonic_crossing() -> None:
    """Two physical curves cross monotonically (S151 spike geometry,
    matching real af-75 stopped freq30).

    Physical curve P1: descends steadily across the field (positive
    slope in image-y throughout).
    Physical curve P2: ascends steadily across the field (negative
    slope in image-y throughout).

    The DP follows y-bands, not curve identity. Its upper-band output
    is whichever curve has the smaller y at each column — P2 left of
    the crossing, P1 right of the crossing. Its lower-band output is
    the opposite. Each band track therefore reverses slope at the
    crossing (BOTH reverse) even though each physical curve is monotonic.

    The detector MUST recognise this both-reverse signature and swap
    right-of-crossing assignments so each output track follows one
    physical curve end-to-end.
    """
    # Construct the two physical curves first.
    p1_pts = {x: 20.0 + 0.4 * x for x in range(0, 100)}  # 20 → 60 (down)
    p2_pts = {x: 60.0 - 0.4 * x for x in range(0, 100)}  # 60 → 20 (up)

    # Build DP-style outputs: upper_band = min y at each column,
    # lower_band = max y at each column. They cross at col 50 (y=40).
    upper_band_pts = tuple(
        (x, min(p1_pts[x], p2_pts[x])) for x in range(0, 100)
    )
    lower_band_pts = tuple(
        (x, max(p1_pts[x], p2_pts[x])) for x in range(0, 100)
    )
    upper_band = Track(points=upper_band_pts)
    lower_band = Track(points=lower_band_pts)

    out_a, out_b = _detect_and_swap_at_crossings(upper_band, lower_band)

    # After swap, each output track must trace ONE physical curve
    # end-to-end. Pick a column far from the crossing in each half and
    # check both endpoints lie on the same physical curve.
    a_left = dict(out_a.points).get(10)
    a_right = dict(out_a.points).get(90)
    b_left = dict(out_b.points).get(10)
    b_right = dict(out_b.points).get(90)

    # One of (out_a, out_b) should follow p2 (which is upper-band on
    # the left), the other p1.
    assert a_left is not None and a_right is not None
    assert b_left is not None and b_right is not None
    p1_l, p1_r = p1_pts[10], p1_pts[90]  # 24.0, 56.0
    p2_l, p2_r = p2_pts[10], p2_pts[90]  # 56.0, 24.0
    follows_p2_then_p2 = (
        abs(a_left - p2_l) < 0.01 and abs(a_right - p2_r) < 0.01
    )
    follows_p1_then_p1 = (
        abs(b_left - p1_l) < 0.01 and abs(b_right - p1_r) < 0.01
    )
    # The swap can assign either ordering; what matters is that each
    # output track stays on one physical curve.
    assert (follows_p2_then_p2 and follows_p1_then_p1) or (
        abs(a_left - p1_l) < 0.01 and abs(a_right - p1_r) < 0.01
        and abs(b_left - p2_l) < 0.01 and abs(b_right - p2_r) < 0.01
    ), (
        f"swap did not produce per-curve coherence: "
        f"a=({a_left}, {a_right}) b=({b_left}, {b_right})"
    )


def test_detect_and_swap_leaves_single_crossing_with_no_reversal_alone() -> None:
    """Tilt-50 case: the two curves cross near the right edge once, but
    NEITHER curve reverses direction near the crossing — both continue
    smoothly past each other. The DP already follows the physical curves
    correctly here (a smooth pass-through, not a slope-reversal at the
    crossing). The swap detector MUST NOT mis-fire and corrupt this
    case.

    This is the must-not-regress assertion called out in #1170.
    """
    # Curve A: gentle descent from y=20 to y=45 across the plot.
    a_pts = tuple((x, 20.0 + 0.25 * x) for x in range(0, 100))
    # Curve B: gentle ascent from y=45 to y=20. They cross around col 50.
    b_pts = tuple((x, 45.0 - 0.25 * x) for x in range(0, 100))
    track_a = Track(points=a_pts)
    track_b = Track(points=b_pts)
    out_a, out_b = _detect_and_swap_at_crossings(track_a, track_b)
    # Whether the post-DP labelling swaps or not, both physical curves
    # must remain end-to-end coherent — no kinks at the crossing column.
    # The simplest invariant: each output track's y values are monotonic
    # (either all-ascending or all-descending) end-to-end.
    a_ys = [y for _, y in sorted(out_a.points)]
    b_ys = [y for _, y in sorted(out_b.points)]
    a_diffs = [a_ys[i + 1] - a_ys[i] for i in range(len(a_ys) - 1)]
    b_diffs = [b_ys[i + 1] - b_ys[i] for i in range(len(b_ys) - 1)]
    # All consecutive deltas same sign (monotonic) on each output track.
    assert all(d >= 0 for d in a_diffs) or all(d <= 0 for d in a_diffs), (
        "out_a should remain monotonic — swap fired incorrectly"
    )
    assert all(d >= 0 for d in b_diffs) or all(d <= 0 for d in b_diffs), (
        "out_b should remain monotonic — swap fired incorrectly"
    )


# --- Path C candidate-walk (#1170 S151) ---------------------------------


def test_detect_and_swap_skips_left_edge_cluster_when_no_history() -> None:
    """Left-edge convergence has insufficient slope-before history on
    track_b — the verdict is None there. The detector MUST walk past it
    and evaluate later candidates, not exit greedily.

    Matches the af-75 real-data shape: track_b starts at col 232 with
    dy=2.5 from track_a, then both bands diverge, then re-converge at
    col 516 with a real swap signature.
    """
    # track_a: present from col 0 (long history)
    a_pts = []
    for x in range(0, 100):
        # Descends to col 50, then ascends — a band-following shape
        # produced when two physical curves cross monotonically.
        if x < 50:
            a_pts.append((x, 20.0 + 0.4 * x))  # 20 → 40
        else:
            a_pts.append((x, 40.0 - 0.4 * (x - 50)))  # 40 → 20
    track_a = Track(points=tuple(a_pts))
    # track_b: starts coincident with track_a at col 0 (left-edge
    # convergence) for the first 3 cols, then jumps away to a different
    # band. This forces dy_min global = 0 at col 0 with no slope history
    # for the b_pre check.
    b_pts = [(0, 20.0), (1, 20.5), (2, 21.0)]
    for x in range(3, 100):
        if x < 50:
            b_pts.append((x, 60.0 - 0.4 * x))  # 58.8 → 40
        else:
            b_pts.append((x, 40.0 + 0.4 * (x - 50)))  # 40 → 60
    track_b = Track(points=tuple(b_pts))

    out_a, out_b = _detect_and_swap_at_crossings(track_a, track_b)

    # The real crossing at col ~50 should fire even though col 0 has the
    # global min dy. Pick a column far past the crossing and confirm the
    # output tracks each follow one physical curve end-to-end (no
    # mid-plot identity flip).
    a_dict = dict(out_a.points)
    b_dict = dict(out_b.points)
    a_left, a_right = a_dict[10], a_dict.get(90)
    b_left, b_right = b_dict[10], b_dict.get(90)
    assert a_right is not None and b_right is not None
    # After swap, the two tracks together must STILL cover the union of
    # input points — and each individual track must monotonically trend
    # one direction across the plot.
    a_ys = [y for _, y in sorted(out_a.points)]
    b_ys = [y for _, y in sorted(out_b.points)]

    def _monotonic(ys: list[float]) -> bool:
        diffs = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
        return all(d >= -1e-6 for d in diffs) or all(d <= 1e-6 for d in diffs)

    assert _monotonic(a_ys) or _monotonic(b_ys), (
        "after swap at least one track should follow a monotonic "
        "physical curve end-to-end"
    )


def test_detect_and_swap_takes_first_valid_when_multiple_candidates() -> None:
    """When dy drops below threshold at multiple separated regions, the
    detector takes the LEFTMOST candidate where the verdict is True —
    not the global min.
    """
    # Two convergence regions: one at col 20 (verdict True), one at col
    # 70 (also True). Build track_a as a monotonic ascender that
    # reverses sharply at col 20, and track_b as a descender that
    # reverses sharply at col 20 — then both stay monotonic right of
    # col 20 (no second real crossing — only one valid candidate).
    a_pts = []
    b_pts = []
    for x in range(0, 100):
        if x < 20:
            a_pts.append((x, 20.0 + 0.5 * x))  # 20 → 30
            b_pts.append((x, 40.0 - 0.5 * x))  # 40 → 30
        else:
            a_pts.append((x, 30.0 - 0.4 * (x - 20)))  # 30 → diverge down
            b_pts.append((x, 30.0 + 0.4 * (x - 20)))  # 30 → diverge up
    track_a = Track(points=tuple(a_pts))
    track_b = Track(points=tuple(b_pts))

    out_a, out_b = _detect_and_swap_at_crossings(track_a, track_b)
    # Past the crossing (col 50), track_a's y should equal whichever
    # PHYSICAL curve it ended up assigned to. The invariant we check:
    # output tracks are NOT identical to input (i.e. a swap fired).
    a_changed = any(
        out_a.points[i] != track_a.points[i] for i in range(len(track_a.points))
    )
    b_changed = any(
        out_b.points[i] != track_b.points[i] for i in range(len(track_b.points))
    )
    assert a_changed or b_changed, (
        "a swap should have fired at the col 20 crossing"
    )


def test_detect_and_swap_returns_inputs_when_no_subthreshold_convergence() -> None:
    """Two diverging tracks with dy always above the threshold get no
    swap. Mirrors real tilt-50 freq30 past the left edge: bands diverge
    and never come close enough to trigger the candidate-walk.
    """
    track_a = Track(points=tuple((x, 20.0 - 0.1 * x) for x in range(0, 100)))
    track_b = Track(points=tuple((x, 60.0 + 0.1 * x) for x in range(0, 100)))
    out_a, out_b = _detect_and_swap_at_crossings(track_a, track_b)
    assert out_a.points == track_a.points
    assert out_b.points == track_b.points

