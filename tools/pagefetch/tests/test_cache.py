"""FileCache tests — key stability and round-trip.

The key scheme must never change: existing on-disk caches in consuming
projects depend on sha256(url)[:16] + suffix. These tests pin it.
"""

import hashlib

from pagefetch import ContentMode, FileCache


def test_url_hash_is_sha256_first_16_hex():
    url = "https://example.com/lens"
    expected = hashlib.sha256(url.encode()).hexdigest()[:16]
    assert FileCache.url_hash(url) == expected
    assert len(FileCache.url_hash(url)) == 16


def test_key_suffix_depends_on_mode(cache: FileCache):
    url = "https://example.com"
    assert cache.key(url, ContentMode.HTML).suffix == ".html"
    assert cache.key(url, ContentMode.TEXT).suffix == ".txt"


def test_key_filename_is_hash_plus_suffix(cache: FileCache):
    url = "https://example.com"
    key = cache.key(url, ContentMode.HTML)
    assert key.name == FileCache.url_hash(url) + ".html"


def test_write_then_read_round_trips(cache: FileCache):
    url = "https://example.com"
    cache.write(url, ContentMode.HTML, "<html>hi</html>")
    assert cache.read(url, ContentMode.HTML) == "<html>hi</html>"


def test_read_missing_returns_none(cache: FileCache):
    assert cache.read("https://nope.example", ContentMode.TEXT) is None


def test_modes_do_not_collide(cache: FileCache):
    url = "https://example.com"
    cache.write(url, ContentMode.HTML, "html-content")
    cache.write(url, ContentMode.TEXT, "text-content")
    assert cache.read(url, ContentMode.HTML) == "html-content"
    assert cache.read(url, ContentMode.TEXT) == "text-content"


def test_default_cache_dir_is_portable():
    # Must not be tied to any project layout — CWD-relative default.
    assert FileCache().cache_dir.name == "pagefetch"


# --- delete / entries / clean ----------------------------------------


def test_delete_removes_entry_and_is_idempotent(cache: FileCache):
    url = "https://example.com"
    cache.write(url, ContentMode.HTML, "<html>hi</html>")
    assert cache.delete(url, ContentMode.HTML) is True
    assert cache.read(url, ContentMode.HTML) is None
    # Second delete is a no-op, not an error.
    assert cache.delete(url, ContentMode.HTML) is False


def test_entries_lists_bodies_excluding_screenshots(cache: FileCache):
    cache.write("https://a.test", ContentMode.HTML, "a")
    cache.write("https://b.test", ContentMode.TEXT, "b")
    # A .png screenshot must not be treated as a page body.
    cache.cache_dir.mkdir(parents=True, exist_ok=True)
    cache.screenshot_path("https://a.test").write_bytes(b"\x89PNG")
    suffixes = sorted(p.suffix for p in cache.entries())
    assert suffixes == [".html", ".txt"]


def test_entries_empty_when_no_cache_dir(tmp_path):
    assert FileCache(cache_dir=tmp_path / "missing").entries() == []


def test_clean_removes_only_junk_and_reports(cache: FileCache):
    cache.write("https://good.test", ContentMode.HTML, "real lens specs")
    cache.write("https://bad.test", ContentMode.HTML, "junk page")

    def classify(body: str) -> str | None:
        return "junk" if "junk" in body else None

    report = cache.clean(classify)
    assert report.kept == 1
    assert len(report.removed) == 1
    assert report.removed[0][1] == "junk"
    assert cache.read("https://good.test", ContentMode.HTML) == "real lens specs"
    assert cache.read("https://bad.test", ContentMode.HTML) is None


def test_clean_dry_run_deletes_nothing(cache: FileCache):
    cache.write("https://bad.test", ContentMode.HTML, "junk page")

    report = cache.clean(lambda body: "junk" if "junk" in body else None, dry_run=True)
    assert report.dry_run is True
    assert len(report.removed) == 1
    # File still present — dry run only reports.
    assert cache.read("https://bad.test", ContentMode.HTML) == "junk page"
