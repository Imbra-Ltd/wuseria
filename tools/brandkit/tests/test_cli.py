"""Tests for the shared CLI + audit runners.

Drive them through a stub tool + FakeFetcher (no network), patching argv,
and assert on captured stdout.
"""

import sys
from pathlib import Path

import pytest

from brandkit import BrandConfig, BrandExtractor, BrandTool, audit, run
from brandkit.cli import format_ts_fields
from pagefetch import ContentMode, FakeFetcher

TOKINA_23_URL = "https://tokinalens.com/product/atx-m-23mm-f1-4-x/"


class StubExtractor(BrandExtractor):
    def __init__(self, optical=None, physical=None):
        self.config = BrandConfig(
            name="Tokina", slug_prefix="tokina", content_mode=ContentMode.HTML
        )
        self._optical = optical or {"elements": 11, "groups": 10}
        self._physical = physical or {}

    def extract_optical(self, content: str) -> dict:
        return dict(self._optical)

    def extract_physical(self, content: str) -> dict:
        return dict(self._physical)


def make_tool(lenses_sample_path, tmp_path, **kw) -> BrandTool:
    fake = FakeFetcher(responses={TOKINA_23_URL: "<html>x</html>"})
    return BrandTool(
        extractor=StubExtractor(**kw),
        source=fake,
        lenses_path=lenses_sample_path,
        specs_root=tmp_path / "optical-specs",
    )


# --- format_ts_fields (moved into brandkit.cli) ---


def test_format_ts_fields_full():
    out = format_ts_fields(
        {"elements": 11, "groups": 10, "special": ["2 SD"], "coating": ["Multi-coating"]}
    )
    assert "opticalElements: 11," in out
    assert "opticalGroups: 10," in out
    assert 'specialElements: ["2 SD"],' in out
    assert 'coating: ["Multi-coating"],' in out


def test_format_ts_fields_omits_absent():
    assert format_ts_fields({"elements": 8}) == "    opticalElements: 8,"


# --- run() (the fetch CLI runner) ---


def test_run_dry_run_lists_lenses(lenses_sample_path, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["fetch_specs.py", "--dry-run"])
    run(make_tool(lenses_sample_path, tmp_path))
    out = capsys.readouterr().out
    assert "Found 2 Tokina lenses" in out
    assert "atx-m 23mm f/1.4 X" in out


def test_run_filter_narrows(lenses_sample_path, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["fetch_specs.py", "--dry-run", "--filter", "33mm"])
    run(make_tool(lenses_sample_path, tmp_path))
    out = capsys.readouterr().out
    assert "Filtered to 1" in out
    assert "33mm" in out


def test_run_specs_only_prints_ts_fields(lenses_sample_path, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["fetch_specs.py", "--specs-only"])
    run(make_tool(lenses_sample_path, tmp_path))
    out = capsys.readouterr().out
    assert "opticalElements: 11," in out


def test_run_verify_reports_clean(lenses_sample_path, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["fetch_specs.py", "--verify"])
    # Fixture stores weight 276 for the 23mm; extractor returns matching.
    run(make_tool(lenses_sample_path, tmp_path, physical={"weight": 276}))
    out = capsys.readouterr().out
    assert "Verify:" in out
    assert "with issues" in out


def test_run_verify_flags_mismatch(lenses_sample_path, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["fetch_specs.py", "--verify"])
    run(make_tool(lenses_sample_path, tmp_path, physical={"weight": 999}))
    out = capsys.readouterr().out
    assert "MISMATCH weight" in out


# --- audit() (the audit runner) ---


def test_audit_reports_missing_fields(lenses_sample_path, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["audit.py"])
    audit(make_tool(lenses_sample_path, tmp_path))
    out = capsys.readouterr().out
    # Audit scans ALL brand entries in lenses.ts (unlike fetch, which needs
    # an officialUrl) — so it sees 3 Tokina lenses incl. the URL-less one,
    # and flags missing fields/images.
    assert "no opticalElements" in out
    assert "no MTF chart" in out
    assert "no officialUrl" in out  # the URL-less fixture lens
    assert "out of 3 lenses" in out
