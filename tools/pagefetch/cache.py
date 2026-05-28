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
from pathlib import Path

from .source import ContentMode


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
