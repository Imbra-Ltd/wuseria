"""Fetch a web page using Playwright (headless Chromium) and print its text content.

Caches responses locally in .cache/fetch/ to avoid repeated HTTP requests.

Usage:
    py scripts/fetch-page.py <url>
    py scripts/fetch-page.py <url> --html        # print raw HTML instead of text
    py scripts/fetch-page.py <url> --wait 5000    # wait N ms after load (for JS rendering)
    py scripts/fetch-page.py <url> --no-cache     # bypass cache, fetch fresh
"""

import hashlib
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache" / "fetch"


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def cache_key(url: str, raw_html: bool) -> Path:
    suffix = ".html" if raw_html else ".txt"
    return CACHE_DIR / (url_hash(url) + suffix)


def screenshot_path(url: str) -> Path:
    return CACHE_DIR / (url_hash(url) + ".png")


def read_cache(url: str, raw_html: bool) -> str | None:
    path = cache_key(url, raw_html)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def write_cache(url: str, raw_html: bool, content: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = cache_key(url, raw_html)
    path.write_text(content, encoding="utf-8")


def fetch_page(
    url: str, raw_html: bool = False, wait_ms: int = 2000
) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
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

        # Scroll through the page to trigger lazy-loaded images
        page.evaluate("""async () => {
            const delay = ms => new Promise(r => setTimeout(r, ms));
            const height = document.body.scrollHeight;
            const step = window.innerHeight;
            for (let y = 0; y < height; y += step) {
                window.scrollTo(0, y);
                await delay(200);
            }
            window.scrollTo(0, 0);
            await delay(500);
        }""")

        if raw_html:
            content = page.content()
        else:
            content = page.inner_text("body")

        png = screenshot_path(url)
        if not png.exists():
            page.screenshot(path=str(png), full_page=True)

        browser.close()
        return content


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    url = sys.argv[1]
    raw_html = "--html" in sys.argv
    no_cache = "--no-cache" in sys.argv
    wait_ms = 2000

    if "--wait" in sys.argv:
        idx = sys.argv.index("--wait")
        if idx + 1 < len(sys.argv):
            wait_ms = int(sys.argv[idx + 1])

    if not no_cache:
        cached = read_cache(url, raw_html)
        if cached is not None:
            sys.stdout.buffer.write(cached.encode("utf-8", errors="replace"))
            sys.stdout.buffer.write(b"\n")
            return

    content = fetch_page(url, raw_html, wait_ms)
    write_cache(url, raw_html, content)
    sys.stdout.buffer.write(content.encode("utf-8", errors="replace"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
