"""Fetch a web page using Playwright (headless Chromium) and print its text content.

Usage:
    py scripts/fetch-page.py <url>
    py scripts/fetch-page.py <url> --html        # print raw HTML instead of text
    py scripts/fetch-page.py <url> --wait 5000    # wait N ms after load (for JS rendering)
"""

import sys
from playwright.sync_api import sync_playwright


def fetch_page(url: str, raw_html: bool = False, wait_ms: int = 2000) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(wait_ms)

        if raw_html:
            content = page.content()
        else:
            content = page.inner_text("body")

        browser.close()
        return content


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    url = sys.argv[1]
    raw_html = "--html" in sys.argv
    wait_ms = 2000

    if "--wait" in sys.argv:
        idx = sys.argv.index("--wait")
        if idx + 1 < len(sys.argv):
            wait_ms = int(sys.argv[idx + 1])

    content = fetch_page(url, raw_html, wait_ms)
    sys.stdout.buffer.write(content.encode("utf-8", errors="replace"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
