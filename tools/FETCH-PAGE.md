# fetch-page.py — Dev Journal

Page fetching utility for optical specs research. Uses a three-tier
strategy that auto-escalates on failure.

## Architecture

```
urllib (plain HTTP, ~1s)
  │
  ├─ success → done
  ├─ HTTP error (404, timeout) → Playwright
  └─ bot protection (captcha, 403 page) → skip Playwright → UC
                                              │
Playwright (headless Chromium, ~5-9s)         │
  │                                           │
  ├─ success → done                           │
  ├─ bot detection → UC  ◄────────────────────┘
  └─ timeout/error → UC
                │
SeleniumBase UC mode (stealth Chrome, ~18-24s)
  │
  ├─ success → done
  └─ failure → "All tiers failed"
```

## Tiers

| Tier | Engine          | Speed   | Use case                                  |
| ---- | --------------- | ------- | ----------------------------------------- |
| 1    | urllib          | ~1s     | Static HTML pages (most sites)            |
| 2    | Playwright      | ~5-9s   | JS-rendered content (SPAs, lazy tabs)     |
| 3    | SeleniumBase UC | ~18-24s | Bot-protected sites (Cloudflare, captcha) |

## CLI

```
py tools/fetch-page.py <url>              # auto mode
py tools/fetch-page.py <url> --html       # raw HTML output
py tools/fetch-page.py <url> --js         # force Playwright
py tools/fetch-page.py <url> --uc         # force SeleniumBase UC
py tools/fetch-page.py <url> --wait 5000  # extra wait (ms)
py tools/fetch-page.py <url> --no-cache   # bypass cache
```

## Bot detection

Detected via response patterns (checked against raw HTML and stripped
text within the first 20KB):

- Captcha redirects (short HTML with meta-refresh)
- "Checking your browser" / "Checking the site connection security"
- "Just a moment..." / "Attention Required...Cloudflare"
- "Verifying you are human" / "This page requires cookies"
- HTTP 403/Access Denied title pages

When urllib detects bot protection, Playwright is skipped entirely
(it would fail on the same protection). Goes straight to UC.

## Event-driven waits (UC mode)

UC mode uses polling instead of fixed sleeps:

1. **Page load**: poll `document.readyState` every 300ms (cheap JS call)
2. **Bot clearance**: once ready, poll `get_page_source()` with exponential
   backoff (0.5s → 0.75s → 1.1s → ... → 2s cap) until bot detection
   patterns disappear. Timeout: 15s.
3. **Scroll/lazy content**: scroll to bottom, poll `scrollHeight` every 300ms
   until it stabilizes (no new content loaded). Timeout: 3s.

This adapts to the actual security handshake time instead of guessing
with fixed sleeps.

## Performance history

### v1 — Playwright only (2026-05-20, commit d7de7c4)

- All requests via Playwright with `networkidle` wait
- ~5-9s for all pages, even static HTML
- Failed on bot-protected sites (zyoptics.net, mobile01.com)

### v2 — Three-tier with auto-escalation (2026-05-25)

- Added urllib as Tier 1, SeleniumBase UC as Tier 3
- Normal sites: ~1s (5-10x faster)
- Bot-protected: ~27s (urllib → Playwright fail → UC)

### v3 — Optimizations (2026-05-25)

1. **Skip Playwright on bot protection**: urllib detects captcha → straight
   to UC. Saves ~5-9s on bot-protected sites.
2. **`domcontentloaded` over `networkidle`**: Playwright ~40% faster.
3. **Event-driven UC waits**: polling replaces fixed sleeps. More reliable
   (no intermittent failures from too-short waits).

Final single-URL timings:

- Normal site (urllib): **~1s**
- JS page (urllib → Playwright): **~5-9s**
- Bot-protected (urllib → UC): **~18-24s**

### v4 — Batch mode with persistent browser (2026-05-25)

Persistent UC session for batch operations. Chrome launches once (~12s),
subsequent pages reuse the session (~3-6s each).

```
py tools/fetch-page.py --batch urls.txt --uc --output-dir out/
```

Benchmark: 3 bot-protected pages (zyoptics.net):

| Page       | Single mode | Batch mode |
| ---------- | ----------- | ---------- |
| 1st (cold) | ~20s        | 11.6s      |
| 2nd        | ~20s        | 3.2s       |
| 3rd        | ~20s        | 2.4s       |
| **Total**  | **~60s**    | **~27s**   |

55% faster on batch. Supports: `--batch file.txt`, `--batch -` (stdin),
or multiple positional URLs. `--output-dir` saves one file per URL.

## Sites tested

| Site                  | Tier used  | Notes                                     |
| --------------------- | ---------- | ----------------------------------------- |
| allphotolenses.com    | urllib     | Static HTML, fast                         |
| ttartisan.com         | Playwright | JS-rendered content (query-param routing) |
| zyoptics.net          | UC         | SiteGround captcha + bot protection       |
| bhphotovideo.com      | Playwright | networkidle timeout on product pages      |
| viltrox.com (Shopify) | urllib     | Static HTML with Shopify JSON             |
| mobile01.com          | UC         | Akamai CDN blocks headless browsers       |

## Dependencies

- **urllib** (stdlib) — always available
- **Playwright** (`pip install playwright`) — optional, Tier 2
- **SeleniumBase** (`pip install seleniumbase`) — optional, Tier 3

Missing dependencies are caught gracefully — the tier is skipped with
a stderr message.

## Cache

Responses cached in `.cache/fetch/` by URL hash. Both text and HTML
variants are cached separately. Use `--no-cache` to bypass.

## Known limitations

- UC mode is ~18-24s minimum due to Chrome launch overhead (~10-12s)
- Some bot-protection pages need >5s for the security handshake
- B&H product pages timeout on Playwright (`networkidle` never fires
  due to continuous ad/tracking requests)
- Single-URL mode launches a new Chrome per call; use batch mode for multiple URLs
