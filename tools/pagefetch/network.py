"""NetworkFetcher — the real four-tier auto-escalating page fetcher.

Tier strategy (auto mode escalates on failure):
  1. urllib (plain HTTP)        — fastest (~1s), most static pages
  2. Playwright (headless)      — JS-rendered pages (~5-9s)
  3. Nodriver (headed Chrome)   — bot-protected sites (~6-8s)
  4. SeleniumBase UC mode       — headless bot bypass fallback (~18-24s)

Auto mode tries urllib first. If bot protection is detected, it skips
Playwright (which would fail the same way) and goes straight to Nodriver,
then UC. If urllib fails for another reason (404, timeout), it tries
Playwright, then Nodriver, then UC.

Third-party browser libraries are imported lazily inside each tier so the
package works with only the standard library installed — unavailable tiers
are skipped gracefully.
"""

import sys
from pathlib import Path

from .cache import FileCache
from .chrome import ChromeReaper
from .detection import html_to_text, is_bot_blocked
from .source import (
    ContentMode,
    FetchOptions,
    FetchResult,
    PageSource,
    Transport,
)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

# Sentinel: urllib detected bot protection (skip Playwright, go to Nodriver/UC).
_BOT_BLOCKED = "@@BOT_BLOCKED@@"


def _scroll_page_js() -> str:
    """JavaScript to scroll a page for lazy-loaded content (Playwright)."""
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


