# ADR-035: pagefetch package and brandkit shared library

**Status:** Accepted
**Date:** 2026-05-28

## Context

The Python tooling under `tools/` has two structural problems.

First, `tools/fetch-page.py` is a 748-line CLI-only script with no
importable API. It implements a valuable four-tier auto-escalating fetch
strategy (urllib to Playwright to Nodriver to SeleniumBase UC), caching,
batch sessions, and bot detection. But because it exposes only a `main()`
entry point, the 9 of 11 brand spec-extraction tools that need web
fetching could not reuse it — they each re-implemented their own transport
(plain urllib, Playwright, or SeleniumBase). The escalation logic, the
single most valuable part, exists in exactly one place that nothing can
call programmatically.

Second, the 11 brand tools (fujifilm, mitakon, samyang, sigma, tamron,
tokina, ttartisan, venus, viltrox, voigtlander, zeiss) each carry a
`common.py` of roughly 250 lines, most of which is identical scaffolding:
`model_to_slug` (byte-identical except a brand-prefix string), the
`lenses.ts` block parser (`re.split(r"(?=\{\s*\n\s*brand:)")` then filter
by brand), `has_mtf_chart` / `has_construction_image` glob checks, file
caching, and `download_image`. This is the "third copy is a bug" rule
(`base/quality.md`) at elevenfold scale. Only the spec-extraction logic
and the image-URL patterns are genuinely brand-specific.

Third, issue #779 asks for a `--verify` mode that cross-validates stored
physical specs (weight, magnification, filter thread, etc.) against the
official product page — born from Session 76, where 10 data errors across
4 Tokina lenses went undetected. No brand tool extracts physical specs
today, so this is net-new per-brand work that needs a clean home.

There is also no precedent in the repository for a shared Python library
under `tools/`, nor any Python test suite — every brand independently
duplicates utilities and nothing is unit-tested.

## Decision

Introduce two packages and the first pytest suite under `tools/`.

**`tools/pagefetch/`** — a self-contained, importable, submodule-ready
package owning all web-transport concerns, with zero coupling to me-fuji.
It exposes a `PageSource` abstract base class and a `NetworkFetcher`
implementation that preserves the existing escalation logic exactly, plus
a `FakeFetcher` test double. The four-tier escalation, cache key scheme
(`sha256(url)[:16]` plus `.txt`/`.html` suffix), and CLI flag surface are
preserved byte-for-byte. The CLI is refactored in place to wrap the class
(`py -m pagefetch`).

```python
class PageSource(ABC):
    @abstractmethod
    def fetch(self, url: str, options: FetchOptions | None = None) -> FetchResult: ...
    @abstractmethod
    def fetch_batch(self, urls: list[str], options=None) -> list[FetchResult]: ...
    @abstractmethod
    def download_bytes(self, url: str, min_size: int = 0) -> bytes | None: ...
    @abstractmethod
    def screenshot(self, url: str, dest: Path, options=None) -> bool: ...
```

Two module globals become instance state: `_spawned_chrome_pids` moves to
a `ChromeReaper` object (which registers its own `atexit` cleanup), and
`CACHE_DIR` becomes a `FileCache(cache_dir=...)` constructor parameter with
a portable default (`./.cache/pagefetch` relative to the working
directory). me-fuji constructs `FileCache(cache_dir=ROOT/".cache"/"fetch")`
to keep existing cached pages valid. Boolean flag parameters (`raw_html`)
are replaced by `ContentMode` and `Transport` enums (`base/quality.md`
bans boolean flag parameters).

**`tools/brandkit/`** — a shared library, me-fuji-coupled (it reads
`src/data/lenses.ts`), holding the invariant brand pipeline via
composition. A `BrandTool` orchestrator is composed with an injected
`PageSource` and an injected per-brand `BrandExtractor` strategy. The
duplicated scaffolding (`model_to_slug`, the `lenses.ts` parser, the
glob checks, image download) moves here once. The brand-specific parts
(spec extraction, image-URL patterns, URL normalization) live behind the
`BrandExtractor` interface with a normalized contract.

