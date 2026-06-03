"""Tests for the MTF rename helper (#1017)."""

from __future__ import annotations

from pathlib import Path

import pytest

from mtfdigitizer.rename import (
    LABEL_SUFFIX,
    RenameError,
    _is_numeric_stem,
    _parse_analysis_md,
    _plan_for_folder,
    _rewrite_analysis,
    _sidecars_for,
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
