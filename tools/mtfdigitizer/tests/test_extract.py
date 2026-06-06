"""Tests for the production extractor entry point (#1021, ADR-041).

Three layers:

- Unit tests on `_should_write_log()` — the gate-at-commit decision
  with hand-built `ChartVerdict` fixtures.
- Unit tests on `production_log.render_production_log()` — the
  markdown renderer is a pure function; verify shape and that
  threshold compare lines reflect the verdict.
- Integration test on `extract_lens()` end-to-end against the
  sigma-16mm-f1-4-dc-dn-c Tier 2 fixture. Confirms the four
  artifacts are written and the `--check` round trip passes.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mtfdigitizer import extract
from mtfdigitizer.extract import (
    _is_tier2,
    _resolve_view_image,
    _should_write_log,
    check_logs,
    extract_lens,
)
from mtfdigitizer.pipeline.rendermatch import FieldIou, RenderMatchScore
from mtfdigitizer.pipeline.types import SampledReading
from mtfdigitizer.pipeline.sampling import SAMPLE_FRACTIONS
from mtfdigitizer.priors import PriorViolation
from mtfdigitizer.production_log import ProductionPanel, render_production_log
from mtfdigitizer.referenceset.charts import (
    ChartView,
    PlotBoxCoords,
    REFERENCE_CHARTS,
    ReferenceChart,
)
from mtfdigitizer.triage import ChartVerdict, LowReason


REPO_ROOT = Path(__file__).resolve().parents[3]


# --- Helpers --------------------------------------------------------------


def _high_verdict() -> ChartVerdict:
    return ChartVerdict(
        source_path="fake.png",
        profile_name="fake-profile",
        verdict="HIGH",
        reasons=(),
        render_match_iou=0.50,
        render_match_precision=0.90,
        prior_violations=(),
    )


def _low_verdict(reason: LowReason = LowReason.PRECISION_BELOW_THRESHOLD) -> ChartVerdict:
    return ChartVerdict(
        source_path="fake.png",
        profile_name="fake-profile",
        verdict="LOW",
        reasons=(reason,),
        render_match_iou=0.50,
        render_match_precision=0.65,
        prior_violations=(),
    )


# --- _should_write_log() --------------------------------------------------


def test_gate_low_verdict_holds_without_accept():
    write, reason = _should_write_log([_low_verdict()], accept_override=False)
    assert not write
    assert reason == "gate-low"


def test_gate_low_verdict_writes_with_accept():
    write, reason = _should_write_log([_low_verdict()], accept_override=True)
    assert write
    assert reason == "accept-override"


def test_gate_high_verdict_holds_when_overlay_glance_required(monkeypatch):
    monkeypatch.setattr(extract, "OVERLAY_GLANCE_REQUIRED", True)
    write, reason = _should_write_log([_high_verdict()], accept_override=False)
    assert not write
    assert reason == "gate-high-pending-glance"


def test_gate_high_verdict_auto_writes_when_glance_not_required(monkeypatch):
    monkeypatch.setattr(extract, "OVERLAY_GLANCE_REQUIRED", False)
    write, reason = _should_write_log([_high_verdict()], accept_override=False)
    assert write
    assert reason == "gate-high-auto"


def test_gate_accept_always_writes_even_on_low(monkeypatch):
    """`--accept` is the maintainer's override; the gate verdict doesn't
    block it. This is the documented escape hatch for Sigma-style sparse
    dashed-M charts that classify LOW but extract cleanly."""
    monkeypatch.setattr(extract, "OVERLAY_GLANCE_REQUIRED", True)
    write, _ = _should_write_log(
        [_low_verdict(LowReason.PRIOR_FAILED_IN_RANGE)], accept_override=True
    )
    assert write


def test_gate_multi_view_one_low_holds_the_lens(monkeypatch):
    """A zoom (wide + tele) holds if any view is LOW — the log writer
    emits one log per lens, so a partial commit is meaningless."""
    monkeypatch.setattr(extract, "OVERLAY_GLANCE_REQUIRED", True)
    write, reason = _should_write_log(
        [_high_verdict(), _low_verdict()], accept_override=False
    )
    assert not write
    assert reason == "gate-low"


def test_gate_multi_view_all_high_pending_glance(monkeypatch):
    monkeypatch.setattr(extract, "OVERLAY_GLANCE_REQUIRED", True)
    write, reason = _should_write_log(
        [_high_verdict(), _high_verdict()], accept_override=False
    )
    assert not write
    assert reason == "gate-high-pending-glance"


def test_gate_multi_view_accept_override_writes_anyway():
    """The escape hatch overrides the gate for multi-view lenses too."""
    write, reason = _should_write_log(
        [_low_verdict(), _low_verdict()], accept_override=True
    )
    assert write
    assert reason == "accept-override"


# --- Tier 2 filter --------------------------------------------------------


def test_is_tier2_requires_plot_box_and_no_ground_truth():
    """Tier 2 = `plot_box is not None and ground_truth is None`."""
    tier1 = ReferenceChart(
        slug="fake", chart_path="x.png", style_family="x",
        apertures=("MAX",), frequencies_lpmm=(10, 30),
        image_height_mm=14.0, notes="",
        plot_box=PlotBoxCoords(x_left=0, x_right=10, y_top=0, y_bottom=10),
        ground_truth={"MAX": {"contrast10S": (None,) * 11}},
    )
    tier2 = ReferenceChart(
        slug="fake", chart_path="x.png", style_family="x",
        apertures=("MAX",), frequencies_lpmm=(10, 30),
        image_height_mm=14.0, notes="",
        plot_box=PlotBoxCoords(x_left=0, x_right=10, y_top=0, y_bottom=10),
        ground_truth=None,
    )
    unscoped = ReferenceChart(
        slug="fake", chart_path="x.png", style_family="x",
        apertures=("MAX",), frequencies_lpmm=(10, 30),
        image_height_mm=14.0, notes="",
        plot_box=None, ground_truth=None,
    )
    assert not _is_tier2(tier1)
    assert _is_tier2(tier2)
    assert not _is_tier2(unscoped)


# --- Canonical chart selection -------------------------------------------


def test_resolve_view_image_prefers_diffraction_when_present(tmp_path):
    """ADR-033 names the canonical chart `-mtf-diffraction.png`. When
    present, the extractor picks it up even if the registry still
    declares the legacy `-mtf-1.png` path (transitional behaviour
    during #1017 rename). The probe runs on the primary view only —
    additional views (zoom tele) already use their canonical
    focal-suffixed name."""
    legacy_dir = tmp_path / "docs" / "optical-specs" / "fake-slug"
    legacy_dir.mkdir(parents=True)
    legacy = legacy_dir / "fake-slug-mtf-1.png"
    legacy.write_bytes(b"legacy")
    canonical = legacy_dir / "fake-slug-mtf-diffraction.png"
    canonical.write_bytes(b"canonical")

    chart = ReferenceChart(
        slug="fake-slug",
        chart_path=str(legacy.relative_to(tmp_path)).replace("\\", "/"),
        style_family="x", apertures=("MAX",), frequencies_lpmm=(10, 30),
        image_height_mm=14.0, notes="",
        plot_box=PlotBoxCoords(x_left=0, x_right=10, y_top=0, y_bottom=10),
    )
    primary_view = chart.views[0]

    import mtfdigitizer.extract as ext_mod
    monkey_root = tmp_path
    original = ext_mod.REPO_ROOT
    ext_mod.REPO_ROOT = monkey_root
    try:
        resolved = _resolve_view_image(chart, primary_view)
    finally:
        ext_mod.REPO_ROOT = original

    assert resolved.name == "fake-slug-mtf-diffraction.png"


def test_resolve_view_image_falls_back_to_legacy(tmp_path):
    legacy_dir = tmp_path / "docs" / "optical-specs" / "fake-slug"
    legacy_dir.mkdir(parents=True)
    legacy = legacy_dir / "fake-slug-mtf-1.png"
    legacy.write_bytes(b"legacy")

    chart = ReferenceChart(
        slug="fake-slug",
        chart_path=str(legacy.relative_to(tmp_path)).replace("\\", "/"),
        style_family="x", apertures=("MAX",), frequencies_lpmm=(10, 30),
        image_height_mm=14.0, notes="",
        plot_box=PlotBoxCoords(x_left=0, x_right=10, y_top=0, y_bottom=10),
    )
    primary_view = chart.views[0]

    import mtfdigitizer.extract as ext_mod
    original = ext_mod.REPO_ROOT
    ext_mod.REPO_ROOT = tmp_path
    try:
        resolved = _resolve_view_image(chart, primary_view)
    finally:
        ext_mod.REPO_ROOT = original

    assert resolved.name == "fake-slug-mtf-1.png"


def test_resolve_view_image_additional_view_skips_canonical_probe(tmp_path):
    """The canonical `-mtf-diffraction.png` probe only fires on the
    primary view. Additional views (zoom tele) declare their full
    focal-suffixed canonical path and must resolve via fallback —
    otherwise both wide and tele would collapse to the same file."""
    lens_dir = tmp_path / "docs" / "optical-specs" / "fake-slug"
    lens_dir.mkdir(parents=True)
    primary = lens_dir / "fake-slug-mtf-diffraction-wide.png"
    primary.write_bytes(b"wide")
    tele = lens_dir / "fake-slug-mtf-diffraction-tele.png"
    tele.write_bytes(b"tele")
    # The bare-canonical lure that would clobber the tele if the probe
    # ran on additional views.
    bare = lens_dir / "fake-slug-mtf-diffraction.png"
    bare.write_bytes(b"bare-lure")

    chart = ReferenceChart(
        slug="fake-slug",
        chart_path=str(primary.relative_to(tmp_path)).replace("\\", "/"),
        style_family="x", apertures=("MAX",), frequencies_lpmm=(10, 30),
        image_height_mm=14.0, notes="",
        plot_box=PlotBoxCoords(x_left=0, x_right=10, y_top=0, y_bottom=10),
        additional_views=(
            ChartView(
                chart_path=str(tele.relative_to(tmp_path)).replace("\\", "/"),
                plot_box=PlotBoxCoords(x_left=0, x_right=10, y_top=0, y_bottom=10),
            ),
        ),
    )

    import mtfdigitizer.extract as ext_mod
    original = ext_mod.REPO_ROOT
    ext_mod.REPO_ROOT = tmp_path
    try:
        primary_resolved = _resolve_view_image(chart, chart.views[0])
        tele_resolved = _resolve_view_image(chart, chart.views[1])
    finally:
        ext_mod.REPO_ROOT = original

    # Primary's diffraction probe finds the bare lure.
    assert primary_resolved.name == "fake-slug-mtf-diffraction.png"
    # Tele's path is preserved untouched — no probe on additional views.
    assert tele_resolved.name == "fake-slug-mtf-diffraction-tele.png"


# --- production_log.render_production_log() ------------------------------


def _fake_panel(verdict: ChartVerdict) -> ProductionPanel:
    readings = tuple(
        SampledReading(
            position_mm=frac * 14.0,
            samples={
                "freq10S": 0.9 - frac * 0.3,
                "freq10M": 0.9 - frac * 0.2,
                "freq30S": 0.8 - frac * 0.3,
                "freq30M": 0.8 - frac * 0.2,
            },
        )
        for frac in SAMPLE_FRACTIONS
    )
    from mtfdigitizer.pipeline.types import ExtractedChart, PlotBox
    extracted = ExtractedChart(
        source_path="fake.png",
        profile_name="fake-profile",
        plot_box=PlotBox(x_left=0, x_right=10, y_top=0, y_bottom=10),
        image_height_mm=14.0,
        readings=readings,
        sister_fallback_count={"contrast10M": 2, "resolution30M": 1},
    )
    return ProductionPanel(
        chart_slug="fake-slug",
        chart_path="docs/optical-specs/fake-slug/fake.png",
        style_family="fake-family",
        plot_box=(0, 10, 0, 10),
        image_height_mm=14.0,
        extracted=extracted,
        verdict=verdict,
    )


def test_production_log_renders_high_verdict_with_no_reasons():
    panel = _fake_panel(_high_verdict())
    text = render_production_log("fake-slug", [panel])
    assert "Gate verdict:** `HIGH`" in text
    assert "both confidence signals cleared" in text
    assert "All four priors held" in text


def test_production_log_renders_low_verdict_with_reason_list():
    panel = _fake_panel(_low_verdict(LowReason.IOU_BELOW_THRESHOLD))
    text = render_production_log("fake-slug", [panel])
    assert "Gate verdict:** `LOW`" in text
    assert "`iou_below_threshold`" in text


def test_production_log_threshold_pass_column_reflects_verdict_numbers():
    panel = _fake_panel(_low_verdict())  # precision 0.65 fails, IoU 0.50 passes
    text = render_production_log("fake-slug", [panel])
    # precision row shows "no", IoU row shows "yes"
    assert "| precision | 0.650 |      0.80 |   no |" in text
    assert "| IoU       | 0.500 |      0.20 |  yes |" in text


def test_production_log_lists_prior_violations_when_present():
    panel = _fake_panel(
        ChartVerdict(
            source_path="fake.png",
            profile_name="fake-profile",
            verdict="LOW",
            reasons=(LowReason.PRIOR_FAILED_IN_RANGE,),
            render_match_iou=0.50,
            render_match_precision=0.85,
            prior_violations=(
                PriorViolation(
                    prior_name="in_range",
                    field="contrast10S",
                    position_index=5,
                    detail="value 1.20 outside [0, 1]",
                ),
            ),
        )
    )
    text = render_production_log("fake-slug", [panel])
    assert "| `in_range` | `contrast10S` | 5 | value 1.20 outside [0, 1] |" in text


# --- Integration: sigma-16mm end-to-end ----------------------------------


_SIGMA_16_SLUG = "sigma-16mm-f1-4-dc-dn-c"


def _sigma_16_present() -> bool:
    return any(c.slug == _SIGMA_16_SLUG for c in REFERENCE_CHARTS)


@pytest.mark.skipif(not _sigma_16_present(), reason="sigma-16mm not in reference set")
def test_extract_lens_sigma16_writes_four_artifacts(tmp_path, monkeypatch, capsys):
    """End-to-end smoke test: the CLI on the real sigma-16mm chart
    writes overlay PNG + SVG + review HTML, and the production
    digitization-log.md when `--accept` is passed.
    """
    # We don't want the test to mutate the committed docs/optical-specs
    # tree, so it runs against the real chart but writes to a tmp lens
    # dir. The trick: monkey-patch REPO_ROOT so artifact paths land in
    # tmp_path, then copy the source PNG into the expected location.
    chart = next(c for c in REFERENCE_CHARTS if c.slug == _SIGMA_16_SLUG)
    src_png = REPO_ROOT / chart.chart_path
    dst_png = tmp_path / chart.chart_path
    dst_png.parent.mkdir(parents=True, exist_ok=True)
    dst_png.write_bytes(src_png.read_bytes())

    monkeypatch.setattr(extract, "REPO_ROOT", tmp_path)

    rc = extract_lens(_SIGMA_16_SLUG, accept_override=True)
    assert rc == 0

    lens_dir = tmp_path / "docs" / "optical-specs" / _SIGMA_16_SLUG
    overlay = lens_dir / f"{_SIGMA_16_SLUG}-mtf-diffraction-overlay.png"
    svg = lens_dir / f"{_SIGMA_16_SLUG}-mtf-diffraction.svg"
    review = lens_dir / f"{_SIGMA_16_SLUG}-mtf-diffraction-review.html"
    log = lens_dir / "digitization-log.md"
    assert overlay.exists() and overlay.stat().st_size > 1000, (
        "overlay PNG should be a real raster"
    )
    assert svg.exists() and svg.stat().st_size > 100
    assert review.exists()
    assert log.exists()

    text = log.read_text(encoding="utf-8")
    assert "Gate verdict:**" in text
    assert "Production-tier log per ADR-041" in text


@pytest.mark.skipif(not _sigma_16_present(), reason="sigma-16mm not in reference set")
def test_extract_hold_does_not_write_log(tmp_path, monkeypatch, capsys):
    """Without `--accept` and with overlay-glance mandatory, a LOW
    verdict must produce overlay/SVG/HTML but *not* the production
    log. Sigma-16mm is reliably LOW (sparse dashed-M, same as 56mm)
    so we can assert HOLD behaviour deterministically."""
    chart = next(c for c in REFERENCE_CHARTS if c.slug == _SIGMA_16_SLUG)
    src_png = REPO_ROOT / chart.chart_path
    dst_png = tmp_path / chart.chart_path
    dst_png.parent.mkdir(parents=True, exist_ok=True)
    dst_png.write_bytes(src_png.read_bytes())

    monkeypatch.setattr(extract, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(extract, "OVERLAY_GLANCE_REQUIRED", True)

    rc = extract_lens(_SIGMA_16_SLUG, accept_override=False)
    assert rc == 0

    lens_dir = tmp_path / "docs" / "optical-specs" / _SIGMA_16_SLUG
    assert (lens_dir / f"{_SIGMA_16_SLUG}-mtf-diffraction-overlay.png").exists()
    assert not (lens_dir / "digitization-log.md").exists(), (
        "HOLD path must not write the production log"
    )


@pytest.mark.skipif(not _sigma_16_present(), reason="sigma-16mm not in reference set")
def test_extract_check_passes_after_fresh_write(tmp_path, monkeypatch):
    """After `extract_lens --accept`, `check_logs()` must return 0 — the
    committed log matches the fresh render. Catches drift in the
    renderer that would silently produce stale logs in CI."""
    chart = next(c for c in REFERENCE_CHARTS if c.slug == _SIGMA_16_SLUG)
    src_png = REPO_ROOT / chart.chart_path
    dst_png = tmp_path / chart.chart_path
    dst_png.parent.mkdir(parents=True, exist_ok=True)
    dst_png.write_bytes(src_png.read_bytes())

    monkeypatch.setattr(extract, "REPO_ROOT", tmp_path)

    assert extract_lens(_SIGMA_16_SLUG, accept_override=True) == 0
    assert check_logs() == 0
