"""Fetch optical specs and images for Venus Laowa.

Thin entry point: builds the Venus BrandTool (VenusExtractor + a pagefetch
NetworkFetcher) and hands it to the shared brandkit CLI runner. venuslens.net
sits behind Cloudflare Turnstile, so the extractor's config selects UC-mode
transport (headed-browser, not CI-friendly).

Note: under Cloudflare, direct image downloads may 403; the generic
download path does not run the old SeleniumBase canvas fallback, so image
saving for Venus stays a manual step (spec extraction is unaffected).

Usage (flags handled by brandkit.run):
    py tools/venus/fetch_specs.py                 # fetch all (specs + images)
    py tools/venus/fetch_specs.py --dry-run       # list lenses without fetching
    py tools/venus/fetch_specs.py --filter 33mm   # filter by model substring
    py tools/venus/fetch_specs.py --verify        # cross-validate physical specs (#779)
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import BrandTool, run  # noqa: E402
from pagefetch import FileCache, NetworkFetcher  # noqa: E402
from venus.extractor import VenusExtractor  # noqa: E402

ROOT = TOOLS_DIR.parent


def build_tool() -> BrandTool:
    return BrandTool(
        extractor=VenusExtractor(),
        source=NetworkFetcher(cache=FileCache(cache_dir=ROOT / ".cache" / "fetch")),
        lenses_path=ROOT / "src" / "data" / "lenses.ts",
        specs_root=ROOT / "docs" / "optical-specs",
    )


if __name__ == "__main__":
    run(build_tool())
