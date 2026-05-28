"""Unified lens lookup — generate research URLs for all major sources.

Given a lens name, outputs direct links and search URLs for every source
in the PLAYBOOK 2.8 priority list. Uses the local LensTip index for
exact matches; generates search URLs for everything else.

Usage:
    py tools/lookup.py "Viltrox 56mm f/1.4"
    py tools/lookup.py "XF 90mm f/2"
    py tools/lookup.py "Sirui Sniper 23mm f/1.2"
    py tools/lookup.py "TTartisan 50mm f/0.95" --open   # open top result in browser
"""

import argparse
import json
import sys
import urllib.parse
from pathlib import Path

LENSTIP_INDEX = Path(__file__).parent / "lenstip" / "lenstip-index.json"


def url_encode(query: str) -> str:
    return urllib.parse.quote_plus(query)


def lenstip_lookup(query: str) -> str | None:
    """Look up a lens in the local LensTip index. Returns URL or None."""
    if not LENSTIP_INDEX.exists():
        return None
    # Import search module
    sys.path.insert(0, str(Path(__file__).parent / "lenstip"))
    from search import search
    results = search(query, limit=1)
    if results and results[0]["score"] > 0.8:
        return results[0]["url"]
    return None


def ddg_site_search(site: str, query: str) -> str:
    """Generate a DuckDuckGo HTML site-search URL (no CAPTCHAs, works with pagefetch)."""
    return f"https://html.duckduckgo.com/html/?q=site%3A{site}+{url_encode(query)}"


def lenstip_search_url(query: str) -> str:
    """Generate a DuckDuckGo site-search URL for LensTip."""
    return ddg_site_search("lenstip.com", query)


def generate_urls(query: str) -> list[tuple[str, str, str]]:
    """Generate research URLs for a lens query.

    Returns list of (source_name, url, note) tuples.
    Uses DuckDuckGo HTML for site-searches (no CAPTCHAs, works with
    pagefetch via plain urllib). Google only for image search.
    """
    q = url_encode(query)
    urls = []

    # --- Priority sources (PLAYBOOK 2.8 order) ---

    # LensTip — local index first, then search fallback
    lenstip_url = lenstip_lookup(query)
    if lenstip_url:
        urls.append(("LensTip (index match)", lenstip_url, "spec page"))
    else:
        urls.append(("LensTip (search)", lenstip_search_url(query), "no index match"))

    # Radojuva
    urls.append((
        "Radojuva",
        ddg_site_search("radojuva.com", query),
        "hands-on measurements",
    ))

    # Phillip Reeve
    urls.append((
        "Phillip Reeve",
        ddg_site_search("phillipreeve.net", query),
        "manual focus specialist",
    ))

    # DPReview
    urls.append((
        "DPReview",
        ddg_site_search("dpreview.com", f"{query} specifications"),
        "spec database (archived)",
    ))

    # Official manufacturer (generic search)
    urls.append((
        "Official page",
        f"https://html.duckduckgo.com/html/?q={q}+official+specifications",
        "manufacturer specs",
    ))

    # Dustin Abbott
    urls.append((
        "Dustin Abbott",
        ddg_site_search("dustinabbott.net", query),
        "trust-3 field + lab",
    ))

    # Opticallimits
    urls.append((
        "Opticallimits",
        ddg_site_search("opticallimits.com", query),
        "lab MTF (ex-photozone)",
    ))

    # Lensrentals (Roger Cicala)
    urls.append((
        "Lensrentals",
        ddg_site_search("lensrentals.com", f"{query} blog"),
        "optical bench MTF",
    ))

    # Photography Life
    urls.append((
        "Photography Life",
        ddg_site_search("photographylife.com", query),
        "spec tables + diagrams",
    ))

    # digitalkamera.de
    urls.append((
        "digitalkamera.de",
        ddg_site_search("digitalkamera.de", f"{query} Datenblatt"),
        "dimensions (German)",
    ))

    # Mobile01
    urls.append((
        "Mobile01",
        ddg_site_search("mobile01.com", query),
        "Taiwan forum, construction diagrams",
    ))

    # Google Image Search for diagrams/MTF (no DDG equivalent)
    urls.append((
        "Construction diagram",
        f"https://www.google.com/search?q={q}+optical+construction+diagram&tbm=isch",
        "image search",
    ))
    urls.append((
        "MTF chart",
        f"https://www.google.com/search?q={q}+MTF+chart&tbm=isch",
        "image search",
    ))

    return urls


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate research URLs for a lens across all sources"
    )
    parser.add_argument("query", help="Lens name to look up")
    parser.add_argument(
        "--open", action="store_true",
        help="Open the top LensTip result in the default browser",
    )
    args = parser.parse_args()

    urls = generate_urls(args.query)

    print(f"Research URLs for: {args.query}\n")
    for source, url, note in urls:
        print(f"  {source} ({note})")
        print(f"    {url}")
        print()

    if args.open:
        import webbrowser
        # Open first URL (LensTip match or search)
        webbrowser.open(urls[0][1])


if __name__ == "__main__":
    main()
