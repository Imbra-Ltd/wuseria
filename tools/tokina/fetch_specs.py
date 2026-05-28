"""Fetch optical specs, MTF charts, and construction diagrams for Tokina.

Thin entry point: builds the Tokina BrandTool (TokinaExtractor + a
pagefetch NetworkFetcher) and hands it to the shared brandkit CLI runner.
Brand-specific parsing lives in extractor.py; the CLI orchestration and all
scaffolding live in brandkit.

Usage (flags handled by brandkit.run):
    py tools/tokina/fetch_specs.py                # fetch all (specs + images)
    py tools/tokina/fetch_specs.py --dry-run      # list lenses without fetching
    py tools/tokina/fetch_specs.py --filter 23mm  # filter by model substring
    py tools/tokina/fetch_specs.py --limit 2      # fetch first N only
    py tools/tokina/fetch_specs.py --specs-only   # only extract specs text
    py tools/tokina/fetch_specs.py --images-only  # only download images
    py tools/tokina/fetch_specs.py --verify       # cross-validate physical specs (#779)
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import BrandTool, run  # noqa: E402
from pagefetch import FileCache, NetworkFetcher  # noqa: E402
from tokina.extractor import TokinaExtractor  # noqa: E402

ROOT = TOOLS_DIR.parent


def build_tool() -> BrandTool:
    return BrandTool(
        extractor=TokinaExtractor(),
        source=NetworkFetcher(cache=FileCache(cache_dir=ROOT / ".cache" / "fetch")),
        lenses_path=ROOT / "src" / "data" / "lenses.ts",
        specs_root=ROOT / "docs" / "optical-specs",
    )


if __name__ == "__main__":
    run(build_tool())
