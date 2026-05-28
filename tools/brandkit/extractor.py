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
    # Extra page paths appended to the lens URL and concatenated with the main
    # page before extraction — e.g. Tamron keeps element/group counts and
    # diagrams on a "spec.html" sub-page. A tuple (not list) keeps the frozen
    # dataclass hashable. Empty means single-page.
    extra_paths: tuple[str, ...] = ()
    # When True and the HTML image path finds nothing, BrandTool opens a live
    # Playwright page and calls extract_images_live — for brands whose image
    # URLs can only be resolved by on-page geometry (Fujifilm's newer pages
    # with generic CDN filenames). The browser stays in brandkit; pagefetch
    # is never handed a live page.
    needs_live_page: bool = False


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

    def extract_image_urls(self, content: str, url: str) -> dict[str, list[str]]:
        """Return MTF and construction-diagram URLs, normalized to
        {"mtf": [...], "construction": [...]}. Brands without published
        diagrams inherit the empty default.

        url is the lens's (normalized) page URL — some brands (Sigma,
        Tamron) derive a product code from it to build image-URL patterns;
        brands that match on page content alone ignore it."""
        return {"mtf": [], "construction": []}

    def extract_images_live(self, page, url: str) -> dict[str, list[str]]:
        """Resolve image URLs from a live browser page when static HTML can't.

        Called by BrandTool only when config.needs_live_page is set and the
        static extract_image_urls returned nothing. `page` is a live
        Playwright Page (brandkit owns it; pagefetch is not involved). The
        default is a no-op — only Fujifilm, whose newer pages use generic CDN
        filenames resolvable only by on-page geometry, overrides it."""
        return {"mtf": [], "construction": []}

    def normalize_url(self, url: str) -> str:
        """Massage an officialUrl before fetching (e.g. Tokina swaps
        hyphens for underscores). Identity by default."""
        return url