```python
class BrandExtractor(ABC):
    config: BrandConfig  # name, slug_prefix, content_mode, transport, has_diagrams
    @abstractmethod
    def extract_optical(self, content: str) -> dict: ...
    def extract_physical(self, content: str) -> dict: return {}  # #779, base default
    def extract_image_urls(self, content: str) -> dict[str, list[str]]:
        return {"mtf": [], "construction": []}  # normalized; no-diagram brands use default
    def normalize_url(self, url: str) -> str: return url
```

Composition is chosen over inheritance deliberately: `base/testing.md`
states "prefer composition over inheritance — composed dependencies can be
injected and swapped in tests; inherited behaviour drags the entire class
hierarchy into every test." Because both `PageSource` and `BrandExtractor`
inject into `BrandTool`, the orchestrator's tests need no network and no
real HTML.

Tokina is migrated first as the proof brand (it motivated #779, uses plain
urllib so it is CI-friendly, and has the cleanest existing code). The
remaining 10 brands and the per-brand `extract_physical` work for #779 are
tracked as follow-up tasks under a tracking epic.

## Alternatives considered

1. **Inheritance hierarchy** — a `BrandFetcher` base class with one
   subclass per brand overriding extraction hooks (Template Method).
   Rejected: the user prefers composition; inheritance couples every
   brand to the transport implementation and, per `base/testing.md`,
   drags the whole hierarchy into each test. The brand variance (HTML vs
   JSON vs text input; dict vs list vs absent image shapes) is absorbed
   more cleanly by a strategy object than by overridable methods.
2. **Leave `fetch-page.py` a script, `subprocess` from brands** — keep
   the current shell-out pattern (as `tools/lenstip/build_index.py`
   already does). Rejected: no testable seam, no path to a reusable
   submodule, and it perpetuates the per-brand transport duplication.
3. **One shared `tools/common.py` module of functions** — extract the
   duplicated helpers into a single procedural module without classes.
   Rejected: it solves the DRY problem but not the injection/testability
   one, and it does not give #779 a clean place to host the
   fetch-extract-diff pipeline. It also leaves transport tangled with
   me-fuji-specific helpers, blocking the submodule goal.
4. **Both packages as one directory** — put transport and brand logic in
   a single package. Rejected: transport must be me-fuji-agnostic to
   become a submodule, while brandkit must read `lenses.ts`. Mixing them
   would couple the submodule to me-fuji.

## Consequences

- First Python test suite under `tools/` (pytest), and first shared
  `tools/` library — both are new conventions documented in CLAUDE.md,
  README, ONBOARDING, and PLAYBOOK.
- `tools/fetch-page.py` is removed; its one code consumer
  (`tools/lenstip/build_index.py`) and five documentation references
  migrate to `py -m pagefetch`.
- pagefetch is submodule-ready (no me-fuji imports, configurable cache,
  own README and tests) but stays in this repo for now; extraction to a
  separate repository and git submodule is deferred to a future session.
- The cache key scheme is preserved exactly, so existing cached pages
  remain valid as long as me-fuji passes `cache_dir=ROOT/".cache"/"fetch"`.
- `extract_physical` has a base default returning `{}`, so brands can
  migrate to brandkit without blocking on #779; physical-spec extraction
  lands per-brand incrementally.
- The normalized `content: str -> dict` extractor contract bends in one
  place: Fujifilm's position-based image-URL fallback uses a live
  Playwright page handle, not a content string. That brand exposes an
  optional `extract_image_urls_live(page)` the `BrandTool` calls only when
  the brand config flags it. This is the single documented exception to
  the otherwise uniform contract.
- Browser-based tiers (Playwright, Nodriver, UC) remain CI-unfriendly
  (Nodriver needs headed Chrome); the escalation orchestration is tested
  with mocked transport methods, and the browser tier bodies stay
  manual-integration-tested as before.
