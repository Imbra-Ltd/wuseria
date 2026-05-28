"""ZeissExtractor + save_pdf tests (PDF-only brand)."""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from brandkit import BrandTool  # noqa: E402
from pagefetch import FakeFetcher  # noqa: E402
from zeiss.extractor import ZeissExtractor  # noqa: E402

PDF_URL = "https://www.zeiss.com/touit-12mm-datasheet.pdf"


@pytest.fixture
def extractor() -> ZeissExtractor:
    return ZeissExtractor()


def test_config_no_diagrams(extractor):
    assert extractor.config.name == "Carl Zeiss"
    assert extractor.config.slug_prefix == "zeiss"
    assert extractor.config.has_diagrams is False


def test_extract_optical_returns_empty(extractor):
    # Nothing to parse — Zeiss data is in the PDF.
    assert extractor.extract_optical("<html>anything</html>") == {}


def test_extract_physical_and_images_empty(extractor):
    assert extractor.extract_physical("x") == {}
    assert extractor.extract_image_urls("x", "u") == {"mtf": [], "construction": []}


def _zeiss_tool(fake, tmp_path) -> BrandTool:
    ts = tmp_path / "lenses.ts"
    ts.write_text(
        'export const lenses = [\n'
        '  {\n'
        '    brand: "Carl Zeiss",\n'
        '    model: "Touit 12mm f/2.8",\n'
        f'    officialUrl: "{PDF_URL}",\n'
        '  },\n'
        '];\n',
        encoding="utf-8",
    )
    return BrandTool(
        extractor=ZeissExtractor(),
        source=fake,
        lenses_path=ts,
        specs_root=tmp_path / "specs",
    )


def test_save_pdf_downloads(tmp_path):
    fake = FakeFetcher(binary={PDF_URL: b"%PDF-1.4" + b"x" * 2000})
    tool = _zeiss_tool(fake, tmp_path)
    lens = tool.resolve_lenses()[0]
    assert tool.has_datasheet(lens) is False
    dest = tool.save_pdf(lens)
    assert dest is not None
    assert dest.name == "zeiss-touit-12mm-f2-8-datasheet.pdf"
    assert dest.exists()
    assert tool.has_datasheet(lens) is True


def test_save_pdf_fails_on_tiny_payload(tmp_path):
    fake = FakeFetcher(binary={PDF_URL: b"%PDF"})  # under min_size 1000
    tool = _zeiss_tool(fake, tmp_path)
    assert tool.save_pdf(tool.resolve_lenses()[0]) is None
