"""Tests for the MTF rename helper (#1017)."""

from __future__ import annotations

from pathlib import Path

import pytest

from mtfdigitizer.rename import (
    LABEL_SUFFIX,
    RenameError,
    _focal_to_segment,
    _is_numeric_stem,
    _parse_analysis_md,
    _plan_for_folder,
    _rewrite_analysis,
    _sidecars_for,
    _split_label,
    _update_charts_py,
)


# --- analysis.md parser ---------------------------------------------------


def test_parse_analysis_md_two_chart_prime():
    text = (
        "# Foo MTF\n"
        "\n"
        "MTF charts:\n"
        "\n"
        "- [foo-mtf-1.png](foo-mtf-1.png) -- diffraction MTF\n"
        "- [foo-mtf-2.png](foo-mtf-2.png) -- geometrical MTF\n"
        "\n"
        "## Chart legend\n"
    )
    assert _parse_analysis_md(text, "foo") == {
        "foo-mtf-1.png": "diffraction",
        "foo-mtf-2.png": "geometric",
    }


def test_parse_analysis_md_unrecognised_label_fails_loud():
    text = (
        "MTF charts:\n"
        "\n"
        "- [foo-mtf-1.png](foo-mtf-1.png) -- something weird\n"
    )
    with pytest.raises(RenameError, match="unrecognised MTF chart label"):
        _parse_analysis_md(text, "foo")


def test_parse_analysis_md_no_list_returns_empty():
    text = "# Foo\n\nno chart list here\n"
    assert _parse_analysis_md(text, "foo") == {}


def test_parse_analysis_md_strips_trailing_parenthetical():
    text = (
        "MTF charts:\n"
        "\n"
        "- [foo-mtf-1.png](foo-mtf-1.png) -- diffraction MTF (10/30 lp/mm)\n"
    )
    assert _parse_analysis_md(text, "foo") == {"foo-mtf-1.png": "diffraction"}


def test_label_suffix_accepts_us_and_uk_spelling():
    # Sigma analysis.md uses "geometrical MTF"; common alternative is
    # the shorter "geometric MTF". Both must map to the same suffix.
    assert LABEL_SUFFIX["geometrical mtf"] == "geometric"
    assert LABEL_SUFFIX["geometric mtf"] == "geometric"


# --- zoom focal-length qualifier -----------------------------------------


def test_parse_analysis_md_zoom_wide_tele():
    text = (
        "MTF charts:\n"
        "\n"
        "- [foo-mtf-1.png](foo-mtf-1.png) -- diffraction MTF (wide)\n"
        "- [foo-mtf-2.png](foo-mtf-2.png) -- diffraction MTF (tele)\n"
        "- [foo-mtf-3.png](foo-mtf-3.png) -- geometrical MTF (wide)\n"
        "- [foo-mtf-4.png](foo-mtf-4.png) -- geometrical MTF (tele)\n"
    )
    assert _parse_analysis_md(text, "foo") == {
        "foo-mtf-1.png": "diffraction-wide",
        "foo-mtf-2.png": "diffraction-tele",
        "foo-mtf-3.png": "geometric-wide",
        "foo-mtf-4.png": "geometric-tele",
    }


def test_parse_analysis_md_zoom_explicit_focal_mm():
    text = (
        "MTF charts:\n"
        "\n"
        "- [foo-mtf-1.png](foo-mtf-1.png) -- diffraction MTF (100mm)\n"
        "- [foo-mtf-2.png](foo-mtf-2.png) -- diffraction MTF (400mm)\n"
    )
    assert _parse_analysis_md(text, "foo") == {
        "foo-mtf-1.png": "diffraction-100mm",
        "foo-mtf-2.png": "diffraction-400mm",
    }


def test_parse_analysis_md_unknown_focal_qualifier_fails_loud():
    text = (
        "MTF charts:\n"
        "\n"
        "- [foo-mtf-1.png](foo-mtf-1.png) -- diffraction MTF (middle)\n"
    )
    with pytest.raises(RenameError, match="unrecognised qualifier"):
        _parse_analysis_md(text, "foo")


