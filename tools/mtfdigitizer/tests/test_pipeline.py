"""Tests for the adaptive MTF extraction pipeline (#935).

Acceptance criteria from issue #935:

- Extracts curves per profile, reads at the 11 fixed points
- Same-color S/M separated by dash-width (connected components), not color
- Missing data reads as None, never fabricated (B2 preserved)
- Reproduces the reference set's shapes
- Tests pass

Plot boxes are pulled from `referenceset/charts.py` so the calibration
runner and the test suite use the same hand-measured boxes — see #953.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mtfdigitizer.pipeline import (
    SAMPLE_POINTS,
    ExtractedChart,
    PlotBox,
    SampledReading,
    extract_chart,
)
from mtfdigitizer.pipeline.sampling import sample_skeleton_at_fraction
from mtfdigitizer.pipeline.plotbox import (
    image_height_mm_to_x_pixel,
    x_pixel_to_image_height_mm,
    y_pixel_to_mtf,
)
from mtfdigitizer.pipeline.split import split_sm_by_cc_width
from mtfdigitizer.profiles import (
    SAMYANG_4COLOR_ALL_SOLID,
    SIGMA_2COLOR_SOLID_DASHED,
)
from mtfdigitizer.referenceset import REFERENCE_CHARTS


REPO_ROOT = Path(__file__).resolve().parents[3]


def _ref(slug: str) -> tuple[Path, PlotBox, float]:
    """Pull (chart_path, plot_box, image_height_mm) from the reference set.

    Tests use the same plot boxes the calibration runner uses, so re-measuring
    one only happens in `referenceset/charts.py`.
    """
    chart = next(c for c in REFERENCE_CHARTS if c.slug == slug)
    assert chart.plot_box is not None, f"{slug}: no plot_box in referenceset"
    box = PlotBox(
        x_left=chart.plot_box.x_left,
        x_right=chart.plot_box.x_right,
        y_top=chart.plot_box.y_top,
        y_bottom=chart.plot_box.y_bottom,
    )
    return REPO_ROOT / chart.chart_path, box, chart.image_height_mm


SIGMA_56_CHART, SIGMA_56_PLOT_BOX, _ = _ref("sigma-56mm-f1-4-dc-dn-c")
SAMYANG_85_CHART, SAMYANG_85_MAX_PLOT_BOX, _ = _ref("samyang-85mm-f1-4-as-if-umc")


def _ref_view_plot_box(slug: str, view_idx: int) -> PlotBox:
    """Pull the plot box for a specific view of a multi-view anchor.

    Samyang charts stack two apertures (max + stopped) in one PNG; each
    view has its own plot box. View 0 == max, view 1 == stopped.
    Per-view `y_top_insets` (#1271, ADR-067) are forwarded so the
    runtime PlotBox matches what production extraction uses.
    """
    chart = next(c for c in REFERENCE_CHARTS if c.slug == slug)
    view = chart.views[view_idx]
    box = view.plot_box
    assert box is not None, f"{slug} view {view_idx}: no plot_box"
    return PlotBox(
        x_left=box.x_left, x_right=box.x_right,
        y_top=box.y_top, y_bottom=box.y_bottom,
        y_top_insets=view.y_top_insets,
    )


SAMYANG_85_STOPPED_PLOT_BOX = _ref_view_plot_box(
    "samyang-85mm-f1-4-as-if-umc", 1,
)


# --- Acceptance: 11 fixed points ------------------------------------------


def test_sample_fractions_are_eleven_evenly_spaced() -> None:
    assert SAMPLE_POINTS == (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)


def test_extract_returns_exactly_eleven_readings() -> None:
    result = extract_chart(
        SAMYANG_85_CHART,
        SAMYANG_4COLOR_ALL_SOLID,
        SAMYANG_85_MAX_PLOT_BOX,
        image_height_mm=21.6,
    )
    assert isinstance(result, ExtractedChart)
    assert len(result.readings) == 11


def test_extract_position_mm_spans_zero_to_image_height() -> None:
    result = extract_chart(
        SAMYANG_85_CHART,
        SAMYANG_4COLOR_ALL_SOLID,
        SAMYANG_85_MAX_PLOT_BOX,
        image_height_mm=21.6,
    )
    assert result.readings[0].position_mm == 0.0
    assert result.readings[-1].position_mm == 21.6


# --- Acceptance: CC-split (same-color S/M, not by color) ------------------


def test_split_sm_by_cc_picks_longest_as_sagittal() -> None:
    """Build a synthetic skeleton: one long solid line + several short
    fragments. The longest CC must be tagged S; the rest M.
    """
    import numpy as np

    skeleton = np.zeros((50, 100), dtype=np.uint8)
    # Long solid horizontal line at row 20
    skeleton[20, 10:90] = 1
    # Three short dashed fragments at row 30
    skeleton[30, 10:18] = 1
    skeleton[30, 25:33] = 1
    skeleton[30, 40:48] = 1

    result = split_sm_by_cc_width(skeleton)
    assert result.sagittal[20, 50] == 1  # the long line
    assert result.meridional[30, 14] == 1  # one of the short fragments
    assert result.sagittal[30, 14] == 0  # short fragments NOT in sagittal
    assert result.meridional[20, 50] == 0  # long line NOT in meridional


def test_sigma_pipeline_actually_splits_s_from_m() -> None:
    """End-to-end Sigma extraction must produce distinct S and M readings;
    they share a color, so CC-split is the only way they're told apart."""
    result = extract_chart(
        SIGMA_56_CHART,
        SIGMA_2COLOR_SOLID_DASHED,
        SIGMA_56_PLOT_BOX,
        image_height_mm=14.0,
    )
    # Mid-chart: the S curve has data (longest CC).
    mid = result.readings[5]  # position 7.0mm
    assert mid.samples.get("freq10S") is not None, "Sigma 10S must be detectable mid-chart"
    assert mid.samples.get("freq30S") is not None, "Sigma 30S must be detectable mid-chart"
    # The S extraction works without confusing M's dashed fragments —
    # value sits in the expected 0.8-1.0 band, not at 0 (the impossible-zero
    # PR #931 guarded against).
    assert 0.80 <= mid.samples.get("freq10S") <= 1.00


# --- Acceptance: B2 — missing data reads as None, never fabricated --------


def test_b2_returns_none_when_skeleton_has_no_data_at_target() -> None:
    """Empty skeleton, sampled anywhere, must return None — not 0, not
    an interpolated guess."""
    import numpy as np

    empty = np.zeros((100, 200), dtype=np.uint8)
    plot_box = PlotBox(x_left=10, x_right=190, y_top=10, y_bottom=90)
    for fraction in SAMPLE_POINTS:
        assert sample_skeleton_at_fraction(empty, fraction, plot_box) is None


def test_intra_curve_interp_replaces_single_sister_fill_with_neighbour_mean() -> None:
    """#1254 — for a sister-filled cell whose neighbours are present and
    NOT sister-filled, the intra-curve interp post-pass replaces the
    cross-curve copy with the linear mean of the field's own neighbours.
    Continuity within one optical curve is a stronger prior than S=~M
    off-axis."""
    from mtfdigitizer.pipeline.pipeline import (
        _replace_sister_fills_with_intra_interp,
    )

    # 11 cells; index 5 was sister-filled with a diverging value (0.74)
    # while the field's own neighbours hold ~0.96.
    samples = {
        "freq30S": (0.96, 0.96, 0.97, 0.97, 0.97, 0.74, 0.96, 0.96, 0.95, 0.93, 0.92),
    }
    sister_filled = {
        "freq30S": (False, False, False, False, False, True, False, False, False, False, False),
    }
    out, count = _replace_sister_fills_with_intra_interp(samples, sister_filled)
    assert count["freq30S"] == 1
    assert out["freq30S"][5] == pytest.approx(0.965), (
        f"sister-filled cell at i=5 should become mean(0.97, 0.96)=0.965, "
        f"got {out['freq30S'][5]}"
    )
    # Non-sister-filled cells must not be touched.
    assert out["freq30S"][:5] == samples["freq30S"][:5]
    assert out["freq30S"][6:] == samples["freq30S"][6:]


def test_intra_curve_interp_handles_multi_cell_sister_fill_run() -> None:
    """#1254 / #1256 — a multi-cell run of sister-filled cells is linearly
    interpolated between its bracketing non-sister-filled endpoints.

    Original single-cell logic from #1254 handled isolated sister-fills
    only; #1256's Samyang 14mm stopped freq30S has a 6-cell run because
    its dark grey 30S curve visually overlaps the bright 10M curve mid-
    field, leaving no extractable ink for ~half the field. The 6 cells
    sister-filled from 30M (which sweeps 0.95->0.55) dragged 30S far
    below its true ~0.97 trajectory; linear interp between the run's
    bracketing real samples (~0.97 left, ~0.96 right) recovers the
    correct shape."""
    from mtfdigitizer.pipeline.pipeline import (
        _replace_sister_fills_with_intra_interp,
    )

    # 11 cells; indices 4 and 5 sister-filled with diverging values.
    samples = {
        "freq30S": (0.96, 0.96, 0.97, 0.97, 0.74, 0.73, 0.96, 0.96, 0.95, 0.93, 0.92),
    }
    sister_filled = {
        "freq30S": (False, False, False, False, True, True, False, False, False, False, False),
    }
    out, count = _replace_sister_fills_with_intra_interp(samples, sister_filled)
    assert count["freq30S"] == 2
    # Linear interp between values[3]=0.97 and values[6]=0.96, span=3:
    # i=4: 0.97 + (1/3)*(0.96-0.97) = 0.9666...
    # i=5: 0.97 + (2/3)*(0.96-0.97) = 0.9633...
    assert out["freq30S"][4] == pytest.approx(0.9666666666666667)
    assert out["freq30S"][5] == pytest.approx(0.9633333333333333)
    # Non-sister-filled cells untouched.
    assert out["freq30S"][:4] == samples["freq30S"][:4]
    assert out["freq30S"][6:] == samples["freq30S"][6:]


def test_intra_curve_interp_skips_run_touching_edge() -> None:
    """#1256 — when a sister-fill run touches the last index there is no
    right bracket, so the run cannot be interpolated. Sister fallback's
    S~=M approximation stands.

    (The mirror case at index 0 cannot happen in practice: center
    symmetry runs downstream and re-asserts S=M at frac 0.0 regardless
    of what happens here.)"""
    from mtfdigitizer.pipeline.pipeline import (
        _replace_sister_fills_with_intra_interp,
    )

    samples = {
        "freq30S": (0.96, 0.96, 0.97, 0.97, 0.96, 0.95, 0.93, 0.92, 0.74, 0.73, 0.72),
    }
    sister_filled = {
        "freq30S": (False, False, False, False, False, False, False, False, True, True, True),
    }
    out, count = _replace_sister_fills_with_intra_interp(samples, sister_filled)
    assert count["freq30S"] == 0
    assert out["freq30S"] == samples["freq30S"]


def test_intra_curve_interp_skips_edge_cells() -> None:
    """#1254 — cells at index 0 and the last index have only one neighbour
    and cannot be safely interpolated; leave them to sister fallback (or
    None) regardless of the sister-fill flag. Center symmetry handles
    index 0 separately downstream."""
    from mtfdigitizer.pipeline.pipeline import (
        _replace_sister_fills_with_intra_interp,
    )

    n = 11
    samples = {"freq30S": (0.50,) + (0.96,) * (n - 2) + (0.50,)}
    sister_filled = {"freq30S": (True,) + (False,) * (n - 2) + (True,)}
    out, count = _replace_sister_fills_with_intra_interp(samples, sister_filled)
    assert count["freq30S"] == 0
    assert out["freq30S"] == samples["freq30S"]


def test_sigma_dashed_M_curves_fully_covered_by_dp_bridging() -> None:
    """Under (SPLIT_BY_DASH, GEODESIC_DP) the dashed M curves are bridged
    end to end: the DP smoothness prior carries a continuous path across
    every dash gap, so both M fields report a value at all 11 samples
    instead of the None-at-gap behaviour of the legacy FREQUENCY dispatch.

    (Before #1015's DP port this chart left contrast10M at 4/11 and
    resolution30M at 3/11 defined; the gaps were dash periods, not
    genuine curve absence — exactly what the DP path is meant to fix.)"""
    result = extract_chart(
        SIGMA_56_CHART,
        SIGMA_2COLOR_SOLID_DASHED,
        SIGMA_56_PLOT_BOX,
        image_height_mm=14.0,
    )
    m_none = sum(
        1 for r in result.readings if r.samples.get("freq10M") is None or r.samples.get("freq30M") is None
    )
    assert m_none == 0, (
        "DP bridging should leave no None in the dashed M curves of a "
        f"full-field Sigma chart; got {m_none}"
    )


# --- Acceptance: reference set shapes reproduced --------------------------


def test_samyang_85_reproduces_reference_center_values() -> None:
    """REFERENCE_SET.md says: '10 lp/mm (dark red and pink) both start ~0.91,
    30S/30M start ~0.70'. Extracted values must sit within ±0.05 of those."""
    result = extract_chart(
        SAMYANG_85_CHART,
        SAMYANG_4COLOR_ALL_SOLID,
        SAMYANG_85_MAX_PLOT_BOX,
        image_height_mm=21.6,
    )
    center = result.readings[0]  # position 0.0mm
    assert center.samples.get("freq10S") is not None
    assert center.samples.get("freq10M") is not None
    assert center.samples.get("freq30S") is not None
    assert center.samples.get("freq30M") is not None
    assert 0.86 <= center.samples.get("freq10S") <= 0.96, (
        f"10S center: expected ~0.91, got {center.samples.get("freq10S"):.3f}"
    )
    assert 0.86 <= center.samples.get("freq10M") <= 0.96, (
        f"10M center: expected ~0.91, got {center.samples.get("freq10M"):.3f}"
    )
    assert 0.65 <= center.samples.get("freq30S") <= 0.75, (
        f"30S center: expected ~0.70, got {center.samples.get("freq30S"):.3f}"
    )
    assert 0.65 <= center.samples.get("freq30M") <= 0.75, (
        f"30M center: expected ~0.70, got {center.samples.get("freq30M"):.3f}"
    )


def test_samyang_85_10S_knees_down_at_edge() -> None:
    """REFERENCE_SET.md: '10S knees down sharply to ~0.78 at edge'."""
    result = extract_chart(
        SAMYANG_85_CHART,
        SAMYANG_4COLOR_ALL_SOLID,
        SAMYANG_85_MAX_PLOT_BOX,
        image_height_mm=21.6,
    )
    edge = result.readings[-1]  # position 21.6mm
    assert edge.samples.get("freq10S") is not None
    # Allow generous tolerance — anti-aliasing at the edge pushes values
    # a little lower than the eye-read shape. The key shape feature is
    # "drops sharply from ~0.91 center to ~0.78 edge", not exact value.
    assert edge.samples.get("freq10S") < 0.85, (
        f"10S edge should drop below 0.85, got {edge.samples.get("freq10S"):.3f}"
    )


def test_samyang_85_stopped_30S_no_sister_fill_spikes_mid_field() -> None:
    """#1254 regression — on the 85mm stopped panel, the 30S skeleton has
    single-column gaps at frac 0.6 and 0.8. Before the intra-curve interp
    post-pass, sister fallback copied 30M's value at those columns
    (~0.74, ~0.73), producing 0.226 / 0.222 spikes against EYE values of
    0.97 / 0.95 — because 30S and 30M legitimately diverge by ~0.2 MTF
    mid-field on this panel (30S flat ~0.97, 30M sweeps 0.95->0.55). The
    intra-curve interpolation pass replaces those sister-filled cells
    with the linear mean of the field's own neighbours. Lock both
    affected cells within tolerance so a future change to sister-fallback
    cannot silently re-introduce the spikes."""
    result = extract_chart(
        SAMYANG_85_CHART,
        SAMYANG_4COLOR_ALL_SOLID,
        SAMYANG_85_STOPPED_PLOT_BOX,
        image_height_mm=21.6,
    )
    frac_06 = result.readings[6].samples.get("freq30S")
    frac_08 = result.readings[8].samples.get("freq30S")
    assert frac_06 is not None, "30S at frac 0.6 must read a value (#1254)"
    assert frac_08 is not None, "30S at frac 0.8 must read a value (#1254)"
    assert 0.92 <= frac_06 <= 1.0, (
        f"30S at frac 0.6: expected ~0.97 (EYE), got {frac_06:.3f} — "
        f"value near 0.74 means sister fallback re-took mid-field (#1254)"
    )
    assert 0.90 <= frac_08 <= 1.0, (
        f"30S at frac 0.8: expected ~0.95 (EYE), got {frac_08:.3f} — "
        f"value near 0.73 means sister fallback re-took mid-field (#1254)"
    )


def test_samyang_14mm_stopped_30S_no_mid_field_sister_drag() -> None:
    """#1256 regression — on the 14mm stopped panel, the dark grey 30S
    curve visually overlaps the bright pink 10M for ~half the field, so
    the 30S skeleton is empty from frac 0.2 through frac 0.7. Before
    the multi-cell sister-fill interp, those 6 cells got sister-filled
    from 30M (which sweeps 0.95->0.55), dragging 30S down to ~0.92->0.89
    and producing a visible 'sudden jump' at frac 0.8 where 30S regains
    its own skeleton at the true ~0.96. Linear interp between the run's
    bracketing real samples (~0.97 at frac 0.1 and ~0.96 at frac 0.8)
    recovers the smooth flat trajectory the user reported as correct.
    Lock both ends of the interpolated run within tolerance."""
    SAMYANG_14_CHART, _, _ = _ref("samyang-14mm-f2-8-ed-as-if-umc")
    pb = _ref_view_plot_box("samyang-14mm-f2-8-ed-as-if-umc", 1)
    result = extract_chart(
        SAMYANG_14_CHART,
        SAMYANG_4COLOR_ALL_SOLID,
        pb,
        image_height_mm=21.6,
    )
    # frac 0.4 and 0.6 are inside the interpolated run; values should be
    # close to 0.97 (linear between ~0.97 left bracket and ~0.96 right).
    frac_04 = result.readings[4].samples.get("freq30S")
    frac_06 = result.readings[6].samples.get("freq30S")
    assert frac_04 is not None, "30S at frac 0.4 must read a value (#1256)"
    assert frac_06 is not None, "30S at frac 0.6 must read a value (#1256)"
    assert 0.94 <= frac_04 <= 1.0, (
        f"30S at frac 0.4: expected ~0.97, got {frac_04:.3f} — value "
        f"near 0.93 means multi-cell sister-fill run not interpolated "
        f"(#1256)"
    )
    assert 0.94 <= frac_06 <= 1.0, (
        f"30S at frac 0.6: expected ~0.97, got {frac_06:.3f} — value "
        f"near 0.91 means multi-cell sister-fill run not interpolated "
        f"(#1256)"
    )


def test_samyang_12mm_fisheye_stopped_per_hue_y_top_inset() -> None:
    """#1257 + #1271 regression — on the 12mm fisheye stopped panel, the
    bright red 10S curve at chart-y 578-580 emits grey AA halos at
    chart-y 577 AND chart-y 581-582 that qualify for the 30M-light-grey
    HSV band (S<40, V in [160,195]).

    The original #1257 fix bumped the whole stopped-panel y_top from 575
    to 583, which also clipped the red 10S core out of the plot box.
    That broke the 10S skeleton — sister-fill from 10M pulled freq10S
    down to ~0.93-0.97 at frac 0.5-0.7, and the coincident-top anchor
    (ADR-066/#1268) then propagated the drop into freq30S, leaving a
    0.03-0.07 residual underestimate on the stopped panel's high-MTF
    region (#1271).

    The replacement mechanism (ADR-067) keeps y_top=575 globally and
    declares a per-hue y_top inset of 8 only on `30M-light-grey`, so:
      - the 10S/10M masks see the full plot box (red curve preserved);
      - the 30M mask is trimmed past the contaminator's halo bands.

    Locks both: no spurious 30M chart-top ridge AND 10S/30S back to
    MTF~1.0 in the coincident-curve region.

    Halo-pair subtraction was rejected as a fix: a 10S-red -> 30M
    halo pair wipes out the 30M mask entirely on the 300mm reflex
    Tier 1 anchor where 30M and 10S are structurally coincident at
    MTF=1.0 across the field. The per-hue inset is the only fix that
    does not regress the anchor.
    """
    SAMYANG_12_CHART, _, _ = _ref("samyang-12mm-f2-8-ed-as-ncs-fish-eye")
    pb = _ref_view_plot_box("samyang-12mm-f2-8-ed-as-ncs-fish-eye", 1)
    # y_top stays at the un-inset detector value; the inset is per-hue.
    assert pb.y_top == 575, (
        f"stopped y_top expected 575 (un-inset, ADR-067), got {pb.y_top}"
    )
    assert ("30M-light-grey", 8) in pb.y_top_insets, (
        f"stopped panel must declare 30M-light-grey y_top_inset=8 "
        f"(#1271, ADR-067); got y_top_insets={pb.y_top_insets!r}"
    )
    result = extract_chart(
        SAMYANG_12_CHART,
        SAMYANG_4COLOR_ALL_SOLID,
        pb,
        image_height_mm=14.2,
    )
    # frac 0.6 was the original #1257 spike — extracted 30M should
    # match the legitimate curve's value (~0.62), not the spurious
    # MTF~1.0 chart-top pickup.
    frac_06 = result.readings[6].samples.get("freq30M")
    assert frac_06 is not None, "30M at frac 0.6 must read a value (#1257)"
    assert 0.50 <= frac_06 <= 0.75, (
        f"30M at frac 0.6: expected ~0.62 (legitimate curve), got "
        f"{frac_06:.3f} — value near 1.0 means chart-top AA halo "
        f"contamination not inset (#1257)"
    )
    # frac 0.7 was the worst #1271 residual cell (10S read 0.93 with
    # the global inset, dragging 30S to 0.93). Without the global inset
    # clipping the red curve, 10S reads ~1.0 again and 30S follows via
    # the coincident-top anchor.
    frac_07_10S = result.readings[7].samples.get("freq10S")
    frac_07_30S = result.readings[7].samples.get("freq30S")
    assert frac_07_10S is not None and frac_07_10S >= 0.97, (
        f"freq10S at frac 0.7: expected ~1.0 (red curve preserved), got "
        f"{frac_07_10S} — value near 0.93 means the global stopped y_top "
        f"inset is still clipping the red 10S core (#1271)"
    )
    assert frac_07_30S is not None and frac_07_30S >= 0.97, (
        f"freq30S at frac 0.7: expected ~1.0 (coincident with 10S at "
        f"top), got {frac_07_30S} — value near 0.93 means the "
        f"coincident-top anchor inherited a clipped 10S (#1271)"
    )


def test_samyang_300mm_reflex_coincident_top_fills_none_cells() -> None:
    """#1277 + ADR-069 regression — on
    `samyang-300mm-f6-3-ed-umc-cs-reflex` both panels show all four
    curves (10S red, 10M pink, 30S dark-grey, 30M light-grey) drawn
    coincident at MTF~1.0 across the full field. The bright 10
    strokes swamp the grey 30 strokes under anti-aliasing, leaving
    BOTH `freq30S` and `freq30M` skeletons completely empty across
    frac 0.1..0.5. Sister fallback cannot fire (both sisters are
    empty), and ADR-068's coincident-top anchor in its original form
    skipped these cells because they were `None`, not sister-filled.

    ADR-069 extends the anchor to fire on None cells too, including
    at frac=0.0: when `freq{lo}{D}` extracts at 0.985 (mild raster
    noise on a true-1.0 chart-top curve), copying that value into
    `freq{hi}{D}` keeps the physical invariant `lo >= hi` intact
    AND avoids a visible upward kink between ADR-066's exact-1.0
    center cell and ADR-069's 0.985 anchored cells at frac>=0.1.

    Expected post-ADR-069:
    - frac 0.0..0.5: freq30S=freq30M=~0.985 (filled from same-direction
      10 curve via ADR-069 — including center)
    - frac 0.6..1.0: extracted directly by the dispatch (~0.985)
    - center MUST match its neighbours so the polyline reads
      continuously without a frac 0.0->0.1 spike
    """
    chart_path, pb, image_height_mm = _ref(
        "samyang-300mm-f6-3-ed-umc-cs-reflex"
    )
    result = extract_chart(
        chart_path,
        SAMYANG_4COLOR_ALL_SOLID,
        pb,
        image_height_mm=image_height_mm,
    )
    # Every cell on every 30-lp/mm curve should now carry a value —
    # the polyline must render continuously from frac 0 to frac 1.
    for i, reading in enumerate(result.readings):
        for field in ("freq30S", "freq30M"):
            v = reading.samples.get(field)
            assert v is not None, (
                f"{field} at frac {i / 10:.1f}: expected a value "
                f"(ADR-069 anchor or ADR-066 center), got None — "
                f"polyline will break (#1277)"
            )
            assert 0.90 <= v <= 1.00, (
                f"{field} at frac {i / 10:.1f}: expected MTF in "
                f"[0.90, 1.00] (coincident with 10 curve at chart "
                f"top), got {v:.3f}"
            )
    # Center must match its neighbours so the polyline doesn't kink.
    # Both freq30S/30M anchored from freq10S/10M, which extract at
    # ~0.985 — no upward spike to 1.0 vs frac 0.1's 0.985.
    center_30S = result.readings[0].samples["freq30S"]
    next_30S = result.readings[1].samples["freq30S"]
    assert abs(center_30S - next_30S) < 0.01, (
        f"freq30S center={center_30S:.3f} vs frac=0.1={next_30S:.3f}: "
        f"expected within 0.01 so the polyline reads continuously. "
        f"A larger gap means ADR-066's exact-1.0 anchor fired at "
        f"center while ADR-069 anchored the rest to a noisier lo "
        f"value — produces a visible kink in the rendered SVG."
    )
    # Physical invariant: hi MTF cannot exceed lo MTF at any frac.
    center_10S = result.readings[0].samples["freq10S"]
    assert center_30S <= center_10S + 1e-6, (
        f"freq30S at center ({center_30S:.3f}) exceeds freq10S "
        f"({center_10S:.3f}) — physically impossible. ADR-066's 1.0 "
        f"anchor must NOT fire here when freq10S sits below 1.0."
    )
    # ADR-069 should have filled multiple None cells (frac 0.0..0.5+).
    assert result.coincident_anchor_count.get("freq30S", 0) >= 6, (
        "freq30S coincident_anchor_count: expected at least 6 None "
        "cells filled (frac 0.0..0.5), got "
        f"{result.coincident_anchor_count.get('freq30S', 0)}"
    )


def test_samyang_10mm_stopped_recovers_30S_30M_at_frac_zero() -> None:
    """#1267 + ADR-069 regression — on the samyang-10mm-f2-8-ed-as-ncs-cs
    stopped panel, the dark-grey 30S curve sits physically underneath
    the saturated-red 10S across the first ~25% of the field, so the
    HSV dispatch cannot separate them: the 30S skeleton's first ink is
    at chart-x 138 (frac ~0.25), and the 30M skeleton's first ink is
    at chart-x 44 (frac ~0.03). Both 30S[0] and 30M[0] are None after
    direct extraction, and sister fallback cannot fill either (it
    needs at least one side of the S/M pair to have a value).

    Originally #1267 was fixed by ADR-066's center-symmetry physics
    anchor (S=M=1.0 at the optical axis). ADR-069 supersedes that
    behaviour at this cell: when freq{lo}{D} at center reads below
    1.0 due to raster noise (here ~0.99 for freq10S), copying lo
    into hi keeps the physical invariant `hi <= lo` true and avoids
    a visible kink between center and frac=0.1. ADR-066 still fires
    on cells the pair gate or threshold rules out.

    The user-facing #1267 deliverable — polyline visibly starts at
    the y-axis instead of ~1.4mm in — is preserved either way."""
    SAMYANG_10_CHART, _, _ = _ref("samyang-10mm-f2-8-ed-as-ncs-cs")
    pb = _ref_view_plot_box("samyang-10mm-f2-8-ed-as-ncs-cs", 1)
    result = extract_chart(
        SAMYANG_10_CHART,
        SAMYANG_4COLOR_ALL_SOLID,
        pb,
        image_height_mm=14.2,
    )
    center = result.readings[0]
    for field in ("freq30S", "freq30M"):
        v = center.samples.get(field)
        assert v is not None, (
            f"{field} at frac=0.0 must be recovered (ADR-066 or "
            f"ADR-069), got None — polyline will not start at y-axis"
        )
        # Physical invariant: hi <= lo at every frac.
        lo_field = "freq10" + field[-1]
        lo_v = center.samples.get(lo_field)
        assert lo_v is not None
        assert v <= lo_v + 1e-6, (
            f"{field}={v:.4f} at center exceeds {lo_field}={lo_v:.4f} "
            f"— physically impossible"
        )
    # No kink: center matches frac=0.1 within tight tolerance so the
    # polyline reads continuously.
    next_30S = result.readings[1].samples["freq30S"]
    assert abs(center.samples["freq30S"] - next_30S) < 0.01, (
        f"freq30S center={center.samples['freq30S']:.4f} vs "
        f"frac=0.1={next_30S:.4f}: expected within 0.01 (no kink)"
    )


def test_samyang_af_12mm_stopped_anchors_10S_10M_at_frac_zero() -> None:
    """#1267 regression — companion of the 10mm test. On the AF 12mm
    stopped panel the freq10S and freq10M skeletons miss the leftmost
    columns; both must be anchored to MTF=1.0 at frac=0.0."""
    chart_path, _, _ = _ref("samyang-af-12mm-f2-0")
    pb = _ref_view_plot_box("samyang-af-12mm-f2-0", 1)
    result = extract_chart(
        chart_path,
        SAMYANG_4COLOR_ALL_SOLID,
        pb,
        image_height_mm=14.2,
    )
    center = result.readings[0]
    for field in ("freq10S", "freq10M"):
        v = center.samples.get(field)
        assert v is not None, (
            f"{field} at frac=0.0 must be center-anchored to 1.0 (#1267), "
            f"got None"
        )
        assert v == pytest.approx(1.0), (
            f"{field} at frac=0.0 expected 1.0 (B4 physics anchor), got {v}"
        )


def test_samyang_12mm_fisheye_stopped_anchors_all_four_at_frac_zero() -> None:
    """#1267 + #1271 — companion of the 10mm test, updated for ADR-067.

    Under #1257's original global stopped-panel y_top inset, the red 10S
    core was clipped out of the plot box, leaving freq10S/freq10M
    skeletons empty at frac=0.0 — the B4 physics anchor (ADR-066) then
    forced both to 1.0. ADR-067's per-hue inset removes the global
    clip, so the 10S core is now visible at frac=0.0 and the sampler
    reads a real value (~0.99) — close to but not exactly 1.0.

    Lock the regenerated behavior: all four fields read ~1.0 at the
    optical axis. The mechanism splits per pair:

      - 10S/10M now have direct ink at frac=0.0 (≥0.95);
      - 30S/30M skeletons remain empty (dark-grey coincident with red
        contaminator, light-grey trimmed by the per-hue inset) and
        still anchor to 1.0 via the physics rule.
    """
    chart_path, _, _ = _ref("samyang-12mm-f2-8-ed-as-ncs-fish-eye")
    pb = _ref_view_plot_box("samyang-12mm-f2-8-ed-as-ncs-fish-eye", 1)
    result = extract_chart(
        chart_path,
        SAMYANG_4COLOR_ALL_SOLID,
        pb,
        image_height_mm=14.2,
    )
    center = result.readings[0]
    for field in ("freq10S", "freq10M", "freq30S", "freq30M"):
        v = center.samples.get(field)
        assert v is not None, (
            f"{field} at frac=0.0 must be present after symmetry + "
            f"physics anchor (ADR-066), got None"
        )
        assert v >= 0.95, (
            f"{field} at frac=0.0 expected ~1.0 (top-plate), got {v}"
        )


def test_center_anchor_never_fires_when_either_side_has_value() -> None:
    """#1267 — the physics anchor must NOT fire when even one side of a
    pair has a value at frac=0.0. The existing symmetry rule (copy S to
    M, or copy the present side to the absent side) takes precedence;
    the anchor is the last-resort fallback only."""
    from mtfdigitizer.pipeline.pipeline import _apply_center_symmetry

    # S present, M None — existing rule: copy S to M; anchor must not fire.
    samples = {
        "freq10S": (0.97, 0.95, 0.90),
        "freq10M": (None, 0.93, 0.88),
    }
    out, anchor = _apply_center_symmetry(samples)
    assert out["freq10M"][0] == pytest.approx(0.97), (
        "M[0] should inherit S[0] when S has a value"
    )
    assert anchor["freq10S"] == 0 and anchor["freq10M"] == 0, (
        f"anchor must not fire when either side has a value, got {anchor}"
    )


def test_samyang_12mm_fisheye_stopped_30S_uses_10S_anchor() -> None:
    """#1269 regression — on the 12mm fisheye stopped panel, the dark-
    grey 30S curve is drawn coincident with dark-red 10S from 0mm to
    ~15mm (chart artist merged the two near-1.0 strokes into one
    visible line). The 30S skeleton is empty in that range; sister
    fallback was inheriting 30M's diving values (~0.5 at frac 0.7),
    producing a visible spike when 30S re-emerges at MTF~0.98 at
    frac 0.8.

    The coincident-top anchor overrides the wrong sister-fills with
    the matching 10S value when 10S is at MTF >= 0.90 (pinned at chart
    top), giving 30S a continuous trace from 1.0 at center down to
    the corner."""
    chart_path, _, _ = _ref("samyang-12mm-f2-8-ed-as-ncs-fish-eye")
    pb = _ref_view_plot_box("samyang-12mm-f2-8-ed-as-ncs-fish-eye", 1)
    result = extract_chart(
        chart_path,
        SAMYANG_4COLOR_ALL_SOLID,
        pb,
        image_height_mm=14.2,
    )
    # Pre-fix: frac 0.5/0.6/0.7 read sister-filled values 0.74/0.63/0.53
    # (inheriting 30M's dive). Post-fix: anchored to 10S, all > 0.85.
    for idx in (5, 6, 7):
        v = result.readings[idx].samples.get("freq30S")
        assert v is not None, f"freq30S at frac {idx/10} must read a value"
        assert v >= 0.85, (
            f"freq30S at frac {idx/10}: expected >= 0.85 (coincident with "
            f"10S at chart top), got {v:.3f} — coincident anchor not firing "
            f"(#1269)"
        )
    # The anchor must have fired (>=1 cell overridden on freq30S).
    assert result.coincident_anchor_count.get("freq30S", 0) >= 1, (
        f"coincident_anchor_count[freq30S] expected >= 1, got "
        f"{result.coincident_anchor_count.get('freq30S', 0)}"
    )


def test_coincident_anchor_fires_on_sister_filled_when_lo_above_threshold() -> None:
    """#1269 — sister-filled high-freq cell whose low-freq sister sits
    at MTF >= 0.90 must inherit the low-freq value, not the sister."""
    from mtfdigitizer.pipeline.pipeline import _apply_coincident_top_anchor

    samples = {
        "freq10S": (1.00, 0.99, 0.98, 0.95, 0.90),
        "freq30S": (0.50, 0.45, 0.40, 0.35, 0.30),  # all sister-filled
    }
    sister_filled = {
        "freq30S": (True, True, True, True, True),
        "freq10S": (False, False, False, False, False),
    }
    out, count = _apply_coincident_top_anchor(samples, sister_filled)
    # Indices 0..4: freq10S is 1.0, 0.99, 0.98, 0.95, 0.90 — all >= 0.90.
    # All five freq30S cells should be overridden.
    assert out["freq30S"] == (1.00, 0.99, 0.98, 0.95, 0.90)
    assert count["freq30S"] == 5


def test_coincident_anchor_does_not_fire_when_lo_below_threshold() -> None:
    """#1269 — when the low-freq curve has dipped below 0.90, the
    coincidence assumption breaks; keep the sister-fill value."""
    from mtfdigitizer.pipeline.pipeline import _apply_coincident_top_anchor

    samples = {
        "freq10S": (1.00, 0.85, 0.70),  # second and third below 0.90
        "freq30S": (0.40, 0.30, 0.20),
    }
    sister_filled = {
        "freq30S": (True, True, True),
        "freq10S": (False, False, False),
    }
    out, count = _apply_coincident_top_anchor(samples, sister_filled)
    # Only index 0 has 10S >= 0.90 — only that cell should be anchored.
    assert out["freq30S"][0] == pytest.approx(1.00)
    assert out["freq30S"][1] == pytest.approx(0.30)
    assert out["freq30S"][2] == pytest.approx(0.20)
    assert count["freq30S"] == 1


def test_coincident_anchor_does_not_fire_when_not_sister_filled() -> None:
    """#1269 — cells with their own extracted value must not be
    overridden, even when the lower-freq curve sits high. The rule
    only repairs sister-fill errors."""
    from mtfdigitizer.pipeline.pipeline import _apply_coincident_top_anchor

    samples = {
        "freq10S": (1.00, 1.00, 0.98),
        "freq30S": (0.95, 0.93, 0.90),  # all genuinely extracted
    }
    sister_filled = {
        "freq30S": (False, False, False),
        "freq10S": (False, False, False),
    }
    out, count = _apply_coincident_top_anchor(samples, sister_filled)
    assert out["freq30S"] == (0.95, 0.93, 0.90)
    assert count["freq30S"] == 0


def test_coincident_anchor_gated_off_when_curves_independent() -> None:
    """#1269 — when the chart has genuinely separate hi/lo curves (lo
    sits at chart top, hi sits 0.3+ MTF below), the anchor must NOT
    fire even if the lo curve is >= 0.90. The gate measures median
    |hi - lo| on cells where both are genuinely extracted; if that
    exceeds 0.05 the anchor is disabled for the pair to avoid
    corrupting sister-filled hi cells with the diverged lo value.

    Catches the samyang-85mm regression: freq10M at MTF 0.91, freq30M
    legitimately at MTF 0.6 across mid-field; 4 of 11 freq30M cells
    are sister-filled. Without the gate the anchor would copy 0.91+
    into those cells, producing 0.3+ MTF errors against ground truth."""
    from mtfdigitizer.pipeline.pipeline import _apply_coincident_top_anchor

    samples = {
        # freq10M pinned at chart top (>= 0.90 across the board)
        "freq10M": (0.92, 0.92, 0.91, 0.91, 0.91, 0.91, 0.91, 0.92, 0.92),
        # freq30M sits ~0.30 below — genuinely separate curve.
        # 3 cells extracted independently (0.62, 0.61, 0.60 — well clear
        # of freq10M), 6 cells were sister-filled.
        "freq30M": (0.62, None, None, None, 0.61, None, None, None, 0.60),
    }
    # Mark the None cells as sister-filled (in real flow they'd be filled
    # from freq30S; here we just simulate the post-sister-fill state).
    samples_filled = {
        "freq10M": samples["freq10M"],
        "freq30M": tuple(
            v if v is not None else 0.91 for v in samples["freq30M"]
        ),
    }
    sister_filled = {
        "freq10M": (False,) * 9,
        "freq30M": tuple(v is None for v in samples["freq30M"]),
    }
    out, count = _apply_coincident_top_anchor(samples_filled, sister_filled)
    # Gate must disable the anchor: every cell stays at its (sister-filled)
    # value of 0.91 — not anchor-overridden to 0.91 again, since the gate
    # prevents firing entirely.
    assert count["freq30M"] == 0, (
        f"anchor must not fire when median |hi-lo| on clean cells "
        f"exceeds 0.05 (curves clearly separate), got "
        f"count={count['freq30M']}"
    )
    # Sister-filled values remain unchanged (the gate skips override).
    for i in (1, 2, 3, 5, 6, 7):
        assert out["freq30M"][i] == pytest.approx(0.91), (
            f"cell {i} should keep sister-fill value 0.91, "
            f"got {out['freq30M'][i]}"
        )


def test_coincident_anchor_handles_meridional() -> None:
    """#1269 — anchor must work on M direction too, not just S."""
    from mtfdigitizer.pipeline.pipeline import _apply_coincident_top_anchor

    samples = {
        "freq10M": (1.00, 0.95),
        "freq30M": (0.50, 0.45),
    }
    sister_filled = {
        "freq30M": (True, True),
        "freq10M": (False, False),
    }
    out, count = _apply_coincident_top_anchor(samples, sister_filled)
    assert out["freq30M"] == (1.00, 0.95)
    assert count["freq30M"] == 2


def test_center_anchor_fires_when_both_sides_none() -> None:
    """#1267 — when BOTH freq{N}S[0] and freq{N}M[0] are None AND no
    lower-freq same-direction value is available, anchor both to
    MTF=1.0 and report the counts."""
    from mtfdigitizer.pipeline.pipeline import _apply_center_symmetry

    samples = {
        "freq30S": (None, 0.95, 0.90),
        "freq30M": (None, 0.93, 0.88),
    }
    out, anchor = _apply_center_symmetry(samples)
    assert out["freq30S"][0] == pytest.approx(1.0)
    assert out["freq30M"][0] == pytest.approx(1.0)
    # Other indices must remain untouched — the rule is frac=0.0 only.
    assert out["freq30S"][1:] == (0.95, 0.90)
    assert out["freq30M"][1:] == (0.93, 0.88)
    assert anchor["freq30S"] == 1 and anchor["freq30M"] == 1


def test_center_anchor_uses_lo_when_available() -> None:
    """ADR-072 (#1279) — when both freq{hi}{S}[0] and freq{hi}{M}[0]
    are None at center BUT same-direction lower-freq cells carry
    values, anchor from those values to preserve the physical
    invariant freq{hi}{D}[0] <= freq{lo}{D}[0].

    Replays viltrox-75 f/1.2: freq30 buried at center, freq10
    extracted at 0.99 — anchor freq30 to 0.99, not 1.0."""
    from mtfdigitizer.pipeline.pipeline import _apply_center_symmetry

    samples = {
        "freq10S": (0.99, 0.99, 0.98),
        "freq10M": (0.99, 0.94, 0.95),
        "freq30S": (None, None, None),
        "freq30M": (None, None, None),
    }
    out, anchor = _apply_center_symmetry(samples)
    # freq10S/M: case 1 (both extracted) — S wins, M overridden.
    assert out["freq10S"][0] == pytest.approx(0.99)
    assert out["freq10M"][0] == pytest.approx(0.99)
    # freq30S/M: ADR-072 anchors from freq10 instead of 1.0.
    assert out["freq30S"][0] == pytest.approx(0.99)
    assert out["freq30M"][0] == pytest.approx(0.99)
    # Anchor counter records only the both-None fills (freq30 pair).
    assert anchor["freq30S"] == 1 and anchor["freq30M"] == 1
    assert anchor["freq10S"] == 0 and anchor["freq10M"] == 0


def test_center_anchor_cross_direction_fallback() -> None:
    """ADR-072 — when same-direction lo is None but cross-direction lo
    has a value, fall back to cross-direction. S=M at the optical axis
    by B4, so either direction is a valid anchor."""
    from mtfdigitizer.pipeline.pipeline import _apply_center_symmetry

    samples = {
        # freq10M[0]=None but freq10S[0]=0.97 is available.
        "freq10S": (0.97, 0.95, 0.93),
        "freq10M": (None, 0.94, 0.92),
        "freq30S": (None, None, None),
        "freq30M": (None, None, None),
    }
    out, anchor = _apply_center_symmetry(samples)
    # freq10: case 2 (M None, S present) — copy S to M.
    assert out["freq10M"][0] == pytest.approx(0.97)
    # freq30S: same-direction lo (freq10S=0.97) exists, use it.
    assert out["freq30S"][0] == pytest.approx(0.97)
    # freq30M: same-direction lo (freq10M) was None going in but case 2
    # filled it with 0.97 before freq30 iteration if order permits.
    # Order-independent fallback chain: when same-dir is None at lookup
    # time, cross-dir gives 0.97. Either path yields 0.97.
    assert out["freq30M"][0] == pytest.approx(0.97)
    assert anchor["freq30S"] == 1 and anchor["freq30M"] == 1


def test_center_anchor_falls_back_to_1_when_no_lower_freq() -> None:
    """ADR-072 — single-frequency chart (only freq30 present), both
    None at center, no lower freq to anchor from: fall back to 1.0.
    Preserves ADR-066 behaviour for charts without a freq10."""
    from mtfdigitizer.pipeline.pipeline import _apply_center_symmetry

    samples = {
        "freq30S": (None, 0.85, 0.80),
        "freq30M": (None, 0.83, 0.78),
    }
    out, anchor = _apply_center_symmetry(samples)
    assert out["freq30S"][0] == pytest.approx(1.0)
    assert out["freq30M"][0] == pytest.approx(1.0)
    assert anchor["freq30S"] == 1 and anchor["freq30M"] == 1


def test_center_anchor_chains_through_anchored_lo() -> None:
    """ADR-072 — when freq10 itself enters _apply_center_symmetry with
    both None, it anchors to 1.0 (no lower freq). When freq30 iterates
    next, freq10 is now 1.0 — so freq30 anchors to 1.0 too. Replays
    samyang-af-12mm stopped (10S+10M None AND 30S+30M None)."""
    from mtfdigitizer.pipeline.pipeline import _apply_center_symmetry

    samples = {
        "freq10S": (None, 0.99, 0.98),
        "freq10M": (None, 0.99, 0.96),
        "freq30S": (None, 0.95, 0.85),
        "freq30M": (None, 0.93, 0.83),
    }
    out, anchor = _apply_center_symmetry(samples)
    # freq10 anchors to 1.0 (no lo).
    assert out["freq10S"][0] == pytest.approx(1.0)
    assert out["freq10M"][0] == pytest.approx(1.0)
    # freq30 sees freq10=1.0 and inherits it.
    assert out["freq30S"][0] == pytest.approx(1.0)
    assert out["freq30M"][0] == pytest.approx(1.0)
    assert anchor["freq10S"] == 1 and anchor["freq10M"] == 1
    assert anchor["freq30S"] == 1 and anchor["freq30M"] == 1


def test_sigma_56_10S_holds_high_until_knee() -> None:
    """REFERENCE_SET.md: 'Sigma 10S solid ~0.97 flat from 0 to ~10mm,
    then knees down'."""
    result = extract_chart(
        SIGMA_56_CHART,
        SIGMA_2COLOR_SOLID_DASHED,
        SIGMA_56_PLOT_BOX,
        image_height_mm=14.0,
    )
    # Read at position 4 (~5.6mm) — well inside the flat region
    flat = result.readings[4]
    assert flat.samples.get("freq10S") is not None
    assert 0.93 <= flat.samples.get("freq10S") <= 1.00, (
        f"Sigma 10S at 5.6mm: expected ~0.97, got {flat.samples.get("freq10S"):.3f}"
    )


def test_sigma_56_reads_at_both_chart_edges() -> None:
    """#954 regression — extract_chart MUST return a value at fractions
    0.0 and 1.0 on the Sigma chart. Both edges returned None before the
    plot-box convention was fixed (axis-line measurement instead of
    data-edge). A future re-measurement that drifts back to the axis
    line would silently re-break boundary readings."""
    result = extract_chart(
        SIGMA_56_CHART,
        SIGMA_2COLOR_SOLID_DASHED,
        SIGMA_56_PLOT_BOX,
        image_height_mm=14.0,
    )
    center = result.readings[0]   # fraction 0.0
    edge = result.readings[-1]    # fraction 1.0
    assert center.samples.get("freq10S") is not None, (
        "Sigma 10S at fraction 0.0 must read a value, not None (#954)"
    )
    assert center.samples.get("freq30S") is not None, (
        "Sigma 30S at fraction 0.0 must read a value, not None (#954)"
    )
    assert edge.samples.get("freq10S") is not None, (
        "Sigma 10S at fraction 1.0 must read a value, not None (#954)"
    )
    assert edge.samples.get("freq30S") is not None, (
        "Sigma 30S at fraction 1.0 must read a value, not None (#954)"
    )


# --- Plot-box arithmetic --------------------------------------------------


def test_y_pixel_to_mtf_top_is_one() -> None:
    box = PlotBox(x_left=10, x_right=110, y_top=20, y_bottom=120)
    assert y_pixel_to_mtf(20, box) == pytest.approx(1.0)


def test_y_pixel_to_mtf_bottom_is_zero() -> None:
    box = PlotBox(x_left=10, x_right=110, y_top=20, y_bottom=120)
    assert y_pixel_to_mtf(120, box) == pytest.approx(0.0)


def test_x_pixel_to_image_height_mm_roundtrip() -> None:
    box = PlotBox(x_left=100, x_right=500, y_top=0, y_bottom=200)
    image_height_mm = 14.0
    for mm in (0.0, 3.5, 7.0, 14.0):
        x = image_height_mm_to_x_pixel(mm, box, image_height_mm)
        back = x_pixel_to_image_height_mm(x, box, image_height_mm)
        assert back == pytest.approx(mm, abs=1e-6)


# --- CC_RANK_BY_MEAN_Y dispatch (#992) ----------------------------------


def test_cc_rank_split_at_largest_y_gap_separates_two_clusters() -> None:
    """Four CCs at y=10, 12, 80, 82 must split into (10, 12) and (80, 82) —
    the largest gap sits at 12→80."""
    import numpy as np

    from mtfdigitizer.pipeline.dispatch import (
        _component_masks_with_mean_y,
        _split_components_at_largest_y_gap,
    )

    skeleton = np.zeros((100, 200), dtype=np.uint8)
    skeleton[10, 10:60] = 1   # long solid, upper
    skeleton[12, 70:90] = 1   # short dashed fragment, upper
    skeleton[80, 10:60] = 1   # long solid, lower
    skeleton[82, 70:90] = 1   # short dashed fragment, lower

    components = _component_masks_with_mean_y(skeleton)
    assert len(components) == 4
    upper, lower = _split_components_at_largest_y_gap(components)
    assert len(upper) == 2
    assert len(lower) == 2
    upper_ys = [np.nonzero(m)[0].mean() for m in upper]
    lower_ys = [np.nonzero(m)[0].mean() for m in lower]
    assert max(upper_ys) < min(lower_ys)


def test_cc_rank_solid_dashed_picks_longest_as_solid() -> None:
    """Inside a cluster, the largest CC by area is the solid line; the
    rest are ORed into the dashed mask."""
    import numpy as np

    from mtfdigitizer.pipeline.dispatch import _solid_dashed_from_components

    long_solid = np.zeros((20, 100), dtype=np.uint8)
    long_solid[5, 10:90] = 1
    short_frag_a = np.zeros((20, 100), dtype=np.uint8)
    short_frag_a[8, 10:25] = 1
    short_frag_b = np.zeros((20, 100), dtype=np.uint8)
    short_frag_b[8, 40:55] = 1

    solid, dashed = _solid_dashed_from_components(
        [short_frag_a, long_solid, short_frag_b]
    )
    assert solid is not None and dashed is not None
    assert solid[5, 50] == 1  # the long line is solid
    assert dashed[8, 15] == 1 and dashed[8, 45] == 1  # both short frags
    assert dashed[5, 50] == 0  # long line not in dashed


def test_cc_rank_solid_dashed_handles_single_component() -> None:
    """One CC in a cluster — solid gets it, dashed is None (no fragments)."""
    import numpy as np

    from mtfdigitizer.pipeline.dispatch import _solid_dashed_from_components

    only = np.zeros((20, 100), dtype=np.uint8)
    only[5, 10:90] = 1

    solid, dashed = _solid_dashed_from_components([only])
    assert solid is not None
    assert dashed is None


def test_ridge_tracking_dispatch_end_to_end_with_viltrox_chart() -> None:
    """End-to-end Viltrox extraction via RIDGE_TRACKING must recover all
    four curves — the calibration regression test for #994.

    Prior dispatches failed on this chart in different ways:
    - Y_BAND_IS_FREQUENCY (run 3) — 30 lp/mm |d| 0.258-0.524, 30M 1/11
    - CC_RANK_BY_MEAN_Y (run 4) — 10S paired 11/11 but reading the
      printed top plot-box border (mapped to MTF=1.0 by a wrong plot
      box that put OTF=1.0 at the "1" label rather than at the gridline
      23 px below); 10M dropped to 0/11
    - RIDGE_TRACKING (run 5) — all four fields paired >=3/11 with med
      |d| <= 0.05; the 10S reading is the actual curve, not the border

    The assertions pin: every field paired >= the run-5 minimums, and
    every value in [0, 1].
    """
    from mtfdigitizer.profiles import VILTROX_BW_DASHED_F12

    viltrox_chart, viltrox_box, viltrox_height = _ref("viltrox-af-75mm-f1-2-pro")
    result = extract_chart(
        viltrox_chart,
        VILTROX_BW_DASHED_F12,
        viltrox_box,
        image_height_mm=viltrox_height,
    )

    paired_counts = {
        "contrast10S": sum(1 for r in result.readings if r.samples.get("freq10S") is not None),
        "contrast10M": sum(1 for r in result.readings if r.samples.get("freq10M") is not None),
        "resolution30S": sum(1 for r in result.readings if r.samples.get("freq30S") is not None),
        "resolution30M": sum(1 for r in result.readings if r.samples.get("freq30M") is not None),
    }
    # Run-5 measured: 10S 11, 10M 5, 30S 7, 30M 3. Asserts hold one less
    # than measured to allow for incidental change without churning the
    # test, while still pinning the "all four fields produce data" win.
    assert paired_counts["contrast10S"] >= 10
    assert paired_counts["contrast10M"] >= 4
    assert paired_counts["resolution30S"] >= 6
    assert paired_counts["resolution30M"] >= 2

    all_values = [
        v
        for r in result.readings
        for v in (r.samples.get("freq10S"), r.samples.get("freq10M"), r.samples.get("freq30S"), r.samples.get("freq30M"))
        if v is not None
    ]
    for v in all_values:
        assert 0.0 <= v <= 1.0, f"value {v} outside [0, 1] range"


# --- Profile dispatch fail-loud -----------------------------------------


def test_extract_raises_for_unimplemented_profile_dispatch() -> None:
    """A profile with an undeclared (style_axis, hue_meaning) combination
    must raise — never silently mis-extract."""
    from mtfdigitizer.profiles.types import HueRange, MtfProfile

    weird = MtfProfile(
        name="weird",
        hues=(HueRange(name="something", h_lo=0, h_hi=10),),
        style_axis="SPLIT_BY_DASH",
        hue_meaning="CURVE_IDENTITY",  # not (SPLIT_BY_DASH, FREQUENCY)
        frequencies_lpmm=(10,),
    )
    with pytest.raises(NotImplementedError):
        extract_chart(
            SAMYANG_85_CHART,
            weird,
            SAMYANG_85_MAX_PLOT_BOX,
            image_height_mm=21.6,
        )


def test_max_10_black_admits_red_stained_overlap_pixels() -> None:
    """The f/2 black solid line can physically overlap the f/8 red lines
    on the right-edge crossing. The PNG renderer blends the colors,
    producing pixels with V<55 but S=255 (low-V red). These are genuinely
    black ink stained red by the overlap — they must be admitted to the
    `max-10-black` mask, not the `stopped-10-red` mask. See #1159.

    Verify with a synthetic HSV pixel matching the failure case at the
    7.5 fisheye max-aperture chart, x=552 y=146: H=0, S=255, V=41."""
    import numpy as np
    from mtfdigitizer.pipeline.masks import masks_by_curve_name
    from mtfdigitizer.profiles.declared import TTARTISAN_4COLOR_DUAL_APERTURE

    # Build a 1x1 HSV image with the stained-black pixel.
    hsv = np.array([[[0, 255, 41]]], dtype=np.uint8)
    masks = masks_by_curve_name(hsv, TTARTISAN_4COLOR_DUAL_APERTURE)

    # The pixel must land in max-10-black (the overlap-recovery branch).
    assert masks["max-10-black"][0, 0], (
        "V<55 pixel was rejected; the overlap-recovery HueRange entry "
        "(s_max=255, v_max=55) is missing or mis-configured."
    )


def test_ttartisan_stopped_30_orange_opts_into_y_anchor() -> None:
    """#1168: the TTartisan `stopped-30-orange` HueRange opts into the
    ridge DP's y-anchor mode. Without it, the unanchored DP swaps S/M
    curve identity per column at dash gaps on the tilt-50 stopped pass
    (where the solid S30 and dashed T30 cross near MTF 0.71 mid-field),
    producing alternating 0.71/0.55 readings."""
    from mtfdigitizer.profiles.declared import TTARTISAN_4COLOR_DUAL_APERTURE

    orange_hues = [
        h for h in TTARTISAN_4COLOR_DUAL_APERTURE.hues
        if h.name == "stopped-30-orange"
    ]
    assert orange_hues, "stopped-30-orange HueRange missing from profile"
    for h in orange_hues:
        assert h.dp_y_anchor is True, (
            f"stopped-30-orange must opt into y_anchor (#1168); got "
            f"dp_y_anchor={h.dp_y_anchor}."
        )


def test_max_30_grey_keeps_default_y_anchor() -> None:
    """`max-30-grey` MUST NOT enable y_anchor. The freq30 max-aperture
    pass has legitimate large dives (the 7.5 fisheye 30M corner case
    documented in #1157); anchoring would punish them and regress the
    #1157 fix. Lock the default in a test so a future per-hue tuning
    pass doesn't silently flip it."""
    from mtfdigitizer.profiles.declared import TTARTISAN_4COLOR_DUAL_APERTURE

    grey = [
        h for h in TTARTISAN_4COLOR_DUAL_APERTURE.hues
        if h.name == "max-30-grey"
    ]
    assert grey, "max-30-grey HueRange missing from profile"
    for h in grey:
        assert h.dp_y_anchor is None, (
            f"max-30-grey must NOT enable y_anchor (would regress "
            f"#1157 corner fix); got dp_y_anchor={h.dp_y_anchor}."
        )


def test_max_10_black_does_not_collide_with_max_30_grey() -> None:
    """The overlap-recovery rule v_max=55 must not catch pixels meant
    for the grey 30 lp/mm mask (V in [90, 160])."""
    import numpy as np
    from mtfdigitizer.pipeline.masks import masks_by_curve_name
    from mtfdigitizer.profiles.declared import TTARTISAN_4COLOR_DUAL_APERTURE

    # A pixel at the bottom of the grey V band; low S to qualify for grey.
    hsv = np.array([[[0, 20, 95]]], dtype=np.uint8)
    masks = masks_by_curve_name(hsv, TTARTISAN_4COLOR_DUAL_APERTURE)

    assert not masks["max-10-black"][0, 0], (
        "V=95 pixel landed in black mask — overlap-recovery rule is "
        "leaking into the grey V band."
    )
    assert masks["max-30-grey"][0, 0], (
        "V=95 pixel did not land in grey mask — grey rule regressed."
    )


def test_edge_bracket_extends_inward_at_left_corner() -> None:
    """TTartisan chart templates render curves with up to 8 px of slack
    between the printed plot axis and where the curves actually start.
    At fraction=0.0 the sampler must extend its bracket INWARD (to the
    right) by up to _EDGE_BRACKET_INWARD px to find the curve, while
    keeping the leftward search tight (never reaching past x_left into
    chrome). #1163-followup."""
    import numpy as np
    from mtfdigitizer.pipeline.sampling import sample_skeleton_at_fraction

    # 100x200 image, plot_box spans full width/height.
    # Skeleton has a single pixel at x=14 (4 px in from the left edge
    # at x_left=10, within the 5-px edge-bracket window). The standard
    # ±3 window from target_x=10 (fraction=0.0) looks in [7, 13] and
    # would miss x=14.
    skeleton = np.zeros((100, 200), dtype=np.uint8)
    skeleton[50, 14] = 1
    plot_box = PlotBox(x_left=10, x_right=190, y_top=10, y_bottom=90)
    # Standard ±3 window misses; edge-widened window catches.
    result = sample_skeleton_at_fraction(skeleton, 0.0, plot_box)
    assert result is not None, (
        "Edge-bracket should reach inward to find the curve 1 px past "
        "the standard ±3 bracket boundary."
    )


def test_edge_bracket_extends_inward_at_right_corner() -> None:
    """Same as the left-corner case but at the right edge: at
    fraction=1.0 the sampler extends INWARD (leftward) to find a curve
    that ends a few px before the printed plot axis."""
    import numpy as np
    from mtfdigitizer.pipeline.sampling import sample_skeleton_at_fraction

    skeleton = np.zeros((100, 200), dtype=np.uint8)
    # Pixel 4 px in from the right edge (x=186 when x_right=190), within
    # the 5-px edge-bracket window. Standard ±3 misses, edge-widened catches.
    skeleton[50, 186] = 1
    plot_box = PlotBox(x_left=10, x_right=190, y_top=10, y_bottom=90)
    result = sample_skeleton_at_fraction(skeleton, 1.0, plot_box)
    assert result is not None, (
        "Edge-bracket should reach inward (leftward) to find the curve "
        "4 px past the standard right-edge ±3 bracket boundary."
    )


def test_edge_bracket_caps_at_inward_distance() -> None:
    """The edge-widened bracket caps at _EDGE_BRACKET_INWARD (5). A
    pixel beyond that range (e.g. 8 px in) still returns None — the
    B2 fail-safe contract is preserved past the widened window."""
    import numpy as np
    from mtfdigitizer.pipeline.sampling import sample_skeleton_at_fraction

    skeleton = np.zeros((100, 200), dtype=np.uint8)
    # Pixel 8 px in from the left edge — beyond the 5-px window.
    skeleton[50, 18] = 1
    plot_box = PlotBox(x_left=10, x_right=190, y_top=10, y_bottom=90)
    result = sample_skeleton_at_fraction(skeleton, 0.0, plot_box)
    assert result is None, (
        "Edge-bracket must cap at _EDGE_BRACKET_INWARD; reaching further "
        "would violate the B2 fail-safe contract on charts with sharp "
        "corner crashes."
    )


def test_edge_bracket_does_not_widen_at_mid_field() -> None:
    """The widened bracket triggers ONLY when target_x is within
    _BRACKET_HALF_WIDTH of the plot edge. Mid-field samples keep the
    standard ±3 window — never extrapolate across dash gaps further
    than the existing tolerance."""
    import numpy as np
    from mtfdigitizer.pipeline.sampling import sample_skeleton_at_fraction

    # Skeleton has a pixel 8 px from the target column at fraction=0.5.
    # That pixel is mid-field, the standard ±3 window should miss it.
    skeleton = np.zeros((100, 200), dtype=np.uint8)
    plot_box = PlotBox(x_left=10, x_right=190, y_top=10, y_bottom=90)
    # fraction=0.5 → target_x = 10 + 0.5*180 = 100. Place pixel at 108
    # (just outside ±3 window). If the bracket widened to 10 here, this
    # would be found.
    skeleton[50, 108] = 1
    result = sample_skeleton_at_fraction(skeleton, 0.5, plot_box)
    assert result is None, (
        "Mid-field sampler must keep the tight ±3 window — bridging "
        "wider than that breaks the B2 fail-safe contract."
    )


def test_strip_plot_box_borders_zeroes_dense_right_edge_column() -> None:
    """#1217 Option 4: a plot-box border line drawn INSIDE the data-edge
    plot box (e.g. af-35 grey mask col 603 with x_right=607) appears as a
    high-density vertical column. Strip it so the DP does not lock onto
    chart decoration."""
    import numpy as np
    from mtfdigitizer.pipeline.masks import strip_plot_box_borders

    # 100x200 image, plot box [10, 190] x [10, 90]; plot height = 81 px.
    mask = np.zeros((100, 200), dtype=bool)
    # Real curve: 5 px in col 600-equivalent (col 185 in this scaled box).
    for y in [20, 21, 22, 23, 24]:
        mask[y, 185] = True
    # Plot-box border: 70 px (>50% of 81-px plot height) at col 188,
    # 2 px inside x_right=190.
    for y in range(15, 85):
        mask[y, 188] = True

    plot_box = PlotBox(x_left=10, x_right=190, y_top=10, y_bottom=90)
    out = strip_plot_box_borders({"grey": mask}, plot_box)

    # Real curve preserved.
    assert out["grey"][20:25, 185].all(), (
        "Real-curve column wrongly stripped — density threshold too low."
    )
    # Border column zeroed.
    assert not out["grey"][:, 188].any(), (
        "Plot-box border column not stripped — col 188 has 70 px (>50% of "
        "plot height 81) and should be detected as chart decoration."
    )


def test_strip_plot_box_borders_noop_when_border_outside_plot_box() -> None:
    """#1217 Option 4: on charts where the plot-box border line is drawn
    OUTSIDE the data-edge plot box (e.g. ttartisan-50 has border at col
    609 with x_right=607), no column inside the box exceeds the density
    threshold and the function is a no-op."""
    import numpy as np
    from mtfdigitizer.pipeline.masks import strip_plot_box_borders

    mask = np.zeros((100, 200), dtype=bool)
    # Real curve: tail near right edge, low density.
    for y in [22, 23, 24, 25, 26]:
        mask[y, 188] = True

    plot_box = PlotBox(x_left=10, x_right=190, y_top=10, y_bottom=90)
    out = strip_plot_box_borders({"grey": mask}, plot_box)

    # No-op: tail-of-curve preserved.
    assert (out["grey"] == mask).all(), (
        "No-op case wrongly stripped low-density tail; threshold should "
        "ignore real-curve density."
    )


def test_apply_small_below_top_cc_filter_drops_below_top_small_ccs() -> None:
    """ADR-074: a small CC sitting >max_y_delta rows below the dominant
    CC's y-centroid AND below min_area pixels is dropped."""
    import numpy as np
    from mtfdigitizer.pipeline.dispatch import _apply_small_below_top_cc_filter

    mask = np.zeros((100, 200), dtype=bool)
    # Dominant CC: long horizontal ridge at y=5 (centroid y=5).
    mask[5, 10:190] = True  # 180 pixels
    # Spurious small CC well below the top.
    mask[60, 50:60] = True  # 10 pixels at centroid y=60

    filters = (("curve", 50, 10),)
    out = _apply_small_below_top_cc_filter({"curve": mask}, filters)

    assert out["curve"][5, 100], "dominant ridge wrongly stripped"
    assert not out["curve"][60, 55], (
        "small below-top CC not stripped — should be dropped "
        "(area=10 < min_area=50, y_delta=55 > max_y_delta=10)."
    )


def test_apply_small_below_top_cc_filter_preserves_legit_near_top_cc() -> None:
    """ADR-074: a CC near the dominant CC's y-centroid is preserved even
    when small (Samyang 85 stopped 10S/10M near-overlap case)."""
    import numpy as np
    from mtfdigitizer.pipeline.dispatch import _apply_small_below_top_cc_filter

    mask = np.zeros((100, 200), dtype=bool)
    mask[5, 10:190] = True  # dominant
    # Small CC just 3 rows below — legitimate near-overlap (S/M curves
    # both at MTF≈1.0 sit within a few px of each other).
    mask[8, 50:70] = True  # 20 pixels at y=8, delta=3

    filters = (("curve", 50, 10),)
    out = _apply_small_below_top_cc_filter({"curve": mask}, filters)

    assert out["curve"][8, 60], (
        "near-top small CC wrongly stripped — y_delta=3 should be "
        "within max_y_delta=10 guard, preserving legit near-overlap."
    )


def test_apply_small_below_top_cc_filter_preserves_below_top_large_cc() -> None:
    """ADR-074: a CC far below the dominant CC is preserved when its
    area meets the min_area threshold — a large fragment is signal, not
    noise."""
    import numpy as np
    from mtfdigitizer.pipeline.dispatch import _apply_small_below_top_cc_filter

    mask = np.zeros((100, 200), dtype=bool)
    mask[5, 10:190] = True  # dominant
    # Large CC well below — area exceeds threshold so kept.
    mask[60:65, 50:100] = True  # 250 pixels

    filters = (("curve", 200, 10),)
    out = _apply_small_below_top_cc_filter({"curve": mask}, filters)

    assert out["curve"][62, 70], (
        "large below-top CC wrongly stripped — area=250 should be "
        "above min_area=200 guard."
    )


def test_apply_small_below_top_cc_filter_noop_on_empty_rules() -> None:
    """ADR-074: empty rule tuple means the function is a pass-through."""
    import numpy as np
    from mtfdigitizer.pipeline.dispatch import _apply_small_below_top_cc_filter

    mask = np.zeros((100, 200), dtype=bool)
    mask[5, 10:190] = True
    mask[60, 50:60] = True

    out = _apply_small_below_top_cc_filter({"curve": mask}, ())

    assert (out["curve"] == mask).all(), (
        "empty rule tuple should be a pure pass-through."
    )


def test_apply_small_below_top_cc_filter_ignores_unknown_curve_names() -> None:
    """ADR-074: a rule naming a curve absent from the masks dict is
    silently ignored (matches the halo_pairs convention for per-aperture
    hue filtering, ADR-044)."""
    import numpy as np
    from mtfdigitizer.pipeline.dispatch import _apply_small_below_top_cc_filter

    mask = np.zeros((100, 200), dtype=bool)
    mask[5, 10:190] = True

    filters = (("does-not-exist", 50, 10),)
    out = _apply_small_below_top_cc_filter({"curve": mask}, filters)

    assert (out["curve"] == mask).all(), (
        "unknown curve name should not affect existing curves."
    )
