"""Orphaned-Chrome cleanup.

Headed browser tiers (Nodriver, SeleniumBase UC) spawn Chrome processes
that can outlive the fetch if something goes wrong. ChromeReaper tracks
the PIDs spawned during its lifetime and kills any survivors at exit.

This is the one Windows-specific, side-effectful part of the package; it
is isolated here so the rest stays portable. On non-Windows platforms the
tasklist call simply yields no PIDs and cleanup is a no-op.
"""

import atexit
import os
import signal
import sys


class ChromeReaper:
    """Tracks Chrome PIDs spawned by this process and reaps survivors."""

    def __init__(self) -> None:
        self._spawned_pids: set[int] = set()
        atexit.register(self.cleanup)

    @staticmethod
    def running_chrome_pids() -> set[int]:
        """All chrome.exe PIDs currently running (Windows only; empty set
        elsewhere or on error)."""
        pids: set[int] = set()
        try:
            import subprocess

            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq chrome.exe", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            for line in result.stdout.strip().splitlines():
                parts = line.strip('"').split('","')
                if len(parts) >= 2:
                    try:
                        pids.add(int(parts[1]))
                    except ValueError:
                        pass
        except Exception:
            pass
        return pids

    def track_new_since(self, pids_before: set[int]) -> None:
        """Record Chrome PIDs that appeared since pids_before was sampled."""
        self._spawned_pids.update(self.running_chrome_pids() - pids_before)

    def cleanup(self) -> None:
        """Kill tracked Chrome processes that are still running."""
        if not self._spawned_pids:
            return
        still_running = self.running_chrome_pids() & self._spawned_pids
        for pid in still_running:
            try:
                os.kill(pid, signal.SIGTERM)
            except (OSError, ProcessLookupError):
                pass
        if still_running:
            print(
                f"[cleanup] Killed {len(still_running)} orphaned Chrome process(es)",
                file=sys.stderr,
            )
