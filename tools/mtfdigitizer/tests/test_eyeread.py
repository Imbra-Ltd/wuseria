"""Tests for the eye-read.md parser + GT updater (ADR-048)."""

from __future__ import annotations

import pytest

from mtfdigitizer.eyeread import (
    Cell,
    column_to_field,
    format_cell,
    heading_to_gt_key,
    parse_cell,
    parse_eye_read,
    views_to_gt,
)


# --- Cell parsing --------------------------------------------------------


def test_parse_bare_number() -> None:
    cell = parse_cell("0.43")
    assert cell == Cell(value=0.43, mark="")
    assert cell.is_verified
    assert cell.gt_value == 0.43


def test_parse_corrected_with_bang() -> None:
    cell = parse_cell("0.45!")
    assert cell == Cell(value=0.45, mark="!")
    assert cell.is_verified
    assert cell.gt_value == 0.45


def test_parse_unknown_with_question() -> None:
    cell = parse_cell("0.43?")
    assert cell == Cell(value=0.43, mark="?")
    assert not cell.is_verified
    assert cell.gt_value is None


def test_parse_bare_question() -> None:
    cell = parse_cell("?")
    assert cell == Cell(value=None, mark="?")
    assert cell.gt_value is None


def test_parse_em_dash() -> None:
    cell = parse_cell("—")
    assert cell == Cell(value=None, mark="")
    assert cell.gt_value is None


def test_parse_empty() -> None:
    assert parse_cell("").gt_value is None
    assert parse_cell("   ").gt_value is None


def test_parse_handles_whitespace_padding() -> None:
    cell = parse_cell("  0.45!  ")
    assert cell == Cell(value=0.45, mark="!")


# --- Cell formatting -----------------------------------------------------


def test_format_bare_value() -> None:
    assert format_cell(Cell(value=0.43, mark=""), width=5) == "0.43 "


def test_format_corrected_value() -> None:
    assert format_cell(Cell(value=0.45, mark="!"), width=5) == "0.45!"


def test_format_question() -> None:
    assert format_cell(Cell(value=None, mark="?"), width=5) == "?    "


def test_format_em_dash() -> None:
    assert format_cell(Cell(value=None, mark=""), width=5) == "—    "


# --- View parsing --------------------------------------------------------


_TWO_VIEW_DOC = """\
# Eye-read — Example

Some prose explaining the format.

## f/1.2 (max)

| Position (mm) | 10S   | 10M   |
| ------------- | ----- | ----- |
| 0.0           | 0.88! | 0.88  |
| 1.4           | 0.89  | 0.90? |
| 14.0          | 0.77! | 0.60! |

## f/5.6 (stopped)

| Position (mm) | 10S   | 10M   |
| ------------- | ----- | ----- |
| 0.0           | 0.95  | 0.95  |
| 14.0          | 0.95  | 0.93  |
"""


def test_parse_eye_read_extracts_two_views() -> None:
    views = parse_eye_read(_TWO_VIEW_DOC)
    assert len(views) == 2
    assert views[0].heading == "f/1.2 (max)"
    assert views[1].heading == "f/5.6 (stopped)"


def test_parse_eye_read_captures_marks() -> None:
    views = parse_eye_read(_TWO_VIEW_DOC)
    max_view = views[0]
    # Row 0: 0.88! corrected, 0.88 silent
    _, row0 = max_view.cells[0]
    assert row0["10S"] == Cell(value=0.88, mark="!")
    assert row0["10M"] == Cell(value=0.88, mark="")
    # Row 1: 0.89 silent, 0.90? unknown
    _, row1 = max_view.cells[1]
    assert row1["10S"] == Cell(value=0.89, mark="")
    assert row1["10M"] == Cell(value=0.90, mark="?")


def test_parse_eye_read_ignores_non_table_headings() -> None:
    doc = _TWO_VIEW_DOC + "\n## Transcribing to GT\n\nSome prose, no table.\n"
    views = parse_eye_read(doc)
    # Still two views — the prose-only heading is skipped.
    assert len(views) == 2


# --- Heading → GT key ----------------------------------------------------


def test_heading_to_gt_key_extracts_parens() -> None:
    assert heading_to_gt_key("f/1.2 (max)") == "max"
    assert heading_to_gt_key("f/5.6 (stopped)") == "stopped"


def test_heading_to_gt_key_returns_none_for_lpmm() -> None:
    # Fuji-style headings have no aperture label; caller supplies default.
    assert heading_to_gt_key("15 lp/mm") is None
    assert heading_to_gt_key("45 lp/mm") is None


# --- Column → field ------------------------------------------------------


def test_column_to_field_adds_freq_prefix() -> None:
    assert column_to_field("10S") == "freq10S"
    assert column_to_field("45M") == "freq45M"


def test_column_to_field_passes_through_full_name() -> None:
    assert column_to_field("freq10S") == "freq10S"


# --- views_to_gt end-to-end ----------------------------------------------


def test_views_to_gt_builds_dict() -> None:
    views = parse_eye_read(_TWO_VIEW_DOC)
    gt = views_to_gt(views, default_aperture="f/1.2")
    assert set(gt.keys()) == {"max", "stopped"}
    assert gt["max"]["freq10S"] == (0.88, 0.89, 0.77)
    # 0.90? in row 1 becomes None in GT
    assert gt["max"]["freq10M"] == (0.88, None, 0.60)
    assert gt["stopped"]["freq10S"] == (0.95, 0.95)


def test_views_to_gt_uses_default_aperture_when_heading_omits() -> None:
    doc = """\
# Eye-read

## 15 lp/mm

| Position (mm) | 15S   | 15M   |
| ------------- | ----- | ----- |
| 0.0           | 0.99  | 0.99  |
"""
    views = parse_eye_read(doc)
    gt = views_to_gt(views, default_aperture="f/4")
    assert "f/4" in gt
    assert gt["f/4"]["freq15S"] == (0.99,)


# --- Round-trip ----------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    ["0.43", "0.45!", "0.43?", "?", "—", "0.00", "1.00"],
)
def test_parse_format_round_trip(raw: str) -> None:
    cell = parse_cell(raw)
    rendered = format_cell(cell, width=5)
    reparsed = parse_cell(rendered)
    assert reparsed == cell
