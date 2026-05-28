"""SigmaExtractor tests against a committed sample page.

Exercises the URL-derived product code path (the contract reason Sigma
needs the lens url passed to extract_image_urls).
"""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from sigma.extractor import SigmaExtractor, url_to_code  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "sigma-30mm-sample.html"
LENS_URL = "https://www.sigma-global.com/en/lenses/c016_30_14/"


@pytest.fixture
def html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture
def extractor() -> SigmaExtractor:
    return SigmaExtractor()


def test_config(extractor):
    assert extractor.config.name == "Sigma"
    assert extractor.config.slug_prefix == "sigma"


def test_url_to_code():
    assert url_to_code(LENS_URL) == "c016_30_14"
    assert url_to_code("https://x/y/c019_30_14") == "c019_30_14"


def test_elements_and_groups(extractor, html):
    specs = extractor.extract_optical(html)
    assert specs["elements"] == 9
    assert specs["groups"] == 7


def test_special_counted(extractor, html):
    specs = extractor.extract_optical(html)
    assert "2 aspherical" in specs["special"]
    assert "1 SLD" in specs["special"]


def test_special_fallback_when_no_count(extractor):
    # A diagram legend mentioning FLD glass with no count → "~1 FLD".
    specs = extractor.extract_optical("<p>11 elements in 9 groups. FLD glass used.</p>")
    assert "~1 FLD" in specs["special"]


def test_coating(extractor, html):
    specs = extractor.extract_optical(html)
    assert specs["coating"] == ["Super Multi-Layer Coating"]


def test_image_urls_use_url_code(extractor, html):
    urls = extractor.extract_image_urls(html, LENS_URL)
    # _specification_01 → construction; _specification_02_* → mtf (2 charts).
    assert len(urls["construction"]) == 1
    assert urls["construction"][0].endswith("c016_30_14_specification_01.png")
    assert len(urls["mtf"]) == 2
    assert all("_specification_02_" in u for u in urls["mtf"])


def test_image_urls_empty_without_url(extractor, html):
    # No url → no code → cannot match Sigma's code-keyed image names.
    assert extractor.extract_image_urls(html, "") == {"mtf": [], "construction": []}
