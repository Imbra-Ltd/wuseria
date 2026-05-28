"""Bot-protection detection.

Pure functions that decide whether a fetched response is a bot-detection
interstitial (Cloudflare, captcha, 403 page) rather than real content.
This drives the escalation decision in NetworkFetcher: a urllib response
that looks bot-blocked skips Playwright and goes straight to a real
browser tier.
"""

import re

# Patterns that indicate bot protection (triggers escalation).
BOT_DETECTION_PATTERNS = [
    r"<title>403\b",
    r"<title>Access Denied",
    r"Checking your browser",
    r"Checking the site connection security",
    r"Enable JavaScript and cookies to continue",
    r"Attention Required.*Cloudflare",
    r"Just a moment\.\.\.",
    r"Verifying you are human",
    r"Please allow cookies",
    r"This page requires cookies to be enabled",
]


def is_bot_blocked(html: str) -> bool:
    """Return True if the response HTML looks like a bot-detection page."""
    # Very short HTML with a meta-refresh is a captcha redirect.
    if len(html) < 500 and "meta" in html and "refresh" in html.lower():
        return True
    # Strip tags for pattern matching — bot pages embed text in JS/CSS-heavy
    # wrappers, so check both the raw head and the de-tagged text.
    text = re.sub(r"<[^>]+>", " ", html[:20000])
    for pattern in BOT_DETECTION_PATTERNS:
        if re.search(pattern, html[:5000], re.IGNORECASE):
            return True
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def html_to_text(html: str) -> str:
    """Strip script/style/tags and collapse whitespace to plain text."""
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()
