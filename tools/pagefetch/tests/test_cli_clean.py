"""CLI --clean-cache tests.

Drive `main()` with `--clean-cache` against a temp cache. `_clean_cache`
uses the default CWD-relative FileCache, so the test chdirs into tmp_path
and seeds `.cache/pagefetch` there.
"""

import os

import pytest

from pagefetch import ContentMode, FileCache
from pagefetch.__main__ import _classify_junk, _make_cache, main


def _seed_default_cache(tmp_path, monkeypatch):
    """Write one good + two junk entries into the CWD-default cache dir.

    Clears PAGEFETCH_CACHE_DIR and chdirs into tmp_path so the CLI's default
    FileCache() resolves to this temp cache — not the project cache (which a
    leaked env var would otherwise point it at)."""
    monkeypatch.delenv("PAGEFETCH_CACHE_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    cache = FileCache(cache_dir=tmp_path / ".cache" / "pagefetch")
    cache.write("https://good.test", ContentMode.HTML, "real lens specs here")
    cache.write("https://gone.test", ContentMode.HTML, "<title>404 Not Found</title>")
    cache.write("https://blocked.test", ContentMode.TEXT, "Too Many Requests")
    return cache


def test_classify_junk_labels():
    assert _classify_junk("real content") is None
    assert _classify_junk("Too Many Requests") == "bot-blocked"
    assert _classify_junk("<title>404 Not Found</title>") == "404/error"


def test_clean_cache_removes_only_junk(tmp_path, monkeypatch):
    cache = _seed_default_cache(tmp_path, monkeypatch)
    monkeypatch.setattr("sys.argv", ["pagefetch", "--clean-cache"])

    main()

    assert cache.read("https://good.test", ContentMode.HTML) == "real lens specs here"
    assert cache.read("https://gone.test", ContentMode.HTML) is None
    assert cache.read("https://blocked.test", ContentMode.TEXT) is None


def test_clean_cache_dry_run_keeps_everything(tmp_path, monkeypatch, capsys):
    cache = _seed_default_cache(tmp_path, monkeypatch)
    monkeypatch.setattr("sys.argv", ["pagefetch", "--clean-cache", "--dry-run"])

    main()

    # Nothing deleted.
    assert cache.read("https://gone.test", ContentMode.HTML) is not None
    assert cache.read("https://blocked.test", ContentMode.TEXT) is not None
    # Reports what it would do.
    err = capsys.readouterr().err
    assert "would remove 2 junk entries" in err
    assert "kept 1" in err


# --- --cache-dir flag ------------------------------------------------


def test_cache_dir_flag_overrides_env(monkeypatch, tmp_path):
    # CLI --cache-dir beats $PAGEFETCH_CACHE_DIR (precedence CLI > env).
    monkeypatch.setenv("PAGEFETCH_CACHE_DIR", str(tmp_path / "fromenv"))
    cli_dir = tmp_path / "fromcli"
    cache = _make_cache(["pagefetch", "https://x.test", "--cache-dir", str(cli_dir)])
    assert cache.cache_dir == cli_dir


def test_no_cache_dir_flag_falls_through_to_env(monkeypatch, tmp_path):
    monkeypatch.setenv("PAGEFETCH_CACHE_DIR", str(tmp_path / "fromenv"))
    cache = _make_cache(["pagefetch", "https://x.test"])
    assert cache.cache_dir == tmp_path / "fromenv"


def test_clean_cache_targets_cache_dir_flag(tmp_path, monkeypatch):
    # --clean-cache --cache-dir sweeps the named dir, not the CWD default.
    monkeypatch.delenv("PAGEFETCH_CACHE_DIR", raising=False)
    target = tmp_path / "target"
    cache = FileCache(cache_dir=target)
    cache.write("https://gone.test", ContentMode.HTML, "<title>404 Not Found</title>")
    cache.write("https://good.test", ContentMode.HTML, "real lens specs here")

    monkeypatch.setattr(
        "sys.argv", ["pagefetch", "--clean-cache", "--cache-dir", str(target)]
    )
    main()

    assert cache.read("https://gone.test", ContentMode.HTML) is None
    assert cache.read("https://good.test", ContentMode.HTML) == "real lens specs here"


def test_invalid_cache_dir_flag_exits_with_error(tmp_path, monkeypatch, capsys):
    a_file = tmp_path / "f.txt"
    a_file.write_text("x", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv", ["pagefetch", "https://x.test", "--cache-dir", str(a_file)]
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    assert "not a directory" in capsys.readouterr().err
