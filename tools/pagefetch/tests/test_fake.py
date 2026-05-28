"""FakeFetcher contract tests — it must honor the PageSource interface."""

from pathlib import Path

from pagefetch import FakeFetcher, FetchOptions, PageSource


def test_fake_is_a_page_source():
    assert isinstance(FakeFetcher(), PageSource)


def test_fetch_returns_mapped_content_and_records_call():
    fake = FakeFetcher(responses={"https://a.test": "<html>A</html>"})
    result = fake.fetch("https://a.test")
    assert result.content == "<html>A</html>"
    assert result.ok is True
    assert result.tier_used == "fake"
    assert fake.calls == ["https://a.test"]


def test_fetch_unmapped_url_is_not_ok():
    fake = FakeFetcher(responses={})
    result = fake.fetch("https://missing.test")
    assert result.content == ""
    assert result.ok is False


def test_fetch_batch_preserves_order():
    fake = FakeFetcher(responses={"u1": "a", "u2": "b"})
    results = fake.fetch_batch(["u2", "u1", "u3"])
    assert [r.url for r in results] == ["u2", "u1", "u3"]
    assert [r.content for r in results] == ["b", "a", ""]


def test_download_bytes_returns_mapped_payload():
    fake = FakeFetcher(binary={"https://img.test": b"\x89PNG..."})
    assert fake.download_bytes("https://img.test") == b"\x89PNG..."
    assert fake.binary_calls == ["https://img.test"]


def test_download_bytes_respects_min_size():
    fake = FakeFetcher(binary={"https://tiny.test": b"xx"})
    assert fake.download_bytes("https://tiny.test", min_size=100) is None


def test_download_bytes_missing_returns_none():
    assert FakeFetcher().download_bytes("https://none.test") is None


def test_screenshot_true_when_mapped(tmp_path: Path):
    fake = FakeFetcher(responses={"https://a.test": "x"})
    assert fake.screenshot("https://a.test", tmp_path / "s.png") is True
    assert fake.screenshot("https://b.test", tmp_path / "s.png") is False


def test_options_are_accepted_but_ignored():
    fake = FakeFetcher(responses={"u": "c"})
    result = fake.fetch("u", FetchOptions())
    assert result.content == "c"
