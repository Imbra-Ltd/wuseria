"""Transport abstraction for page fetching.

Defines the PageSource interface that concrete fetchers (NetworkFetcher)
and test doubles (FakeFetcher) implement, plus the typed options and
result shapes that flow through it. This module has no third-party or
project dependencies — it is the stable contract the rest of the package
and any consumer depend on.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ContentMode(Enum):
    """What form fetched content takes."""

    TEXT = "text"  # tags stripped, whitespace collapsed
    HTML = "html"  # raw HTML


class Transport(Enum):
    """Which transport tier to use. AUTO escalates on failure."""

    AUTO = "auto"  # urllib, escalating to playwright/nodriver/uc as needed
    PLAYWRIGHT = "playwright"  # force headless Chromium
    NODRIVER = "nodriver"  # force headed Chrome via CDP
    UC = "uc"  # force SeleniumBase UC mode


@dataclass(frozen=True)
class FetchOptions:
    """Options for a single fetch. Immutable so it can be shared safely."""

    mode: ContentMode = ContentMode.TEXT
    transport: Transport = Transport.AUTO
    wait_ms: int = 500
    use_cache: bool = True


@dataclass(frozen=True)
class FetchResult:
    """Outcome of a fetch. content is "" when every tier failed."""

    url: str
    content: str
    tier_used: str  # "urllib" | "playwright" | "nodriver" | "uc" | "cache" | "fake" | "none"
    ok: bool


class PageSource(ABC):
    """A source of page content.

    Concrete implementations fetch over the network by any means; test
    doubles return canned content. Implementations MUST NOT couple to any
    consuming project's layout — transport only.
    """

    @abstractmethod
    def fetch(self, url: str, options: FetchOptions | None = None) -> FetchResult:
        """Fetch one URL. Never raises for fetch failure — returns a
        FetchResult with ok=False and content="" instead."""

    @abstractmethod
    def fetch_batch(
        self, urls: list[str], options: FetchOptions | None = None
    ) -> list[FetchResult]:
        """Fetch many URLs, reusing one browser session where applicable.
        Order of results matches the input order."""

    @abstractmethod
    def download_bytes(self, url: str, min_size: int = 0) -> bytes | None:
        """Download raw bytes (images, PDFs). Returns None on failure or
        when the payload is smaller than min_size. The caller owns the
        destination path and naming — this is transport only."""

    @abstractmethod
    def screenshot(
        self, url: str, dest: Path, options: FetchOptions | None = None
    ) -> bool:
        """Capture a full-page screenshot to dest. Returns True on success."""