def test_split_label_with_and_without_parenthetical():
    assert _split_label("diffraction mtf") == ("diffraction mtf", None)
    assert _split_label("diffraction mtf (wide)") == ("diffraction mtf", "wide")
    assert _split_label("diffraction mtf (10/30 lp/mm)") == (
        "diffraction mtf",
        "10/30 lp/mm",
    )


def test_focal_to_segment_named_numeric_and_frequency_annotation():
    # Named qualifiers pass through.
    assert _focal_to_segment("wide", "label", "foo", "foo-mtf-1.png") == "wide"
    assert _focal_to_segment("tele", "label", "foo", "foo-mtf-1.png") == "tele"
    # Numeric focal lengths normalise to NNmm.
    assert _focal_to_segment("100mm", "label", "foo", "foo-mtf-1.png") == "100mm"
    # Frequency annotations are NOT focal qualifiers — return empty so
    # the legacy "(10/30 lp/mm)" form on prime labels keeps parsing.
    assert _focal_to_segment("10/30 lp/mm", "label", "foo", "foo-mtf-1.png") == ""


# --- sidecar discovery + numeric-stem filter -----------------------------


def test_is_numeric_stem_accepts_only_pure_digits():
    base = Path("foo-mtf-1.png")
    assert _is_numeric_stem(base, "foo") is True
    assert _is_numeric_stem(Path("foo-mtf-12.png"), "foo") is True
    assert _is_numeric_stem(Path("foo-mtf-1-overlay.png"), "foo") is False
    assert _is_numeric_stem(Path("foo-mtf-diffraction.png"), "foo") is False
    assert _is_numeric_stem(Path("foo-mtf.png"), "foo") is False


def test_sidecars_for_finds_existing_companions(tmp_path):
    parent = tmp_path
    main = parent / "foo-mtf-1.png"
    main.write_bytes(b"")
    svg = parent / "foo-mtf-1.svg"
    svg.write_bytes(b"")
    overlay = parent / "foo-mtf-1-overlay.png"
    overlay.write_bytes(b"")
    # review.html intentionally absent
    found = {p.name for p in _sidecars_for(main)}
    assert found == {"foo-mtf-1.svg", "foo-mtf-1-overlay.png"}


# --- analysis.md rewrite --------------------------------------------------


def test_rewrite_analysis_replaces_all_basenames():
    text = (
        "MTF charts:\n"
        "- [foo-mtf-1.png](foo-mtf-1.png) -- diffraction MTF\n"
        "- [foo-mtf-2.png](foo-mtf-2.png) -- geometrical MTF\n"
        "\n"
        "Also see [foo-mtf-1-overlay.png](foo-mtf-1-overlay.png).\n"
    )
    name_map = {
        "foo-mtf-1.png": "foo-mtf-diffraction.png",
        "foo-mtf-2.png": "foo-mtf-geometric.png",
        "foo-mtf-1-overlay.png": "foo-mtf-diffraction-overlay.png",
    }
    rewritten = _rewrite_analysis(text, name_map)
    assert "foo-mtf-1.png" not in rewritten
    assert "foo-mtf-2.png" not in rewritten
    assert "foo-mtf-1-overlay.png" not in rewritten
    assert "foo-mtf-diffraction.png" in rewritten
    assert "foo-mtf-geometric.png" in rewritten
    assert "foo-mtf-diffraction-overlay.png" in rewritten


# --- folder planning end-to-end ------------------------------------------


def _make_prime_folder(tmp_path: Path, slug: str) -> Path:
    folder = tmp_path / slug
    folder.mkdir()
    (folder / f"{slug}-mtf-1.png").write_bytes(b"png1")
    (folder / f"{slug}-mtf-1.svg").write_bytes(b"svg1")
    (folder / f"{slug}-mtf-1-overlay.png").write_bytes(b"overlay")
    (folder / f"{slug}-mtf-2.png").write_bytes(b"png2")
    (folder / "analysis.md").write_text(
        "MTF charts:\n"
        "\n"
        f"- [{slug}-mtf-1.png]({slug}-mtf-1.png) -- diffraction MTF\n"
        f"- [{slug}-mtf-2.png]({slug}-mtf-2.png) -- geometrical MTF\n"
        "\n"
        "## Legend\n",
        encoding="utf-8",
    )
    return folder


