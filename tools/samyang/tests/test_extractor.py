"""SamyangExtractor tests against a committed sample page."""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from samyang.extractor import SamyangExtractor  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "samyang-14mm-sample.html"


@pytest.fixture
def html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture
def extractor() -> SamyangExtractor:
    return SamyangExtractor()


def test_config(extractor):
    assert extractor.config.name == "Samyang"
    assert extractor.config.slug_prefix == "samyang"


def test_elements_and_groups_from_spec_block(extractor, html):
    specs = extractor.extract_optical(html)
    assert specs["elements"] == 14
    assert specs["groups"] == 12


def test_nav_elements_count_not_picked_up(extractor, html):
    # The nav link "85mm F1.4 (9 elements)" must not leak into the count.
    specs = extractor.extract_optical(html)
    assert specs["elements"] != 9


def test_special_elements_aspherical_summed(extractor, html):
    specs = extractor.extract_optical(html)
    # 1 H-ASP + 1 ASP both map to "aspherical" → summed to 2.
    assert "2 aspherical" in specs["special"]
    assert "2 ED" in specs["special"]


def test_coating_umc(extractor, html):
    specs = extractor.extract_optical(html)
    assert specs["coating"] == ["UMC"]


def test_image_urls_resolved(extractor, html):
    urls = extractor.extract_image_urls(html)
    assert urls["mtf"] == ["https://www.lksamyang.com/upload/editor/5678"]
    assert urls["construction"] == ["https://www.lksamyang.com/upload/editor/1234"]


def test_no_spec_block_returns_empty(extractor):
    assert extractor.extract_optical("<html><body>nothing here</body></html>") == {}
