"""Tests for the shared plot-box geometry primitives."""

from __future__ import annotations

from mtfdigitizer.plotbox_primitives import (
    cluster_consecutive,
    collapse_runs,
)


def test_cluster_consecutive_empty() -> None:
    assert cluster_consecutive([], gap=1) == []


def test_cluster_consecutive_single_value() -> None:
    assert cluster_consecutive([7], gap=3) == [[7]]


def test_cluster_consecutive_within_gap_groups() -> None:
    assert cluster_consecutive([1, 2, 4], gap=2) == [[1, 2, 4]]


def test_cluster_consecutive_exceeds_gap_splits() -> None:
    assert cluster_consecutive([1, 2, 5, 6], gap=1) == [[1, 2], [5, 6]]


def test_cluster_consecutive_gap_boundary_inclusive() -> None:
    assert cluster_consecutive([1, 4], gap=3) == [[1, 4]]
    assert cluster_consecutive([1, 5], gap=3) == [[1], [5]]


def test_cluster_consecutive_three_clusters() -> None:
    assert cluster_consecutive([0, 1, 10, 11, 12, 50], gap=2) == [
        [0, 1],
        [10, 11, 12],
        [50],
    ]


def test_collapse_runs_empty() -> None:
    assert collapse_runs([]) == []


def test_collapse_runs_single() -> None:
    assert collapse_runs([42]) == [42]


def test_collapse_runs_adjacent_returns_midpoint() -> None:
    assert collapse_runs([10, 11, 12]) == [11]


def test_collapse_runs_gapped_keeps_separate() -> None:
    assert collapse_runs([10, 11, 20, 21]) == [10, 20]


def test_collapse_runs_custom_max_gap() -> None:
    # (10+13)/2 = 11.5 -> 12 under banker's rounding
    assert collapse_runs([10, 13, 20], max_gap=3) == [12, 20]


def test_collapse_runs_midpoint_uses_run_endpoints() -> None:
    # midpoint takes first and last value of the run, not the mean
    assert collapse_runs([10, 11, 14], max_gap=3) == [12]