def test_plan_for_folder_two_chart_prime_includes_sidecars(tmp_path):
    folder = _make_prime_folder(tmp_path, "foo-bar")
    plan = _plan_for_folder(folder)
    assert plan is not None
    moves = {(r.old.name, r.new.name) for r in plan.renames}
    assert moves == {
        ("foo-bar-mtf-1.png", "foo-bar-mtf-diffraction.png"),
        ("foo-bar-mtf-1.svg", "foo-bar-mtf-diffraction.svg"),
        ("foo-bar-mtf-1-overlay.png", "foo-bar-mtf-diffraction-overlay.png"),
        ("foo-bar-mtf-2.png", "foo-bar-mtf-geometric.png"),
    }
    assert "foo-bar-mtf-diffraction.png" in plan.analysis_new
    assert "foo-bar-mtf-1.png" not in plan.analysis_new


def test_plan_for_folder_missing_label_fails_loud(tmp_path):
    slug = "foo-bar"
    folder = tmp_path / slug
    folder.mkdir()
    (folder / f"{slug}-mtf-1.png").write_bytes(b"")
    (folder / f"{slug}-mtf-2.png").write_bytes(b"")
    # analysis.md lists only -mtf-1 — the script must refuse to guess
    # the type of -mtf-2 rather than silently leaving it numeric.
    (folder / "analysis.md").write_text(
        "MTF charts:\n"
        "\n"
        f"- [{slug}-mtf-1.png]({slug}-mtf-1.png) -- diffraction MTF\n",
        encoding="utf-8",
    )
    with pytest.raises(RenameError, match="missing from"):
        _plan_for_folder(folder)


def test_plan_for_folder_duplicate_suffix_fails_loud(tmp_path):
    # Two files both labelled "diffraction MTF" — this is the zoom case
    # the issue defers to a follow-up; the script must reject it rather
    # than overwriting one with the other.
    slug = "foo-bar"
    folder = tmp_path / slug
    folder.mkdir()
    (folder / f"{slug}-mtf-1.png").write_bytes(b"")
    (folder / f"{slug}-mtf-2.png").write_bytes(b"")
    (folder / "analysis.md").write_text(
        "MTF charts:\n"
        "\n"
        f"- [{slug}-mtf-1.png]({slug}-mtf-1.png) -- diffraction MTF\n"
        f"- [{slug}-mtf-2.png]({slug}-mtf-2.png) -- diffraction MTF\n",
        encoding="utf-8",
    )
    with pytest.raises(RenameError, match="both map to suffix"):
        _plan_for_folder(folder)


def test_plan_for_folder_zoom_wide_tele(tmp_path):
    slug = "foo-zoom"
    folder = tmp_path / slug
    folder.mkdir()
    for n in (1, 2, 3, 4):
        (folder / f"{slug}-mtf-{n}.png").write_bytes(b"")
    (folder / "analysis.md").write_text(
        "MTF charts:\n"
        "\n"
        f"- [{slug}-mtf-1.png]({slug}-mtf-1.png) -- diffraction MTF (wide)\n"
        f"- [{slug}-mtf-2.png]({slug}-mtf-2.png) -- diffraction MTF (tele)\n"
        f"- [{slug}-mtf-3.png]({slug}-mtf-3.png) -- geometrical MTF (wide)\n"
        f"- [{slug}-mtf-4.png]({slug}-mtf-4.png) -- geometrical MTF (tele)\n",
        encoding="utf-8",
    )
    plan = _plan_for_folder(folder)
    assert plan is not None
    moves = {(r.old.name, r.new.name) for r in plan.renames}
    assert moves == {
        (f"{slug}-mtf-1.png", f"{slug}-mtf-diffraction-wide.png"),
        (f"{slug}-mtf-2.png", f"{slug}-mtf-diffraction-tele.png"),
        (f"{slug}-mtf-3.png", f"{slug}-mtf-geometric-wide.png"),
        (f"{slug}-mtf-4.png", f"{slug}-mtf-geometric-tele.png"),
    }


