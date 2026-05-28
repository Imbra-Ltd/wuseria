"""FujifilmExtractor tests — the static (HTML) path.

The position-based live-page fallback (extract_images_live) needs a real
Playwright page and is exercised manually, not here.
"""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from pagefetch import Transport  # noqa: E402
from fujifilm.extractor import FujifilmExtractor, url_to_slug  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "fujifilm-xf16mm-spec.html"
LENS_URL = "https://fujifilm-x.com/global/products/lenses/xf16mmf14-r-wr/"


@pytest.fixture
def html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture
def extractor() -> FujifilmExtractor:
    return FujifilmExtractor()


def test_config_playwright_and_live(extractor):
    assert extractor.config.name == "Fujifilm"
    assert extractor.config.transport is Transport.PLAYWRIGHT
    assert extractor.config.needs_live_page is True


def test_normalize_url_appends_specifications(extractor):
    assert extractor.normalize_url(LENS_URL).endswith("/specifications/")
    # Idempotent — does not double-append.
    once = extractor.normalize_url(LENS_URL)
    assert extractor.normalize_url(once) == once


def test_url_to_slug_strips_specifications(extractor):
    assert url_to_slug(LENS_URL + "specifications/") == "xf16mmf14-r-wr"


def test_elements_groups(extractor, html):
    specs = extractor.extract_optical(html)
    assert specs["elements"] == 13
    assert specs["groups"] == 11


def test_special_elements(extractor, html):
    specs = extractor.extract_optical(html)
    assert "2 aspherical" in specs["special"]
    assert "3 ED" in specs["special"]


def test_coating_super_ebc_always_plus_nano_gi(extractor, html):
    specs = extractor.extract_optical(html)
    assert "Super EBC" in specs["coating"]  # always present
    assert "Nano-GI" in specs["coating"]


def test_coating_super_ebc_when_page_silent(extractor):
    # Even a page that mentions no coating yields Super EBC.
    specs = extractor.extract_optical("<p>10 elements in 8 groups</p>")
    assert specs["coating"] == ["Super EBC"]


def test_named_image_urls_cross_and_specifications(extractor, html):
    urls = extractor.extract_image_urls(html, LENS_URL + "specifications/")
    assert any(u.endswith("xf16mmf14-r-wr_cross.webp") for u in urls["construction"])
    # mtf_15 (Specifications-images2) ordered before mtf_45 (images3).
    assert len(urls["mtf"]) == 2
    assert urls["mtf"][0].endswith("Specifications-images2.png")
    assert urls["mtf"][1].endswith("Specifications-images3.png")


def test_no_images_without_match(extractor):
    urls = extractor.extract_image_urls("<html>no diagrams</html>", LENS_URL)
    assert urls == {"mtf": [], "construction": []}
