"""Shared fixtures for the brandkit test suite."""

import sys
from pathlib import Path

import pytest

# tools/ is two levels up (tools/brandkit/tests/conftest.py).
TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def lenses_sample_path() -> Path:
    return FIXTURES / "lenses_sample.ts"
