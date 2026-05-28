"""FakeFetcher — a deterministic PageSource test double.

Returns canned content from a URL-to-content map, with no network, no
browser, and no disk. It records the URLs it was asked to fetch so tests
can assert on call behavior. It is part of the public package surface so
consumers (e.g. brand tools) can test their pipelines against it.
"""

from pathlib import Path

from .source import FetchOptions, FetchResult, PageSource


class FakeFetcher(PageSource):
    """A PageSource backed by in-memory maps instead of the network."""

    def __init__(
        self,
        responses: dict[str, str] | None = None,
        binary: dict[str, bytes] | None = None,
    ) -> None:
        self._responses = responses or {}
        self._binary = binary or {}
        self.calls: list[str] = []
        self.binary_calls: list[str] = []

    def fetch(self, url: str, options: FetchOptions | None = None) -> FetchResult:
        self.calls.append(url)
        content = self._responses.get(url, "")
        return FetchResult(
            url=url, content=content, tier_used="fake", ok=bool(content)
        )

    def fetch_batch(
        self, urls: list[str], options: FetchOptions | None = None
    ) -> list[FetchResult]:
        return [self.fetch(url, options) for url in urls]

    def download_bytes(self, url: str, min_size: int = 0) -> bytes | None:
        self.binary_calls.append(url)
        data = self._binary.get(url)
        if data is None or len(data) < min_size:
            return None
        return data

    def screenshot(
        self, url: str, dest: Path, options: FetchOptions | None = None
    ) -> bool:
        return url in self._responses
