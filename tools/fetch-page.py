"""Fetch a web page and print its text content.

Four-tier fetching strategy (auto-escalates on failure):
  1. urllib (plain HTTP) — fastest (~1s), works for most static pages
  2. Playwright (headless Chromium) — for JS-rendered pages (~5-9s)
  3. Nodriver (headed Chrome via CDP) — for bot-protected sites (~6-8s)
  4. SeleniumBase UC mode — fallback for headless bot bypass (~18-24s)

Auto mode tries urllib first. If bot protection is detected (captcha,
403 page), skips Playwright and goes to Nodriver. If urllib fails for
other reasons (404, timeout), tries Playwright first then Nodriver/UC.

Batch mode keeps one browser session open for all URLs.

Caches responses locally in .cache/fetch/ to avoid repeated requests.

Usage:
    py tools/fetch-page.py <url>                          # single URL, auto mode
    py tools/fetch-page.py <url> --html                   # raw HTML output
    py tools/fetch-page.py <url> --js                     # force Playwright
    py tools/fetch-page.py <url> --nodriver               # force Nodriver (headed)
    py tools/fetch-page.py <url> --uc                     # force SeleniumBase UC
    py tools/fetch-page.py <url> --wait 5000              # extra wait (ms)
    py tools/fetch-page.py <url> --no-cache               # bypass cache

    py tools/fetch-page.py --batch urls.txt               # batch from file
    py tools/fetch-page.py --batch urls.txt --nodriver    # batch with Nodriver
    py tools/fetch-page.py --batch urls.txt --output-dir out/  # save to files
    py tools/fetch-page.py url1 url2 url3                 # batch from args
    echo url | py tools/fetch-page.py --batch -           # batch from stdin
"""

import atexit
import hashlib
import os
import re
import signal
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Track Chrome PIDs spawned by this process for cleanup
_spawned_chrome_pids: set[int] = set()


def _get_chrome_pids() -> set[int]:
    """Get all chrome.exe PIDs currently running (Windows only)."""
    pids = set()
    try:
        import subprocess
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.strip().splitlines():
            parts = line.strip('"').split('","')
            if len(parts) >= 2:
                try:
                    pids.add(int(parts[1]))
                except ValueError:
                    pass
    except Exception:
        pass
    return pids


def _cleanup_chrome() -> None:
    """Kill Chrome processes that were spawned by this script."""
    if not _spawned_chrome_pids:
        return
    still_running = _get_chrome_pids() & _spawned_chrome_pids
    for pid in still_running:
        try:
            os.kill(pid, signal.SIGTERM)
        except (OSError, ProcessLookupError):
            pass
    if still_running:
        print(f"[cleanup] Killed {len(still_running)} orphaned Chrome process(es)", file=sys.stderr)


atexit.register(_cleanup_chrome)

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache" / "fetch"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

# Patterns that indicate bot protection (triggers escalation)
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


def _is_bot_blocked(html: str) -> bool:
    """Check if the response HTML looks like a bot-detection page."""
    # Very short HTML with meta-refresh is a captcha redirect
    if len(html) < 500 and "meta" in html and "refresh" in html.lower():
        return True
    # Strip tags for pattern matching (bot pages embed text in JS/CSS-heavy wrappers)
    text = re.sub(r"<[^>]+>", " ", html[:20000])
    for pattern in BOT_DETECTION_PATTERNS:
        if re.search(pattern, html[:5000], re.IGNORECASE):
            return True
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def _scroll_page_js() -> str:
    """JavaScript snippet to scroll through a page for lazy-loaded content."""
    return """async () => {
        const delay = ms => new Promise(r => setTimeout(r, ms));
        const height = document.body.scrollHeight;
        const step = window.innerHeight;
        for (let y = 0; y < height; y += step) {
            window.scrollTo(0, y);
            await delay(200);
        }
        window.scrollTo(0, 0);
        await delay(500);
    }"""


# --- Tier 1: urllib (plain HTTP) ---


# Sentinel: urllib detected bot protection (skip Playwright, go to UC)
_BOT_BLOCKED = "@@BOT_BLOCKED@@"


