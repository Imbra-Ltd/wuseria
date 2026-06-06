"""One-shot migration: rewrite src/data/mtf-readings.ts from the legacy
`{contrast10S, contrast10M, resolution30S, resolution30M}` fields to the
generalized `samples: {10: {S, M}, 30: {S, M}}` shape declared by ADR-042.

The data file follows a uniform pattern:

    {
        position: 0,
        contrast10S: 0.98,
        contrast10M: 0.98,
        resolution30S: 0.89,
        resolution30M: 0.89,
    },

becomes:

    {
        position: 0,
        samples: {
            10: { S: 0.98, M: 0.98 },
            30: { S: 0.89, M: 0.89 },
        },
    },

Approach: stateful line scanner that detects the start of a reading row
(the `position:` line) and emits a transformed block when the four
expected fields follow in order. Refuses (raises) on any unexpected
shape so partial migrations fail loud.

Run from repo root: `py scripts/migrate-mtf-readings-to-samples.py`
Idempotent guard: refuses to run if the file already contains `samples:`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET = REPO_ROOT / "src" / "data" / "mtf-readings.ts"

POSITION_RE = re.compile(r"^(?P<indent>\s*)position:\s*(?P<value>[^,]+),\s*$")
FIELD_RE = re.compile(
    r"^(?P<indent>\s*)(?P<name>contrast10S|contrast10M|resolution30S|resolution30M):\s*(?P<value>[^,]+),\s*$"
)
EXPECTED_ORDER: tuple[str, ...] = (
    "contrast10S",
    "contrast10M",
    "resolution30S",
    "resolution30M",
)


def migrate(text: str) -> str:
    if "samples:" in text:
        raise SystemExit(
            "ERROR: input already contains `samples:` — file appears already migrated"
        )

    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    n = len(lines)
    rows_migrated = 0

    while i < n:
        line = lines[i]
        m = POSITION_RE.match(line)
        if not m:
            out.append(line)
            i += 1
            continue

        # We're at a `position:` line. The next four lines MUST be the
        # canonical contrast10S, contrast10M, resolution30S, resolution30M
        # in that order. Any deviation is a data quirk — refuse rather
        # than guess.
        if i + 4 >= n:
            raise SystemExit(
                f"ERROR: line {i + 1}: position row followed by fewer than 4 lines"
            )

        field_indent = ""
        values: dict[str, str] = {}
        for k, expected in enumerate(EXPECTED_ORDER, start=1):
            fm = FIELD_RE.match(lines[i + k])
            if not fm:
                raise SystemExit(
                    f"ERROR: line {i + 1 + k}: expected field {expected!r}, got: "
                    f"{lines[i + k].rstrip()!r}"
                )
            if fm.group("name") != expected:
                raise SystemExit(
                    f"ERROR: line {i + 1 + k}: expected field {expected!r}, "
                    f"got {fm.group('name')!r}"
                )
            values[expected] = fm.group("value")
            field_indent = fm.group("indent")

        pos_indent = m.group("indent")
        pos_value = m.group("value")
        inner_indent = field_indent + "  "

        out.append(f"{pos_indent}position: {pos_value},\n")
        out.append(f"{field_indent}samples: {{\n")
        out.append(
            f"{inner_indent}10: {{ S: {values['contrast10S']}, "
            f"M: {values['contrast10M']} }},\n"
        )
        out.append(
            f"{inner_indent}30: {{ S: {values['resolution30S']}, "
            f"M: {values['resolution30M']} }},\n"
        )
        out.append(f"{field_indent}}},\n")

        rows_migrated += 1
        i += 5  # consumed: position line + 4 field lines

    print(f"Migrated {rows_migrated} reading rows.", file=sys.stderr)
    return "".join(out)


def main() -> int:
    if not TARGET.exists():
        print(f"ERROR: {TARGET} not found", file=sys.stderr)
        return 1
    src = TARGET.read_text(encoding="utf-8")
    out = migrate(src)
    TARGET.write_text(out, encoding="utf-8")
    print(f"Wrote {TARGET}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
