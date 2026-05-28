"""TTArtisanExtractor tests against a committed sample page."""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from ttartisan.extractor import TTArtisanExtractor  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ttartisan-90mm-sample.html"


@pytest.fixture
def html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture
def extractor() -> TTArtisanExtractor:
    return TTArtisanExtractor()


def test_config_brand_name_lowercase_a(extractor):
    # lenses.ts uses "TTartisan", not "TTArtisan".
    assert extractor.config.name == "TTartisan"
    assert extractor.config.slug_prefix == "ttartisan"


def test_elements_groups_from_spec_table(extractor, html):
    specs = extractor.extract_optical(html)
    assert specs["elements"] == 11
    assert specs["groups"] == 8


def test_special_ed_and_hr(extractor, html):
    specs = extractor.extract_optical(html)
    assert "2 ED" in specs["special"]
    assert "2 HR" in specs["special"]


def test_achromatic_doublet(extractor, html):
    specs = extractor.extract_optical(html)
    assert "4 achromatic doublet" in specs["special"]


def test_coating_mc_multilayer(extractor, html):
    specs = extractor.extract_optical(html)
    assert specs["coating"] == ["MC Multi-Layer"]


def test_named_image_patterns(extractor, html):
    urls = extractor.extract_image_urls(html)
    assert any(u.endswith("Specification-MTF.webp") for u in urls["mtf"])
    assert any(u.endswith("Specification-OD-EN.webp") for u in urls["construction"])


def test_slr_variants_excluded(extractor, html):
    urls = extractor.extract_image_urls(html)
    all_urls = urls["mtf"] + urls["construction"]
    assert not any("-slr" in u.lower() for u in all_urls)


def test_relative_urls_resolved(extractor, html):
    urls = extractor.extract_image_urls(html)
    assert all(u.startswith("https://www.ttartisan.com/") for u in urls["mtf"])


def test_extract_physical_inline_specs(extractor, html):
    phys = extractor.extract_physical(html)
    assert phys["filterThread"] == 67
    assert phys["apertureBlades"] == 12
    assert phys["maxAperture"] == 1.25
    assert phys["minFocusDistance"] == 900  # 0.9m -> mm
    assert phys["focalLengthMin"] == 90
    assert phys["focalLengthMax"] == 90
    assert phys["maxMagnification"] == 0.2  # 1:5


def test_extract_physical_weight_range_takes_higher(extractor, html):
    # "Around 620~640g" -> the higher (final) value.
    assert extractor.extract_physical(html)["weight"] == 640


def test_extract_physical_tilt_angle_when_present(extractor):
    html = "<p>Focal length 35mm Maximum aperture F1.4 Tilt Angle 8 Weight Around 350g</p>"
    assert extractor.extract_physical(html)["tiltAngle"] == 8