def fetch_urllib(url: str, raw_html: bool) -> str | None:
    """Fetch via plain urllib. Returns content, _BOT_BLOCKED sentinel, or None."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        print(f"[urllib] HTTP {e.code}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[urllib] {e}", file=sys.stderr)
        return None

    if _is_bot_blocked(html):
        print("[urllib] Bot protection detected", file=sys.stderr)
        return _BOT_BLOCKED

    if raw_html:
        return html

    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# --- Tier 2: Playwright (headless Chromium) ---


def fetch_playwright(url: str, raw_html: bool, wait_ms: int = 500) -> str | None:
    """Fetch a page via Playwright. Returns content or None on failure.

    Uses domcontentloaded (not networkidle) — 2-3s faster on ad-heavy pages.
    For pages needing extra JS time, pass --wait to increase the post-load delay.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[playwright] Not installed", file=sys.stderr)
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=USER_AGENT)
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(wait_ms)
            page.evaluate(_scroll_page_js())

            html = page.content()
            if _is_bot_blocked(html):
                print("[playwright] Bot detection page received", file=sys.stderr)
                browser.close()
                return None

            if raw_html:
                content = html
            else:
                content = page.inner_text("body")

            png = screenshot_path(url)
            if not png.exists():
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(png), full_page=True)

            browser.close()
            return content
    except Exception as e:
        print(f"[playwright] {e}", file=sys.stderr)
        return None


# --- Tier 3: Nodriver (headed Chrome via CDP) ---


def fetch_nodriver(url: str, raw_html: bool, wait_ms: int = 500) -> str | None:
    """Fetch a page via Nodriver (headed Chrome, no driver binary).

    Nodriver connects directly to Chrome via CDP WebSocket — no
    ChromeDriver binary to fingerprint. Requires headed mode (a Chrome
    window opens briefly). Faster than SeleniumBase UC (~6-8s vs ~18-24s).
    """
    try:
        import nodriver as uc_nd
    except ImportError:
        print("[nodriver] Not installed", file=sys.stderr)
        return None

    import asyncio

    async def _fetch() -> str | None:
        browser = None
        try:
            pids_before = _get_chrome_pids()
            browser = await uc_nd.start(headless=False)
            _spawned_chrome_pids.update(_get_chrome_pids() - pids_before)
            page = await browser.get(url)

            # Event-driven wait: poll readyState then check bot detection
            import time as _time

            deadline = _time.monotonic() + 15
            while _time.monotonic() < deadline:
                try:
                    ready = await page.evaluate("document.readyState")
                    if ready == "complete":
                        break
                except Exception:
                    pass
                await page.sleep(0.3)

            # Check for bot protection with backoff
            interval = 0.5
            while _time.monotonic() < deadline:
                html = await page.get_content()
                if not _is_bot_blocked(html):
                    break
                await page.sleep(interval)
                interval = min(interval * 1.5, 2.0)
            else:
                print("[nodriver] Bot detection page still present", file=sys.stderr)
                return None

            if wait_ms > 500:
                await page.sleep(wait_ms / 1000)

            # Scroll for lazy content
            try:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.sleep(0.5)
            except Exception:
                pass

            html = await page.get_content()
            if _is_bot_blocked(html):
                print("[nodriver] Bot detection page still present", file=sys.stderr)
                return None

            if raw_html:
                return html

            text = re.sub(r"<[^>]+>", " ", html)
            text = re.sub(r"\s+", " ", text).strip()
            return text
        except Exception as e:
            print(f"[nodriver] {e}", file=sys.stderr)
            return None
        finally:
            if browser:
                browser.stop()

    try:
        return asyncio.run(_fetch())
    except Exception as e:
        print(f"[nodriver] {e}", file=sys.stderr)
        return None


