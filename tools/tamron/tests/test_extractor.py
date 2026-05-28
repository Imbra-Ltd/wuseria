"""TamronExtractor tests, plus the dual-page concatenation via BrandTool.

Tamron splits specs across the main page and a spec.html sub-page. The
extractor sees the concatenated HTML (brandkit handles the second fetch via
config.extra_paths), so these tests feed it main+spec combined, and one test
drives BrandTool with a FakeFetcher to prove the two-page fetch works.
"""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import BrandTool  # noqa: E402
from pagefetch import FakeFetcher  # noqa: E402
from tamron.extractor import TamronExtractor, url_to_code  # noqa: E402

FIXDIR = Path(__file__).resolve().parent / "fixtures"
MAIN = (FIXDIR / "tamron-17-70-main.html").read_text(encoding="utf-8")
SPEC = (FIXDIR / "tamron-17-70-spec.html").read_text(encoding="utf-8")
LENS_URL = "https://www.tamron.com/global/consumer/lenses/b070/"


@pytest.fixture
def extractor() -> TamronExtractor:
    return TamronExtractor()


def test_config_declares_spec_subpage(extractor):
    assert extractor.config.name == "Tamron"
    assert extractor.config.extra_paths == ("spec.html",)


def test_url_to_code():
    assert url_to_code(LENS_URL) == "b070"


def test_elements_groups_from_spec_page(extractor):
    # Counts live on the spec page; only present in the combined HTML.
    specs = extractor.extract_optical(MAIN + SPEC)
    assert specs["elements"] == 16
    assert specs["groups"] == 12


def test_special_from_main_page(extractor):
    specs = extractor.extract_optical(MAIN + SPEC)
    assert "2 XLD" in specs["special"]
    assert "2 LD" in specs["special"]
    assert "1 GM aspherical" in specs["special"]
    assert "1 hybrid aspherical" in specs["special"]


def test_coating_bbar_g2_and_fluorine(extractor):
    specs = extractor.extract_optical(MAIN + SPEC)
    assert "BBAR G2" in specs["coating"]
    assert "fluorine" in specs["coating"]


def test_image_urls_svg_with_code(extractor):
    urls = extractor.extract_image_urls(MAIN + SPEC, LENS_URL)
    assert len(urls["construction"]) == 1
    assert urls["construction"][0].endswith("b070_lens-construction_en.svg")
    assert len(urls["mtf"]) == 2
    assert all(u.endswith(".svg") and "_mtf_" in u for u in urls["mtf"])
    # Relative MTF URLs resolved against the base.
    assert all(u.startswith("https://") for u in urls["mtf"])


def test_brandtool_concatenates_two_pages(tmp_path):
    # BrandTool must fetch lens.url AND lens.url/spec.html, concatenate, so
    # the spec-page-only element count is visible to extract_optical.
    spec_url = LENS_URL.rstrip("/") + "/spec.html"
    fake = FakeFetcher(responses={LENS_URL: MAIN, spec_url: SPEC})

    # A tiny lenses.ts fixture with one Tamron lens.
    ts = tmp_path / "lenses.ts"
    ts.write_text(
        'export const lenses = [\n'
        '  {\n'
        '    brand: "Tamron",\n'
        '    model: "17-70mm f/2.8 Di III-A VC RXD",\n'
        f'    officialUrl: "{LENS_URL}",\n'
        '  },\n'
        '];\n',
        encoding="utf-8",
    )
    tool = BrandTool(
        extractor=TamronExtractor(),
        source=fake,
        lenses_path=ts,
        specs_root=tmp_path / "specs",
    )
    lens = tool.resolve_lenses()[0]
    specs = tool.fetch_optical(lens)
    assert specs["elements"] == 16  # only present on the spec sub-page
    # Both pages were fetched.
    assert LENS_URL in fake.calls
    assert spec_url in fake.calls
