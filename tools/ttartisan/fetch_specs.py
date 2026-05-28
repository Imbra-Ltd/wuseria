"""Fetch optical specs, MTF charts, and construction diagrams for TTartisan.

Thin entry point: builds the TTartisan BrandTool (TTArtisanExtractor + a
pagefetch NetworkFetcher) and hands it to the shared brandkit CLI runner.

Note: AF 75mm f/2.0 uses the ttartisan.store Shopify URL, which carries no
spec data; the extractor simply returns nothing for it (no special-case).

Usage (flags handled by brandkit.run):
    py tools/ttartisan/fetch_specs.py                # fetch all (specs + images)
    py tools/ttartisan/fetch_specs.py --dry-run      # list lenses without fetching
    py tools/ttartisan/fetch_specs.py --filter 35mm  # filter by model substring
    py tools/ttartisan/fetch_specs.py --verify       # cross-validate physical specs (#779)
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import BrandTool, run  # noqa: E402
from pagefetch import FileCache, NetworkFetcher  # noqa: E402
from ttartisan.extractor import TTArtisanExtractor  # noqa: E402

ROOT = TOOLS_DIR.parent


def build_tool() -> BrandTool:
    return BrandTool(
        extractor=TTArtisanExtractor(),
        source=NetworkFetcher(cache=FileCache(cache_dir=ROOT / ".cache" / "fetch")),
        lenses_path=ROOT / "src" / "data" / "lenses.ts",
        specs_root=ROOT / "docs" / "optical-specs",
    )


if __name__ == "__main__":
    run(build_tool())