async def _nodriver_fetch_with_browser(browser, url: str, raw_html: bool, wait_ms: int = 500) -> str | None:
    """Fetch a page using an existing Nodriver browser (batch mode)."""
    import time as _time

    try:
        page = await browser.get(url)

        deadline = _time.monotonic() + 15
        while _time.monotonic() < deadline:
            try:
                ready = await page.evaluate("document.readyState")
                if ready == "complete":
                    break
            except Exception:
                pass
            await page.sleep(0.3)

        interval = 0.5
        while _time.monotonic() < deadline:
            html = await page.get_content()
            if not _is_bot_blocked(html):
                break
            await page.sleep(interval)
            interval = min(interval * 1.5, 2.0)
        else:
            print("[nodriver] Bot detection page still present", file=sys.stderr)
            return None

        if wait_ms > 500:
            await page.sleep(wait_ms / 1000)

        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.sleep(0.5)
        except Exception:
            pass

        html = await page.get_content()
        if _is_bot_blocked(html):
            print("[nodriver] Bot detection page still present", file=sys.stderr)
            return None

        if raw_html:
            return html

        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    except Exception as e:
        print(f"[nodriver] {e}", file=sys.stderr)
        return None


# --- Tier 4: SeleniumBase UC mode ---


def _uc_wait_for_page(sb, timeout_s: int = 15) -> bool:
    """Wait for a real page to load past any bot protection interstitial.

    Two phases:
    1. Wait for document.readyState === "complete" (cheap JS call)
    2. Once ready, check page source for bot detection (expensive, done once)
       If still blocked, poll with increasing intervals until timeout.

    Returns True if a real page loaded, False on timeout.
    """
    import time

    deadline = time.monotonic() + timeout_s

    # Phase 1: wait for readyState (fast polling, cheap call)
    while time.monotonic() < deadline:
        try:
            if sb.execute_script("return document.readyState") == "complete":
                break
        except Exception:
            pass
        sb.sleep(0.3)

    # Phase 2: check for bot protection (poll with backoff)
    interval = 0.5
    while time.monotonic() < deadline:
        try:
            html = sb.get_page_source()
            if not _is_bot_blocked(html):
                return True
        except Exception:
            pass
        sb.sleep(interval)
        interval = min(interval * 1.5, 2.0)

    return False


def _uc_wait_for_scroll(sb, timeout_s: int = 3) -> None:
    """Scroll to bottom and wait for DOM height to stabilize (lazy content)."""
    import time

    try:
        prev_height = sb.execute_script(
            "return document.body ? document.body.scrollHeight : 0"
        )
        if not prev_height:
            return
        sb.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            sb.sleep(0.3)
            new_height = sb.execute_script("return document.body.scrollHeight")
            if new_height == prev_height:
                return
            prev_height = new_height
            sb.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    except Exception:
        pass


def _fetch_uc_with_session(sb, url: str, raw_html: bool, wait_ms: int = 500) -> str | None:
    """Fetch a page using an existing SeleniumBase UC session."""
    try:
        sb.open(url)

        if not _uc_wait_for_page(sb):
            print("[uc] Bot detection page still present after timeout", file=sys.stderr)
            return None

        if wait_ms > 500:
            sb.sleep(wait_ms / 1000)

        _uc_wait_for_scroll(sb)

        html = sb.get_page_source()
        if _is_bot_blocked(html):
            print("[uc] Bot detection page still present", file=sys.stderr)
            return None

        if raw_html:
            return html

        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    except Exception as e:
        print(f"[uc] {e}", file=sys.stderr)
        return None


def fetch_uc(url: str, raw_html: bool, wait_ms: int = 500) -> str | None:
    """Fetch a page via SeleniumBase UC mode (bot bypass). Returns content or None.

    Launches a new Chrome session for a single page. For batch operations,
    use _fetch_uc_with_session() with a shared SB instance.
    """
    try:
        from seleniumbase import SB
    except ImportError:
        print("[uc] SeleniumBase not installed", file=sys.stderr)
        return None

    try:
        pids_before = _get_chrome_pids()
        with SB(uc=True, headless=True) as sb:
            _spawned_chrome_pids.update(_get_chrome_pids() - pids_before)
            return _fetch_uc_with_session(sb, url, raw_html, wait_ms)
    except Exception as e:
        print(f"[uc] {e}", file=sys.stderr)
        return None



