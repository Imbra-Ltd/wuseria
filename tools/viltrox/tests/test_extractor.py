"""ViltroxExtractor tests — JSON content + inferred-coating default."""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from viltrox.extractor import ViltroxExtractor, url_to_handle  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "viltrox-27mm-product.json"


@pytest.fixture
def product_json() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture
def extractor() -> ViltroxExtractor:
    return ViltroxExtractor()


def test_config_no_diagrams(extractor):
    assert extractor.config.name == "Viltrox"
    assert extractor.config.has_diagrams is False


def test_normalize_url_appends_json(extractor):
    assert (
        extractor.normalize_url("https://viltrox.com/products/af-27mm-f1-2-pro-xf")
        == "https://viltrox.com/products/af-27mm-f1-2-pro-xf.json"
    )


def test_url_to_handle():
    assert url_to_handle("https://viltrox.com/products/af-9mm-f2-8-xf") == "af-9mm-f2-8-xf"


def test_elements_groups_from_json_body(extractor, product_json):
    specs = extractor.extract_optical(product_json)
    assert specs["elements"] == 15
    assert specs["groups"] == 11


def test_special_elements(extractor, product_json):
    specs = extractor.extract_optical(product_json)
    assert "2 aspherical" in specs["special"]
    assert "1 ED" in specs["special"]
    assert "3 HR" in specs["special"]


def test_coating_read_from_page_not_inferred(extractor, product_json):
    specs = extractor.extract_optical(product_json)
    assert specs["coating"] == ["HD Nano multilayer coating"]
    assert "coating_inferred" not in specs


def test_coating_inferred_when_absent(extractor):
    # No coating mention → brand default, flagged inferred.
    body = '{"product": {"body_html": "<p>10 elements in 8 groups.</p>"}}'
    specs = extractor.extract_optical(body)
    assert specs["coating"] == ["HD Nano multilayer coating"]
    assert specs["coating_inferred"] is True


def test_slash_format_elements_groups(extractor):
    body = '{"product": {"body_html": "<p>Optical Design: 9/11 Elements</p>"}}'
    specs = extractor.extract_optical(body)
    # Pattern 2 reads N/M as elements/groups.
    assert specs["elements"] == 9
    assert specs["groups"] == 11


def test_malformed_json_returns_empty(extractor):
    assert extractor.extract_optical("not json at all") == {}


def test_no_images(extractor, product_json):
    # has_diagrams False → base default empty image dict.
    assert extractor.extract_image_urls(product_json, "https://x") == {"mtf": [], "construction": []}
