# fetch-page — moved

The page-fetch utility has been refactored from a single
`tools/fetch-page.py` script into the importable, submodule-ready
**`tools/pagefetch/`** package (ADR-035).

- **Architecture, CLI, performance history, sites tested:**
  see [`pagefetch/README.md`](pagefetch/README.md)
- **CLI:** `py -m pagefetch <url>` (run from `tools/`) — was
  `py tools/fetch-page.py <url>`
- **Library:** `from pagefetch import NetworkFetcher, FetchOptions, ContentMode`

This pointer file is kept so existing links resolve. New content lives in
the package README.
