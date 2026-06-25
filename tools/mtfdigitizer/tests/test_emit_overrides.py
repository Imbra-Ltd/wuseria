"""Tests for the override-respecting splice helper (#1301, #1305).

`_emit_overrides.parse_overrides` extracts eye-read override blocks
from a committed entry's literal text; `apply_overrides` overlays
those blocks back onto a freshly-emitted literal. The combination
makes `emit_*_tier2 --write` non-destructive over hand-patched cells.
"""

from __future__ import annotations

import textwrap

from mtfdigitizer.scripts._emit_overrides import (
    OverrideBlock,
    apply_overrides,
    extract_entry_text,
    parse_overrides,
)


# Shape mirrors the af-35 entry as it lives in mtf-readings.ts today
# (lines 13510–13601). One override at position 12.6 on freq 30; every
# other cell is plain extractor output.
AF35_ENTRY = textwrap.dedent('''\
      "ttartisan-af-35mm-f1-8": {
        source: "https://www.ttartisan.com/?af-lens/AF-35-II.html",
        mtfType: "computed",
        charts: [
          {
            aperture: "f/1.8",
            confidence: "HIGH",
            readings: [
              {
                position: 0,
                samples: {
                  10: { S: 0.95, M: 0.95 },
                  30: { S: 0.79, M: 0.79 },
                },
              },
              {
                position: 12.6,
                samples: {
                  10: { S: 0.71, M: 0.89 },
                  // 30 M: eye-read override 0.58 (extractor produces 0.66 ---
                  // ridge tracker still locks onto solid S30 at the right
                  // corner crossing despite #1214 fixing pos 14). See
                  // docs/optical-specs/ttartisan-af-35mm-f1-8/eye-read.md.
                  // WARN: emit_ttartisan_tier2 --write will overwrite this.
                  30: { S: 0.31, M: 0.58 },
                },
              },
              {
                position: 14,
                samples: {
                  10: { S: 0.38, M: 0.88 },
                  30: { S: 0.12, M: null },
                },
              },
            ],
          },
        ],
      },
''')


def test_parse_overrides_finds_marked_cell():
    """A cell with `eye-read override` in the comment block above is
    extracted, keyed by (aperture, position, freq)."""
    overrides = parse_overrides(AF35_ENTRY)
    assert ("f/1.8", 12.6, 30) in overrides
    block = overrides[("f/1.8", 12.6, 30)]
    assert block.aperture == "f/1.8"
    assert block.position_mm == 12.6
    assert block.freq == 30
    # The override cell line is preserved verbatim.
    assert "S: 0.31, M: 0.58" in block.cell_line
    # The comment block is the 5 contiguous `//` lines above the cell.
    assert len(block.comment_lines) == 5
    assert "eye-read override 0.58" in block.comment_lines[0]
    assert "WARN" in block.comment_lines[-1]


def test_parse_overrides_skips_cells_without_marker():
    """Cells without `eye-read override` in their comment block stay
    out of the overrides map."""
    overrides = parse_overrides(AF35_ENTRY)
    # pos 0 / 14 have no comment block at all
    assert ("f/1.8", 0.0, 10) not in overrides
    assert ("f/1.8", 0.0, 30) not in overrides
    assert ("f/1.8", 14.0, 10) not in overrides
    assert ("f/1.8", 14.0, 30) not in overrides
    # pos 12.6 / freq 10 has no comment block (just neighbouring cell did)
    assert ("f/1.8", 12.6, 10) not in overrides


def test_parse_overrides_ignores_unmarked_comment_block():
    """A comment block above a cell that does NOT contain the marker
    is NOT treated as an override."""
    entry = textwrap.dedent('''\
              {
                position: 5.6,
                samples: {
                  // some unrelated commentary
                  // about this cell
                  10: { S: 0.5, M: 0.5 },
                },
              },
    ''')
    overrides = parse_overrides(entry)
    assert overrides == {}


