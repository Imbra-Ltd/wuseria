"""Bot-detection tests — one per pattern plus the meta-refresh case."""

import pytest

from pagefetch import is_bot_blocked
from pagefetch.detection import BOT_DETECTION_PATTERNS, html_to_text

REAL_PAGE = "<html><body>" + ("Lorem ipsum lens specs. " * 100) + "</body></html>"


def test_real_page_is_not_blocked():
    assert is_bot_blocked(REAL_PAGE) is False


def test_short_meta_refresh_is_blocked():
    html = '<html><head><meta http-equiv="refresh" content="0;url=/x"></head></html>'
    assert is_bot_blocked(html) is True


def test_long_page_with_meta_refresh_is_not_short_circuited():
    # The meta-refresh short-circuit only fires under 500 bytes.
    html = '<meta refresh>' + ("x" * 600)
    assert is_bot_blocked(html) is False


@pytest.mark.parametrize(
    "snippet",
    [
        "<title>403 Forbidden</title>",
        "<title>Access Denied</title>",
        "Checking your browser before accessing",
        "Checking the site connection security",
        "Enable JavaScript and cookies to continue",
        "Attention Required! | Cloudflare",
        "Just a moment...",
        "Verifying you are human",
        "Please allow cookies",
        "This page requires cookies to be enabled",
    ],
)
def test_each_bot_pattern_is_detected(snippet):
    html = f"<html><body>{snippet}</body></html>"
    assert is_bot_blocked(html) is True


def test_patterns_list_is_covered_by_parametrization():
    # Guard: if a new pattern is added, the parametrized test above must grow.
    assert len(BOT_DETECTION_PATTERNS) == 10


def test_html_to_text_strips_scripts_styles_and_tags():
    html = (
        "<html><head><style>.a{color:red}</style>"
        "<script>var x=1;</script></head>"
        "<body><p>Hello   world</p></body></html>"
    )
    assert html_to_text(html) == "Hello world"