def test_plan_for_folder_no_numeric_files_returns_none(tmp_path):
    # Folder already in canonical form — nothing to do.
    slug = "foo-bar"
    folder = tmp_path / slug
    folder.mkdir()
    (folder / f"{slug}-mtf.png").write_bytes(b"")
    (folder / "analysis.md").write_text(
        f"MTF charts:\n\n- [{slug}-mtf.png]({slug}-mtf.png) -- diffraction MTF\n",
        encoding="utf-8",
    )
    assert _plan_for_folder(folder) is None


# --- charts.py rewrite ---------------------------------------------------


def test_update_charts_py_dry_run_does_not_write(tmp_path, monkeypatch):
    fake = tmp_path / "charts.py"
    fake.write_text(
        'foo = ReferenceChart(\n'
        '    chart_path="docs/optical-specs/sigma-56mm-f1-4-dc-dn-c/'
        'sigma-56mm-f1-4-dc-dn-c-mtf-1.png",\n'
        ')\n',
        encoding="utf-8",
    )
    monkeypatch.setattr("mtfdigitizer.rename.CHARTS_PY", fake)
    name_map = {
        "sigma-56mm-f1-4-dc-dn-c-mtf-1.png": "sigma-56mm-f1-4-dc-dn-c-mtf-diffraction.png",
    }
    n = _update_charts_py(name_map, apply=False)
    assert n == 1
    # File unchanged — dry-run mode.
    assert "sigma-56mm-f1-4-dc-dn-c-mtf-1.png" in fake.read_text(encoding="utf-8")


# --- ADR-033 amendment (S119): vendors with no diff/geo pair ------------


def test_parse_analysis_md_zoom_explicit_focal_no_chart_type():
    # Tamron / Tokina / Laowa publish a single MTF chart-type with
    # no diffraction-vs-geometric distinction (verified S119); the
    # filename suffix is the focal length only.
    text = (
        "MTF charts:\n"
        "\n"
        "- [foo-mtf-1.svg](foo-mtf-1.svg) -- MTF (11mm)\n"
        "- [foo-mtf-2.svg](foo-mtf-2.svg) -- MTF (20mm)\n"
    )
    assert _parse_analysis_md(text, "foo") == {
        "foo-mtf-1.svg": "11mm",
        "foo-mtf-2.svg": "20mm",
    }


def test_parse_analysis_md_macro_compound_qualifier():
    # Laowa 65mm 2x macro publishes three panels keyed by focus
    # distance / magnification.
    text = (
        "MTF charts:\n"
        "\n"
        "- [foo-mtf-1.png](foo-mtf-1.png) -- MTF (65mm, inf)\n"
        "- [foo-mtf-2.png](foo-mtf-2.png) -- MTF (65mm, 1x)\n"
        "- [foo-mtf-3.png](foo-mtf-3.png) -- MTF (65mm, 2x)\n"
    )
    assert _parse_analysis_md(text, "foo") == {
        "foo-mtf-1.png": "65mm-inf",
        "foo-mtf-2.png": "65mm-1x",
        "foo-mtf-3.png": "65mm-2x",
    }


def test_parse_analysis_md_shift_lens_unshifted_shifted():
    # Laowa Zero-D Shift publishes two panels per lens — one for the
    # unshifted image circle, one for the shifted (extended) circle.
    text = (
        "MTF charts:\n"
        "\n"
        "- [foo-mtf-1.png](foo-mtf-1.png) -- MTF (unshifted)\n"
        "- [foo-mtf-2.png](foo-mtf-2.png) -- MTF (shifted)\n"
    )
    assert _parse_analysis_md(text, "foo") == {
        "foo-mtf-1.png": "unshifted",
        "foo-mtf-2.png": "shifted",
    }


def test_focal_to_segment_new_vocabulary():
    for token in ("inf", "1x", "2x", "unshifted", "shifted"):
        assert _focal_to_segment(token, "label", "foo", "foo-mtf-1.png") == token


def test_label_suffix_accepts_bare_mtf():
    # The ADR-033 amendment introduced bare `mtf` (no diffraction/geometric
    # prefix) for vendors with one chart-type. Its suffix is empty so the
    # qualifier stands alone in the filename.
    assert LABEL_SUFFIX["mtf"] == ""


