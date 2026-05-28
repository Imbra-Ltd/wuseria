"""BrandTool orchestration tests — driven by FakeFetcher + a stub extractor.

These prove the composition seam: no network, no real HTML. The stub
extractor returns canned dicts so the test exercises the orchestrator's
pipeline (resolve, fetch, extract, verify, validate, save images), not any
brand's parsing.
"""

from pathlib import Path

import pytest

from brandkit import BrandConfig, BrandExtractor, BrandTool
from pagefetch import ContentMode, FakeFetcher

TOKINA_23_URL = "https://tokinalens.com/product/atx-m-23mm-f1-4-x/"


class StubExtractor(BrandExtractor):
    """Canned extractor for orchestration tests."""

    def __init__(self, has_diagrams=True, physical=None, images=None):
        self.config = BrandConfig(
            name="Tokina",
            slug_prefix="tokina",
            content_mode=ContentMode.HTML,
            has_diagrams=has_diagrams,
        )
        self._physical = physical or {}
        self._images = images or {"mtf": [], "construction": []}

    def extract_optical(self, content: str) -> dict:
        return {"elements": 11, "groups": 10}

    def extract_physical(self, content: str) -> dict:
        return dict(self._physical)

    def extract_image_urls(self, content: str) -> dict:
        return {k: list(v) for k, v in self._images.items()}


def make_tool(fake: FakeFetcher, lenses_path: Path, tmp_path: Path, **kw) -> BrandTool:
    return BrandTool(
        extractor=StubExtractor(**kw),
        source=fake,
        lenses_path=lenses_path,
        specs_root=tmp_path / "optical-specs",
    )


def test_resolve_lenses_uses_brand_and_url(lenses_sample_path, tmp_path):
    tool = make_tool(FakeFetcher(), lenses_sample_path, tmp_path)
    models = [e.model for e in tool.resolve_lenses()]
    assert models == ["atx-m 23mm f/1.4 X", "atx-m 33mm f/1.4 X"]


def test_slug_for_uses_config_prefix(lenses_sample_path, tmp_path):
    tool = make_tool(FakeFetcher(), lenses_sample_path, tmp_path)
    assert tool.slug_for("atx-m 23mm f/1.4 X") == "tokina-atx-m-23mm-f1-4-x"


def test_fetch_optical_runs_through_fake(lenses_sample_path, tmp_path):
    fake = FakeFetcher(responses={TOKINA_23_URL: "<html>page</html>"})
    tool = make_tool(fake, lenses_sample_path, tmp_path)
    lens = tool.resolve_lenses()[0]
    assert tool.fetch_optical(lens) == {"elements": 11, "groups": 10}
    assert fake.calls == [TOKINA_23_URL]


def test_fetch_optical_empty_when_fetch_fails(lenses_sample_path, tmp_path):
    fake = FakeFetcher(responses={})  # URL not mapped -> empty content
    tool = make_tool(fake, lenses_sample_path, tmp_path)
    assert tool.fetch_optical(tool.resolve_lenses()[0]) == {}


def test_verify_reports_no_mismatch_when_specs_agree(lenses_sample_path, tmp_path):
    fake = FakeFetcher(responses={TOKINA_23_URL: "<html>x</html>"})
    tool = make_tool(fake, lenses_sample_path, tmp_path, physical={"weight": 276})
    # Fixture stores weight 276 for the 23mm; extractor returns 276.
    assert tool.verify(tool.resolve_lenses()[0]) == []


def test_verify_reports_mismatch(lenses_sample_path, tmp_path):
    fake = FakeFetcher(responses={TOKINA_23_URL: "<html>x</html>"})
    tool = make_tool(fake, lenses_sample_path, tmp_path, physical={"weight": 999})
    mismatches = tool.verify(tool.resolve_lenses()[0])
    assert len(mismatches) == 1
    assert mismatches[0].field == "weight"


def test_validate_url_ok_when_content_returned(lenses_sample_path, tmp_path):
    fake = FakeFetcher(responses={TOKINA_23_URL: "<html>real</html>"})
    tool = make_tool(fake, lenses_sample_path, tmp_path)
    status = tool.validate_url(tool.resolve_lenses()[0])
    assert status.ok is True


def test_validate_url_fails_when_no_content(lenses_sample_path, tmp_path):
    fake = FakeFetcher(responses={})  # broken URL -> no content
    tool = make_tool(fake, lenses_sample_path, tmp_path)
    status = tool.validate_url(tool.resolve_lenses()[0])
    assert status.ok is False


def test_no_diagram_brand_returns_empty_image_urls(lenses_sample_path, tmp_path):
    fake = FakeFetcher(responses={TOKINA_23_URL: "<html>x</html>"})
    tool = make_tool(fake, lenses_sample_path, tmp_path, has_diagrams=False)
    assert tool.fetch_image_urls(tool.resolve_lenses()[0]) == {"mtf": [], "construction": []}


def test_save_images_downloads_and_names(lenses_sample_path, tmp_path):
    mtf_url = "https://cdn.test/chart.png"
    fake = FakeFetcher(
        responses={TOKINA_23_URL: "<html>x</html>"},
        binary={mtf_url: b"\x89PNG" + b"x" * 600},
    )
    tool = make_tool(
        fake, lenses_sample_path, tmp_path, images={"mtf": [mtf_url], "construction": []}
    )
    lens = tool.resolve_lenses()[0]
    written = tool.save_images(lens, tool.fetch_image_urls(lens))
    assert len(written) == 1
    assert written[0].name == "tokina-atx-m-23mm-f1-4-x-mtf.png"
    assert written[0].exists()


def test_save_images_skips_too_small(lenses_sample_path, tmp_path):
    mtf_url = "https://cdn.test/tiny.png"
    fake = FakeFetcher(
        responses={TOKINA_23_URL: "<html>x</html>"},
        binary={mtf_url: b"tiny"},  # under min_size=500
    )
    tool = make_tool(
        fake, lenses_sample_path, tmp_path, images={"mtf": [mtf_url], "construction": []}
    )
    lens = tool.resolve_lenses()[0]
    assert tool.save_images(lens, tool.fetch_image_urls(lens)) == []


def test_multiple_mtf_charts_get_indexed_names(lenses_sample_path, tmp_path):
    urls = ["https://cdn.test/a.png", "https://cdn.test/b.png"]
    fake = FakeFetcher(
        responses={TOKINA_23_URL: "<html>x</html>"},
        binary={u: b"\x89PNG" + b"y" * 600 for u in urls},
    )
    tool = make_tool(
        fake, lenses_sample_path, tmp_path, images={"mtf": urls, "construction": []}
    )
    lens = tool.resolve_lenses()[0]
    written = sorted(p.name for p in tool.save_images(lens, tool.fetch_image_urls(lens)))
    assert written == [
        "tokina-atx-m-23mm-f1-4-x-mtf-1.png",
        "tokina-atx-m-23mm-f1-4-x-mtf-2.png",
    ]
