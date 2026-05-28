"""brandkit — shared library for me-fuji brand optical-spec tools.

Holds the invariant brand pipeline so the ~250 lines of scaffolding that
were duplicated across 11 brand tools (slug generation, lenses.ts parsing,
specs-folder checks, image download, spec cross-validation) live once.

A brand tool supplies a BrandExtractor (the brand-specific parsing) and
composes it with a PageSource from the pagefetch package:

    from pagefetch import NetworkFetcher, FileCache
    from brandkit import BrandTool
    from tokina.extractor import TokinaExtractor

    tool = BrandTool(
        extractor=TokinaExtractor(),
        source=NetworkFetcher(cache=FileCache(ROOT / ".cache" / "fetch")),
        lenses_path=ROOT / "src" / "data" / "lenses.ts",
        specs_root=ROOT / "docs" / "optical-specs",
    )

Unlike pagefetch, brandkit is me-fuji-specific — it reads lenses.ts.
"""

from .audit import audit
from .cli import format_ts_fields, run
from .diff import Mismatch, diff_physical
from .extractor import BrandConfig, BrandExtractor
from .lenses import PHYSICAL_FIELDS, LensEntry, LensesFile
from .slug import model_to_slug
from .specs_dir import (
    detect_ext,
    has_construction_image,
    has_mtf_chart,
    image_dest,
)
from .tool import BrandTool, UrlStatus

__all__ = [
    "run",
    "audit",
    "format_ts_fields",
    "BrandTool",
    "UrlStatus",
    "BrandExtractor",
    "BrandConfig",
    "LensesFile",
    "LensEntry",
    "PHYSICAL_FIELDS",
    "model_to_slug",
    "diff_physical",
    "Mismatch",
    "has_mtf_chart",
    "has_construction_image",
    "image_dest",
    "detect_ext",
]
