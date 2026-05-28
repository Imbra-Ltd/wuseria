"""ZeissExtractor — the Carl Zeiss Touit BrandExtractor strategy.

Zeiss Touit lenses are discontinued: the product pages are gone (404) and
the officialUrl fields point at PDF datasheets on zeiss.com. There is no live
page to parse, so this extractor returns nothing from extract_optical /
extract_physical / extract_image_urls — the real work is downloading the PDF
(BrandTool.save_pdf), and specs are read from the PDF manually.

has_diagrams is False; the lens URL is a .pdf, so the tool's job is save_pdf,
not spec scraping. Kept as a BrandExtractor so Zeiss still resolves lenses
and validates URLs through the shared brandkit machinery.
"""

from pagefetch import ContentMode, Transport

from brandkit import BrandConfig, BrandExtractor


class ZeissExtractor(BrandExtractor):
    config = BrandConfig(
        name="Carl Zeiss",
        slug_prefix="zeiss",
        content_mode=ContentMode.HTML,
        transport=Transport.AUTO,
        has_diagrams=False,
    )

    def extract_optical(self, content: str) -> dict:
        # Nothing to parse — Zeiss data lives in the downloaded PDF datasheet.
        return {}
