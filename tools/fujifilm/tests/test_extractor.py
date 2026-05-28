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


def test_extract_physical_full_spec_table(extractor, html):
    phys = extractor.extract_physical(html)
    assert phys["focalLengthMin"] == 16
    assert phys["focalLengthMax"] == 16
    assert phys["maxAperture"] == 1.4
    assert phys["apertureBlades"] == 9
    assert phys["maxMagnification"] == 0.21
    assert phys["weight"] == 375
    assert phys["filterThread"] == 67
    assert phys["diameter"] == 73.4
    assert phys["length"] == 73


def test_extract_physical_min_focus_takes_macro(extractor, html):
    # Focus range "Normal 60cm - inf  Macro 15cm - inf" -> closer is 15cm.
    assert extractor.extract_physical(html)["minFocusDistance"] == 150  # 15cm -> mm


def test_extract_physical_zoom_focal_range(extractor):
    html = "<td>Focal length</td><td>f=10-24mm (15-36mm equivalent)</td>"
    phys = extractor.extract_physical(html)
    assert phys["focalLengthMin"] == 10
    assert phys["focalLengthMax"] == 24


def test_extract_physical_comma_weight(extractor):
    # Weights >=1000g use a comma thousands separator on the spec page
    # (e.g. XF 200mm f/2 reads "2,265g") — the digits before the comma
    # must not be dropped (#906).
    html = "<td>Weight *2 (approx.)</td><td>2,265g</td>"
    assert extractor.extract_physical(html)["weight"] == 2265


def test_extract_physical_plain_weight_unaffected(extractor):
    # Sub-1000g weights have no separator and must still parse.
    html = "<td>Weight</td><td>375g</td>"
    assert extractor.extract_physical(html)["weight"] == 375


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
