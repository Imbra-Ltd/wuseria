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
    """
    chart = next(c for c in REFERENCE_CHARTS if c.slug == slug)
    box = chart.views[view_idx].plot_box
    assert box is not None, f"{slug} view {view_idx}: no plot_box"
    return PlotBox(
        x_left=box.x_left, x_right=box.x_right,
        y_top=box.y_top, y_bottom=box.y_bottom,
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


def test_intra_curve_interp_skips_adjacent_sister_fills() -> None:
    """#1254 — when sister-filled cells run consecutively (i and i+1 both
    filled), do NOT interpolate either one. Interpolating across a run
    propagates the sister-fill error to its neighbours; the gap is too
    wide for intra-curve continuity to help, and the existing sister
    fallback is the right answer at that point."""
    from mtfdigitizer.pipeline.pipeline import (
        _replace_sister_fills_with_intra_interp,
    )

    samples = {
        "freq30S": (0.96, 0.96, 0.97, 0.97, 0.74, 0.73, 0.96, 0.96, 0.95, 0.93, 0.92),
    }
    sister_filled = {
        "freq30S": (False, False, False, False, True, True, False, False, False, False, False),
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
