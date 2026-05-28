"""TokinaExtractor tests against a committed sample page.

Pure string-to-dict tests — no network. They pin the brand-specific
parsing that was ported from the old common.py.
"""

import sys
from pathlib import Path

import pytest

TOKINA_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = TOKINA_DIR.parent
for p in (str(TOOLS_DIR), str(TOKINA_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from extractor import TokinaExtractor  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tokina-23mm-sample.html"


@pytest.fixture
def html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture
def extractor() -> TokinaExtractor:
    return TokinaExtractor()


def test_config_identifies_tokina(extractor):
    assert extractor.config.name == "Tokina"
    assert extractor.config.slug_prefix == "tokina"
    assert extractor.config.has_diagrams is True


def test_normalize_url_swaps_hyphens_for_underscores(extractor):
    url = "https://tokinalens.com/product/atx-m-23mm-f1-4-x/"
    assert (
        extractor.normalize_url(url)
        == "https://tokinalens.com/product/atx_m_23mm_f1_4_x/"
    )


def test_normalize_url_leaves_other_urls_alone(extractor):
    other = "https://example.com/some-page/"
    assert extractor.normalize_url(other) == other


def test_extract_optical_elements_and_groups(extractor, html):
    specs = extractor.extract_optical(html)
    assert specs["elements"] == 11
    assert specs["groups"] == 10


def test_extract_optical_special_from_spec_text(extractor, html):
    specs = extractor.extract_optical(html)
    assert "2 SD" in specs["special"]


def test_extract_optical_coating(extractor, html):
    specs = extractor.extract_optical(html)
    assert specs["coating"] == ["Multi-coating"]


def test_extract_image_urls_named_patterns(extractor, html):
    urls = extractor.extract_image_urls(html)
    assert any(u.endswith("atxm_23_constr.jpg") for u in urls["construction"])
    assert any(u.endswith("atxm_23_mtf.jpg") for u in urls["mtf"])
    # URLs resolved to absolute.
    assert all(u.startswith("https://tokinalens.com/") for u in urls["construction"])


def test_extract_image_urls_empty_when_no_diagrams(extractor):
    urls = extractor.extract_image_urls("<html><body>no images</body></html>")
    assert urls == {"mtf": [], "construction": []}


def test_numbered_fallback_for_zoom_lenses(extractor):
    html = (
        '<img src="/uploads/images/catalog/product/atx-m/11-18/05_1.png">'
        '<img src="/uploads/images/catalog/product/atx-m/11-18/05_2.png">'
        '<img src="/uploads/images/catalog/product/atx-m/11-18/05_3.png">'
    )
    urls = extractor.extract_image_urls(html)
    assert len(urls["construction"]) == 1  # 05_1
    assert len(urls["mtf"]) == 2  # 05_2, 05_3
