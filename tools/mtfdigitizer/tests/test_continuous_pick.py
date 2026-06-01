"""Tests for the continuous-pick curve extraction helpers."""

from __future__ import annotations

from mtfdigitizer.pipeline.continuous_pick import CurvePoints, _densify_curve


def test_densify_fills_missing_columns_by_linear_interpolation() -> None:
    sparse = CurvePoints(points=((0, 100.0), (4, 108.0)))
    dense = _densify_curve(sparse)
    assert dense.points == (
        (0, 100.0),
        (1, 102.0),
        (2, 104.0),
        (3, 106.0),
        (4, 108.0),
    )


def test_densify_preserves_curve_endpoints() -> None:
    sparse = CurvePoints(points=((10, 50.0), (15, 55.0), (25, 75.0)))
    dense = _densify_curve(sparse)
    assert dense.points[0] == (10, 50.0)
    assert dense.points[-1] == (25, 75.0)


def test_densify_does_not_extrapolate_beyond_first_or_last_anchor() -> None:
    sparse = CurvePoints(points=((100, 200.0), (110, 210.0)))
    dense = _densify_curve(sparse)
    xs = [x for x, _ in dense.points]
    assert min(xs) == 100
    assert max(xs) == 110


def test_densify_leaves_already_dense_curve_unchanged() -> None:
    dense_in = CurvePoints(points=tuple((x, float(x)) for x in range(5)))
    out = _densify_curve(dense_in)
    assert out.points == dense_in.points


def test_densify_returns_empty_curve_unchanged() -> None:
    assert _densify_curve(CurvePoints(points=())).points == ()


def test_densify_single_point_curve_unchanged() -> None:
    one = CurvePoints(points=((42, 99.0),))
    assert _densify_curve(one).points == ((42, 99.0),)