def test_parse_overrides_handles_multiple_overrides_in_one_entry():
    """Two overrides in the same entry both surface, keyed independently."""
    entry = textwrap.dedent('''\
              {
                aperture: "f/1.2",
                readings: [
                  {
                    position: 5.0,
                    samples: {
                      // eye-read override 0.4
                      10: { S: 0.4, M: 0.4 },
                    },
                  },
                  {
                    position: 10.0,
                    samples: {
                      // eye-read override 0.6
                      30: { S: 0.6, M: 0.6 },
                    },
                  },
                ],
              },
    ''')
    overrides = parse_overrides(entry)
    assert ("f/1.2", 5.0, 10) in overrides
    assert ("f/1.2", 10.0, 30) in overrides
    assert len(overrides) == 2


def test_parse_overrides_isolates_per_aperture_panels():
    """Two panels (apertures) on one lens — an override on one panel
    MUST NOT apply to a same-(position, freq) cell on the other.

    Regression: the first wiring of this helper keyed only on
    (position, freq), so the af-35 f/1.8 override at pos 12.6 was
    incorrectly overlaid onto the f/5.6 cell at the same position
    during the splice smoke test.
    """
    entry = textwrap.dedent('''\
              {
                aperture: "f/1.8",
                readings: [
                  {
                    position: 12.6,
                    samples: {
                      // eye-read override 0.58
                      30: { S: 0.31, M: 0.58 },
                    },
                  },
                ],
              },
              {
                aperture: "f/5.6",
                readings: [
                  {
                    position: 12.6,
                    samples: {
                      30: { S: 0.82, M: 0.67 },
                    },
                  },
                ],
              },
    ''')
    overrides = parse_overrides(entry)
    # Only the f/1.8 panel carries the override.
    assert ("f/1.8", 12.6, 30) in overrides
    assert ("f/5.6", 12.6, 30) not in overrides


def test_apply_overrides_preserves_marker_block():
    """`apply_overrides` substitutes the override block (comment + cell)
    for the corresponding cell line in the fresh literal."""
    fresh = textwrap.dedent('''\
              {
                aperture: "f/1.8",
                readings: [
                  {
                    position: 12.6,
                    samples: {
                      10: { S: 0.71, M: 0.89 },
                      30: { S: 0.31, M: 0.66 },
                    },
                  },
                ],
              },
    ''')
    block = OverrideBlock(
        aperture="f/1.8",
        position_mm=12.6,
        freq=30,
        comment_lines=(
            "                      // 30 M: eye-read override 0.58",
            "                      // WARN: ...",
        ),
        cell_line="                      30: { S: 0.31, M: 0.58 },",
    )
    out = apply_overrides(fresh, {("f/1.8", 12.6, 30): block})
    # Override comment + cell line are present
    assert "eye-read override 0.58" in out
    assert "S: 0.31, M: 0.58" in out
    # The extractor's wrong value is NOT
    assert "S: 0.31, M: 0.66" not in out
    # The non-overridden cell (freq 10) is unchanged
    assert "10: { S: 0.71, M: 0.89 }" in out


def test_apply_overrides_does_not_leak_across_apertures():
    """An override scoped to one aperture MUST NOT overlay onto a
    same-(position, freq) cell in a different aperture panel.

    This regression test pins down the bug found in the first wiring:
    the f/1.8 override at pos 12.6 / freq 30 was applied to the f/5.6
    cell at the same position during the af-35 --check smoke test.
    """
    fresh = textwrap.dedent('''\
              {
                aperture: "f/1.8",
                readings: [
                  {
                    position: 12.6,
                    samples: {
                      30: { S: 0.31, M: 0.66 },
                    },
                  },
                ],
              },
              {
                aperture: "f/5.6",
                readings: [
                  {
                    position: 12.6,
                    samples: {
                      30: { S: 0.82, M: 0.67 },
                    },
                  },
                ],
              },
    ''')
    block = OverrideBlock(
        aperture="f/1.8",
        position_mm=12.6,
        freq=30,
        comment_lines=("                      // eye-read override 0.58",),
        cell_line="                      30: { S: 0.31, M: 0.58 },",
    )
    out = apply_overrides(fresh, {("f/1.8", 12.6, 30): block})
    # f/1.8 panel: extractor value replaced
    assert "M: 0.58" in out
    # f/5.6 panel: extractor value still present (NOT clobbered)
    assert "S: 0.82, M: 0.67" in out


