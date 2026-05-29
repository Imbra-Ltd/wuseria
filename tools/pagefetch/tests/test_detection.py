"""Bot-detection tests — one per pattern plus the meta-refresh case."""

import pytest

from pagefetch import (
    is_bot_blocked,
    is_cacheable_junk,
    is_error_page,
    looks_like_real_content,
)
from pagefetch.detection import (
    BOT_DETECTION_PATTERNS,
    ERROR_PAGE_PATTERNS,
    MIN_REAL_CONTENT_BYTES,
    html_to_text,
)

REAL_PAGE = "<html><body>" + ("Lorem ipsum lens specs. " * 100) + "</body></html>"
# A real content page comfortably above the size floor.
BIG_REAL_PAGE = "<html><body>" + ("Lorem ipsum lens specs. " * 1000) + "</body></html>"


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
        "<title>429 Too Many Requests</title>",
        "Too Many Requests",
        "Rate limit exceeded",
        "Our systems have detected unusual traffic",
        "We detected a translation service and are reloading",
        '<script src="/cdn-cgi/challenge-platform/h/b/orchestrate"></script>',
        '<div id="cf-challenge-running">',
        '<div id="px-captcha">',
        "_pxhd=abc123",
    ],
)
def test_each_bot_pattern_is_detected(snippet):
    html = f"<html><body>{snippet}</body></html>"
    assert is_bot_blocked(html) is True


def test_patterns_list_is_covered_by_parametrization():
    # Guard: if a new pattern is added, the parametrized test above must grow.
    assert len(BOT_DETECTION_PATTERNS) == 19


def test_html_to_text_strips_scripts_styles_and_tags():
    html = (
        "<html><head><style>.a{color:red}</style>"
        "<script>var x=1;</script></head>"
        "<body><p>Hello   world</p></body></html>"
    )
    assert html_to_text(html) == "Hello world"


# --- looks_like_real_content -----------------------------------------


def test_big_real_page_is_real_content():
    assert looks_like_real_content(BIG_REAL_PAGE) is True


def test_bot_blocked_page_is_not_real_content():
    # Recognized bot page fails regardless of size.
    big_bot_page = "Too Many Requests" + ("x" * 20000)
    assert looks_like_real_content(big_bot_page) is False


def test_short_page_is_not_real_content():
    # A throttle/error stub below the floor is rejected even with no
    # recognizable bot text (the B&H ~7-8 KB throttle-page case).
    stub = "<html><body>" + ("x" * 7700) + "</body></html>"
    assert len(stub) < MIN_REAL_CONTENT_BYTES
    assert looks_like_real_content(stub) is False


def test_min_bytes_threshold_is_configurable():
    page = "<html>" + ("x" * 2000) + "</html>"
    assert looks_like_real_content(page, min_bytes=10_000) is False
    assert looks_like_real_content(page, min_bytes=1_000) is True


def test_big_real_page_is_not_an_error_page():
    assert is_error_page(BIG_REAL_PAGE) is False


@pytest.mark.parametrize(
    "snippet",
    [
        "<title>404 Not Found</title>",
        "<title>Page Not Found</title>",
        "<title>410 Gone</title>",
        "<h1>404 error</h1>",
        "<p>Page Not Found</p>",
        "The page you requested could not be found",
        "This product is no longer available",
        "This item is no longer available for purchase",
        "This model has been discontinued",
    ],
)
def test_each_error_pattern_is_detected(snippet):
    html = f"<html><body>{snippet}</body></html>"
    assert is_error_page(html) is True


def test_error_patterns_list_is_covered_by_parametrization():
    # Guard: if a new error pattern is added, the parametrized test must grow.
    assert len(ERROR_PAGE_PATTERNS) == 9


def test_error_page_even_when_large_is_not_real_content():
    # A soft-404 served as a big HTTP-200 page is still not real content.
    soft_404 = "<title>Page Not Found</title>" + ("filler " * 5000)
    assert len(soft_404) >= MIN_REAL_CONTENT_BYTES
    assert is_error_page(soft_404) is True
    assert looks_like_real_content(soft_404) is False


# --- is_cacheable_junk -----------------------------------------------


def test_real_page_is_not_cacheable_junk():
    assert is_cacheable_junk(BIG_REAL_PAGE) is False


def test_bot_page_is_cacheable_junk():
    assert is_cacheable_junk("<body>Too Many Requests</body>") is True


def test_error_page_is_cacheable_junk():
    assert is_cacheable_junk("<title>404 Not Found</title>") is True
