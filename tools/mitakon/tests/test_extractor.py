"""MitakonExtractor tests — UC transport, panel-1 counts, HRI summing."""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from pagefetch import Transport  # noqa: E402
from mitakon.extractor import MitakonExtractor  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "mitakon-35mm-sample.html"


@pytest.fixture
def html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture
def extractor() -> MitakonExtractor:
    return MitakonExtractor()


def test_config_uc_no_diagrams(extractor):
    assert extractor.config.name == "Mitakon"
    assert extractor.config.transport is Transport.UC
    assert extractor.config.has_diagrams is False


def test_elements_groups_from_spec_panel(extractor, html):
    specs = extractor.extract_optical(html)
    assert specs["elements"] == 11
    assert specs["groups"] == 9


def test_hri_extra_and_plain_summed(extractor, html):
    specs = extractor.extract_optical(html)
    # "two Extra-High RI" + "one High RI" → 3 HRI (text numbers normalized).
    assert "3 HRI" in specs["special"]


def test_other_special_elements(extractor, html):
    specs = extractor.extract_optical(html)
    assert "1 aspherical" in specs["special"]
    assert "2 ED" in specs["special"]


def test_coating(extractor, html):
    specs = extractor.extract_optical(html)
    assert specs["coating"] == ["Multi-layer coating"]


def test_hri_plain_only():
    # When only plain "high refractive" is present, it covers all HRI.
    ex = MitakonExtractor()
    html = "<p>10 elements in 8 groups. 2 High Refractive Index elements.</p>"
    specs = ex.extract_optical(html)
    assert "2 HRI" in specs["special"]


def test_no_diagrams_empty_images(extractor, html):
    assert extractor.extract_image_urls(html, "https://x") == {"mtf": [], "construction": []}
