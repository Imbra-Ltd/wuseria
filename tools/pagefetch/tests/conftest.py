"""Shared pytest fixtures for the pagefetch test suite.

Adds the tools/ directory to sys.path so `import pagefetch` resolves when
tests run from anywhere, and provides a temp-dir-backed FileCache.
"""

import sys
from pathlib import Path

import pytest

# tools/ is two levels up from this file (tools/pagefetch/tests/conftest.py).
TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from pagefetch import FileCache  # noqa: E402


@pytest.fixture
def cache(tmp_path: Path) -> FileCache:
    return FileCache(cache_dir=tmp_path / "cache")
