"""Shared utilities for Sigma lens data tools.

Provides lens extraction from lenses.ts, slug generation, page fetching,
optical spec parsing, and image downloading for Sigma product pages.
"""

import hashlib
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"
CACHE_DIR = ROOT / ".cache" / "fetch"

BASE_URL = "https://www.sigma-global.com"

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


def extract_sigma_lenses() -> list[dict]:
    """Extract Sigma lens model + officialUrl from lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    blocks = re.split(r"(?=\{\s*\n\s*brand:)", content)
    lenses = []
    for block in blocks:
        if 'brand: "Sigma"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        url_m = re.search(r'officialUrl:\s*\n?\s*"([^"]+)"', block)
        if model_m and url_m:
            lenses.append({"model": model_m.group(1), "url": url_m.group(1)})
    return lenses


def model_to_slug(model: str) -> str:
    """Convert model name to file slug: 16mm f/1.4 DC DN C -> sigma-16mm-f1-4-dc-dn-c"""
    slug = model.lower().replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return f"sigma-{slug}"


def url_to_code(url: str) -> str:
    """Extract the product code from a Sigma URL.

    https://www.sigma-global.com/en/lenses/c017_16_14/ -> c017_16_14
    """
    return url.rstrip("/").split("/")[-1]


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


def extract_specs(html: str) -> dict:
    """Extract optical specs from Sigma product page HTML.

    Returns dict with keys: elements, groups, special, coating.
    """
    # Strip HTML tags for text matching
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    specs: dict = {}

    # Normalize text numbers
    for word, digit in TEXT_NUMS.items():
        text = re.sub(rf"\b{word}\b", digit, text, flags=re.IGNORECASE)

    # Elements and groups
    m = re.search(
        r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?",
        text, re.IGNORECASE,
    )
    if m:
        specs["elements"] = int(m.group(1))
        specs["groups"] = int(m.group(2))

    # Special elements — Sigma uses FLD, SLD, ELD, aspherical
    # Some pages give explicit counts ("3 FLD"), others just mention types
    # in the diagram legend ("SLD glass", "Aspherical lens"). For uncounted
    # mentions we fall back to counting occurrences in the text.
    special = []

    type_patterns = [
        ("aspherical", [
            r"(\d+)\s*(?:molded\s+glass\s+)?aspherical\s+(?:lens|element)",
            r"(\d+)\s*aspherical\b",
        ]),
        ("FLD", [
            r"(\d+)\s*FLD\b",
        ]),
        ("SLD", [
            r"(\d+)\s*SLD\b",
        ]),
        ("ELD", [
            r"(\d+)\s*ELD\b",
        ]),
    ]

    for label, patterns in type_patterns:
        found = False
        for pat in patterns:
            m3 = re.search(pat, text, re.IGNORECASE)
            if m3:
                special.append(f"{m3.group(1)} {label}")
                found = True
                break

        # Fallback: type mentioned without a count (diagram legend, prose).
        # Default to 1 and mark with ~ to flag for manual verification
        # against the construction diagram image.
        if not found:
            fallback_patterns = {
                "aspherical": r"\b(?:aspherical\s+(?:lens|element)|aspherical\b)",
                "FLD": r"\bFLD\s+(?:glass|element|lens)",
                "SLD": r"\bSLD\s+(?:glass|element|lens)",
                "ELD": r"\bELD\s+(?:glass|element|lens)",
            }
            pat = fallback_patterns.get(label)
            if pat and re.search(pat, text, re.IGNORECASE):
                special.append(f"~1 {label}")

    specs["special"] = special

    # Coating — Sigma uses "Super Multi-Layer Coating"
    coating = []
    if re.search(r"Super\s+Multi[- ]Layer\s+Coating", text, re.IGNORECASE):
        coating.append("Super Multi-Layer Coating")

    specs["coating"] = coating

    return specs


# --- Image extraction ---


def extract_image_urls(html: str, code: str) -> dict[str, list[str]]:
    """Extract MTF chart and construction diagram URLs from page HTML.

    Sigma pages use several naming variants:
    - {code}_specification_01_N.png   (older pages)
    - {code}_specification_01.png     (newer pages, no sub-number)
    - {code}_specification_2.png      (older pages, no leading zero)
    - /images/{code}_specification_*  (some pages use images/ subdir)
    - MTF charts use _specification_02_*

    Primes have 2 MTF charts (diffraction + geometrical).
    Zooms have 4+ MTF charts (multiple focal lengths x 2 types).
    """
    urls: dict[str, list[str]] = {"mtf": [], "construction": []}

    # Match all specification images — flexible pattern for varying naming
    pattern = re.compile(
        r'(?:src|href)="([^"]*' + re.escape(code) + r'_specification[^"]*\.png)"',
        re.IGNORECASE,
    )

    for m in pattern.finditer(html):
        src = m.group(1)
        full_url = src if src.startswith("http") else BASE_URL + src

        # Construction diagrams: _specification_01 or _specification_2
        # (but NOT _specification_02_ which are MTF charts)
        if re.search(r"_specification_(?:01(?:_\d+)?|[12])\.png$", src, re.IGNORECASE):
            if full_url not in urls["construction"]:
                urls["construction"].append(full_url)
        elif "_specification_02_" in src:
            if full_url not in urls["mtf"]:
                urls["mtf"].append(full_url)

    return urls


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
