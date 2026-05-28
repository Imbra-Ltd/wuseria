"""BrandTool — the invariant brand pipeline, composed from injected parts.

BrandTool owns everything that is the same for every brand: resolving the
lens list from lenses.ts, fetching pages through a PageSource, slug and
specs-folder bookkeeping, downloading images, and (for #779) cross-
validating physical specs. The brand-specific extraction is delegated to
an injected BrandExtractor; the transport to an injected PageSource.

Because both collaborators are injected, BrandTool is tested with a
FakeFetcher and a stub extractor — no network, no real HTML.
"""

from dataclasses import dataclass
from pathlib import Path

from pagefetch import FetchOptions, PageSource

from .diff import Mismatch, diff_physical
from .extractor import BrandExtractor
from .lenses import LensEntry, LensesFile
from .slug import model_to_slug
from .specs_dir import detect_ext, has_construction_image, has_mtf_chart, image_dest


@dataclass(frozen=True)
class UrlStatus:
    """Result of validating a lens's officialUrl (#779)."""

    url: str
    ok: bool
    detail: str


class BrandTool:
    """Orchestrates spec/image extraction and verification for one brand."""

    def __init__(
        self,
        extractor: BrandExtractor,
        source: PageSource,
        lenses_path: Path,
        specs_root: Path,
    ):
        self._ex = extractor
        self._src = source
        self.lenses_path = lenses_path
        self._lenses = LensesFile(lenses_path)
        self._specs_root = specs_root

    @property
    def config(self):
        return self._ex.config

    def slug_for(self, model: str) -> str:
        return model_to_slug(self._ex.config.slug_prefix, model)

    def resolve_lenses(self) -> list[LensEntry]:
        """Every lens for this brand, with URLs normalized."""
        return self._lenses.entries_for(
            self._ex.config.name, normalize_url=self._ex.normalize_url
        )

    def _fetch_content(self, url: str, use_cache: bool = True) -> str:
        opts = FetchOptions(
            mode=self._ex.config.content_mode,
            transport=self._ex.config.transport,
            use_cache=use_cache,
        )
        return self._src.fetch(url, opts).content

    def fetch_optical(self, lens: LensEntry) -> dict:
        content = self._fetch_content(lens.url)
        return self._ex.extract_optical(content) if content else {}

    def fetch_physical(self, lens: LensEntry) -> dict[str, float]:
        content = self._fetch_content(lens.url)
        return self._ex.extract_physical(content) if content else {}

    def fetch_image_urls(self, lens: LensEntry) -> dict[str, list[str]]:
        if not self._ex.config.has_diagrams:
            return {"mtf": [], "construction": []}
        content = self._fetch_content(lens.url)
        return self._ex.extract_image_urls(content) if content else {"mtf": [], "construction": []}

    def has_mtf(self, lens: LensEntry) -> bool:
        return self.has_mtf_for_slug(self.slug_for(lens.model))

    def has_construction(self, lens: LensEntry) -> bool:
        return self.has_construction_for_slug(self.slug_for(lens.model))

    def has_mtf_for_slug(self, slug: str) -> bool:
        return has_mtf_chart(self._specs_root, slug)

    def has_construction_for_slug(self, slug: str) -> bool:
        return has_construction_image(self._specs_root, slug)

    def save_images(self, lens: LensEntry, urls: dict[str, list[str]]) -> list[Path]:
        """Download MTF/construction images to the lens's specs folder.

        Naming and destination are this tool's policy; the byte transfer is
        the PageSource's. Returns the paths actually written."""
        slug = self.slug_for(lens.model)
        written: list[Path] = []
        for kind in ("mtf", "construction"):
            found = urls.get(kind, [])
            multiple = len(found) > 1
            for i, url in enumerate(found, start=1):
                dest = image_dest(
                    self._specs_root,
                    slug,
                    kind,
                    detect_ext(url),
                    index=i if multiple else None,
                )
                if dest.exists():
                    continue
                data = self._src.download_bytes(url, min_size=500)
                if data:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(data)
                    written.append(dest)
        return written

    # --- #779 verification -------------------------------------------

    def verify(self, lens: LensEntry) -> list[Mismatch]:
        """Cross-validate stored physical specs against the official page."""
        extracted = self.fetch_physical(lens)
        return diff_physical(lens.physical, extracted)

    def validate_url(self, lens: LensEntry) -> UrlStatus:
        """Confirm the officialUrl resolves to real content, not a failure
        or a bot/redirect page. Catches the broken-URL class from Session 76."""
        result = self._src.fetch(
            lens.url, FetchOptions(mode=self._ex.config.content_mode, use_cache=False)
        )
        if not result.ok:
            return UrlStatus(lens.url, ok=False, detail="no content / fetch failed")
        return UrlStatus(lens.url, ok=True, detail=f"ok ({result.tier_used})")
