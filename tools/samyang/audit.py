"""Audit Samyang lens data completeness.

Thin entry point: builds the Samyang BrandTool and hands it to the shared
brandkit audit runner, which checks lenses.ts field presence plus MTF /
construction image presence.

Usage:
    py tools/samyang/audit.py                  # full audit
    py tools/samyang/audit.py --filter 12mm    # filter by model substring
    py tools/samyang/audit.py --missing        # show only lenses with missing data
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import audit  # noqa: E402

from samyang.fetch_specs import build_tool  # noqa: E402


if __name__ == "__main__":
    audit(build_tool())
