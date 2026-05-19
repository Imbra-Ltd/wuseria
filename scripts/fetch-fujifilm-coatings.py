"""Fetch Fujifilm lens overview pages and extract coating information.

Scans for Nano-GI, HT-EBC, and Super EBC mentions in product descriptions.
Uses the same cache as fetch-page.py.

Usage:
    py scripts/fetch-fujifilm-coatings.py
"""

import hashlib
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
CACHE_DIR = ROOT / ".cache" / "fetch"


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def read_cache(url: str) -> str | None:
    path = CACHE_DIR / (url_hash(url) + ".txt")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def write_cache(url: str, content: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / (url_hash(url) + ".txt")
    path.write_text(content, encoding="utf-8")


def extract_fujifilm_lenses() -> list[dict]:
    content = LENSES_TS.read_text(encoding="utf-8")
    pattern = re.compile(
        r'brand:\s*"Fujifilm"[\s\S]*?'
        r'model:\s*"([^"]+)"[\s\S]*?'
        r'officialUrl:\s*"([^"]+)"'
    )
    return [{"model": m.group(1), "url": m.group(2)} for m in pattern.finditer(content)]


def extract_coatings(text: str) -> list[str]:
    coatings = ["Super EBC"]  # all Fujifilm lenses have this
    if re.search(r"Nano[- ]GI", text, re.IGNORECASE):
        coatings.append("Nano-GI")
    if re.search(r"HT[- ]EBC", text, re.IGNORECASE):
        coatings.append("HT-EBC")
    return coatings


def main() -> None:
    lenses = extract_fujifilm_lenses()
    print(f"Found {len(lenses)} Fujifilm lenses")

    # Check which need fetching
    to_fetch = []
    for lens in lenses:
        if read_cache(lens["url"]) is None:
            to_fetch.append(lens)

    print(f"{len(lenses) - len(to_fetch)} cached, {len(to_fetch)} need fetching")

    if to_fetch:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                )
            )

            for i, lens in enumerate(to_fetch):
                print(f"  Fetching [{i + 1}/{len(to_fetch)}] {lens['model']}...")
                page = context.new_page()
                try:
                    page.goto(lens["url"], wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(2000)
                    text = page.inner_text("body")
                    write_cache(lens["url"], text)
                except Exception as e:
                    print(f"    WARN: {e}")
                finally:
                    page.close()

            browser.close()

    # Extract coatings from all cached pages
    print("\n=== Coating results ===")
    out_path = ROOT / ".cache" / "fujifilm-specs" / "fujifilm-coatings.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        for lens in lenses:
            text = read_cache(lens["url"]) or ""
            coatings = extract_coatings(text)
            coating_str = ", ".join(coatings)
            extra = " + " + ", ".join(coatings[1:]) if len(coatings) > 1 else ""
            print(f"  {lens['model']}: {coating_str}")
            f.write(f"{lens['model']}|{coating_str}\n")

    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    main()
