"""Filesystem cache for fetched pages.

Caches responses on disk keyed by a hash of the URL, so repeated fetches
of the same page during a session are free. The cache directory is a
constructor parameter (not a module global) so the package stays portable:
a consuming project points it wherever it likes; the default is relative
to the current working directory.

The key scheme (sha256(url) truncated to 16 hex chars, plus a .txt/.html
suffix) is fixed — changing it would silently invalidate every existing
cached file.
"""

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .source import ContentMode


@dataclass
class CleanReport:
    """Outcome of a cache sweep. `removed` pairs each purged file with the
    reason it was junk; `dry_run` means nothing was actually deleted."""

    removed: list[tuple[Path, str]] = field(default_factory=list)
    kept: int = 0
    dry_run: bool = False


class FileCache:
    """A directory of cached page responses and screenshots."""

    def __init__(self, cache_dir: Path | None = None):
        # Default is portable (CWD-relative), not tied to any project layout.
        self.cache_dir = cache_dir or (Path.cwd() / ".cache" / "pagefetch")

    @staticmethod
    def url_hash(url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def key(self, url: str, mode: ContentMode) -> Path:
        suffix = ".html" if mode is ContentMode.HTML else ".txt"
        return self.cache_dir / (self.url_hash(url) + suffix)

    def screenshot_path(self, url: str) -> Path:
        return self.cache_dir / (self.url_hash(url) + ".png")

    def read(self, url: str, mode: ContentMode) -> str | None:
        path = self.key(url, mode)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def write(self, url: str, mode: ContentMode, content: str) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.key(url, mode).write_text(content, encoding="utf-8")

    def delete(self, url: str, mode: ContentMode) -> bool:
        """Remove one cached entry. Returns True if a file was removed.
        Idempotent — a missing entry is not an error."""
        path = self.key(url, mode)
        if path.exists():
            path.unlink()
            return True
        return False

    def entries(self) -> list[Path]:
        """All cached page bodies (.txt / .html). Screenshots (.png) are not
        page content and are excluded."""
        if not self.cache_dir.exists():
            return []
        return sorted(
            p
            for p in self.cache_dir.iterdir()
            if p.is_file() and p.suffix in (".txt", ".html")
        )

    def clean(
        self, classify: Callable[[str], str | None], dry_run: bool = False
    ) -> CleanReport:
        """Sweep the cache, removing entries whose body is junk.

        `classify(body)` returns a short reason string when the body is junk
        (e.g. "404/error", "bot-blocked") or None to keep it. Real content is
        kept. With `dry_run=True` nothing is deleted — the report lists what
        would be removed.
        """
        report = CleanReport(dry_run=dry_run)
        for path in self.entries():
            try:
                body = path.read_text(encoding="utf-8")
            except OSError:
                continue
            reason = classify(body)
            if reason is None:
                report.kept += 1
                continue
            report.removed.append((path, reason))
            if not dry_run:
                path.unlink()
        return report
