# pagefetch

A self-contained, auto-escalating web page fetcher. It fetches a URL by
the cheapest means that works — plain HTTP for static pages, escalating
through headless and headed browsers for JS-rendered and bot-protected
sites — and caches responses on disk.

`pagefetch` has no dependency on any consuming project. It is built to be
extracted into a standalone repository or git submodule and reused
anywhere.

## Quick start

```python
from pagefetch import NetworkFetcher, FetchOptions, ContentMode

fetcher = NetworkFetcher()
result = fetcher.fetch(
    "https://example.com",
    FetchOptions(mode=ContentMode.HTML),
)
if result.ok:
    print(result.tier_used, len(result.content))
```

Only the standard library is required for the urllib tier. The browser
tiers are optional (see [Dependencies](#dependencies)).

## CLI

```
py -m pagefetch <url>              # auto mode
py -m pagefetch <url> --html       # raw HTML output (default: text)
py -m pagefetch <url> --js         # force Playwright
py -m pagefetch <url> --nodriver   # force Nodriver (headed)
py -m pagefetch <url> --uc         # force SeleniumBase UC
py -m pagefetch <url> --wait 5000  # extra post-load wait (ms)
py -m pagefetch <url> --no-cache   # bypass cache
py -m pagefetch --clean-cache      # purge bot/404 junk from the cache
py -m pagefetch --clean-cache --dry-run   # list junk, delete nothing

py -m pagefetch --batch urls.txt              # batch from file
py -m pagefetch --batch -                      # batch from stdin
py -m pagefetch url1 url2 url3                  # batch from args
py -m pagefetch --batch urls.txt --output-dir out/  # one file per URL
```

The CLI must be run with `tools/` on the import path (run it from the
`tools/` directory, or set `PYTHONPATH=tools`).

## Library API

| Symbol           | Purpose                                         |
| ---------------- | ----------------------------------------------- |
| `PageSource`     | Abstract base — the transport interface         |
| `NetworkFetcher` | Real fetcher with four-tier escalation          |
| `FakeFetcher`    | Test double backed by a URL→content map         |
| `FileCache`      | On-disk response cache (configurable directory) |
| `FetchOptions`   | `mode`, `transport`, `wait_ms`, `use_cache`     |
| `FetchResult`    | `url`, `content`, `tier_used`, `ok`             |
| `ContentMode`    | `TEXT` (stripped) / `HTML` (raw)                |
| `Transport`      | `AUTO` / `PLAYWRIGHT` / `NODRIVER` / `UC`       |
| `is_bot_blocked` | Pure bot-detection predicate                    |

Inject a `PageSource` into your own code so it can be faked in tests:

```python
def scrape(source: PageSource, url: str) -> str:
    return source.fetch(url, FetchOptions(mode=ContentMode.HTML)).content

# in tests:
from pagefetch import FakeFetcher
assert scrape(FakeFetcher({url: "<html>...</html>"}), url) == "<html>...</html>"
```

## Architecture

```
urllib (plain HTTP, ~1s)
  ├─ success → done
  ├─ HTTP error (404, timeout) → Playwright
  └─ bot protection (captcha, 403) → skip Playwright → Nodriver
                                            │
Playwright (headless Chromium, ~5-9s)       │
  ├─ success → done                         │
  └─ bot detection / error → Nodriver ◄─────┘
                │
Nodriver (headed Chrome via CDP, ~6-8s)
  ├─ success → done
  └─ failure → UC
                │
SeleniumBase UC (headless stealth Chrome, ~18-24s)
  ├─ success → done
  └─ failure → all tiers failed (content="")
```

| Tier | Engine          | Speed   | Mode     | Use case                               |
| ---- | --------------- | ------- | -------- | -------------------------------------- |
| 1    | urllib          | ~1s     | —        | Static HTML (most sites)               |
| 2    | Playwright      | ~5-9s   | headless | JS-rendered content                    |
| 3    | Nodriver        | ~6-8s   | headed   | Bot-protected sites (no driver binary) |
| 4    | SeleniumBase UC | ~18-24s | headless | Headless-only fallback                 |

When urllib detects bot protection, Playwright is skipped (it would fail
the same way) and the fetcher goes straight to Nodriver, then UC.

### Bot detection

A response is treated as a bot-detection interstitial when it matches a
known pattern (Cloudflare "Just a moment" / `challenge-platform`,
"Checking your browser", 403/429/Access Denied titles, "Too Many Requests"
/ rate-limit / "unusual traffic" throttles, PerimeterX markers, cookie
walls) or is a short HTML page with a meta-refresh redirect. See
`detection.py`.

`looks_like_real_content(html, min_bytes=10_000)` is the broader gate: a
response that is bot-blocked, a 404/gone error page, **or implausibly
short** (below the size floor) is not real content. This catches
throttle/error stubs that carry no recognizable bot text (e.g. a
retailer's ~7-8 KB "slow down" page). Such responses are never cached or
re-served, and in AUTO mode a bot-block/short stub triggers escalation to a
browser tier instead of being accepted as content.

`is_error_page(html)` recognizes 404/410 and soft-404 bodies (a
discontinued product served as HTTP 200 with a "page not found" / "no
longer available" body). A genuine 404 is **terminal**: it is not cached
and does not escalate (every tier returns the same error). See `detection.py`.

### Event-driven waits (browser tiers)

Browser tiers poll instead of sleeping a fixed time: wait for
`document.readyState === "complete"`, then poll the page source with
exponential backoff (0.5s → 2s cap, 15s timeout) until bot-detection
patterns disappear, then scroll and poll `scrollHeight` until it
stabilizes. This adapts to the actual security handshake time.

### Cache

Responses are cached by `sha256(url)[:16]` plus a `.txt`/`.html` suffix,
under the directory passed to `FileCache` (default `./.cache/pagefetch`).
Text and HTML variants are cached separately. The key scheme is fixed —
changing it would invalidate existing caches.

Only real content is cached: bot-blocked, 404/gone, and implausibly short
responses are kept out of the cache (see Bot detection). On read, a cached
body that is recognizably a bot/throttle page **or a 404/gone error page**
is ignored, **deleted**, and re-fetched — so a cache poisoned before this
guard existed, or one whose product was discontinued after caching,
self-heals on the next fetch rather than re-serving junk (and the dead file
does not linger).

To purge accumulated junk in bulk, `py -m pagefetch --clean-cache` sweeps
the cache and removes every bot-blocked / 404 entry, keeping real content;
`--dry-run` lists what it would remove without deleting. The "junk"
definition (`is_cacheable_junk`) is shared by the read-time scrub and the
sweep, so they never drift.

The cache has **no TTL** — validity is decided by content, not age. Specs
rarely change; discontinuation surfaces as a 404 (handled above); price
refreshes are deliberate `--no-cache` passes. See ADR-037.

```python
from pathlib import Path
from pagefetch import NetworkFetcher, FileCache

fetcher = NetworkFetcher(cache=FileCache(cache_dir=Path("/my/cache")))
```

## Dependencies

| Dependency        | Tier | Required |
| ----------------- | ---- | -------- |
| `urllib` (stdlib) | 1    | always   |
| `playwright`      | 2    | optional |
| `nodriver`        | 3    | optional |
| `seleniumbase`    | 4    | optional |

Missing optional dependencies are handled gracefully — the tier is
skipped with a stderr message. Install what you need:

```
pip install -r requirements.txt
playwright install chromium
```

## Tests

```
cd tools && py -m pytest pagefetch/tests/ -v
```

The escalation logic is tested by stubbing the four tier methods, so the
suite runs with no network and no browser. Browser-tier method bodies
require headed Chrome and are validated manually.

## Performance history

- **v1** — Playwright-only, `networkidle` wait. ~5-9s everywhere; failed
  on bot-protected sites.
- **v2** — three tiers (urllib → Playwright → UC). Normal ~1s; bot ~27s.
- **v3** — skip Playwright on bot detection; `domcontentloaded` over
  `networkidle`; event-driven UC waits. Normal ~1s, JS ~5-9s, bot ~18-24s.
- **v4** — persistent-browser batch mode. 3 bot-protected pages: ~60s → ~27s.
- **v5** — Nodriver tier (CDP, no driver binary), preferred over UC in
  auto. 3 bot-protected pages: 27s → 16s.
- **v6** — refactored from a single 748-line script into this package
  (PageSource ABC + NetworkFetcher + FakeFetcher), CLI wraps the class.
  Behavior preserved; see ADR-035.
- **v7** — throttle pages no longer poison the cache (#881): broadened bot
  detection (429 / rate-limit / "unusual traffic" / PerimeterX / Cloudflare
  challenge runtime) and added a `looks_like_real_content` size floor so
  implausibly short stubs escalate instead of being cached; cached bot/
  throttle bodies are ignored on read and re-fetched.
- **v8** — 404 / gone handling and cache validity by content (ADR-037): a
  404/410/soft-404 page is terminal (not cached, no escalation); cached
  error bodies self-heal on read (handles products discontinued after
  caching). No TTL — validity is content-based, not time-based.
- **v9** — cache cleanup: junk entries are deleted (not just ignored) when
  scrubbed on read, so dead files do not linger; `--clean-cache` (with
  `--dry-run`) sweeps the cache of bot/404 entries on demand.

### Sites tested

| Site               | Tier       | Notes                                   |
| ------------------ | ---------- | --------------------------------------- |
| allphotolenses.com | urllib     | static HTML                             |
| ttartisan.com      | Playwright | JS-rendered (query-param routing)       |
| zyoptics.net       | Nodriver   | SiteGround captcha + bot protection     |
| bhphotovideo.com   | Nodriver   | bypasses Cloudflare (headed)            |
| viltrox.com        | urllib     | static HTML + Shopify JSON              |
| mobile01.com       | UC         | Akamai blocks headless browsers         |
| adorama.com        | BLOCKED    | PerimeterX "Press & Hold" — manual only |

## Known limitations

- Nodriver requires headed mode (a Chrome window opens) — not for CI.
- UC mode is ~18-24s minimum due to Chrome launch overhead.
- PerimeterX "Press & Hold" (Adorama) blocks all automated tools.
- Single-URL mode launches a new browser per call; use batch for many URLs.
