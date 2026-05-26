"""Build a local LensTip lens index from their catalog pages.

Scrapes manufacturer pages on lenstip.com to create a JSON lookup table
mapping lens names to their spec page URLs. This solves the problem of
LensTip using opaque numeric IDs in URLs that are impossible to guess.

Usage:
    py tools/lenstip/build_index.py                  # build full index
    py tools/lenstip/build_index.py --brand Fujifilm  # single brand only
    py tools/lenstip/build_index.py --no-cache        # bypass cache

Output: tools/lenstip/lenstip-index.json
"""

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

BASE_URL = "https://www.lenstip.com"
TOOL_DIR = Path(__file__).parent
INDEX_FILE = TOOL_DIR / "lenstip-index.json"
FETCH_PAGE = Path(__file__).parent.parent / "fetch-page.py"

# Manufacturer IDs from the LensTip dropdown (producent select element).
# Format: {dropdown_value: (url_name, display_name)}
MANUFACTURERS = {
    "147": ("7Artisans", "7Artisans"),
    "152": ("AstrHori", "AstrHori"),
    "26": ("Canon", "Canon"),
    "16": ("Carl_Zeiss", "Carl Zeiss"),
    "94": ("CCCP", "CCCP"),
    "86": ("Cosina", "Cosina"),
    "100": ("Falcon", "Falcon"),
    "66": ("Fujifilm", "Fujifilm"),
    "131": ("Hasselblad", "Hasselblad"),
    "112": ("IBE_Optics", "IBE Optics"),
    "127": ("Irix", "Irix"),
    "103": ("Kenko", "Kenko"),
    "38": ("Konica_Minolta", "Konica Minolta"),
    "31": ("Kowa", "Kowa"),
    "42": ("Leica", "Leica"),
    "95": ("Mamiya", "Mamiya"),
    "128": ("Meike", "Meike"),
    "113": ("Mitakon", "Mitakon"),
    "77": ("Nikon_Nikkor", "Nikon Nikkor"),
    "39": ("Olympus", "Olympus"),
    "150": ("OM_System", "OM System"),
    "64": ("Panasonic", "Panasonic"),
    "13": ("Pentax", "Pentax"),
    "79": ("Rollei", "Rollei"),
    "135": ("SainSonic", "SainSonic"),
    "68": ("Samsung", "Samsung"),
    "96": ("Samyang", "Samyang"),
    "83": ("Schneider-Kreuznach", "Schneider-Kreuznach"),
    "73": ("Sigma", "Sigma"),
    "146": ("Sirui", "Sirui"),
    "111": ("SLR_Magic", "SLR Magic"),
    "62": ("Sony", "Sony"),
    "76": ("Tamron", "Tamron"),
    "154": ("Thypoch", "Thypoch"),
    "82": ("Tokina", "Tokina"),
    "148": ("TTartisan", "TTartisan"),
    "125": ("Venus_Optics_LAOWA", "Venus Optics LAOWA"),
    "136": ("Viltrox", "Viltrox"),
    "85": ("Vivitar", "Vivitar"),
    "92": ("Voigtlander", "Voigtlander"),
    "93": ("Yashica", "Yashica"),
    "118": ("Yongnuo", "Yongnuo"),
}

# Pattern: <id>-<Name>-lens_specifications.html
SPEC_LINK_RE = re.compile(
    r'href="(\d+-[^"]*-lens_specifications\.html)"'
)

# Extract lens name from the link text (h2 tag content)
LENS_NAME_RE = re.compile(
    r'<h2><a href="\d+-[^"]*-lens_specifications\.html">([^<]+)</a></h2>'
)


def fetch_html(url: str, *, no_cache: bool = False) -> str:
    """Fetch a page using fetch-page.py and return raw HTML."""
    cmd = [sys.executable, str(FETCH_PAGE), url, "--html"]
    if no_cache:
        cmd.append("--no-cache")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"  WARNING: fetch failed for {url}: {result.stderr[:200]}")
        return ""
    return result.stdout


def parse_lenses_from_html(html: str) -> list[dict]:
    """Extract lens entries from a manufacturer page HTML."""
    lenses = []
    seen_ids = set()

    # Find all spec links and their names
    for match in SPEC_LINK_RE.finditer(html):
        href = match.group(1)
        lens_id = href.split("-")[0]
        if lens_id in seen_ids:
            continue
        seen_ids.add(lens_id)

        # Extract the lens name from the nearest h2 tag
        # Look backwards from the href position for the name
        url = f"{BASE_URL}/{href}"

        lenses.append({
            "id": int(lens_id),
            "url": url,
            "href": href,
        })

    # Now extract names — match h2 links to their hrefs
    for name_match in LENS_NAME_RE.finditer(html):
        name = name_match.group(1).strip()
        href_in_name = name_match.group(0)
        # Find the ID from this match
        id_match = re.search(r'href="(\d+)-', href_in_name)
        if id_match:
            lens_id = id_match.group(1)
            for lens in lenses:
                if str(lens["id"]) == lens_id and "name" not in lens:
                    lens["name"] = name
                    break

    # Fallback: derive name from URL slug for any missing names
    for lens in lenses:
        if "name" not in lens:
            slug = lens["href"].split("-", 1)[1].replace("-lens_specifications.html", "")
            lens["name"] = slug.replace("_", " ")

    return lenses


def build_index(
    *, brand_filter: str | None = None, no_cache: bool = False
) -> dict:
    """Build the full lens index by scraping manufacturer pages."""
    index = {
        "_meta": {
            "source": "lenstip.com",
            "description": "LensTip lens index — maps lens names to spec page URLs",
            "total_lenses": 0,
            "total_brands": 0,
        },
        "brands": {},
    }

    brands_to_fetch = []
    for mid, (url_name, display_name) in MANUFACTURERS.items():
        if brand_filter and brand_filter.lower() not in display_name.lower():
            continue
        brands_to_fetch.append((mid, url_name, display_name))

    print(f"Building LensTip index for {len(brands_to_fetch)} brand(s)...")

    total_lenses = 0
    for i, (mid, url_name, display_name) in enumerate(brands_to_fetch):
        url = f"{BASE_URL}/{mid}-{url_name}-lenses.html"
        print(f"  [{i + 1}/{len(brands_to_fetch)}] {display_name}...", end=" ", flush=True)

        html = fetch_html(url, no_cache=no_cache)
        if not html:
            print("FAILED")
            continue

        lenses = parse_lenses_from_html(html)
        print(f"{len(lenses)} lenses")

        if lenses:
            index["brands"][display_name] = [
                {"id": l["id"], "name": l["name"], "url": l["url"]}
                for l in sorted(lenses, key=lambda x: x["name"])
            ]
            total_lenses += len(lenses)

        # Be polite — small delay between requests
        if i < len(brands_to_fetch) - 1:
            time.sleep(0.5)

    index["_meta"]["total_lenses"] = total_lenses
    index["_meta"]["total_brands"] = len(index["brands"])

    return index


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build LensTip lens index from catalog pages"
    )
    parser.add_argument(
        "--brand", type=str, help="Filter to a single brand (case-insensitive substring)"
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="Bypass fetch-page.py cache"
    )
    args = parser.parse_args()

    index = build_index(brand_filter=args.brand, no_cache=args.no_cache)

    INDEX_FILE.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nIndex saved to {INDEX_FILE}")
    print(f"Total: {index['_meta']['total_lenses']} lenses across {index['_meta']['total_brands']} brands")


if __name__ == "__main__":
    main()
