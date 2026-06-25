"""Eye-read override preservation for emit_*_tier2 splice (#1301, #1305).

Some MTF chart cells are mistracked by the ridge-tracker extractor but
the correct value is documented in `docs/optical-specs/<slug>/eye-read.md`.
The maintainer applies the corrected value inline in
`src/data/mtf-readings.ts` with a comment block whose first or any line
contains the literal string ``eye-read override``. Without this module,
the next `emit_*_tier2 --write` would silently clobber those cells back
to the (wrong) extractor output.

The detector here scans committed entry text for cells annotated with
the override marker and returns enough information for the splice to
swap the override block back over the freshly emitted cell line.

Grammar of an override:

    <indent>// ... eye-read override ... (the marker; may be one of many comment lines)
    <indent>// ... (zero or more additional comment lines)
    <indent><freq>: { S: <V>, M: <V> },

The contiguous run of `//` lines immediately above a freq cell line
is preserved verbatim, along with the cell line itself. Whitespace
and exact byte content carry through unchanged.

Override key: ``(slug, position_mm, freq)``. The freq line is the
preservation unit — the comment may say "30 M: override 0.58" but
the data row is `30: { S: ..., M: ... },`, which is the cell-line
unit the splice can match against the fresh literal.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


# Marker that flags an override comment block. Match is case-sensitive
# and literal; underscoring/hyphenation variants are explicitly NOT
# supported — the convention is the literal string ``eye-read override``.
OVERRIDE_MARKER = "eye-read override"


# Cell line: 14 leading spaces (one per emit level: chart → readings →
# reading → samples → freq), then ``<freq>: { S: ..., M: ... },``.
# The freq must be an integer; S and M values may be null or numeric.
_CELL_LINE_RE = re.compile(
    r"^(?P<indent>\s+)(?P<freq>\d+):\s*\{\s*S:\s*[^,]+,\s*M:\s*[^}]+\},\s*$"
)

# Position line: ``            position: <value>,`` at the parent indent
# (12 spaces in emit output). Captures the numeric position.
_POSITION_LINE_RE = re.compile(
    r"^\s+position:\s*(?P<pos>-?\d+(?:\.\d+)?),\s*$"
)

# Aperture line: ``        aperture: "f/N",`` — discriminates which
# MtfChart panel (which f-stop) a cell belongs to. A single lens has
# multiple panels (TTartisan: f/max + f/5.6; Fuji zooms: wide + tele),
# so two cells can share (position, freq) under different apertures.
_APERTURE_LINE_RE = re.compile(
    r'^\s+aperture:\s*"(?P<aperture>[^"]+)",\s*$'
)

# Comment line at the cell indent: ``// ...``. Trailing newline kept off.
_COMMENT_LINE_RE = re.compile(r"^\s+//.*$")


@dataclass(frozen=True)
class OverrideBlock:
    """One preserved cell line and its comment block.

    The block is keyed by ``(aperture, position_mm, freq)`` and carries
    the verbatim text lines (without trailing newlines) so the splice
    can re-emit them byte-for-byte. Aperture is part of the key because
    a lens has multiple MtfChart panels (e.g. TTartisan: max + stopped;
    Fuji zooms: wide + tele) and the same (position, freq) cell appears
    in each — overrides MUST be panel-specific.
    """

    aperture: str
    position_mm: float
    freq: int
    comment_lines: tuple[str, ...]
    cell_line: str


# Key shape: (aperture, position_mm, freq).
OverrideKey = tuple[str, float, int]


def parse_overrides(entry_text: str) -> dict[OverrideKey, OverrideBlock]:
    """Extract override blocks from one committed entry's literal text.

    `entry_text` is the multi-line text of a single ``"slug": { ... },``
    entry (the slug header line through its closing brace). Returns a
    dict keyed by ``(aperture, position_mm, freq)`` so the splice can
    look up overrides per cell within each MtfChart panel.

    A cell qualifies as an override iff the contiguous run of comment
    lines immediately above it contains the literal ``eye-read override``
    marker in at least one of those comments.
    """
    lines = entry_text.splitlines()
    overrides: dict[OverrideKey, OverrideBlock] = {}

    current_aperture: str | None = None
    current_position: float | None = None
    for index, line in enumerate(lines):
        ap_match = _APERTURE_LINE_RE.match(line)
        if ap_match:
            current_aperture = ap_match.group("aperture")
            current_position = None
            continue

        pos_match = _POSITION_LINE_RE.match(line)
        if pos_match:
            current_position = float(pos_match.group("pos"))
            continue

        cell_match = _CELL_LINE_RE.match(line)
        if (
            not cell_match
            or current_aperture is None
            or current_position is None
        ):
            continue

        # Walk backward to collect the contiguous run of comment lines
        # directly above this cell line.
        comment_run: list[str] = []
        scan = index - 1
        while scan >= 0 and _COMMENT_LINE_RE.match(lines[scan]):
            comment_run.append(lines[scan])
            scan -= 1
        comment_run.reverse()

        if not comment_run:
            continue

        if not any(OVERRIDE_MARKER in c for c in comment_run):
            continue

        freq = int(cell_match.group("freq"))
        overrides[(current_aperture, current_position, freq)] = OverrideBlock(
            aperture=current_aperture,
            position_mm=current_position,
            freq=freq,
            comment_lines=tuple(comment_run),
            cell_line=line,
        )

    return overrides


def apply_overrides(
    fresh_literal: str,
    overrides: dict[OverrideKey, OverrideBlock],
) -> str:
    """Overlay `overrides` onto the freshly-emitted entry literal text.

    For each ``(aperture, position, freq)`` in `overrides`, find the
    matching cell line in `fresh_literal` (under the corresponding
    ``aperture:`` panel and ``position:`` reading) and replace it with
    the override's comment lines followed by the override's cell line.

    Cells in `fresh_literal` that do not have an override pass through
    unchanged. Overrides whose key no longer appears in the fresh
    literal are skipped silently — the underlying reading may have
    been dropped by the extractor (e.g. all-null row drop) or the
    panel may have been renamed, in which case there is nothing to
    overlay.
    """
    if not overrides:
        return fresh_literal

    lines = fresh_literal.splitlines(keepends=True)
    out: list[str] = []

    current_aperture: str | None = None
    current_position: float | None = None
    for line in lines:
        ap_match = _APERTURE_LINE_RE.match(line)
        if ap_match:
            current_aperture = ap_match.group("aperture")
            current_position = None
            out.append(line)
            continue

        pos_match = _POSITION_LINE_RE.match(line)
        if pos_match:
            current_position = float(pos_match.group("pos"))
            out.append(line)
            continue

        cell_match = _CELL_LINE_RE.match(line)
        if (
            not cell_match
            or current_aperture is None
            or current_position is None
        ):
            out.append(line)
            continue

        freq = int(cell_match.group("freq"))
        override = overrides.get((current_aperture, current_position, freq))
        if override is None:
            out.append(line)
            continue

        # Replace this cell line with the comment block + override cell
        # line. Comment lines carry no trailing newline (splitlines()
        # stripped them in `parse_overrides`), so add one each.
        for comment in override.comment_lines:
            out.append(comment + "\n")
        out.append(override.cell_line + "\n")

    return "".join(out)


# --- entry-text extraction ------------------------------------------------
#
# Both emit scripts need to pull the text of a single committed entry by
# slug — the same brace-depth walk the splice already does, but yielding
# the entry text instead of skipping past it.


_ENTRY_OPEN_RE = re.compile(r'^\s*"(?P<slug>[^"]+)":\s*\{\s*$')


def overlay_committed_overrides(
    source: str, fresh_entries: dict[str, str]
) -> dict[str, str]:
    """Return a copy of `fresh_entries` with committed overrides preserved.

    For each slug in `fresh_entries`, looks up the entry's existing text
    in `source`, scans it for `eye-read override` cells, and overlays
    those cells onto the freshly-emitted literal. Slugs not yet present
    in `source` (new lenses being added) pass through unchanged.

    This is the single seam both `emit_ttartisan_tier2` and
    `emit_fuji_tier2` use to gate `--write` on existing overrides
    without each script knowing about the override grammar.
    """
    out: dict[str, str] = {}
    for slug, fresh_literal in fresh_entries.items():
        committed = extract_entry_text(source, slug)
        if committed is None:
            out[slug] = fresh_literal
            continue
        overrides = parse_overrides(committed)
        out[slug] = apply_overrides(fresh_literal, overrides)
    return out


def extract_entry_text(source: str, slug: str) -> str | None:
    """Return the multi-line text of one entry's literal, or None.

    Walks `source` line by line; on hitting the entry-open line for
    `slug`, consumes lines until brace depth returns to zero. Returns
    the entry's text with trailing newlines preserved on each line.

    Returns None if the slug is not present (a new lens being added),
    in which case the caller has nothing to preserve.
    """
    lines = source.splitlines(keepends=True)
    n = len(lines)
    i = 0
    while i < n:
        m = _ENTRY_OPEN_RE.match(lines[i])
        if m and m.group("slug") == slug:
            collected: list[str] = []
            brace_depth = 0
            while i < n:
                cur = lines[i]
                collected.append(cur)
                brace_depth += cur.count("{") - cur.count("}")
                i += 1
                if brace_depth <= 0:
                    break
            return "".join(collected)
        i += 1
    return None
