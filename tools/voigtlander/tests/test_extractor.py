"""VoigtlanderExtractor tests against a committed sample page."""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from pagefetch import Transport  # noqa: E402
from voigtlander.extractor import VoigtlanderExtractor  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "voigtlander-nokton-sample.html"


@pytest.fixture
def html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture
def extractor() -> VoigtlanderExtractor:
    return VoigtlanderExtractor()


def test_config_uses_playwright(extractor):
    assert extractor.config.name == "Voigtlander"
    assert extractor.config.transport is Transport.PLAYWRIGHT


def test_elements_groups(extractor, html):
    specs = extractor.extract_optical(html)
    assert specs["elements"] == 10
    assert specs["groups"] == 8


def test_no_special_or_coating_keys(extractor, html):
    # Voigtlander extractor reports only elements/groups.
    specs = extractor.extract_optical(html)
    assert "special" not in specs
    assert "coating" not in specs


def test_construction_german_filename(extractor, html):
    urls = extractor.extract_image_urls(html)
    assert len(urls["construction"]) == 1
    assert urls["construction"][0].endswith("Linsenschnitt-Nokton-35.png")
    assert urls["mtf"] == []  # Voigtlander publishes no MTF charts


def test_no_match_returns_empty(extractor):
    assert extractor.extract_optical("<p>no spec here</p>") == {}
