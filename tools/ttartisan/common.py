"""Shared utilities for TTartisan lens data tools.

Provides lens extraction from lenses.ts, slug generation, page fetching,
optical spec parsing, and image downloading for TTartisan product pages.

TTartisan uses two site patterns:
- Main site: ttartisan.com with query-param routing (/?category/id.html)
- Shopify store: ttartisan.store/products/ (AF 75mm f/2.0 only)

Image naming conventions vary by page age:
- Newer: /static/upload/other/{CODE}/Specification-MTF.webp
- Older: /static/upload/other/{CODE}/Specification-1.webp (MTF),
         Specification-2-EN.webp (construction)
- Legacy: /static/upload/image/{date}/{timestamp}.jpg
"""

import hashlib
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"
CACHE_DIR = ROOT / ".cache" / "fetch"

BASE_URL = "https://www.ttartisan.com"

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


def extract_ttartisan_lenses() -> list[dict]:
    """Extract TTartisan lens model + officialUrl from lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    blocks = re.split(r"(?=\{\s*\n\s*brand:)", content)
    lenses = []
    for block in blocks:
        if 'brand: "TTartisan"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        url_m = re.search(r'officialUrl:\s*\n?\s*"([^"]+)"', block)
        if model_m and url_m:
            lenses.append({"model": model_m.group(1), "url": url_m.group(1)})
    return lenses


def model_to_slug(model: str) -> str:
    """Convert model name to file slug: AF 35mm f/1.8 -> ttartisan-af-35mm-f1-8"""
    slug = model.lower().replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return f"ttartisan-{slug}"


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


def _strip_html(html: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text)


def extract_specs(html: str) -> dict:
    """Extract optical specs from TTartisan product page HTML.

    Returns dict with keys: elements, groups, special, coating.

    TTartisan page structure:
    - Spec table uses <table class="specification"> with elements/groups row
    - Special elements mentioned in prose text (not in spec table)
    - Coating rarely mentioned (only 500mm f/6.3 has "MC Multi-Layer Coatings")

    Strategy: elements/groups from the spec table, special elements from
    the product description paragraph near the "elements in groups" mention,
    coating from the full page text (safe — no false positives).
    """
    # Elements and groups — try spec table first, fall back to full page text.
    # Some pages use <table class="specification">, others use plain tables.
    spec_text = ""
    table_m = re.search(
        r'<table[^>]*class="specification"[^>]*>(.*?)</table>',
        html, re.DOTALL | re.IGNORECASE,
    )
    if table_m:
        spec_text = re.sub(r"<[^>]+>", " ", table_m.group(1))
        spec_text = re.sub(r"\s+", " ", spec_text)
    else:
        # Fallback: search all tables on the page
        for t_m in re.finditer(r"<table[^>]*>(.*?)</table>", html, re.DOTALL | re.IGNORECASE):
            t_text = re.sub(r"<[^>]+>", " ", t_m.group(1))
            t_text = re.sub(r"\s+", " ", t_text)
            if re.search(r"elements?\s+(?:in\s+)?\d+\s*groups?", t_text, re.IGNORECASE):
                spec_text = t_text
                break

    specs: dict = {}

    m = re.search(
        r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?",
        spec_text, re.IGNORECASE,
    )
    if not m:
        # Last resort: search full page text
        full = re.sub(r"<[^>]+>", " ", html)
        full = re.sub(r"\s+", " ", full)
        m = re.search(
            r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?",
            full, re.IGNORECASE,
        )
    if m:
        specs["elements"] = int(m.group(1))
        specs["groups"] = int(m.group(2))

    # Special elements from full page text.
    # Safe for ED/HR/LD/UD/achromatic — these terms don't appear in navigation.
    # Aspherical/ASPH is excluded because navigation has "F2.8 ASPH" model names.
    full_text = _strip_html(html)
    special = _extract_special_elements(full_text)
    specs["special"] = special
    coating: list[str] = []
    if re.search(r"MC\s+Multi[- ]?Layer", full_text, re.IGNORECASE):
        coating.append("MC Multi-Layer")
    elif re.search(r"multi[- ]?layer\s+coat", full_text, re.IGNORECASE):
        coating.append("Multi-layer coating")
    elif re.search(r"multi[- ]?coat", full_text, re.IGNORECASE):
        coating.append("Multi-coating")
    specs["coating"] = coating

    return specs


def _extract_special_elements(text: str) -> list[str]:
    """Extract special element types from product description text.

    TTartisan uses various terms for special glass:
    - ED / extra-low dispersion
    - HR / high-refractive / high-index
    - LD / low dispersion
    - UD / ultra-low dispersion
    - aspherical / ASPH (rare in TTartisan — most are navigation false positives)
    - achromatic doublet
    """
    special = []

    # Written-out patterns with counts (most reliable)
    # e.g. "one low dispersion element and three high refractive elements"
    # e.g. "2 extra-low dispersion glass and 2 high index glass"
    # e.g. "1 ultra-low dispersion element and 2 high-index glasses"
    # e.g. "including 6 high-index lenses"
    # e.g. "two ultra-low dispersion (UD) elements"
    # e.g. "2 high-refractive elements and 2 ED (Extra-low Dispersion) elements"

    text_nums = {
        "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    }
    normalized = text
    for word, digit in text_nums.items():
        normalized = re.sub(rf"\b{word}\b", digit, normalized, flags=re.IGNORECASE)

    type_patterns = [
        ("aspherical", [
            r"(\d+)\s*(?:aspherical|asph\.?)\s*(?:lens|element|glass)",
        ]),
        ("ED", [
            r"(\d+)\s*(?:extra[- ]low[- ]dispersion|ED)\s*(?:\([^)]*\)\s*)?(?:lens|element|glass)",
            r"(\d+)\s*ED\s*\(",
        ]),
        ("HR", [
            r"(\d+)\s*(?:high[- ]?refract(?:ive|ion)|high[- ]?index)\s*(?:lens|element|glass)",
        ]),
        ("LD", [
            r"(\d+)\s*(?:low[- ]dispersion)\s*(?:lens|element|glass)",
        ]),
        ("UD", [
            r"(\d+)\s*(?:ultra[- ]low[- ]dispersion)\s*(?:\([^)]*\)\s*)?(?:lens|element|glass)",
        ]),
    ]

    for label, patterns in type_patterns:
        for pat in patterns:
            m = re.search(pat, normalized, re.IGNORECASE)
            if m:
                special.append(f"{m.group(1)} {label}")
                break

    # Achromatic doublets (90mm f/1.25: "4 Sets of Achromatic Doublets")
    m_achro = re.search(r"(\d+)\s*(?:sets?\s+of\s+)?achromatic\s+doublets?", normalized, re.IGNORECASE)
    if m_achro:
        special.append(f"{m_achro.group(1)} achromatic doublet")

    return special


# --- Image extraction ---


def extract_image_urls(html: str) -> dict[str, list[str]]:
    """Extract MTF chart and construction diagram URLs from TTartisan product page.

    TTartisan uses several naming conventions:
    - Specification-MTF.webp (MTF chart)
    - Specification-OD-EN.webp (optical design / construction diagram)
    - Specification-1.webp or Specification-1-M.webp (MTF chart, older pattern)
    - Specification-2-EN.webp or Specification-2-M-EN.webp (construction, older)
    - Legacy: /static/upload/image/{date}/{timestamp}.jpg (must identify manually)
    """
    urls: dict[str, list[str]] = {"mtf": [], "construction": []}

    # All image src/href on the page
    all_imgs = re.findall(r'(?:src|href)="([^"]+\.(?:webp|jpg|png))"', html, re.IGNORECASE)

    for img in all_imgs:
        full_url = _resolve_url(img)
        lower = img.lower()

        # Skip SLR-mount variants — we only want mirrorless (X/GFX mount)
        if "-slr" in lower:
            continue

        # Named MTF pattern
        if "specification-mtf" in lower:
            if full_url not in urls["mtf"]:
                urls["mtf"].append(full_url)
        # Named construction pattern (OD = Optical Design)
        elif "specification-od" in lower:
            if full_url not in urls["construction"]:
                urls["construction"].append(full_url)
        # Numbered pattern: Specification-1 = MTF, Specification-2 = construction
        # May have extra segments like -M, -EN, -M-EN, -SLR-EN
        elif re.search(r"specification-1(?:-[a-z]+)*\.(?:webp|jpg|png)", lower):
            if full_url not in urls["mtf"]:
                urls["mtf"].append(full_url)
        elif re.search(r"specification-2(?:-[a-z]+)*\.(?:webp|jpg|png)", lower):
            if full_url not in urls["construction"]:
                urls["construction"].append(full_url)

    return urls


def _resolve_url(src: str) -> str:
    """Resolve a potentially relative TTartisan image URL to absolute."""
    if src.startswith("http"):
        return src
    if src.startswith("/"):
        return BASE_URL + src
    return BASE_URL + "/" + src


def download_image(url: str, dest: Path, min_size: int = 500) -> bool:
    """Download an image to dest. Returns True on success."""
    if dest.exists():
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if len(data) < min_size:
                return False
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"    WARN: download failed for {dest.name}: {e}")
        return False
