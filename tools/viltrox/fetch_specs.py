"""Fetch optical specs for Viltrox (Shopify JSON storefront).

Thin entry point: builds the Viltrox BrandTool (ViltroxExtractor + a
pagefetch NetworkFetcher) and hands it to the shared brandkit CLI runner.
Specs come from the product JSON API (the extractor's normalize_url appends
.json); Viltrox publishes no MTF/construction diagrams, so --images-only is
a no-op. For gallery-image scraping see download_images.py.

Usage (flags handled by brandkit.run):
    py tools/viltrox/fetch_specs.py                # fetch all specs
    py tools/viltrox/fetch_specs.py --dry-run      # list lenses without fetching
    py tools/viltrox/fetch_specs.py --filter 13mm  # filter by model substring
    py tools/viltrox/fetch_specs.py --verify       # cross-validate physical specs (#779)
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import BrandTool, run  # noqa: E402
from pagefetch import FileCache, NetworkFetcher  # noqa: E402
from viltrox.extractor import ViltroxExtractor  # noqa: E402

ROOT = TOOLS_DIR.parent


def build_tool() -> BrandTool:
    return BrandTool(
        extractor=ViltroxExtractor(),
        source=NetworkFetcher(cache=FileCache(cache_dir=ROOT / ".cache" / "fetch")),
        lenses_path=ROOT / "src" / "data" / "lenses.ts",
        specs_root=ROOT / "docs" / "optical-specs",
    )


if __name__ == "__main__":
    run(build_tool())
