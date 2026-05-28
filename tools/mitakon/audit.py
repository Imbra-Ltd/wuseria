"""Audit Mitakon lens data completeness.

Thin entry point: builds the Mitakon BrandTool and hands it to the shared
brandkit audit runner.

Usage:
    py tools/mitakon/audit.py                 # full audit
    py tools/mitakon/audit.py --filter 35mm   # filter by model substring
    py tools/mitakon/audit.py --missing       # show only lenses with missing data
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import audit  # noqa: E402

from mitakon.fetch_specs import build_tool  # noqa: E402


if __name__ == "__main__":
    audit(build_tool())
