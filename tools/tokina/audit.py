"""Audit Tokina lens data completeness.

Thin entry point: builds the Tokina BrandTool and hands it to the shared
brandkit audit runner, which checks lenses.ts field presence plus MTF /
construction image presence.

Usage:
    py tools/tokina/audit.py                  # full audit
    py tools/tokina/audit.py --filter 23mm    # filter by model substring
    py tools/tokina/audit.py --missing        # show only lenses with missing data
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import audit  # noqa: E402

from tokina.fetch_specs import build_tool  # noqa: E402


if __name__ == "__main__":
    audit(build_tool())
