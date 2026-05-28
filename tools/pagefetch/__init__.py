"""pagefetch — a self-contained, auto-escalating web page fetcher.

Public API:

    from pagefetch import NetworkFetcher, FetchOptions, ContentMode

    fetcher = NetworkFetcher()
    result = fetcher.fetch("https://example.com",
                           FetchOptions(mode=ContentMode.HTML))
    if result.ok:
        print(result.content)

The fetcher escalates urllib -> Playwright -> Nodriver -> SeleniumBase UC
as needed. See README.md for the full strategy and CLI usage.

This package has no dependency on any consuming project — it is built to
be extracted into a standalone repository / git submodule.
"""

from .cache import FileCache
from .detection import BOT_DETECTION_PATTERNS, html_to_text, is_bot_blocked
from .fake import FakeFetcher
from .network import DEFAULT_USER_AGENT, NetworkFetcher
from .source import (
    ContentMode,
    FetchOptions,
    FetchResult,
    PageSource,
    Transport,
)

__all__ = [
    "PageSource",
    "NetworkFetcher",
    "FakeFetcher",
    "FileCache",
    "FetchOptions",
    "FetchResult",
    "ContentMode",
    "Transport",
    "is_bot_blocked",
    "html_to_text",
    "BOT_DETECTION_PATTERNS",
    "DEFAULT_USER_AGENT",
]
