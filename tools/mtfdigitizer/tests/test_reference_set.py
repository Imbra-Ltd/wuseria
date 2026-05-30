"""Internal-consistency tests for the MTF reference set (#933).

These tests do NOT exercise an extractor — there isn't one yet (#935).
They check the reference set is internally consistent: declared style
families match what's listed, no duplicates, all chart files exist on
disk, and the documented count (8) matches what's exported.
"""

from __future__ import annotations

from pathlib import Path

from mtfdigitizer.referenceset import REFERENCE_CHARTS
from mtfdigitizer.referenceset.charts import STYLE_FAMILIES


REPO_ROOT = Path(__file__).resolve().parents[3]


# The eight families the digitizer must handle — single source of truth
# for "what styles exist in docs/optical-specs/". If a new family appears,
# it goes in this list AND a reference chart for it goes in REFERENCE_CHARTS.
EXPECTED_FAMILIES = frozenset(
    [
        "mainstream-2color-solid-dashed",
        "mainstream-4color-all-solid",
        "samecolor-dashed-sm",
        "2color-frequency",
        "bw-dashed-promo",
        "multifreq-press-kit",
        "idealized-flat",
        "soft-multicurve-promo",
    ]
)


def test_reference_set_size_is_within_target() -> None:
    """#933 acceptance: ~6-10 charts spanning the style range."""
    assert 6 <= len(REFERENCE_CHARTS) <= 10


def test_no_duplicate_slugs() -> None:
    slugs = [chart.slug for chart in REFERENCE_CHARTS]
    assert len(slugs) == len(set(slugs)), "duplicate slug in REFERENCE_CHARTS"


def test_every_chart_file_exists() -> None:
    """The chart_path on every entry must resolve to a real file on disk."""
    for chart in REFERENCE_CHARTS:
        path = REPO_ROOT / chart.chart_path
        assert path.is_file(), f"missing chart file: {chart.chart_path}"


def test_every_declared_family_has_a_reference_chart() -> None:
    """The reference set must cover every declared style family."""
    assert STYLE_FAMILIES == EXPECTED_FAMILIES, (
        f"missing families: {EXPECTED_FAMILIES - STYLE_FAMILIES}; "
        f"unexpected families: {STYLE_FAMILIES - EXPECTED_FAMILIES}"
    )


def test_no_empty_fields() -> None:
    for chart in REFERENCE_CHARTS:
        assert chart.slug
        assert chart.chart_path
        assert chart.style_family
        assert chart.apertures, f"{chart.slug}: must list at least one aperture"
        assert chart.frequencies_lpmm, f"{chart.slug}: must list at least one frequency"
        assert chart.image_height_mm > 0, f"{chart.slug}: image_height_mm must be > 0"
        assert chart.notes, f"{chart.slug}: notes are mandatory ground-truth"


def test_chart_path_starts_with_docs_optical_specs() -> None:
    """All reference charts live under docs/optical-specs/<slug>/ (ADR-031)."""
    for chart in REFERENCE_CHARTS:
        prefix = f"docs/optical-specs/{chart.slug}/"
        assert chart.chart_path.startswith(prefix), (
            f"{chart.slug}: chart_path should start with {prefix!r}, "
            f"got {chart.chart_path!r}"
        )


def test_ground_truth_charts_carry_plot_box() -> None:
    """A chart with ground truth must have a plot box (you need both
    to run the calibration runner). The inverse is also enforced — a
    chart with a plot box but no ground truth is unfinished work."""
    for chart in REFERENCE_CHARTS:
        if chart.ground_truth is not None:
            assert chart.plot_box is not None, (
                f"{chart.slug}: has ground_truth but no plot_box"
            )
        if chart.plot_box is not None:
            assert chart.ground_truth is not None, (
                f"{chart.slug}: has plot_box but no ground_truth"
            )


def test_ground_truth_has_eleven_values_per_curve() -> None:
    """The 11-point sampling grid is fixed (ADR-038 §3); ground truth
    rows must match it. A wrong length means the row was hand-typed
    incorrectly and would silently mis-align with the extractor output."""
    for chart in REFERENCE_CHARTS:
        if chart.ground_truth is None:
            continue
        for aperture, fields in chart.ground_truth.items():
            for field_name, values in fields.items():
                assert len(values) == 11, (
                    f"{chart.slug} [{aperture}] {field_name}: "
                    f"expected 11 values, got {len(values)}"
                )


def test_ground_truth_values_in_mtf_range() -> None:
    """MTF values must sit in [0, 1] — anything outside is a typo."""
    for chart in REFERENCE_CHARTS:
        if chart.ground_truth is None:
            continue
        for aperture, fields in chart.ground_truth.items():
            for field_name, values in fields.items():
                for i, v in enumerate(values):
                    if v is None:
                        continue
                    assert 0.0 <= v <= 1.0, (
                        f"{chart.slug} [{aperture}] {field_name}[{i}] = {v}: "
                        f"out of MTF range [0, 1]"
                    )


def test_ground_truth_field_names_are_canonical() -> None:
    """Field names must match the SampledReading schema in pipeline/types.py."""
    canonical = {"contrast10S", "contrast10M", "resolution30S", "resolution30M"}
    for chart in REFERENCE_CHARTS:
        if chart.ground_truth is None:
            continue
        for aperture, fields in chart.ground_truth.items():
            unknown = set(fields) - canonical
            assert not unknown, (
                f"{chart.slug} [{aperture}]: unknown fields {unknown}; "
                f"must be a subset of {canonical}"
            )


# Note: a specs-log.md check belongs to a project-wide audit, not to the
# reference-set sanity tests. CLAUDE.md §1.2 requires it for every lens
# folder; verifying that is out of scope for #933 and tracked separately.
