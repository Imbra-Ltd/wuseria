"""Fetch optical specs and construction diagrams for Voigtlander.

Thin entry point: builds the Voigtlander BrandTool (VoigtlanderExtractor +
a pagefetch NetworkFetcher) and hands it to the shared brandkit CLI runner.
Voigtlander pages render via a Divi/JS theme, so the extractor's config
selects Playwright transport (headed-browser, not CI-friendly).

Usage (flags handled by brandkit.run):
    py tools/voigtlander/fetch_specs.py                # fetch all (specs + images)
    py tools/voigtlander/fetch_specs.py --dry-run      # list lenses without fetching
    py tools/voigtlander/fetch_specs.py --filter 35mm  # filter by model substring
    py tools/voigtlander/fetch_specs.py --verify       # cross-validate physical specs (#779)
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import BrandTool, run  # noqa: E402
from pagefetch import FileCache, NetworkFetcher  # noqa: E402
from voigtlander.extractor import VoigtlanderExtractor  # noqa: E402

ROOT = TOOLS_DIR.parent


def build_tool() -> BrandTool:
    return BrandTool(
        extractor=VoigtlanderExtractor(),
        source=NetworkFetcher(cache=FileCache(cache_dir=ROOT / ".cache" / "fetch")),
        lenses_path=ROOT / "src" / "data" / "lenses.ts",
        specs_root=ROOT / "docs" / "optical-specs",
    )


if __name__ == "__main__":
    run(build_tool())
