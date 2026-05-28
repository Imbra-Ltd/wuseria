"""VenusExtractor tests — incl. the CSS-hex false-positive guard."""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from pagefetch import Transport  # noqa: E402
from venus.extractor import VenusExtractor  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "venus-argus-sample.html"


@pytest.fixture
def html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture
def extractor() -> VenusExtractor:
    return VenusExtractor()


def test_config_uc_transport_and_brand(extractor):
    assert extractor.config.name == "Venus Laowa"
    assert extractor.config.slug_prefix == "venus-laowa"
    assert extractor.config.transport is Transport.UC


def test_elements_groups(extractor, html):
    specs = extractor.extract_optical(html)
    assert specs["elements"] == 14
    assert specs["groups"] == 9


def test_special_from_parenthetical(extractor, html):
    specs = extractor.extract_optical(html)
    assert "2 aspherical" in specs["special"]
    assert "3 ED" in specs["special"]
    assert "2 UHR" in specs["special"]  # "a pair of" -> 2


def test_css_hex_not_matched_as_ed(extractor):
    # #8ed1fc contains "8ed" but has no qualifying noun → must NOT match ED.
    html = '<style>.x{color:#8ed1fc}</style><p>12 elements in 7 groups</p>'
    specs = extractor.extract_optical(html)
    assert specs["special"] == []


def test_coating_frog_eye(extractor, html):
    specs = extractor.extract_optical(html)
    assert "Frog Eye Coating" in specs["coating"]


def test_image_urls_lazy_attrs_and_thumb_skip(extractor, html):
    urls = extractor.extract_image_urls(html)
    assert any(u.endswith("Argus-33mm-MTF.png") for u in urls["mtf"])
    assert any(u.endswith("Argus-33mm-Lens-Structure.png") for u in urls["construction"])
    # The 150x150 thumbnail is skipped.
    all_urls = urls["mtf"] + urls["construction"]
    assert not any("150x" in u for u in all_urls)


def test_construction_url_encoded_chinese(extractor):
    html = '<img src="/uploads/%E5%85%89%E8%B7%AF%E5%9B%BE-33mm.png">'
    urls = extractor.extract_image_urls(html)
    assert len(urls["construction"]) == 1