class NetworkFetcher(PageSource):
    """Fetches pages over the network with auto-escalating transport."""

    def __init__(
        self,
        cache: FileCache | None = None,
        user_agent: str = DEFAULT_USER_AGENT,
        reaper: ChromeReaper | None = None,
    ) -> None:
        self._cache = cache or FileCache()
        self._ua = user_agent
        self._reaper = reaper or ChromeReaper()

    # --- public PageSource interface ---------------------------------

    def fetch(self, url: str, options: FetchOptions | None = None) -> FetchResult:
        opts = options or FetchOptions()
        content, tier = self._fetch_single(url, opts)
        return FetchResult(url=url, content=content, tier_used=tier, ok=bool(content))

    def fetch_batch(
        self, urls: list[str], options: FetchOptions | None = None
    ) -> list[FetchResult]:
        opts = options or FetchOptions()
        return self._run_batch(urls, opts)

    def download_bytes(self, url: str, min_size: int = 0) -> bytes | None:
        import urllib.request

        try:
            req = urllib.request.Request(url, headers={"User-Agent": self._ua})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
        except Exception as e:
            print(f"[download] {e}", file=sys.stderr)
            return None
        if len(data) < min_size:
            return None
        return data

    def screenshot(
        self, url: str, dest: Path, options: FetchOptions | None = None
    ) -> bool:
        opts = options or FetchOptions()
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("[playwright] Not installed", file=sys.stderr)
            return False
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=self._ua)
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(opts.wait_ms)
                dest.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(dest), full_page=True)
                browser.close()
            return True
        except Exception as e:
            print(f"[playwright] {e}", file=sys.stderr)
            return False

    # --- tier 1: urllib ----------------------------------------------

    def _fetch_urllib(self, url: str, mode: ContentMode) -> str | None:
        """Fetch via plain urllib. Returns content, the _BOT_BLOCKED
        sentinel, or None."""
        import urllib.error
        import urllib.request

        try:
            req = urllib.request.Request(url, headers={"User-Agent": self._ua})
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            print(f"[urllib] HTTP {e.code}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"[urllib] {e}", file=sys.stderr)
            return None

        if is_bot_blocked(html):
            print("[urllib] Bot protection detected", file=sys.stderr)
            return _BOT_BLOCKED

        if mode is ContentMode.HTML:
            return html
        return html_to_text(html)

    # --- tier 2: Playwright ------------------------------------------

    def _fetch_playwright(
        self, url: str, mode: ContentMode, wait_ms: int
    ) -> str | None:
        """Fetch via headless Chromium. Uses domcontentloaded (not
        networkidle) — faster on ad-heavy pages."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("[playwright] Not installed", file=sys.stderr)
            return None

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=self._ua)
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(wait_ms)
                page.evaluate(_scroll_page_js())

                html = page.content()
                if is_bot_blocked(html):
                    print("[playwright] Bot detection page received", file=sys.stderr)
                    browser.close()
                    return None

                content = html if mode is ContentMode.HTML else page.inner_text("body")

                png = self._cache.screenshot_path(url)
                if not png.exists():
                    png.parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(png), full_page=True)

                browser.close()
                return content
        except Exception as e:
            print(f"[playwright] {e}", file=sys.stderr)
            return None

    # --- tier 3: Nodriver --------------------------------------------

    def _fetch_nodriver(
        self, url: str, mode: ContentMode, wait_ms: int
    ) -> str | None:
        """Fetch via Nodriver (headed Chrome via CDP, no driver binary)."""
        try:
            import nodriver as uc_nd
        except ImportError:
            print("[nodriver] Not installed", file=sys.stderr)
            return None

        import asyncio

        async def _fetch() -> str | None:
            browser = None
            try:
                pids_before = self._reaper.running_chrome_pids()
                browser = await uc_nd.start(headless=False)
                self._reaper.track_new_since(pids_before)
                page = await browser.get(url)
                return await self._nodriver_read_page(page, mode, wait_ms)
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

    async def _nodriver_read_page(self, page, mode: ContentMode, wait_ms: int) -> str | None:
        """Wait for a Nodriver page to clear bot protection and read it.

        Shared by single-fetch and batch (persistent browser) paths.
        """
        import time as _time

        deadline = _time.monotonic() + 15
        while _time.monotonic() < deadline:
            try:
                if await page.evaluate("document.readyState") == "complete":
                    break
            except Exception:
                pass
            await page.sleep(0.3)

        interval = 0.5
        while _time.monotonic() < deadline:
            html = await page.get_content()
            if not is_bot_blocked(html):
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
        if is_bot_blocked(html):
            print("[nodriver] Bot detection page still present", file=sys.stderr)
            return None

        return html if mode is ContentMode.HTML else html_to_text(html)

    async def _nodriver_fetch_with_browser(
        self, browser, url: str, mode: ContentMode, wait_ms: int
    ) -> str | None:
        """Fetch using an existing Nodriver browser (batch mode)."""
        try:
            page = await browser.get(url)
            return await self._nodriver_read_page(page, mode, wait_ms)
        except Exception as e:
            print(f"[nodriver] {e}", file=sys.stderr)
            return None

    # --- tier 4: SeleniumBase UC -------------------------------------

    def _fetch_uc(self, url: str, mode: ContentMode, wait_ms: int) -> str | None:
        """Fetch via SeleniumBase UC mode. Launches a new session per call;
        batch mode reuses one via _fetch_uc_with_session."""
        try:
            from seleniumbase import SB
        except ImportError:
            print("[uc] SeleniumBase not installed", file=sys.stderr)
            return None

        try:
            pids_before = self._reaper.running_chrome_pids()
            with SB(uc=True, headless=True) as sb:
                self._reaper.track_new_since(pids_before)
                return self._fetch_uc_with_session(sb, url, mode, wait_ms)
        except Exception as e:
            print(f"[uc] {e}", file=sys.stderr)
            return None

    def _fetch_uc_with_session(
        self, sb, url: str, mode: ContentMode, wait_ms: int
    ) -> str | None:
        """Fetch a page using an existing SeleniumBase UC session."""
        try:
            sb.open(url)
            if not self._uc_wait_for_page(sb):
                print("[uc] Bot detection page still present after timeout", file=sys.stderr)
                return None
            if wait_ms > 500:
                sb.sleep(wait_ms / 1000)
            self._uc_wait_for_scroll(sb)
            html = sb.get_page_source()
            if is_bot_blocked(html):
                print("[uc] Bot detection page still present", file=sys.stderr)
                return None
            return html if mode is ContentMode.HTML else html_to_text(html)
        except Exception as e:
            print(f"[uc] {e}", file=sys.stderr)
            return None

    @staticmethod
    def _uc_wait_for_page(sb, timeout_s: int = 15) -> bool:
        """Wait past a bot-protection interstitial: first for readyState,
        then poll the page source for bot detection with backoff."""
        import time

        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            try:
                if sb.execute_script("return document.readyState") == "complete":
                    break
            except Exception:
                pass
            sb.sleep(0.3)

        interval = 0.5
        while time.monotonic() < deadline:
            try:
                if not is_bot_blocked(sb.get_page_source()):
                    return True
            except Exception:
                pass
            sb.sleep(interval)
            interval = min(interval * 1.5, 2.0)
        return False

    @staticmethod
    def _uc_wait_for_scroll(sb, timeout_s: int = 3) -> None:
        """Scroll to bottom and wait for DOM height to stabilize."""
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

    # --- escalation orchestrator -------------------------------------

    def _fetch_single(
        self, url: str, opts: FetchOptions, sb_session=None
    ) -> tuple[str, str]:
        """Fetch one URL, escalating tiers as needed.

        Returns (content, tier_used). content is "" if every tier failed.
        Shared by single and batch modes. The batch loop drives a
        persistent Nodriver browser itself; sb_session lets a persistent
        UC session flow through to escalation.
        """
        mode, wait_ms = opts.mode, opts.wait_ms

        if opts.use_cache:
            cached = self._cache.read(url, mode)
            if cached is not None:
                return cached, "cache"

        content, tier = self._escalate(url, opts, sb_session)

        if content:
            self._cache.write(url, mode, content)
        return content, tier

    def _escalate(
        self, url: str, opts: FetchOptions, sb_session
    ) -> tuple[str, str]:
        """Run the tier strategy for opts.transport. Returns (content, tier)."""
        mode, wait_ms = opts.mode, opts.wait_ms

        if opts.transport is Transport.UC:
            content = self._uc_either(sb_session, url, mode, wait_ms)
            return content, "uc" if content else "none"

        if opts.transport is Transport.NODRIVER:
            content = self._nodriver_either(url, mode, wait_ms)
            return content, "nodriver" if content else "none"

        if opts.transport is Transport.PLAYWRIGHT:
            content = self._fetch_playwright(url, mode, wait_ms) or ""
            return content, "playwright" if content else "none"

        # AUTO: urllib first, then escalate.
        result = self._fetch_urllib(url, mode)
        if result and result != _BOT_BLOCKED:
            return result, "urllib"

        if result == _BOT_BLOCKED:
            # Bot protection: skip Playwright (it would fail too).
            print("[auto] Skipping Playwright (bot protection), trying Nodriver...", file=sys.stderr)
            content = self._nodriver_either(url, mode, wait_ms)
            if content:
                return content, "nodriver"
            print("[auto] Nodriver failed, escalating to UC...", file=sys.stderr)
            content = self._uc_either(sb_session, url, mode, wait_ms)
            return content, "uc" if content else "none"

        # Non-bot failure (404, timeout): Playwright, then Nodriver, then UC.
        print("[auto] Escalating to Playwright...", file=sys.stderr)
        content = self._fetch_playwright(url, mode, wait_ms) or ""
        if content:
            return content, "playwright"
        print("[auto] Escalating to Nodriver...", file=sys.stderr)
        content = self._nodriver_either(url, mode, wait_ms)
        if content:
            return content, "nodriver"
        print("[auto] Escalating to UC...", file=sys.stderr)
        content = self._uc_either(sb_session, url, mode, wait_ms)
        return content, "uc" if content else "none"

    def _nodriver_either(self, url, mode, wait_ms) -> str:
        """Nodriver fetch. The batch loop drives the persistent browser
        directly (see _run_batch); single/escalation fetches are standalone."""
        return self._fetch_nodriver(url, mode, wait_ms) or ""

    def _uc_either(self, sb_session, url, mode, wait_ms) -> str:
        """UC via a persistent batch session if given, else standalone."""
        if sb_session:
            return self._fetch_uc_with_session(sb_session, url, mode, wait_ms) or ""
        return self._fetch_uc(url, mode, wait_ms) or ""

    # --- batch -------------------------------------------------------

    def _run_batch(self, urls: list[str], opts: FetchOptions) -> list[FetchResult]:
        """Fetch many URLs with one persistent browser session.

        Mirrors the original batch behavior: the browser launches once and
        stays open for all pages. Nodriver is preferred for bot-protected
        batches; UC is the fallback. Returns results in input order.
        """
        import asyncio
        import time

        results: list[FetchResult] = []

        needs_nodriver = opts.transport is Transport.NODRIVER
        needs_uc = opts.transport is Transport.UC
        force_js = opts.transport is Transport.PLAYWRIGHT

        # Auto mode: probe the first URL to decide if a persistent bot-tier
        # session is warranted.
        if not needs_nodriver and not needs_uc and not force_js and urls:
            if self._fetch_urllib(urls[0], opts.mode) == _BOT_BLOCKED:
                needs_nodriver = True

        nd_browser = None
        sb_session = None
        sb_context = None
        loop = None

        if needs_nodriver:
            try:
                import nodriver as uc_nd

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                pids_before = self._reaper.running_chrome_pids()
                nd_browser = loop.run_until_complete(uc_nd.start(headless=False))
                self._reaper.track_new_since(pids_before)
                print(f"[batch] Persistent Nodriver session started for {len(urls)} URLs", file=sys.stderr)
            except ImportError:
                print("[batch] Nodriver not installed, falling back to UC", file=sys.stderr)
                needs_nodriver, needs_uc = False, True
            except Exception as e:
                print(f"[batch] Nodriver failed to start: {e}, falling back to UC", file=sys.stderr)
                needs_nodriver, needs_uc = False, True

        if needs_uc and not nd_browser:
            try:
                from seleniumbase import SB

                pids_before = self._reaper.running_chrome_pids()
                sb_context = SB(uc=True, headless=True)
                sb_session = sb_context.__enter__()
                self._reaper.track_new_since(pids_before)
                print(f"[batch] Persistent UC session started for {len(urls)} URLs", file=sys.stderr)
            except ImportError:
                print("[batch] SeleniumBase not installed, falling back to per-URL mode", file=sys.stderr)

        try:
            ok = fail = 0
            for i, url in enumerate(urls):
                t0 = time.monotonic()
                print(f"[batch] [{i + 1}/{len(urls)}] {url}", file=sys.stderr)

                if nd_browser and needs_nodriver:
                    content = (
                        loop.run_until_complete(
                            self._nodriver_fetch_with_browser(
                                nd_browser, url, opts.mode, opts.wait_ms
                            )
                        )
                        or ""
                    )
                    tier = "nodriver" if content else "none"
                else:
                    content, tier = self._fetch_single(url, opts, sb_session=sb_session)

                elapsed = time.monotonic() - t0
                if content:
                    self._cache.write(url, opts.mode, content)
                    ok += 1
                    print(f"[batch]   -> {len(content)} bytes ({elapsed:.1f}s)", file=sys.stderr)
                else:
                    fail += 1
                    print(f"[batch]   FAILED ({elapsed:.1f}s)", file=sys.stderr)

                results.append(
                    FetchResult(url=url, content=content, tier_used=tier, ok=bool(content))
                )

            print(f"[batch] Done: {ok} ok, {fail} failed", file=sys.stderr)
        finally:
            if nd_browser:
                nd_browser.stop()
            if sb_context:
                sb_context.__exit__(None, None, None)

        return results
