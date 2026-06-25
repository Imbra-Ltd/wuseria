"""Tests for the `--check` mode of `emit_*_tier2` scripts (#1296).

Both `emit_ttartisan_tier2` and `emit_fuji_tier2` expose a `--check`
flag that renders entries in memory, diffs against the committed
`src/data/mtf-readings.ts`, and exits non-zero on drift. This is the
gate that catches the next "extractor evolved past the last bulk
re-emit" case at PR time instead of months later.

The unit tests below exercise the shared diff helper and the script
wiring with a fabricated source string — they do not depend on the
production data file's current state. A separate marker test
documents the known production-data drift (both brands stale as of
S184) so the gate's behavior is recorded even while the catch-up
PRs are in flight.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mtfdigitizer.scripts._emit_check import report_drift


def test_report_drift_returns_0_on_match(capsys: pytest.CaptureFixture[str]) -> None:
    """Identical source/patched → exit 0, OK line on stderr."""
    text = "const x = 1;\n"
    rc = report_drift(Path("dummy.ts"), text, text, label="dummy")
    assert rc == 0
    err = capsys.readouterr().err
    assert "OK:" in err
    assert "dummy" in err


def test_report_drift_returns_1_on_drift(capsys: pytest.CaptureFixture[str]) -> None:
    """Different source/patched → exit 1, FAIL line + diff on stderr."""
    source = "const x = 1;\n"
    patched = "const x = 2;\n"
    rc = report_drift(Path("dummy.ts"), source, patched, label="dummy")
    assert rc == 1
    err = capsys.readouterr().err
    assert "FAIL:" in err
    # Unified diff markers present
    assert "-const x = 1;" in err
    assert "+const x = 2;" in err


def test_report_drift_diff_names_the_file(capsys: pytest.CaptureFixture[str]) -> None:
    """The diff header references the file by basename so the reader
    knows which file to refresh."""
    rc = report_drift(
        Path("src/data/mtf-readings.ts"),
        "a\n",
        "b\n",
        label="dummy",
    )
    assert rc == 1
    err = capsys.readouterr().err
    assert "mtf-readings.ts (committed)" in err
    assert "mtf-readings.ts (re-emitted)" in err


def test_report_drift_fail_message_points_to_write(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """FAIL message tells the reader exactly which command refreshes
    the file — the gate is only useful if the next step is obvious."""
    rc = report_drift(Path("x.ts"), "a\n", "b\n", label="dummy")
    assert rc == 1
    err = capsys.readouterr().err
    assert "--write" in err


# --- script wiring --------------------------------------------------------
#
# These tests exercise the emit_* main() paths with --check enabled.
# They run the real extractor pipeline against the real production
# data file — so they are EXPECTED to fail until the bulk-refresh
# catch-up PRs land (#1296 path 1).
#
# Once the catch-up lands, flip these from `xfail(strict=True)` to a
# plain assertion. The strict marker means a passing run is itself a
# test failure — that is the signal to remove the marker.


def test_ttartisan_check_passes_on_production_data() -> None:
    """Production gate: TTartisan tier 2 entries match the extractor.

    Flipped from xfail-strict to hard assertion in S187: the af-35
    eye-read override (the only remaining cell of drift after S184's
    bulk refresh) is now preserved across `--write` by the override-
    respecting splice (#1301 fix-path-2). If this regresses, either
    the splice's override detector broke or a new cell drifted that
    has no override — investigate before flipping back.
    """
    from mtfdigitizer.scripts.emit_ttartisan_tier2 import main

    assert main(["--check"]) == 0


def test_fuji_check_passes_on_production_data() -> None:
    """Production gate: Fujifilm tier 2 entries match the extractor.

    Flipped from xfail-strict to hard assertion after the S185 Fuji
    bulk refresh (#1303). If this regresses, the next bulk refresh
    needs to happen — the strict marker has done its job.
    """
    from mtfdigitizer.scripts.emit_fuji_tier2 import main

    assert main(["--check"]) == 0
