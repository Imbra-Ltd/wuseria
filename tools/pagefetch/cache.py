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
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .source import ContentMode

# A consuming project can point every entry point (CLI included) at one
# cache directory by setting this env var, without the package hardcoding
# any project layout. Explicit cache_dir= still wins over it.
CACHE_DIR_ENV = "PAGEFETCH_CACHE_DIR"


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
        # Precedence: explicit arg > PAGEFETCH_CACHE_DIR env > CWD-relative
        # default. The default stays portable (not tied to any project
        # layout); a consumer uses the env var to unify all entry points.
        if cache_dir is not None:
            self.cache_dir = Path(cache_dir)
            source = "cache_dir argument"
        elif os.environ.get(CACHE_DIR_ENV):
            self.cache_dir = Path(os.environ[CACHE_DIR_ENV])
            source = f"${CACHE_DIR_ENV}"
        else:
            self.cache_dir = Path.cwd() / ".cache" / "pagefetch"
            source = "default"
        # Validate at construction, not at first write — a bad value (a path
        # that is a file, or whose parent is missing/read-only) fails here
        # with a clear message instead of cryptically on the first cache op.
        self._validate_cache_dir(source)

    def _validate_cache_dir(self, source: str) -> None:
        """Fail fast if the resolved cache dir cannot be created/written.

        Does not create the directory — that stays lazy (write()). It only
        confirms the path is usable: not an existing non-directory, and the
        nearest existing ancestor is a writable directory.
        """
        path = self.cache_dir
        if path.exists() and not path.is_dir():
            raise ValueError(
                f"pagefetch cache dir (from {source}) is not a directory: {path}"
            )
        # Walk up to the nearest existing ancestor and check it is writable.
        ancestor = path
        while not ancestor.exists():
            parent = ancestor.parent
            if parent == ancestor:  # reached filesystem root
                break
            ancestor = parent
        if not ancestor.is_dir():
            raise ValueError(
                f"pagefetch cache dir (from {source}) has a non-directory "
                f"ancestor: {ancestor} (for {path})"
            )
        if not os.access(ancestor, os.W_OK):
            raise ValueError(
                f"pagefetch cache dir (from {source}) is not writable: "
                f"{path} (nearest existing ancestor {ancestor} is read-only)"
            )

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
