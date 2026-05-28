"""ViltroxExtractor tests — theme-HTML spec table (#901).

Viltrox moved its specs out of the Shopify JSON into a spec table in the
theme HTML. These exercise the X-mount column selection (the table lists one
column per mount, in no fixed order), the label/unit drift across product
generations, and the inferred-coating default.
"""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from viltrox.extractor import ViltroxExtractor  # noqa: E402

FIXDIR = Path(__file__).resolve().parent / "fixtures"
PAGE_27 = FIXDIR / "viltrox-27mm-page.html"  # columns E / Z / XF (X last)
PAGE_33 = FIXDIR / "viltrox-33mm-page.html"  # columns E / X / EF-M / Z (X 2nd)


@pytest.fixture
def extractor() -> ViltroxExtractor:
    return ViltroxExtractor()


def test_config_no_diagrams(extractor):
    assert extractor.config.name == "Viltrox"
    assert extractor.config.has_diagrams is False


def test_normalize_url_is_identity(extractor):
    # Specs now live on the HTML page; no .json suffix (#901).
    url = "https://viltrox.com/products/viltrox-af-27mm-f-1-2-pro-xf-mount"
    assert extractor.normalize_url(url) == url


# --- extract_optical ----------------------------------------------------


def test_elements_groups_from_spec_table(extractor):
    specs = extractor.extract_optical(PAGE_27.read_text(encoding="utf-8"))
    assert specs["elements"] == 15
    assert specs["groups"] == 11


def test_elements_groups_label_drift(extractor):
    # 33mm page uses the same 'Lens Elements' label but a different column order.
    specs = extractor.extract_optical(PAGE_33.read_text(encoding="utf-8"))
    assert specs["elements"] == 10
    assert specs["groups"] == 9


def test_special_empty_when_description_names_no_counts(extractor):
    # The 33mm description names no special-element counts -> [].
    specs = extractor.extract_optical(PAGE_33.read_text(encoding="utf-8"))
    assert specs["special"] == []


def test_special_ignores_page_hex_noise(extractor):
    # A CSS color-scheme UUID ending '...b953ed' must NOT read as '953 ED':
    # the scan is scoped to the description block, not the whole page.
    html = (
        '<style>.x{--scheme-45d804b953ed:#000}</style>'
        '<div class="product__description rte"><p>A fine lens.</p></div>'
        '<table><tr><td>Lens Elements</td><td>9/8</td></tr></table>'
    )
    assert extractor.extract_optical(html)["special"] == []


def test_special_counts_from_description(extractor):
    html = (
        '<div class="product__description rte">'
        '<p>Built with 2 aspherical and 1 ED element.</p></div>'
        '<table><tr><td>Lens Elements</td><td>9/8</td></tr></table>'
    )
    special = extractor.extract_optical(html)["special"]
    assert "2 aspherical" in special
    assert "1 ED" in special


def test_coating_brand_default_inferred(extractor):
    # Pages don't list the coating; the brand default fills it, flagged.
    specs = extractor.extract_optical(PAGE_27.read_text(encoding="utf-8"))
    assert specs["coating"] == ["HD Nano multilayer coating"]
    assert specs["coating_inferred"] is True


# --- extract_physical (#901 / #779) -------------------------------------


def test_extract_physical_x_mount_column_last(extractor):
    # 27mm columns are E / Z / XF -> X-mount is the LAST value.
    phys = extractor.extract_physical(PAGE_27.read_text(encoding="utf-8"))
    assert phys["filterThread"] == 67
    assert phys["diameter"] == 82.0
    assert phys["length"] == 92.0
    assert phys["weight"] == 560  # XF column, not the E column's 565
    assert phys["apertureBlades"] == 11
    assert phys["maxMagnification"] == 0.15  # "0.15X" -> 0.15
    assert phys["minFocusDistance"] == 280  # 0.28m -> mm
    assert phys["afMotor"] == "STM+Lead screw"


def test_extract_physical_x_mount_column_middle(extractor):
    # 33mm columns are E / X / EF-M / Z -> X-mount is the SECOND value.
    phys = extractor.extract_physical(PAGE_33.read_text(encoding="utf-8"))
    assert phys["filterThread"] == 52  # "Φ52" (no mm) -> 52
    assert phys["diameter"] == 65.0  # X-mount col, not the Z col's 69
    assert phys["length"] == 72.0
    assert phys["weight"] == 270  # X-mount col, not the Z col's 310
    assert phys["apertureBlades"] == 9
    assert phys["maxMagnification"] == 0.1  # "0.1" (no X) -> 0.1
    assert phys["minFocusDistance"] == 400  # 0.4m -> mm


def test_extract_physical_empty_without_table(extractor):
    assert extractor.extract_physical("<p>no spec table</p>") == {}


def test_no_images(extractor):
    # has_diagrams False -> base default empty image dict.
    page = PAGE_27.read_text(encoding="utf-8")
    assert extractor.extract_image_urls(page, "https://x") == {"mtf": [], "construction": []}
