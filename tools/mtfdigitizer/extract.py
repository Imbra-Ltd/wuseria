"""Production extraction CLI (ADR-041 Tier 2).

Sister to `calibrate.py`: where calibration runs the extractor against
charts with eye-read ground truth and reports per-position offsets,
this entry point runs the extractor against production-tier lenses
(no per-lens GT) and emits four artifacts per lens, gated by the two
confidence signals ADR-038 §4 already specifies (render-match +
plausibility priors).

Emitted artifacts under `docs/optical-specs/<lens-slug>/`:

- `<chart-stem>-overlay.png` — extractor's 11-point polylines drawn over
  the original chart (mandatory maintainer glance until ~20 lenses ship
  without a false-positive auto-accept).
- `<chart-stem>-review.html` — the 3-panel composite from `review.py`
  (original + SVG + overlay). Same as the calibration-tier review file.
- `<chart-stem>.svg` — provenance SVG from `svg.py`.
- `digitization-log.md` — production log written by `production_log.py`
  (no EYE column, lists the gate decision + signal values).

Usage::

    cd tools
    py -m mtfdigitizer.extract <lens-slug>            # one lens, gated commit
    py -m mtfdigitizer.extract <lens-slug> --accept   # bypass HOLD, write anyway
    py -m mtfdigitizer.extract --all                  # every Tier 2 lens that has no log yet
    py -m mtfdigitizer.extract --check                # re-render all production logs, fail on staleness

Gate at commit time:

The extractor always writes the overlay, SVG, and review HTML — those
are inspection artifacts the maintainer needs even when reviewing a
HOLD. The production `digitization-log.md` is written only when the
gate accepts. With `--accept` the maintainer overrides the gate and
the log is written regardless.

Implements #1021 per the ADR-041 Tier 2 design.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .family_profile import profile_for_chart
from .pipeline import PlotBox, extract_chart, score_chart
from .pipeline.rendermatch import DEFAULT_DILATION_RADIUS_PX
from .pipeline.types import ExtractedChart
from .priors import check_all
from .production_log import ProductionPanel, render_production_log
from .referenceset.charts import (
    REFERENCE_CHARTS,
    ChartView,
    PlotBoxCoords,
    ReferenceChart,
)
from .review import write_review
from .svg import render_svg
from .triage import ChartVerdict, triage


REPO_ROOT = Path(__file__).resolve().parents[2]


# --- Configuration knobs --------------------------------------------------
# Centralised here per #1021. Tuning data lives in `referenceset/triage.md`
# (thresholds) and `referenceset/plausibility.md` (priors); the gate itself
# is `triage.triage()`.

# Whether a HIGH verdict alone is sufficient to write the production log,
# or whether the maintainer must glance at the overlay first. Mandatory
# until ~20 production lenses ship without a false-positive auto-accept
# (per #1021's recommended initial setting); becomes a config toggle once
# trust data exists.
OVERLAY_GLANCE_REQUIRED: bool = True


# --- Tier 2 chart filter --------------------------------------------------


def _is_tier2(chart: ReferenceChart) -> bool:
    """A Tier 2 chart has a `plot_box` (extractor can run) and no
    `ground_truth` (no calibration anchor — production tier per ADR-041).
    """
    return chart.plot_box is not None and chart.ground_truth is None


def _tier2_charts() -> list[ReferenceChart]:
    return [c for c in REFERENCE_CHARTS if _is_tier2(c)]


def _chart_by_slug(slug: str) -> ReferenceChart | None:
    for c in REFERENCE_CHARTS:
        if c.slug == slug:
            return c
    return None


# --- Canonical chart path with legacy fallback ----------------------------


def _resolve_view_image(chart: ReferenceChart, view: ChartView) -> Path:
    """Return the absolute path to a view's chart raster.

    Honors ADR-033's canonical `-mtf-diffraction.png` (or
    `-mtf-diffraction-<focal>.png` for zooms) if present; otherwise
    falls back to the path the view declares. The canonical-name probe
    only fires on the primary view (the slug-bare name), so additional
    zoom views — whose `chart_path` is already the focal-suffixed
    canonical (`...-wide.png`, `...-tele.png`) — resolve via fallback.

    Resolution order:

    1. `<slug>-mtf-diffraction.png` in the same folder (primary view only)
    2. `view.chart_path` (always exists for additional views)
    """
    declared = REPO_ROOT / view.chart_path
    is_primary = view.chart_path == chart.chart_path
    if is_primary:
        canonical_name = f"{chart.slug}-mtf-diffraction.png"
        canonical = declared.parent / canonical_name
        if canonical.exists():
            return canonical
    return declared


# --- Pipeline orchestration -----------------------------------------------


def _to_plotbox(coords: PlotBoxCoords) -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
    )


@dataclass(frozen=True)
class ExtractRun:
    """The full output of one chart view's extraction pass."""

    chart: ReferenceChart
    view: ChartView
    image_path: Path
    plot_box: PlotBox
    extracted: ExtractedChart
    verdict: ChartVerdict


