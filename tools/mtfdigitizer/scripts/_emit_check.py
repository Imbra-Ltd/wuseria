"""Shared --check helper for emit_*_tier2 scripts (#1296).

Both `emit_ttartisan_tier2` and `emit_fuji_tier2` need an in-memory
"is the committed `mtf-readings.ts` up to date with the current
extractor output?" gate. Each script owns its own `_splice_entries`
(the splice patterns differ slightly), but the diff/exit logic is
identical — that's what lives here.
"""

from __future__ import annotations

import difflib
import sys
from pathlib import Path


def report_drift(
    path: Path,
    source: str,
    patched: str,
    *,
    label: str,
) -> int:
    """Compare `source` (committed file text) to `patched` (in-memory
    re-emit) and return a process exit code.

    Returns 0 on match, 1 on drift. On drift, writes a unified diff
    to stderr so the failure is actionable without an extra command.
    """
    if source == patched:
        print(
            f"OK: {label} entries in {path.name} match current "
            f"extractor output.",
            file=sys.stderr,
        )
        return 0

    diff = difflib.unified_diff(
        source.splitlines(keepends=True),
        patched.splitlines(keepends=True),
        fromfile=f"{path.name} (committed)",
        tofile=f"{path.name} (re-emitted)",
        n=3,
    )
    sys.stderr.writelines(diff)
    print(
        f"\nFAIL: {label} entries in {path.name} drift from current "
        f"extractor output. Run the same script with --write to refresh, "
        f"review the diff, then commit.",
        file=sys.stderr,
    )
    return 1