def test_apply_overrides_no_overrides_returns_input_unchanged():
    """Empty overrides map → fresh literal returned verbatim."""
    fresh = "hello\nworld\n"
    assert apply_overrides(fresh, {}) == fresh


def test_apply_overrides_skips_missing_position():
    """Overrides whose (aperture, position, freq) is not present in the
    fresh literal are silently skipped — the row may have been dropped
    by the extractor (e.g. all-null row), nothing to overlay."""
    fresh = textwrap.dedent('''\
              {
                aperture: "f/1.2",
                readings: [
                  {
                    position: 1.4,
                    samples: {
                      10: { S: 0.9, M: 0.9 },
                    },
                  },
                ],
              },
    ''')
    block = OverrideBlock(
        aperture="f/1.2",
        position_mm=99.0,  # not in fresh
        freq=30,
        comment_lines=("// orphaned",),
        cell_line="                      30: { S: 0.1, M: 0.1 },",
    )
    out = apply_overrides(fresh, {("f/1.2", 99.0, 30): block})
    # Fresh literal is unchanged (no insertion, no removal)
    assert out == fresh


def test_apply_overrides_skips_missing_freq_at_known_position():
    """Override at a position present in fresh but with a freq the
    fresh row does not carry — no overlay performed."""
    fresh = textwrap.dedent('''\
              {
                aperture: "f/1.2",
                readings: [
                  {
                    position: 5.0,
                    samples: {
                      10: { S: 0.9, M: 0.9 },
                    },
                  },
                ],
              },
    ''')
    block = OverrideBlock(
        aperture="f/1.2",
        position_mm=5.0,
        freq=40,  # fresh row has freq 10 only
        comment_lines=("// orphaned",),
        cell_line="                      40: { S: 0.1, M: 0.1 },",
    )
    out = apply_overrides(fresh, {("f/1.2", 5.0, 40): block})
    assert out == fresh
    assert "40:" not in out


def test_extract_entry_text_returns_full_literal():
    """Pulls one slug's entry text from a multi-entry source."""
    source = textwrap.dedent('''\
      const mtfReadings = {
        "lens-a": {
          source: "https://a/",
          mtfType: "computed",
          charts: [
            { aperture: "f/1.2", confidence: "HIGH", readings: [] },
          ],
        },
        "lens-b": {
          source: "https://b/",
          mtfType: "computed",
          charts: [],
        },
      };
    ''')
    entry_a = extract_entry_text(source, "lens-a")
    assert entry_a is not None
    assert '"lens-a"' in entry_a
    assert '"lens-b"' not in entry_a
    assert "https://a/" in entry_a
    assert "https://b/" not in entry_a


def test_extract_entry_text_returns_none_when_slug_absent():
    """A slug not present in source returns None (new lens being added)."""
    source = '"other-lens": {\n  source: "https://x/",\n},\n'
    assert extract_entry_text(source, "missing") is None


def test_roundtrip_af35_override_survives_overlay():
    """End-to-end on the af-35 shape: parse the committed entry, then
    overlay onto a fresh literal where the override cell has the
    extractor's wrong value — the override wins."""
    overrides = parse_overrides(AF35_ENTRY)
    fresh = textwrap.dedent('''\
              {
                aperture: "f/1.8",
                readings: [
                  {
                    position: 12.6,
                    samples: {
                      10: { S: 0.71, M: 0.89 },
                      30: { S: 0.31, M: 0.66 },
                    },
                  },
                ],
              },
    ''')
    out = apply_overrides(fresh, overrides)
    assert "M: 0.58" in out
    assert "M: 0.66" not in out
    # WARN line carried over too
    assert "WARN" in out
