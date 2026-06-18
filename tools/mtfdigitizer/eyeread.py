"""Eye-read.md parser and GT updater (ADR-048).

A Tier 1 anchor's `eye-read.md` is the single source of truth for the
maintainer's reading of each sample position. Each cell carries one
of three states:

- bare number (e.g. `0.43`) — extractor's prediction, maintainer
  judged it fine ("silent verification").
- number with `!` (e.g. `0.45!`) — maintainer-corrected.
- number with `?` (e.g. `0.43?`) or bare `?` — maintainer hasn't
  read this cell; becomes `None` in the GT tuple.

This module knows how to:

1. **Parse** an existing `eye-read.md` into a `GroundTruthCurves`-
   shaped dict for transcription, plus a parallel mark map for the
   scaffolder's refresh-on-rerun logic.
2. **Transcribe** that GT dict into the matching `_<LENS>_GT` tuple
   inside `referenceset/charts.py`, preserving surrounding code.
3. **Run calibrate** for the affected chart and report per-field
   deltas.

The CLI lives in this module: ``py -m mtfdigitizer.eyeread <slug>
[--apply]``.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


# --- Cell state ----------------------------------------------------------


@dataclass(frozen=True)
class Cell:
    """One parsed cell from an eye-read.md table.

    `value` is the displayed number (always present for bare numbers
    and ``!``/``?``-marked numbers; ``None`` for cells that are
    literally just ``?`` or empty). `mark` is ``""``, ``"!"`` or
    ``"?"``.
    """

    value: float | None
    mark: str

    @property
    def is_verified(self) -> bool:
        return self.mark != "?" and self.value is not None

    @property
    def gt_value(self) -> float | None:
        """Value to write into the `_<LENS>_GT` tuple.

        Per ADR-048: bare and ``!`` cells become their numeric value;
        ``?`` and empty cells become ``None``.
        """
        return self.value if self.is_verified else None


def parse_cell(raw: str) -> Cell:
    """Parse one cell's text into a `Cell` value.

    Accepts the formats produced by the scaffolder (`0.43`, `0.45!`,
    `0.43?`, `—`, bare `?`, empty) plus loose whitespace.
    """
    text = raw.strip()
    if not text or text in {"—", "-", "None"}:
        return Cell(value=None, mark="")
    if text == "?":
        return Cell(value=None, mark="?")
    mark = ""
    if text.endswith("!") or text.endswith("?"):
        mark = text[-1]
        text = text[:-1].strip()
    # The extractor emits `—   ` (em-dash plus pad) for missing values;
    # treat any non-numeric body as None at this point.
    try:
        value = float(text)
    except ValueError:
        return Cell(value=None, mark=mark)
    return Cell(value=value, mark=mark)


def format_cell(cell: Cell, width: int = 5) -> str:
    """Render a cell back to markdown text.

    `width` is the column width to right-pad to (matters for stable
    diffs when the scaffolder rewrites the file). Marks count toward
    the width — `0.45!` and `0.43 ` occupy the same column width.
    """
    if cell.value is None and cell.mark == "?":
        return "?".ljust(width)
    if cell.value is None:
        return "—".ljust(width)
    body = f"{cell.value:.2f}{cell.mark}"
    return body.ljust(width)


# --- File parsing --------------------------------------------------------


# A view is one second-level heading whose body is a markdown table.
# The heading text appears as a column-group title in the scaffolder
# (e.g. `## f/1.2 (max)`, `## 15 lp/mm`). The aperture or frequency
# label is what we map back to the GT-dict key.
_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
# Table rows look like `| 0.0 | 0.88! | 0.88 | 0.41 | 0.41 |` — leading
# pipe, position cell, then one cell per field, trailing pipe.
_ROW_RE = re.compile(r"^\|(.+)\|\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ParsedView:
    """One view's parsed table — heading text, column headers, rows.

    `cells` is a list of (position_mm, dict_of_field_name_to_Cell)
    pairs, in source order.
    """

    heading: str
    column_headers: tuple[str, ...]
    cells: tuple[tuple[float, dict[str, Cell]], ...]


def _split_row(row_text: str) -> list[str]:
    """Split a `|`-delimited markdown row into cell strings (trimmed)."""
    return [c.strip() for c in row_text.strip().strip("|").split("|")]


def parse_eye_read(text: str) -> list[ParsedView]:
    """Parse an eye-read.md body into one ParsedView per view.

    Robust to extra prose between views. Skips any second-level
    heading whose body doesn't look like a sample-position table
    (headers row + separator row + at least one data row).
    """
    headings = list(_HEADING_RE.finditer(text))
    if not headings:
        return []
    bounds: list[tuple[str, int, int]] = []
    for i, m in enumerate(headings):
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        bounds.append((m.group(1).strip(), start, end))

    views: list[ParsedView] = []
    for heading, start, end in bounds:
        section = text[start:end]
        rows = [m.group(1) for m in _ROW_RE.finditer(section)]
        if len(rows) < 3:
            continue
        header_cells = _split_row(rows[0])
        # Separator row second; we don't actually need it after the
        # heading check above. Data rows are everything after.
        data_rows = rows[2:]
        if header_cells[0].lower().replace(" ", "") not in (
            "position(mm)", "position", "pos", "frac"
        ):
            continue
        column_headers = tuple(header_cells[1:])
        parsed_rows: list[tuple[float, dict[str, Cell]]] = []
        for row in data_rows:
            cells = _split_row(row)
            if len(cells) < 2:
                continue
            try:
                position = float(cells[0])
            except ValueError:
                continue
            field_cells: dict[str, Cell] = {}
            for header, cell_text in zip(column_headers, cells[1:]):
                field_cells[header] = parse_cell(cell_text)
            parsed_rows.append((position, field_cells))
        views.append(
            ParsedView(
                heading=heading,
                column_headers=column_headers,
                cells=tuple(parsed_rows),
            )
        )
    return views


# --- Heading → GT key mapping --------------------------------------------


def heading_to_gt_key(heading: str) -> str | None:
    """Map a view heading like ``f/1.2 (max)`` or ``15 lp/mm`` to the
    GT-dict key (``"max"`` or ``"f/4"``).

    The scaffolder writes both kinds of headings:

    - TTartisan dual-aperture: ``f/1.2 (max)`` → GT key ``"max"``.
    - Fuji permfreq: ``15 lp/mm`` → GT key is the lens's only
      aperture label (e.g. ``"f/4"``). The caller resolves the
      aperture from the chart entry; this helper returns ``None`` so
      the caller knows to use the chart-supplied default.
    """
    m = re.search(r"\(([^)]+)\)\s*$", heading)
    if m:
        return m.group(1).strip()
    if heading.endswith("lp/mm"):
        return None
    return heading.strip()


def column_to_field(header: str) -> str:
    """Map a column header (e.g. ``10S``, ``45M``) to a field name
    (``"freq10S"``, ``"freq45M"``). Returns the header unchanged if
    it already looks like a field name.
    """
    if header.startswith("freq"):
        return header
    return f"freq{header}"


# --- GT building ---------------------------------------------------------


def views_to_gt(
    views: list[ParsedView], default_aperture: str
) -> dict[str, dict[str, tuple[float | None, ...]]]:
    """Build a ``GroundTruthCurves``-shaped dict from parsed views.

    `default_aperture` is used when a view heading doesn't carry one
    (Fuji permfreq case — every view shares the lens's only aperture
    label).
    """
    out: dict[str, dict[str, list[float | None]]] = {}
    for view in views:
        ap = heading_to_gt_key(view.heading) or default_aperture
        bucket = out.setdefault(ap, {})
        for header in view.column_headers:
            bucket.setdefault(column_to_field(header), [])
        for position, fields in view.cells:
            del position  # source-order is the contract; positions checked elsewhere
            for header in view.column_headers:
                field = column_to_field(header)
                cell = fields.get(header)
                bucket[field].append(cell.gt_value if cell else None)
    return {ap: {f: tuple(v) for f, v in fields.items()} for ap, fields in out.items()}


# --- GT writer (referenceset/charts.py) ----------------------------------


_CHARTS_PATH = REPO_ROOT / "tools" / "mtfdigitizer" / "referenceset" / "charts.py"


def _format_value(v: float | None) -> str:
    if v is None:
        return "None"
    return f"{v:.2f}"


def _format_tuple(values: tuple[float | None, ...]) -> str:
    return "(" + ", ".join(_format_value(v) for v in values) + ")"


def replace_gt_in_charts(
    gt_var: str,
    new_gt: dict[str, dict[str, tuple[float | None, ...]]],
    *,
    charts_path: Path = _CHARTS_PATH,
) -> tuple[str, str]:
    """Rewrite the ``_<LENS>_GT`` literal in ``referenceset/charts.py``
    to the new content.

    Returns ``(old_text, new_text)`` — the caller decides whether to
    write the new text to disk. The replacement preserves the
    surrounding leading comment and downstream code; only the literal
    dict body changes. Field comments inside the existing literal are
    NOT preserved (they reference the prior data and would mislead).
    """
    src = charts_path.read_text(encoding="utf-8")
    # Find the assignment line. Then walk forward to find the matching
    # closing brace at the same indentation level.
    pat = re.compile(rf"^({re.escape(gt_var)}: GroundTruthCurves = \{{)$", re.MULTILINE)
    m = pat.search(src)
    if not m:
        raise ValueError(f"could not find `{gt_var}: GroundTruthCurves = {{` in {charts_path}")
    # Walk lines forward; balance braces ignoring strings.
    start = m.start()
    open_line_end = m.end()
    depth = 1
    i = open_line_end
    while i < len(src) and depth > 0:
        ch = src[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                # Include the closing brace
                i += 1
                break
        i += 1
    if depth != 0:
        raise ValueError(f"unbalanced braces walking `{gt_var}` literal")
    new_literal = _render_gt_literal(gt_var, new_gt)
    return src, src[:start] + new_literal + src[i:]


def _render_gt_literal(
    gt_var: str, gt: dict[str, dict[str, tuple[float | None, ...]]]
) -> str:
    """Render a `_<LENS>_GT` dict as a Python literal matching the
    existing charts.py style."""
    lines = [f"{gt_var}: GroundTruthCurves = {{"]
    for ap, fields in gt.items():
        lines.append(f'    "{ap}": {{')
        for field, values in fields.items():
            lines.append(f'        "{field}": {_format_tuple(values)},')
        lines.append("    },")
    lines.append("}")
    return "\n".join(lines)


# --- Anchor resolution ---------------------------------------------------


def gt_var_for_chart(chart) -> str:
    """Mirror the scaffolder's logic to derive ``_<LENS>_GT`` from a
    chart slug. Kept local so this module doesn't import from
    `scripts/` (which depends on PIL etc.).
    """
    style = chart.style_family
    parts = chart.slug.split("-")
    if style == "fujifilm-permfreq":
        cohort = parts[1].upper()
        focal = parts[2].replace("mm", "")
        return f"_FUJI_{cohort}_{focal}_GT"
    if style == "ttartisan-4color-dual-aperture":
        # Most slugs are `ttartisan-NNmm-...` with focal at parts[1].
        # AF lenses (`ttartisan-af-NNmm-...`) and tilt lenses
        # (`ttartisan-tilt-NNmm-...`) carry the prefix segment first,
        # so the focal is at parts[2] and the variant prefix appears
        # in the GT-var name to keep it unique across the cohort.
        if parts[1] in {"af", "tilt"}:
            variant = parts[1].upper()
            focal = parts[2].replace("mm", "")
            return f"_TTARTISAN_{variant}_{focal}_GT"
        focal = parts[1].replace("mm", "")
        return f"_TTARTISAN_{focal}_GT"
    raise ValueError(
        f"{chart.slug}: style_family {style!r} not supported by eyeread"
    )


def default_aperture_for_chart(chart) -> str:
    """The aperture key used when a view heading omits one (Fuji case)."""
    if chart.apertures:
        return chart.apertures[0]
    return "f/?"


# --- CLI -----------------------------------------------------------------


def _find_anchor(slug: str):
    from mtfdigitizer.referenceset.charts import REFERENCE_CHARTS

    for chart in REFERENCE_CHARTS:
        if chart.slug == slug:
            return chart
    raise SystemExit(f"{slug}: not in REFERENCE_CHARTS")


def _eye_read_path(chart) -> Path:
    return (REPO_ROOT / chart.chart_path).parent / "eye-read.md"


def _verified_counts(views: list[ParsedView]) -> tuple[int, int, int, int]:
    """Return (corrected, silent_verified, unknown, total) counts."""
    corrected = silent = unknown = total = 0
    for view in views:
        for _, fields in view.cells:
            for cell in fields.values():
                total += 1
                if cell.mark == "!":
                    corrected += 1
                elif cell.mark == "?":
                    unknown += 1
                elif cell.value is not None:
                    silent += 1
                else:
                    unknown += 1
    return corrected, silent, unknown, total


def transcribe(slug: str, *, apply: bool) -> int:
    """Parse the anchor's eye-read.md, build the GT dict, and either
    preview the new ``_<LENS>_GT`` literal or write it to charts.py.
    """
    chart = _find_anchor(slug)
    path = _eye_read_path(chart)
    if not path.exists():
        raise SystemExit(f"{slug}: {path} does not exist")
    views = parse_eye_read(path.read_text(encoding="utf-8"))
    if not views:
        raise SystemExit(f"{slug}: no parseable views in {path}")
    gt = views_to_gt(views, default_aperture_for_chart(chart))
    gt_var = gt_var_for_chart(chart)
    corrected, silent, unknown, total = _verified_counts(views)
    print(
        f"{slug}: {total} cells — "
        f"{corrected} corrected (!), {silent} silently verified, "
        f"{unknown} unknown (?)",
        file=sys.stderr,
    )
    _, new_src = replace_gt_in_charts(gt_var, gt)
    if not apply:
        print(_render_gt_literal(gt_var, gt))
        print(
            "\nPreview only — pass --apply to write to charts.py.",
            file=sys.stderr,
        )
        return 0
    _CHARTS_PATH.write_text(new_src, encoding="utf-8", newline="\n")
    print(f"wrote: {gt_var} in {_CHARTS_PATH.relative_to(REPO_ROOT)}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("slug", help="Tier 1 anchor slug to transcribe")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write the new _<LENS>_GT into referenceset/charts.py "
        "(default: preview to stdout)",
    )
    args = parser.parse_args(argv)
    return transcribe(args.slug, apply=args.apply)


if __name__ == "__main__":
    sys.exit(main())
