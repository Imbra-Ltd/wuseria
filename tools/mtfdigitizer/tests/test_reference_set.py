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
        "2color-frequency-cc-rank",
        "bw-dashed-promo",
        "multifreq-press-kit",
        "idealized-flat",
        "soft-multicurve-promo",
    ]
)


def test_reference_set_size_is_within_target() -> None:
    """#933 acceptance was ~6-10 style-spanning charts; the set now also
    holds calibrated charts emitted to the site (one per lens slug as
    each brand's #795-style digitization task ships). Upper bound is a
    loose sanity check, not a design ceiling — bump as needed."""
    assert 6 <= len(REFERENCE_CHARTS) <= 50


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
    """All reference charts live under docs/optical-specs/<lens_slug>/
    (ADR-031). The reference-set slug MAY append a `-at-XXmm` panel
    suffix to disambiguate zoom focal-length panels (e.g. the 11-18mm
    zoom has two MTF panels); chart_path uses the lens slug regardless."""
    import re
    panel_suffix = re.compile(r"-at-\d+(\.\d+)?mm$")
    for chart in REFERENCE_CHARTS:
        lens_slug = panel_suffix.sub("", chart.slug)
        prefix = f"docs/optical-specs/{lens_slug}/"
        assert chart.chart_path.startswith(prefix), (
            f"{chart.slug}: chart_path should start with {prefix!r}, "
            f"got {chart.chart_path!r}"
        )


def test_ground_truth_charts_carry_plot_box() -> None:
    """A chart with ground truth must have a plot box (you need both
    to run the calibration runner).

    The inverse no longer holds: ADR-041 introduced Tier 2 charts that
    carry a plot box (the extractor needs one to run) but no ground
    truth (the production tier accepts on render-match + plausibility
    priors, not eye-reads). See `extract.py`."""
    for chart in REFERENCE_CHARTS:
        if chart.ground_truth is not None:
            assert chart.plot_box is not None, (
                f"{chart.slug}: has ground_truth but no plot_box"
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
