"""TokinaExtractor tests against a committed sample page.

Pure string-to-dict tests — no network. They pin the brand-specific
parsing that was ported from the old common.py.
"""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from tokina.extractor import TokinaExtractor  # noqa: E402

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


def test_extract_physical_dimensions(extractor, html):
    phys = extractor.extract_physical(html)
    assert phys["weight"] == 276  # last-occurrence wins over the widget junk
    assert phys["filterThread"] == 52
    assert phys["apertureBlades"] == 9
    assert phys["minFocusDistance"] == 300  # 0.3m -> mm
    assert phys["maxMagnification"] == 0.1  # 1:10 -> decimal
    assert phys["diameter"] == 65
    assert phys["length"] == 72


def test_extract_physical_optical_and_flags(extractor, html):
    phys = extractor.extract_physical(html)
    assert phys["maxAperture"] == 1.4
    assert phys["focalLengthMin"] == 23  # prime -> min == max
    assert phys["focalLengthMax"] == 23
    assert phys["hasApertureRing"] is True
    assert phys["isApertureClickless"] is True
    assert phys["hasFocusRing"] is True


def test_extract_physical_omits_unstated_flags(extractor, html):
    # The Tokina page does not state OIS / weather-sealing / AF motor for this
    # lens — they must be omitted, not returned False (so the stored False is
    # never falsely flagged as a mismatch).
    phys = extractor.extract_physical(html)
    assert "hasOis" not in phys
    assert "isWeatherSealed" not in phys
    assert "afMotor" not in phys


def test_physical_diff_catches_swapped_weight(extractor, html):
    # The Session-76 bug: 23mm stored with the 33mm's weight (285). verify()
    # must flag it. Here we diff the extracted 276 against a wrong stored 285.
    from brandkit import diff_physical

    extracted = extractor.extract_physical(html)
    stored_wrong = {"weight": 285}  # the swapped value
    mismatches = diff_physical(stored_wrong, extracted)
    assert any(m.field == "weight" for m in mismatches)


def test_physical_clean_when_stored_matches(extractor, html):
    from brandkit import diff_physical

    extracted = extractor.extract_physical(html)
    stored_correct = {"weight": 276, "filterThread": 52, "apertureBlades": 9}
    assert diff_physical(stored_correct, extracted) == []


def test_numbered_fallback_for_zoom_lenses(extractor):
    html = (
        '<img src="/uploads/images/catalog/product/atx-m/11-18/05_1.png">'
        '<img src="/uploads/images/catalog/product/atx-m/11-18/05_2.png">'
        '<img src="/uploads/images/catalog/product/atx-m/11-18/05_3.png">'
    )
    urls = extractor.extract_image_urls(html)
    assert len(urls["construction"]) == 1  # 05_1
    assert len(urls["mtf"]) == 2  # 05_2, 05_3
