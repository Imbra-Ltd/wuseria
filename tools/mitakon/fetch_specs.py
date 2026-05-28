"""Fetch optical specs for Mitakon (Zhongyi Optics).

Thin entry point: builds the Mitakon BrandTool (MitakonExtractor + a
pagefetch NetworkFetcher) and hands it to the shared brandkit CLI runner.
zyoptics.net blocks urllib + Playwright, so the extractor's config selects
UC-mode transport (headed-browser, not CI-friendly). Mitakon publishes no
MTF/construction diagrams (has_diagrams False), so --images-only is a no-op.

Usage (flags handled by brandkit.run):
    py tools/mitakon/fetch_specs.py                # fetch all specs
    py tools/mitakon/fetch_specs.py --dry-run      # list lenses without fetching
    py tools/mitakon/fetch_specs.py --filter 35mm  # filter by model substring
    py tools/mitakon/fetch_specs.py --verify       # cross-validate physical specs (#779)
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import BrandTool, run  # noqa: E402
from pagefetch import FileCache, NetworkFetcher  # noqa: E402
from mitakon.extractor import MitakonExtractor  # noqa: E402

ROOT = TOOLS_DIR.parent


def build_tool() -> BrandTool:
    return BrandTool(
        extractor=MitakonExtractor(),
        source=NetworkFetcher(cache=FileCache(cache_dir=ROOT / ".cache" / "fetch")),
        lenses_path=ROOT / "src" / "data" / "lenses.ts",
        specs_root=ROOT / "docs" / "optical-specs",
    )


if __name__ == "__main__":
    run(build_tool())