def _run_view(chart: ReferenceChart, view: ChartView) -> ExtractRun:
    """Run one chart view through extract → score → priors → triage.

    No I/O beyond reading the chart raster.
    """
    assert view.plot_box is not None, (
        f"chart {chart.slug!r} view {view.chart_path!r} has no plot_box — "
        "cannot run extractor"
    )
    profile = profile_for_chart(chart)
    image_path = _resolve_view_image(chart, view)
    plot_box = _to_plotbox(view.plot_box)

    extracted = extract_chart(
        image_path, profile, plot_box, image_height_mm=chart.image_height_mm
    )
    score = score_chart(
        image_path,
        profile,
        plot_box,
        image_height_mm=chart.image_height_mm,
        readings=extracted.readings,
        dilation_radius_px=DEFAULT_DILATION_RADIUS_PX,
    )
    violations = check_all(extracted.readings)
    verdict = triage(score, violations)
    return ExtractRun(
        chart=chart,
        view=view,
        image_path=image_path,
        plot_box=plot_box,
        extracted=extracted,
        verdict=verdict,
    )


def _run_all_views(chart: ReferenceChart) -> list[ExtractRun]:
    """Run every view this lens publishes. Each view contributes one
    panel to the lens's single digitization-log.md.
    """
    return [_run_view(chart, view) for view in chart.views]


# --- Acceptance decision --------------------------------------------------


def _should_write_log(
    verdicts: list[ChartVerdict], *, accept_override: bool
) -> tuple[bool, str]:
    """The gate-at-commit decision over every view of a lens.

    Returns (write: bool, reason: str). When the maintainer passed
    `--accept`, the log is written regardless of verdict — the reason
    is recorded as 'accept-override' so the run output is honest about
    bypassing the gate.

    A multi-view lens (zoom: wide + tele) holds if **any** view is
    LOW; HIGH-pending-glance fires only when every view is HIGH. The
    log writer emits one log per lens regardless, so partial accepts
    are not a meaningful state.
    """
    if accept_override:
        return True, "accept-override"
    if not all(v.verdict == "HIGH" for v in verdicts):
        return False, "gate-low"
    if not OVERLAY_GLANCE_REQUIRED:
        return True, "gate-high-auto"
    return False, "gate-high-pending-glance"


# --- Artifact writers -----------------------------------------------------


def _lens_dir_for(chart: ReferenceChart) -> Path:
    # Reference charts live at docs/optical-specs/<slug>/<file>;
    # the lens dir is the parent of the declared chart path.
    return (REPO_ROOT / chart.chart_path).parent


def _write_inspection_artifacts(run: ExtractRun) -> tuple[Path, Path, Path]:
    """Write one view's SVG + overlay PNG + review HTML.

    Always written, regardless of the gate decision — the maintainer
    needs them to eye-glance a HOLD. Artifacts are named by the chart
    image stem so multiple views in the same folder do not collide.
    """
    lens_dir = _lens_dir_for(run.chart)
    lens_dir.mkdir(parents=True, exist_ok=True)

    svg_path = lens_dir / f"{run.image_path.stem}.svg"
    svg_path.write_text(render_svg(run.extracted), encoding="utf-8")

    outputs = write_review(
        run.extracted,
        run.image_path,
        plot_box=run.plot_box,
        image_height_mm=run.chart.image_height_mm,
        svg_path=svg_path,
        out_dir=lens_dir,
    )
    return svg_path, outputs.overlay_path, outputs.html_path


def _panel_for(run: ExtractRun) -> ProductionPanel:
    """Build the one log panel for a single view of a lens."""
    plot_box_tuple = (
        run.plot_box.x_left,
        run.plot_box.x_right,
        run.plot_box.y_top,
        run.plot_box.y_bottom,
    )
    return ProductionPanel(
        chart_slug=run.chart.slug,
        chart_path=run.view.chart_path,
        style_family=run.chart.style_family,
        plot_box=plot_box_tuple,
        image_height_mm=run.chart.image_height_mm,
        extracted=run.extracted,
        verdict=run.verdict,
    )


def _render_log_for(runs: list[ExtractRun]) -> str:
    """Render the lens's full digitization-log.md — one panel per view."""
    assert runs, "cannot render a log with zero panels"
    slug = runs[0].chart.slug
    panels = [_panel_for(r) for r in runs]
    return render_production_log(slug, panels)


def _log_path_for(chart: ReferenceChart) -> Path:
    return _lens_dir_for(chart) / "digitization-log.md"


# --- Top-level commands ---------------------------------------------------


