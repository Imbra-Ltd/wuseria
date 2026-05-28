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
