"""Fetch optical specs, MTF charts, and construction diagrams for Fujifilm.

Thin entry point: builds the Fujifilm BrandTool (FujifilmExtractor + a
pagefetch NetworkFetcher) and hands it to the shared brandkit CLI runner.
Fujifilm pages are JS-rendered, so the extractor's config selects Playwright
transport; specs live on a /specifications/ sub-page (normalize_url). When
the named-CDN image patterns find nothing (newer pages), brandkit opens a
live Playwright page and the extractor resolves image URLs by on-page
geometry (config.needs_live_page).

Note: coatings are now part of extract_optical (every lens gets Super EBC,
plus optional Nano-GI / HT-EBC), so the old --coatings-only flag is gone.

Usage (flags handled by brandkit.run):
    py tools/fujifilm/fetch_specs.py                # fetch all (specs + images)
    py tools/fujifilm/fetch_specs.py --dry-run      # list lenses without fetching
    py tools/fujifilm/fetch_specs.py --filter gf    # filter by model substring
    py tools/fujifilm/fetch_specs.py --verify       # cross-validate physical specs (#779)
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import BrandTool, run  # noqa: E402
from pagefetch import FileCache, NetworkFetcher  # noqa: E402
from fujifilm.extractor import FujifilmExtractor  # noqa: E402

ROOT = TOOLS_DIR.parent


def build_tool() -> BrandTool:
    return BrandTool(
        extractor=FujifilmExtractor(),
        source=NetworkFetcher(cache=FileCache(cache_dir=ROOT / ".cache" / "fetch")),
        lenses_path=ROOT / "src" / "data" / "lenses.ts",
        specs_root=ROOT / "docs" / "optical-specs",
    )


if __name__ == "__main__":
    run(build_tool())