def extract_lens(slug: str, *, accept_override: bool) -> int:
    """Extract one lens. Returns 0 on success, non-zero on error.

    A lens with N views produces N × (SVG + overlay + review.html) plus
    one digitization-log.md with N panels. The gate aggregates verdicts
    across views — a single LOW holds the entire lens.
    """
    chart = _chart_by_slug(slug)
    if chart is None:
        print(f"ERROR: unknown lens slug {slug!r}", file=sys.stderr)
        return 1
    if not _is_tier2(chart):
        print(
            f"ERROR: {slug!r} is not a Tier 2 chart "
            f"(needs plot_box set and ground_truth None). "
            f"plot_box={'present' if chart.plot_box else 'missing'}, "
            f"ground_truth={'present' if chart.ground_truth else 'missing'}.",
            file=sys.stderr,
        )
        return 1

    n_views = len(chart.views)
    suffix = "" if n_views == 1 else f" — {n_views} views"
    print(f"Extracting {slug} ({chart.style_family}){suffix}...")
    runs = _run_all_views(chart)

    rel = lambda p: p.relative_to(REPO_ROOT)
    for run in runs:
        svg_path, overlay_path, html_path = _write_inspection_artifacts(run)
        print(f"  wrote {rel(svg_path)}")
        print(f"  wrote {rel(overlay_path)}")
        print(f"  wrote {rel(html_path)}")

        precision = run.verdict.render_match_precision
        iou = run.verdict.render_match_iou
        p_str = f"{precision:.3f}" if precision is not None else "—"
        i_str = f"{iou:.3f}" if iou is not None else "—"
        view_label = run.image_path.stem
        print(
            f"  verdict ({view_label}): {run.verdict.verdict}  "
            f"(precision={p_str}, IoU={i_str}, "
            f"prior_violations={len(run.verdict.prior_violations)})"
        )

    write, reason = _should_write_log(
        [r.verdict for r in runs], accept_override=accept_override
    )
    if not write:
        print(
            f"  HOLD ({reason}): overlay PNG(s) written for maintainer glance; "
            f"re-run with --accept to commit the production log."
        )
        return 0

    log_path = _log_path_for(chart)
    log_path.write_text(_render_log_for(runs), encoding="utf-8")
    print(f"  wrote {rel(log_path)}  ({reason})")
    return 0


def extract_all(*, accept_override: bool) -> int:
    """Run every Tier 2 lens that does not yet have a committed
    `digitization-log.md`. Stops on the first HOLD so the maintainer
    can review before continuing.
    """
    pending: list[ReferenceChart] = []
    for chart in _tier2_charts():
        if not _log_path_for(chart).exists():
            pending.append(chart)
    if not pending:
        print("No pending Tier 2 lenses — every chart already has a log.")
        return 0

    print(f"Pending: {len(pending)} Tier 2 lens(es).")
    for chart in pending:
        rc = extract_lens(chart.slug, accept_override=accept_override)
        if rc != 0:
            return rc
        if not _log_path_for(chart).exists():
            print(
                f"\nStopping on HOLD at {chart.slug}. "
                f"Inspect the overlay and re-run with --accept "
                f"(or fix the chart) before continuing.",
                file=sys.stderr,
            )
            return 0
    return 0


def check_logs(charts: Iterable[ReferenceChart] | None = None) -> int:
    """Re-render every production log in memory and compare to disk.

    Returns 0 when every committed log matches; 1 when any differ or
    are missing. Mirrors `log._check_logs` for the calibration tier.
    """
    target = list(charts) if charts is not None else _tier2_charts()
    target = [c for c in target if _log_path_for(c).exists()]
    if not target:
        print("OK: no production logs to check (none committed yet).")
        return 0

    failures: list[str] = []
    for chart in target:
        runs = _run_all_views(chart)
        expected = _render_log_for(runs)
        path = _log_path_for(chart)
        rel = path.relative_to(REPO_ROOT)
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            failures.append(f"  STALE    {rel}")
    if failures:
        print(
            f"{len(failures)} production log(s) out of date. "
            f"Re-run `py -m mtfdigitizer.extract <slug>` to refresh:"
        )
        for line in failures:
            print(line)
        return 1
    print(f"OK: {len(target)} production log(s) up to date.")
    return 0


# --- CLI -----------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "slug",
        nargs="?",
        help="reference-set lens slug to extract (Tier 2 only). "
        "Omit when using --all or --check.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="run every Tier 2 lens that does not yet have a "
        "committed digitization-log.md; stops on first HOLD",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="re-render every committed production log and exit "
        "non-zero if any differ from the fresh render. No writes.",
    )
    parser.add_argument(
        "--accept",
        action="store_true",
        help="bypass the gate / overlay-glance requirement and write "
        "the production digitization-log.md regardless of verdict",
    )
    args = parser.parse_args(argv)

    mode_count = sum([bool(args.slug), args.all, args.check])
    if mode_count == 0:
        parser.error("must pass a lens slug, --all, or --check")
    if mode_count > 1:
        parser.error("slug, --all, and --check are mutually exclusive")

    if args.check:
        return check_logs()
    if args.all:
        return extract_all(accept_override=args.accept)
    return extract_lens(args.slug, accept_override=args.accept)


if __name__ == "__main__":
    sys.exit(main())
