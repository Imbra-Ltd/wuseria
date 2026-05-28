"""BrandExtractor — the per-brand strategy injected into BrandTool.

Each brand's product pages differ in markup, in what specs they expose,
and in how images are named. A BrandExtractor encapsulates exactly those
brand-specific differences behind a normalized contract, so the BrandTool
orchestrator never branches on brand.

The contract is deliberately narrow: every method takes the fetched
content as a string and returns a normalized dict. Brands whose pages are
JSON (e.g. Viltrox) parse the string themselves; brands with no diagrams
(e.g. Mitakon, Viltrox, Zeiss) inherit the empty defaults.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from pagefetch import ContentMode, Transport


@dataclass(frozen=True)
class BrandConfig:
    """Static facts about a brand that the orchestrator needs."""

    name: str  # exact brand string in lenses.ts, e.g. "Tokina"
    slug_prefix: str  # folder-slug prefix, e.g. "tokina"
    content_mode: ContentMode = ContentMode.HTML
    transport: Transport = Transport.AUTO
    has_diagrams: bool = True


class BrandExtractor(ABC):
    """Strategy for pulling specs and image URLs out of a brand's pages."""

    config: BrandConfig

    @abstractmethod
    def extract_optical(self, content: str) -> dict:
        """Parse optical construction from page content.

        Returns a dict that may contain: elements (int), groups (int),
        special (list[str]), coating (list[str]). Brands without a given
        field simply omit it (or return an empty list)."""

    def extract_physical(self, content: str) -> dict[str, float]:
        """Parse physical specs for cross-validation (#779).

        Returns a subset of weight, maxMagnification, minFocusDistance,
        filterThread, apertureBlades, diameter, length. The base default
        returns nothing, so a brand can migrate before implementing this."""
        return {}

    def extract_image_urls(self, content: str) -> dict[str, list[str]]:
        """Return MTF and construction-diagram URLs, normalized to
        {"mtf": [...], "construction": [...]}. Brands without published
        diagrams inherit the empty default."""
        return {"mtf": [], "construction": []}

    def normalize_url(self, url: str) -> str:
        """Massage an officialUrl before fetching (e.g. Tokina swaps
        hyphens for underscores). Identity by default."""
        return url
