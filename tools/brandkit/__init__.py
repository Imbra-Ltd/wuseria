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

On import it points pagefetch's cache at the project cache (`.cache/fetch`)
by setting PAGEFETCH_CACHE_DIR if unset, so the bare `py -m pagefetch` CLI
shares the one cache the brand tools use rather than creating a second
`tools/.cache/pagefetch` from the package's CWD-relative default. brandkit
is the right place for this: it is the me-fuji-specific layer and may know
the project layout (pagefetch itself must not).
"""

import os as _os
from pathlib import Path as _Path

# tools/brandkit/__init__.py -> repo root is two levels up.
_ROOT = _Path(__file__).resolve().parent.parent.parent
_os.environ.setdefault("PAGEFETCH_CACHE_DIR", str(_ROOT / ".cache" / "fetch"))

from .audit import audit
from .cli import format_ts_fields, run
from .diff import Mismatch, diff_physical
from .extractor import BrandConfig, BrandExtractor
from .lenses import (
    FIELD_KIND,
    PHYSICAL_FIELDS,
    PHYSICAL_SPEC_FIELDS,
    LensEntry,
    LensesFile,
    PhysicalValue,
)
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
    "PhysicalValue",
    "PHYSICAL_FIELDS",
    "PHYSICAL_SPEC_FIELDS",
    "FIELD_KIND",
    "model_to_slug",
    "diff_physical",
    "Mismatch",
    "has_mtf_chart",
    "has_construction_image",
    "image_dest",
    "detect_ext",
]
