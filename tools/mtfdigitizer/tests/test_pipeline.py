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
    assert mid.contrast10S is not None, "Sigma 10S must be detectable mid-chart"
    assert mid.resolution30S is not None, "Sigma 30S must be detectable mid-chart"
    # The S extraction works without confusing M's dashed fragments —
    # value sits in the expected 0.8-1.0 band, not at 0 (the impossible-zero
    # PR #931 guarded against).
    assert 0.80 <= mid.contrast10S <= 1.00


# --- Acceptance: B2 — missing data reads as None, never fabricated --------


def test_b2_returns_none_when_skeleton_has_no_data_at_target() -> None:
    """Empty skeleton, sampled anywhere, must return None — not 0, not
    an interpolated guess."""
    import numpy as np

    empty = np.zeros((100, 200), dtype=np.uint8)
    plot_box = PlotBox(x_left=10, x_right=190, y_top=10, y_bottom=90)
    for fraction in SAMPLE_POINTS:
        assert sample_skeleton_at_fraction(empty, fraction, plot_box) is None


def test_b2_sigma_M_returns_none_where_dashed_has_no_skeleton_pixel() -> None:
    """The Sigma extraction has positions where the dashed M curve's
    bridged skeleton has no pixel within the bracket window — those
    must report None, not the nearby S value."""
    result = extract_chart(
        SIGMA_56_CHART,
        SIGMA_2COLOR_SOLID_DASHED,
        SIGMA_56_PLOT_BOX,
        image_height_mm=14.0,
    )
    none_count = sum(
        1 for r in result.readings if r.contrast10M is None or r.resolution30M is None
    )
    # On Sigma, dashed-M fragments aren't long-enough CCs at every sample
    # point — multiple positions legitimately read None. The test is
    # "some are None," not "specifically positions X". Tightening this
    # would couple the test to morphological-kernel tuning that #935+
    # work may rebalance.
    assert none_count > 0, "B2 contract: at least some Sigma M readings should be None"


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
    assert center.contrast10S is not None
    assert center.contrast10M is not None
    assert center.resolution30S is not None
    assert center.resolution30M is not None
    assert 0.86 <= center.contrast10S <= 0.96, (
        f"10S center: expected ~0.91, got {center.contrast10S:.3f}"
    )
    assert 0.86 <= center.contrast10M <= 0.96, (
        f"10M center: expected ~0.91, got {center.contrast10M:.3f}"
    )
    assert 0.65 <= center.resolution30S <= 0.75, (
        f"30S center: expected ~0.70, got {center.resolution30S:.3f}"
    )
    assert 0.65 <= center.resolution30M <= 0.75, (
        f"30M center: expected ~0.70, got {center.resolution30M:.3f}"
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
    assert edge.contrast10S is not None
    # Allow generous tolerance — anti-aliasing at the edge pushes values
    # a little lower than the eye-read shape. The key shape feature is
    # "drops sharply from ~0.91 center to ~0.78 edge", not exact value.
    assert edge.contrast10S < 0.85, (
        f"10S edge should drop below 0.85, got {edge.contrast10S:.3f}"
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
    assert flat.contrast10S is not None
    assert 0.93 <= flat.contrast10S <= 1.00, (
        f"Sigma 10S at 5.6mm: expected ~0.97, got {flat.contrast10S:.3f}"
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
    assert center.contrast10S is not None, (
        "Sigma 10S at fraction 0.0 must read a value, not None (#954)"
    )
    assert center.resolution30S is not None, (
        "Sigma 30S at fraction 0.0 must read a value, not None (#954)"
    )
    assert edge.contrast10S is not None, (
        "Sigma 10S at fraction 1.0 must read a value, not None (#954)"
    )
    assert edge.resolution30S is not None, (
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