def _fetch_single(
    url: str, raw_html: bool, wait_ms: int,
    force_js: bool, force_nodriver: bool, force_uc: bool, no_cache: bool,
    sb_session=None, nd_browser=None,
) -> str:
    """Fetch a single URL. Shared by single and batch modes."""
    if not no_cache:
        cached = read_cache(url, raw_html)
        if cached is not None:
            return cached

    content = ""

    if force_uc:
        if sb_session:
            content = _fetch_uc_with_session(sb_session, url, raw_html, wait_ms) or ""
        else:
            content = fetch_uc(url, raw_html, wait_ms) or ""
    elif force_nodriver:
        if nd_browser:
            import asyncio
            content = asyncio.get_event_loop().run_until_complete(
                _nodriver_fetch_with_browser(nd_browser, url, raw_html, wait_ms)
            ) or ""
        else:
            content = fetch_nodriver(url, raw_html, wait_ms) or ""
    elif force_js:
        content = fetch_playwright(url, raw_html, wait_ms) or ""
    else:
        # Auto mode: try urllib first, then escalate
        result = fetch_urllib(url, raw_html)
        if result and result != _BOT_BLOCKED:
            content = result
        elif result == _BOT_BLOCKED:
            # Bot protection: skip Playwright, try Nodriver then UC
            print("[auto] Skipping Playwright (bot protection), trying Nodriver...", file=sys.stderr)
            if nd_browser:
                import asyncio
                content = asyncio.get_event_loop().run_until_complete(
                    _nodriver_fetch_with_browser(nd_browser, url, raw_html, wait_ms)
                ) or ""
            else:
                content = fetch_nodriver(url, raw_html, wait_ms) or ""
            if not content:
                print("[auto] Nodriver failed, escalating to UC...", file=sys.stderr)
                if sb_session:
                    content = _fetch_uc_with_session(sb_session, url, raw_html, wait_ms) or ""
                else:
                    content = fetch_uc(url, raw_html, wait_ms) or ""
        else:
            # Non-bot failure (404, timeout): try Playwright then Nodriver then UC
            print("[auto] Escalating to Playwright...", file=sys.stderr)
            content = fetch_playwright(url, raw_html, wait_ms) or ""
            if not content:
                print("[auto] Escalating to Nodriver...", file=sys.stderr)
                content = fetch_nodriver(url, raw_html, wait_ms) or ""
            if not content:
                print("[auto] Escalating to UC...", file=sys.stderr)
                if sb_session:
                    content = _fetch_uc_with_session(sb_session, url, raw_html, wait_ms) or ""
                else:
                    content = fetch_uc(url, raw_html, wait_ms) or ""

    if content:
        write_cache(url, raw_html, content)
    return content


