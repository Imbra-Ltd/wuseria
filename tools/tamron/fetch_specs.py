"""Fetch optical specs, MTF charts, and construction diagrams for Tamron.

Thin entry point: builds the Tamron BrandTool (TamronExtractor + a pagefetch
NetworkFetcher) and hands it to the shared brandkit CLI runner. Tamron's
data spans the main page + a spec.html sub-page; the extractor declares that
via config.extra_paths and brandkit concatenates them.

Usage (flags handled by brandkit.run):
    py tools/tamron/fetch_specs.py                 # fetch all (specs + images)
    py tools/tamron/fetch_specs.py --dry-run       # list lenses without fetching
    py tools/tamron/fetch_specs.py --filter 17-70  # filter by model substring
    py tools/tamron/fetch_specs.py --verify        # cross-validate physical specs (#779)
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import BrandTool, run  # noqa: E402
from pagefetch import FileCache, NetworkFetcher  # noqa: E402
from tamron.extractor import TamronExtractor  # noqa: E402

ROOT = TOOLS_DIR.parent


def build_tool() -> BrandTool:
    return BrandTool(
        extractor=TamronExtractor(),
        source=NetworkFetcher(cache=FileCache(cache_dir=ROOT / ".cache" / "fetch")),
        lenses_path=ROOT / "src" / "data" / "lenses.ts",
        specs_root=ROOT / "docs" / "optical-specs",
    )


if __name__ == "__main__":
    run(build_tool())
