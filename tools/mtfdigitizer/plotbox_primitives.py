"""Shared geometry primitives for plot-box detectors.

The brand-specific detectors (samyang_plotbox, ttartisan_plotbox,
fuji_plotbox, pipeline.plotbox for Sigma) each scan an MTF chart for
axis lines and gridlines, and each one needs to collapse the resulting
runs of adjacent pixel indices into single representative values or
clusters. Before this module each detector carried its own copy of the
same loop.

`cluster_consecutive` and `collapse_runs` are the only two primitives
duplicated across more than two call sites — image loading is handled
by `loader.load_chart_gray` / `loader.load_chart_bgr`; everything else
(axis-line thresholds, tick-label widths, frame-edge offsets) is
genuinely brand-specific and stays local.
"""

from __future__ import annotations


def cluster_consecutive(values: list[int], gap: int) -> list[list[int]]:
    """Group sorted integers into runs where consecutive values differ
    by at most `gap`.

    Used to convert sets of "qualifying" pixel rows or columns (e.g.
    every column with high vertical ink coverage) into discrete clusters
    representing distinct chart features (left frame vs right frame,
    each label below the x-axis, etc.).

    Empty input returns an empty list; a single-element input returns
    one single-element cluster.
    """
    if not values:
        return []
    clusters: list[list[int]] = [[values[0]]]
    for v in values[1:]:
        if v - clusters[-1][-1] <= gap:
            clusters[-1].append(v)
        else:
            clusters.append([v])
    return clusters


def collapse_runs(values: list[int], max_gap: int = 2) -> list[int]:
    """Collapse runs of adjacent integers into a single midpoint per run.

    Useful when an axis line or gridline is rendered 2-3 px thick and
    shows up as several adjacent rows in a horizontal-line scan. The
    midpoint of each run is the single y value the detector wants.

    `max_gap` controls how close two values must be to count as the
    same run. Default 2 px matches the gridline-thickness use case.
    """
    if not values:
        return []
    runs: list[list[int]] = [[values[0]]]
    for v in values[1:]:
        if v - runs[-1][-1] <= max_gap:
            runs[-1].append(v)
        else:
            runs.append([v])
    return [int(round((r[0] + r[-1]) / 2)) for r in runs]
