"""NetworkFetcher escalation tests.

The four transport tier methods are stubbed so no real network or browser
is touched. We assert the ORDER in which tiers are attempted under each
scenario — this is the core escalation contract.
"""

import pytest

from pagefetch import ContentMode, FetchOptions, NetworkFetcher, Transport
from pagefetch.network import _BOT_BLOCKED


@pytest.fixture
def fetcher(cache):
    return NetworkFetcher(cache=cache)


def _stub_tiers(fetcher, monkeypatch, urllib_result, pw=None, nd=None, uc=None):
    """Replace the four tier methods with recording stubs.

    urllib_result: what _fetch_urllib returns (content / _BOT_BLOCKED / None).
    pw/nd/uc: what each browser tier returns ("" or content).
    Returns the list that records call order.
    """
    calls: list[str] = []

    def fake_urllib(url, mode):
        calls.append("urllib")
        return urllib_result

    def fake_pw(url, mode, wait_ms):
        calls.append("playwright")
        return pw

    def fake_nd(url, mode, wait_ms):
        calls.append("nodriver")
        return nd

    def fake_uc(url, mode, wait_ms):
        calls.append("uc")
        return uc

    monkeypatch.setattr(fetcher, "_fetch_urllib", fake_urllib)
    monkeypatch.setattr(fetcher, "_fetch_playwright", fake_pw)
    monkeypatch.setattr(fetcher, "_fetch_nodriver", fake_nd)
    monkeypatch.setattr(fetcher, "_fetch_uc", fake_uc)
    return calls


def test_urllib_success_does_not_escalate(fetcher, monkeypatch):
    calls = _stub_tiers(fetcher, monkeypatch, urllib_result="real content")
    result = fetcher.fetch("https://x.test", FetchOptions(use_cache=False))
    assert calls == ["urllib"]
    assert result.tier_used == "urllib"
    assert result.content == "real content"
    assert result.ok is True


def test_bot_blocked_skips_playwright_goes_to_nodriver(fetcher, monkeypatch):
    calls = _stub_tiers(
        fetcher, monkeypatch, urllib_result=_BOT_BLOCKED, nd="from nodriver"
    )
    result = fetcher.fetch("https://x.test", FetchOptions(use_cache=False))
    assert calls == ["urllib", "nodriver"]  # playwright NOT called
    assert "playwright" not in calls
    assert result.tier_used == "nodriver"


def test_bot_blocked_nodriver_fails_falls_to_uc(fetcher, monkeypatch):
    calls = _stub_tiers(
        fetcher, monkeypatch, urllib_result=_BOT_BLOCKED, nd="", uc="from uc"
    )
    result = fetcher.fetch("https://x.test", FetchOptions(use_cache=False))
    assert calls == ["urllib", "nodriver", "uc"]
    assert result.tier_used == "uc"


def test_non_bot_failure_escalates_playwright_then_nodriver_then_uc(fetcher, monkeypatch):
    calls = _stub_tiers(
        fetcher, monkeypatch, urllib_result=None, pw="", nd="", uc="from uc"
    )
    result = fetcher.fetch("https://x.test", FetchOptions(use_cache=False))
    assert calls == ["urllib", "playwright", "nodriver", "uc"]
    assert result.tier_used == "uc"


def test_non_bot_failure_playwright_succeeds_stops_there(fetcher, monkeypatch):
    calls = _stub_tiers(fetcher, monkeypatch, urllib_result=None, pw="from pw")
    result = fetcher.fetch("https://x.test", FetchOptions(use_cache=False))
    assert calls == ["urllib", "playwright"]
    assert result.tier_used == "playwright"


def test_all_tiers_fail_returns_not_ok(fetcher, monkeypatch):
    calls = _stub_tiers(
        fetcher, monkeypatch, urllib_result=None, pw="", nd="", uc=""
    )
    result = fetcher.fetch("https://x.test", FetchOptions(use_cache=False))
    assert calls == ["urllib", "playwright", "nodriver", "uc"]
    assert result.ok is False
    assert result.tier_used == "none"
    assert result.content == ""


def test_force_uc_uses_only_uc(fetcher, monkeypatch):
    calls = _stub_tiers(fetcher, monkeypatch, urllib_result="x", uc="uc only")
    result = fetcher.fetch(
        "https://x.test", FetchOptions(transport=Transport.UC, use_cache=False)
    )
    assert calls == ["uc"]
    assert result.tier_used == "uc"


def test_force_nodriver_uses_only_nodriver(fetcher, monkeypatch):
    calls = _stub_tiers(fetcher, monkeypatch, urllib_result="x", nd="nd only")
    result = fetcher.fetch(
        "https://x.test", FetchOptions(transport=Transport.NODRIVER, use_cache=False)
    )
    assert calls == ["nodriver"]


def test_force_playwright_uses_only_playwright(fetcher, monkeypatch):
    calls = _stub_tiers(fetcher, monkeypatch, urllib_result="x", pw="pw only")
    result = fetcher.fetch(
        "https://x.test", FetchOptions(transport=Transport.PLAYWRIGHT, use_cache=False)
    )
    assert calls == ["playwright"]


def test_cache_hit_skips_all_tiers(fetcher, monkeypatch, cache):
    cache.write("https://x.test", ContentMode.TEXT, "cached!")
    calls = _stub_tiers(fetcher, monkeypatch, urllib_result="should not be used")
    result = fetcher.fetch("https://x.test", FetchOptions(use_cache=True))
    assert calls == []
    assert result.tier_used == "cache"
    assert result.content == "cached!"


def test_successful_fetch_is_written_to_cache(fetcher, monkeypatch, cache):
    _stub_tiers(fetcher, monkeypatch, urllib_result="fresh")
    fetcher.fetch("https://x.test", FetchOptions(use_cache=True))
    assert cache.read("https://x.test", ContentMode.TEXT) == "fresh"
