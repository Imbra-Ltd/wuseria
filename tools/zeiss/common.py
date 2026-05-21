"""Shared utilities for Carl Zeiss lens data tools.

Provides lens extraction from lenses.ts, slug generation, and PDF datasheet
downloading for Carl Zeiss Touit lenses.

Note: Zeiss Touit lenses are discontinued. The official product pages are gone
(404). The officialUrl fields point to PDF datasheets hosted on zeiss.com.
These PDFs contain optical construction diagrams and MTF charts but specs
must be extracted manually from the downloaded PDFs.
"""

import hashlib
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"
CACHE_DIR = ROOT / ".cache" / "fetch"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


# --- File existence checks ---


def has_mtf_chart(slug: str) -> bool:
    """Check if an MTF chart image exists in optical-specs/{slug}/."""
    specs_dir = OPTICAL_SPECS_DIR / slug
    if not specs_dir.is_dir():
        return False
    return bool([f for f in specs_dir.glob(f"{slug}-mtf*") if f.suffix in (".png", ".jpg", ".webp")])


def has_construction_image(slug: str) -> bool:
    """Check if an optical construction diagram exists in optical-specs/{slug}/."""
    specs_dir = OPTICAL_SPECS_DIR / slug
    if not specs_dir.is_dir():
        return False
    return bool([f for f in specs_dir.glob(f"{slug}-construction*") if f.suffix in (".png", ".jpg", ".webp")])


def has_datasheet(slug: str) -> bool:
    """Check if a PDF datasheet exists in optical-specs/{slug}/."""
    specs_dir = OPTICAL_SPECS_DIR / slug
    if not specs_dir.is_dir():
        return False
    return bool(list(specs_dir.glob(f"{slug}-datasheet.pdf")))


# --- Lens extraction ---


def extract_zeiss_lenses() -> list[dict]:
    """Extract Carl Zeiss lens model + officialUrl from lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    blocks = re.split(r"(?=\{\s*\n\s*brand:)", content)
    lenses = []
    for block in blocks:
        if 'brand: "Carl Zeiss"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        url_m = re.search(r'officialUrl:\s*\n?\s*"([^"]+)"', block)
        if model_m and url_m:
            lenses.append({"model": model_m.group(1), "url": url_m.group(1)})
    return lenses


def model_to_slug(model: str) -> str:
    """Convert model name to file slug: Touit 12mm f/2.8 -> zeiss-touit-12mm-f2-8"""
    slug = model.lower().replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return f"zeiss-{slug}"


# --- Download ---


def download_pdf(url: str, dest: Path) -> bool:
    """Download a PDF datasheet to dest. Returns True on success."""
    if dest.exists():
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if len(data) < 1000:
                return False
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"    WARN: download failed for {dest.name}: {e}")
        return False
