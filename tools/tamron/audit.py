"""Audit Tamron lens data completeness.

Thin entry point: builds the Tamron BrandTool and hands it to the shared
brandkit audit runner.

Usage:
    py tools/tamron/audit.py                 # full audit
    py tools/tamron/audit.py --filter 17-70  # filter by model substring
    py tools/tamron/audit.py --missing       # show only lenses with missing data
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import audit  # noqa: E402

from tamron.fetch_specs import build_tool  # noqa: E402


if __name__ == "__main__":
    audit(build_tool())