def test_plan_for_folder_handles_bare_mtf_png_as_panel_1(tmp_path):
    # Legacy convention: when a folder has both `<slug>-mtf.png` AND
    # `<slug>-mtf-N.png`, the bare file is panel 1 of N (older folders
    # saved the first panel without a `-1` suffix).
    slug = "venus-zoom"
    folder = tmp_path / slug
    folder.mkdir()
    (folder / f"{slug}-mtf.png").write_bytes(b"panel1")
    (folder / f"{slug}-mtf-2.png").write_bytes(b"panel2")
    (folder / "analysis.md").write_text(
        "MTF charts:\n"
        "\n"
        f"- [{slug}-mtf.png]({slug}-mtf.png) -- MTF (8mm)\n"
        f"- [{slug}-mtf-2.png]({slug}-mtf-2.png) -- MTF (16mm)\n",
        encoding="utf-8",
    )
    plan = _plan_for_folder(folder)
    assert plan is not None
    moves = {(r.old.name, r.new.name) for r in plan.renames}
    assert moves == {
        (f"{slug}-mtf.png", f"{slug}-mtf-8mm.png"),
        (f"{slug}-mtf-2.png", f"{slug}-mtf-16mm.png"),
    }


def test_plan_for_folder_rewrites_specs_log_md(tmp_path):
    # specs-log.md prose mentions of `-mtf-1.png` / `-mtf-2.png` must
    # be rewritten alongside analysis.md, otherwise documentation goes
    # out of sync with the rename.
    slug = "tokina-foo"
    folder = tmp_path / slug
    folder.mkdir()
    (folder / f"{slug}-mtf-1.png").write_bytes(b"")
    (folder / f"{slug}-mtf-2.png").write_bytes(b"")
    (folder / "analysis.md").write_text(
        "MTF charts:\n"
        "\n"
        f"- [{slug}-mtf-1.png]({slug}-mtf-1.png) -- MTF (11mm)\n"
        f"- [{slug}-mtf-2.png]({slug}-mtf-2.png) -- MTF (18mm)\n",
        encoding="utf-8",
    )
    (folder / "specs-log.md").write_text(
        f"The two panels are stored as `{slug}-mtf-1.png` (11mm) "
        f"and `{slug}-mtf-2.png` (18mm).\n",
        encoding="utf-8",
    )
    plan = _plan_for_folder(folder)
    assert plan is not None
    assert len(plan.other_md_updates) == 1
    md_path, _old, new_text = plan.other_md_updates[0]
    assert md_path.name == "specs-log.md"
    assert f"{slug}-mtf-1.png" not in new_text
    assert f"{slug}-mtf-11mm.png" in new_text
    assert f"{slug}-mtf-18mm.png" in new_text


def test_update_charts_py_apply_rewrites_literal(tmp_path, monkeypatch):
    fake = tmp_path / "charts.py"
    fake.write_text(
        'foo = ReferenceChart(\n'
        '    chart_path="docs/optical-specs/sigma-56mm-f1-4-dc-dn-c/'
        'sigma-56mm-f1-4-dc-dn-c-mtf-1.png",\n'
        ')\n'
        '# A prose mention of sigma-56mm-f1-4-dc-dn-c-mtf-1.png in a comment.\n',
        encoding="utf-8",
    )
    monkeypatch.setattr("mtfdigitizer.rename.CHARTS_PY", fake)
    name_map = {
        "sigma-56mm-f1-4-dc-dn-c-mtf-1.png": "sigma-56mm-f1-4-dc-dn-c-mtf-diffraction.png",
    }
    n = _update_charts_py(name_map, apply=True)
    assert n == 1
    text = fake.read_text(encoding="utf-8")
    # chart_path literal rewritten.
    assert (
        'chart_path="docs/optical-specs/sigma-56mm-f1-4-dc-dn-c/'
        'sigma-56mm-f1-4-dc-dn-c-mtf-diffraction.png"'
    ) in text
    # Prose comment NOT touched — pattern only matches chart_path="..." form.
    assert "# A prose mention of sigma-56mm-f1-4-dc-dn-c-mtf-1.png" in text
