"""Audit Carl Zeiss lens data completeness.

Thin entry point: builds the Zeiss BrandTool and hands it to the shared
brandkit audit runner, with an extra check for the PDF datasheet (Zeiss is
PDF-only, so the datasheet stands in for diagram presence).

Usage:
    py tools/zeiss/audit.py                  # full audit
    py tools/zeiss/audit.py --filter 12mm    # filter by model substring
    py tools/zeiss/audit.py --missing        # show only lenses with missing data
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import LensEntry, audit  # noqa: E402

from zeiss.fetch_specs import build_tool  # noqa: E402


def _datasheet_check(tool, model: str) -> list[str]:
    lens = LensEntry(model=model, url="")
    return [] if tool.has_datasheet(lens) else ["no PDF datasheet"]


if __name__ == "__main__":
    audit(build_tool(), extra_checks=_datasheet_check)