def _run_batch(
    urls: list[str], raw_html: bool, wait_ms: int,
    force_js: bool, force_nodriver: bool, force_uc: bool, no_cache: bool,
    output_dir: str | None,
) -> None:
    """Fetch multiple URLs with a persistent browser session.

    Browser launches once and stays open for all pages. Nodriver batch
    uses async event loop; UC batch uses sync SB session.

    Output goes to --output-dir (one file per URL) or stdout (separated
    by delimiter lines).
    """
    import asyncio
    import time

    out_path = Path(output_dir) if output_dir else None
    if out_path:
        out_path.mkdir(parents=True, exist_ok=True)

    # Determine which persistent session to use
    needs_nodriver = force_nodriver
    needs_uc = force_uc
    if not needs_nodriver and not needs_uc and not force_js and urls:
        result = fetch_urllib(urls[0], raw_html)
        if result == _BOT_BLOCKED:
            needs_nodriver = True  # Prefer Nodriver for bot-protected batch

    nd_browser = None
    sb_session = None
    sb_context = None
    loop = None

    if needs_nodriver:
        try:
            import nodriver as uc_nd
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            pids_before = _get_chrome_pids()
            nd_browser = loop.run_until_complete(uc_nd.start(headless=False))
            _spawned_chrome_pids.update(_get_chrome_pids() - pids_before)
            print(f"[batch] Persistent Nodriver session started for {len(urls)} URLs", file=sys.stderr)
        except ImportError:
            print("[batch] Nodriver not installed, falling back to UC", file=sys.stderr)
            needs_nodriver = False
            needs_uc = True
        except Exception as e:
            print(f"[batch] Nodriver failed to start: {e}, falling back to UC", file=sys.stderr)
            needs_nodriver = False
            needs_uc = True

    if needs_uc and not nd_browser:
        try:
            from seleniumbase import SB
            pids_before = _get_chrome_pids()
            sb_context = SB(uc=True, headless=True)
            sb_session = sb_context.__enter__()
            _spawned_chrome_pids.update(_get_chrome_pids() - pids_before)
            print(f"[batch] Persistent UC session started for {len(urls)} URLs", file=sys.stderr)
        except ImportError:
            print("[batch] SeleniumBase not installed, falling back to per-URL mode", file=sys.stderr)

    try:
        stats = {"ok": 0, "fail": 0}
        for i, url in enumerate(urls):
            t0 = time.monotonic()
            print(f"[batch] [{i + 1}/{len(urls)}] {url}", file=sys.stderr)

            if nd_browser and (force_nodriver or needs_nodriver):
                content = loop.run_until_complete(
                    _nodriver_fetch_with_browser(nd_browser, url, raw_html, wait_ms)
                ) or ""
            else:
                content = _fetch_single(
                    url, raw_html, wait_ms, force_js, False, force_uc, no_cache,
                    sb_session=sb_session,
                )

            elapsed = time.monotonic() - t0

            if content:
                if not no_cache:
                    write_cache(url, raw_html, content)
                stats["ok"] += 1
                if out_path:
                    fname = url_hash(url) + (".html" if raw_html else ".txt")
                    (out_path / fname).write_text(content, encoding="utf-8")
                    print(f"[batch]   -> {fname} ({len(content)} bytes, {elapsed:.1f}s)", file=sys.stderr)
                else:
                    sys.stdout.buffer.write(f"--- {url} ---\n".encode())
                    sys.stdout.buffer.write(content.encode("utf-8", errors="replace"))
                    sys.stdout.buffer.write(b"\n")
            else:
                stats["fail"] += 1
                print(f"[batch]   FAILED ({elapsed:.1f}s)", file=sys.stderr)

        print(f"[batch] Done: {stats['ok']} ok, {stats['fail']} failed", file=sys.stderr)
    finally:
        if nd_browser:
            nd_browser.stop()
        if sb_context:
            sb_context.__exit__(None, None, None)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    raw_html = "--html" in sys.argv
    no_cache = "--no-cache" in sys.argv
    force_js = "--js" in sys.argv
    force_nodriver = "--nodriver" in sys.argv
    force_uc = "--uc" in sys.argv

    wait_ms = 500
    if "--wait" in sys.argv:
        idx = sys.argv.index("--wait")
        if idx + 1 < len(sys.argv):
            wait_ms = int(sys.argv[idx + 1])

    output_dir = None
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    batch_file = None
    if "--batch" in sys.argv:
        idx = sys.argv.index("--batch")
        if idx + 1 < len(sys.argv):
            batch_file = sys.argv[idx + 1]

    # Collect URLs: positional args that aren't flags
    flags = {"--html", "--no-cache", "--js", "--nodriver", "--uc", "--wait", "--batch", "--output-dir"}
    skip_next = False
    urls = []
    for arg in sys.argv[1:]:
        if skip_next:
            skip_next = False
            continue
        if arg in {"--wait", "--batch", "--output-dir"}:
            skip_next = True
            continue
        if arg.startswith("--"):
            continue
        urls.append(arg)

    # Add URLs from batch file
    if batch_file:
        batch_path = Path(batch_file)
        if batch_path.exists():
            for line in batch_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
        elif batch_file == "-":
            for line in sys.stdin:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
        else:
            print(f"Batch file not found: {batch_file}", file=sys.stderr)
            sys.exit(1)

    if not urls:
        print(__doc__)
        sys.exit(1)

    if len(urls) == 1 and not output_dir:
        # Single URL mode — original behavior
        content = _fetch_single(urls[0], raw_html, wait_ms, force_js, force_nodriver, force_uc, no_cache)
        sys.stdout.buffer.write(content.encode("utf-8", errors="replace"))
        sys.stdout.buffer.write(b"\n")
    else:
        # Batch mode — persistent browser session
        _run_batch(urls, raw_html, wait_ms, force_js, force_nodriver, force_uc, no_cache, output_dir)


if __name__ == "__main__":
    main()
