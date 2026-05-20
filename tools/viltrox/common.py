"""Shared utilities for Viltrox lens data tools.

Provides lens extraction from lenses.ts, slug generation, Shopify JSON
fetching, and optical spec parsing for Viltrox product pages.

Note: Viltrox uses a Shopify storefront. Product specs are in the JSON
API at /products/{handle}.json. Unlike Sigma/Fujifilm, Viltrox does NOT
provide MTF charts or construction diagrams on their website.
"""

import hashlib
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"
CACHE_DIR = ROOT / ".cache" / "fetch"

BASE_URL = "https://viltrox.com"

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


def extract_viltrox_lenses() -> list[dict]:
    """Extract Viltrox lens model + officialUrl from lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    blocks = re.split(r"(?=\{\s*\n\s*brand:)", content)
    lenses = []
    for block in blocks:
        if 'brand: "Viltrox"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        url_m = re.search(r'officialUrl:\s*\n?\s*"([^"]+)"', block)
        if model_m and url_m:
            lenses.append({"model": model_m.group(1), "url": url_m.group(1)})
    return lenses


def model_to_slug(model: str) -> str:
    """Convert model name to file slug: AF 13mm f/1.4 STM -> viltrox-af-13mm-f1-4-stm"""
    slug = model.lower().replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return f"viltrox-{slug}"


def url_to_handle(url: str) -> str:
    """Extract Shopify product handle from URL.

    https://viltrox.com/products/af-9mm-f2-8-xf -> af-9mm-f2-8-xf
    """
    return url.rstrip("/").split("/products/")[-1]


# --- Caching ---


def _cache_path(url: str, suffix: str = ".json") -> Path:
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


def fetch_product_json(url: str, timeout: int = 30) -> dict:
    """Fetch product data from Shopify JSON API. Returns parsed JSON."""
    json_url = url.rstrip("/") + ".json"
    cached = read_cache(json_url)
    if cached:
        return json.loads(cached)

    req = urllib.request.Request(json_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    write_cache(json_url, text)
    return json.loads(text)


# --- Spec extraction ---


def extract_specs(product_data: dict) -> dict:
    """Extract optical specs from Shopify product JSON.

    Parses body_html for elements, groups, special elements, and coating.
    Returns dict with keys: elements, groups, special, coating.
    """
    body = product_data.get("product", {}).get("body_html", "")
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", body)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    specs: dict = {}

    # Elements and groups — multiple patterns for Viltrox's inconsistent format
    # Pattern 1: "N elements in M groups" (standard)
    m = re.search(r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?", text, re.IGNORECASE)
    if m:
        specs["elements"] = int(m.group(1))
        specs["groups"] = int(m.group(2))

    # Pattern 2: "N/M Elements" or "N/M Optical Design" (Viltrox shorthand)
    if "elements" not in specs:
        m = re.search(r"(\d+)/(\d+)\s*(?:Elements|Optical\s+Design)", text, re.IGNORECASE)
        if m:
            # Viltrox uses elements/groups order
            specs["elements"] = int(m.group(1))
            specs["groups"] = int(m.group(2))

    # Pattern 3: "N/M Elements (specs)" where first is groups (seen on 56mm f/1.7: "9/11")
    if "elements" not in specs:
        m = re.search(r"(\d+)/(\d+)\s*Elements?", text, re.IGNORECASE)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            # Larger number is elements
            if a > b:
                specs["elements"] = a
                specs["groups"] = b
            else:
                specs["elements"] = b
                specs["groups"] = a

    # Special elements
    special = []
    type_patterns = [
        ("aspherical", r"(\d+)\s*(?:aspherical|asph)\b"),
        ("ED", r"(\d+)\s*ED\b"),
        ("HR", r"(\d+)\s*(?:HR|HRI|High[- ]Refract(?:ive|ion)(?:\s+(?:Index|index))?)\b"),
        ("LD", r"(\d+)\s*(?:LD|Low[- ]Dispersion)\b"),
    ]

    for label, pat in type_patterns:
        m2 = re.search(pat, text, re.IGNORECASE)
        if m2:
            special.append(f"{m2.group(1)} {label}")

    specs["special"] = special

    # Coating
    coating = []
    if re.search(r"(?:HD\s+)?Nano\s+(?:multi[- ]?layer\s+)?coating", text, re.IGNORECASE):
        coating.append("Nano multilayer coating")
    elif re.search(r"nano[- ]?coat", text, re.IGNORECASE):
        coating.append("Nano coating")

    specs["coating"] = coating

    return specs
