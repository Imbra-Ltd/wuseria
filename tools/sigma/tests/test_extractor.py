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

FIXDIR = Path(__file__).resolve().parent / "fixtures"
FIXTURE = FIXDIR / "sigma-30mm-sample.html"
PHYS_PRIME = FIXDIR / "sigma-physical-sample.html"
PHYS_ZOOM = FIXDIR / "sigma-physical-zoom-sample.html"
PHYS_ASCII = FIXDIR / "sigma-physical-ascii-colon-sample.html"
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


# --- extract_physical (#779 / #897) -------------------------------------


def test_extract_physical_prime(extractor):
    phys = extractor.extract_physical(PHYS_PRIME.read_text(encoding="utf-8"))
    assert phys["filterThread"] == 52
    assert phys["diameter"] == 65.4
    assert phys["length"] == 71.3  # first per-mount (L-Mount) value
    assert phys["weight"] == 280  # first per-mount value
    assert phys["apertureBlades"] == 9
    assert phys["hasCircularAperture"] is True  # "Rounded diaphragm"
    assert phys["minFocusDistance"] == 300  # 30cm -> mm
    assert phys["maxMagnification"] == round(1 / 7, 3)  # 1:7


def test_extract_physical_weight_thousands_separator(extractor):
    # A telephoto's "1,135g" must parse as 1135, not 135.
    phys = extractor.extract_physical(PHYS_ZOOM.read_text(encoding="utf-8"))
    assert phys["weight"] == 1135


def test_extract_physical_zoom_mfd_range_takes_wide(extractor):
    # "112(W) - 160(T)cm" -> wide (first) figure, in mm.
    phys = extractor.extract_physical(PHYS_ZOOM.read_text(encoding="utf-8"))
    assert phys["minFocusDistance"] == 1120


def test_extract_physical_dimensions_lowercase_x(extractor):
    # Some pages use "φ86.0mm x 197.2mm" (lowercase x) not the × sign.
    phys = extractor.extract_physical(PHYS_ZOOM.read_text(encoding="utf-8"))
    assert phys["diameter"] == 86.0
    assert phys["length"] == 197.2


def test_extract_physical_ascii_colon_mount_label(extractor):
    # Newer pages use "Canon RF Mount: 250g" (ASCII colon), not fullwidth.
    phys = extractor.extract_physical(PHYS_ASCII.read_text(encoding="utf-8"))
    assert phys["filterThread"] == 62
    assert phys["weight"] == 250  # first per-mount value, ASCII-colon split


def test_extract_physical_empty_page(extractor):
    # A page with no spec rows yields no physical specs.
    assert extractor.extract_physical("<p>no specs here</p>") == {}
