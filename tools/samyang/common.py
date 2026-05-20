"""Shared utilities for Samyang lens data tools.

Provides lens extraction from lenses.ts, slug generation, page fetching,
optical spec parsing, and image downloading for Samyang product pages.
"""

import hashlib
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"
CACHE_DIR = ROOT / ".cache" / "fetch"

BASE_URL = "https://www.lksamyang.com"

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


# --- Lens extraction ---


def extract_samyang_lenses() -> list[dict]:
    """Extract Samyang lens model + officialUrl from lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    # Split into individual lens blocks
    blocks = re.split(r"(?=\{\s*\n\s*brand:)", content)
    lenses = []
    for block in blocks:
        if 'brand: "Samyang"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        url_m = re.search(r'officialUrl:\s*\n?\s*"([^"]+)"', block)
        if model_m and url_m:
            lenses.append({"model": model_m.group(1), "url": url_m.group(1)})
    return lenses


def model_to_slug(model: str) -> str:
    """Convert model name to file slug: 12mm f/2.0 NCS CS -> samyang-12mm-f2-0-ncs-cs"""
    slug = model.lower().replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return f"samyang-{slug}"


# --- Caching ---


def _cache_path(url: str, suffix: str = ".html") -> Path:
    h = hashlib.sha256(url.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{h}{suffix}"


def read_cache(url: str) -> str | None:
    path = _cache_path(url)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def write_cache(url: str, content: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(url)
    path.write_text(content, encoding="utf-8")


# --- Page fetching ---


def fetch_page(url: str, timeout: int = 30) -> str:
    """Fetch a page via urllib. Returns HTML content. Uses cache."""
    cached = read_cache(url)
    if cached:
        return cached

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    write_cache(url, html)
    return html


# --- Spec extraction ---


TEXT_NUMS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
}


def _extract_spec_block(text: str) -> str:
    """Extract the first spec table block from page text.

    Samyang pages list specs between 'Optical Construction' and
    'Minimum Focusing Distance'. This avoids false positives from
    navigation, other product links, and marketing text.
    """
    m = re.search(
        r"Optical Construction\s+(.*?)Minimum Focusing",
        text, re.IGNORECASE | re.DOTALL,
    )
    return m.group(1) if m else ""


def extract_specs(html: str) -> dict:
    """Extract optical specs from Samyang product page HTML.

    Returns dict with keys: elements, groups, special, coating.
    """
    # Strip HTML tags for text matching
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    specs: dict = {}

    # Target the first spec table block to avoid false matches from
    # navigation links and other product listings on the page
    block = _extract_spec_block(text)
    if not block:
        return specs

    # Normalize text numbers
    for word, digit in TEXT_NUMS.items():
        block = re.sub(rf"\b{word}\b", digit, block, flags=re.IGNORECASE)

    # Elements and groups
    m = re.search(
        r"(\d+)\s*(?:lenses|elements?)\s+(?:in\s+)?(\d+)\s*groups?",
        block, re.IGNORECASE,
    )
    if m:
        specs["elements"] = int(m.group(1))
        specs["groups"] = int(m.group(2))

    # Special elements — match both "N type" and "type N" formats
    # Samyang uses both: "(1 H-ASP, 1 ASP, and 3 ED)" and "H-ASP 1, ASP 1, ED 3"
    special = []
    seen_types = set()

    type_patterns = [
        ("aspherical", [
            r"(\d+)\s*(?:glass\s+)?(?:aspherical|ASP)\s+(?:lens|element)",
            r"(\d+)\s*(?:glass\s+)?(?:aspherical|ASP)\b",
            r"\b(?:ASP)\s+(\d+)",
        ]),
        ("aspherical", [
            r"(\d+)\s*(?:hybrid\s+aspherical|H-ASP)\b",
            r"\bH-ASP\s+(\d+)",
        ]),
        ("ED", [
            r"(\d+)\s*(?:extra[- ]?low[- ]?dispersion|ED)\s+(?:lens|element)",
            r"(\d+)\s*(?:extra[- ]?low[- ]?dispersion|ED)\b",
            r"\bED\s+(\d+)",
        ]),
        ("HR", [
            r"(\d+)\s*(?:high[- ]?refractive|HR)\s+(?:lens|element)",
            r"(\d+)\s*(?:high[- ]?refractive|HR)\b",
            r"\bHR\s+(\d+)",
        ]),
    ]

    for label, patterns in type_patterns:
        count = 0
        for pat in patterns:
            m3 = re.search(pat, block, re.IGNORECASE)
            if m3:
                count = int(m3.group(1))
                break

        if count > 0:
            if label in seen_types:
                for i, s in enumerate(special):
                    if s.endswith(label):
                        existing = int(s.split()[0])
                        special[i] = f"{existing + count} {label}"
                        break
            else:
                special.append(f"{count} {label}")
                seen_types.add(label)

    specs["special"] = special

    # Coating — from the spec table block only (not full page)
    coating = []
    if re.search(r"Coating\s+NCS\b|Nano\s*Coating\s*System", block, re.IGNORECASE):
        coating.append("NCS")
    elif re.search(r"Coating\s+UMC\b|Ultra\s*Multi\s*Coat", block, re.IGNORECASE):
        coating.append("UMC")
    elif re.search(r"Coating\s+MC\b", block, re.IGNORECASE):
        coating.append("MC")
    else:
        # Fallback: check the broader text but only near "Coating" keyword
        cm = re.search(r"Coating\s+(\w+)", text)
        if cm:
            val = cm.group(1).upper()
            if val in ("NCS", "UMC", "MC"):
                coating.append(val)

    specs["coating"] = coating

    return specs


# --- Image extraction ---


def extract_image_urls(html: str) -> dict[str, str]:
    """Extract MTF chart and construction diagram URLs from page HTML.

    Samyang pages use: <strong>MTF Chart</strong> followed by <img src="...">,
    and <li class="optical-construction"><strong>Optical Construction</strong>
    followed by <img src="...">.

    Image src paths are extensionless (/upload/editor/NNNN) but serve as JPEG.
    """
    urls: dict[str, str] = {}

    # MTF chart: after "MTF Chart" or "MTF CHART"
    m = re.search(
        r"MTF\s*(?:Chart|CHART)\s*</strong>[^<]*<img\s+src=\"([^\"]+)\"",
        html, re.IGNORECASE,
    )
    if m:
        src = m.group(1)
        urls["mtf"] = src if src.startswith("http") else BASE_URL + src

    # Construction diagram: after "Optical Construction"
    m = re.search(
        r"Optical\s*Construction\s*</strong>[^<]*<img\s+src=\"([^\"]+)\"",
        html, re.IGNORECASE,
    )
    if m:
        src = m.group(1)
        urls["construction"] = src if src.startswith("http") else BASE_URL + src

    return urls


def download_image(url: str, dest: Path, min_size: int = 500) -> bool:
    """Download an image to dest. Returns True on success."""
    if dest.exists():
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read()
            if len(data) < min_size:
                return False

            # Determine extension from Content-Type since URLs are extensionless
            ext_map = {
                "image/jpeg": ".jpg",
                "image/png": ".png",
                "image/webp": ".webp",
                "image/gif": ".gif",
            }
            ext = ext_map.get(content_type, ".jpg")

            # Adjust dest extension if needed
            if dest.suffix != ext:
                dest = dest.with_suffix(ext)

            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"    WARN: download failed for {dest.name}: {e}")
        return False
