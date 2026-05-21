"""Shared utilities for Tokina lens data tools.

Provides lens extraction from lenses.ts, slug generation, page fetching,
optical spec parsing, and image downloading for Tokina product pages.
"""

import hashlib
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"
CACHE_DIR = ROOT / ".cache" / "fetch"

BASE_URL = "https://tokinalens.com"

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


def extract_tokina_lenses() -> list[dict]:
    """Extract Tokina lens model + officialUrl from lenses.ts.

    Tokina's site uses underscores in product slugs but the officialUrl
    in lenses.ts may use hyphens. This function normalises the URL to
    the underscore form that the site actually serves.
    """
    content = LENSES_TS.read_text(encoding="utf-8")
    blocks = re.split(r"(?=\{\s*\n\s*brand:)", content)
    lenses = []
    for block in blocks:
        if 'brand: "Tokina"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        url_m = re.search(r'officialUrl:\s*\n?\s*"([^"]+)"', block)
        if model_m and url_m:
            url = _normalise_tokina_url(url_m.group(1))
            lenses.append({"model": model_m.group(1), "url": url})
    return lenses


def _normalise_tokina_url(url: str) -> str:
    """Convert hyphenated product slug to underscore form.

    https://tokinalens.com/product/atx-m-23mm-f1-4-x/
    -> https://tokinalens.com/product/atx_m_23mm_f1_4_x/
    """
    prefix = BASE_URL + "/product/"
    if not url.startswith(prefix):
        return url
    slug = url[len(prefix):]
    slug = slug.replace("-", "_")
    return prefix + slug


def model_to_slug(model: str) -> str:
    """Convert model name to file slug: atx-m 23mm f/1.4 X -> tokina-atx-m-23mm-f1-4-x"""
    slug = model.lower().replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return f"tokina-{slug}"


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


def extract_specs(html: str) -> dict:
    """Extract optical specs from Tokina product page HTML.

    Returns dict with keys: elements, groups, special, coating.
    """
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    specs: dict = {}

    # Elements and groups
    m = re.search(
        r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?",
        text, re.IGNORECASE,
    )
    if m:
        specs["elements"] = int(m.group(1))
        specs["groups"] = int(m.group(2))

    # Special elements — Tokina uses SD (Super Low Dispersion),
    # aspherical, ED
    special = []

    type_patterns = [
        ("aspherical", [
            r"(\d+)\s*aspherical\s*(?:lens|element)",
            r"(\d+)\s*aspherical\b",
        ]),
        ("SD", [
            r"(\d+)\s*(?:Super\s+)?Low[- ]Dispersion\s*\(SD\)",
            r"(\d+)\s*SD\s+glass",
            r"(\d+)\s*SD\b",
        ]),
        ("ED", [
            r"(\d+)\s*ED\s+(?:glass|element|lens)",
            r"(\d+)\s*ED\b",
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

        if not found:
            fallback_patterns = {
                "aspherical": r"\baspherical\s+(?:lens|element)",
                "SD": r"\b(?:Super\s+)?Low[- ]Dispersion\b|\bSD\s+glass",
                "ED": r"\bED\s+(?:glass|element|lens)",
            }
            pat = fallback_patterns.get(label)
            if pat and re.search(pat, text, re.IGNORECASE):
                special.append(f"~1 {label}")

    specs["special"] = special

    # Coating — Tokina uses "Multi-coating"
    coating = []
    if re.search(r"Multi[- ]?coating", text, re.IGNORECASE):
        coating.append("Multi-coating")

    specs["coating"] = coating

    return specs


# --- Image extraction ---


def extract_image_urls(html: str) -> dict[str, list[str]]:
    """Extract MTF chart and construction diagram URLs from Tokina product page.

    Tokina uses two naming conventions:
    - Named: atxm_{focal}_mtf.jpg, atxm_{focal}_constr.jpg
    - Numbered: 05_1.png (construction), 05_2.png (MTF), 05_3.png (MTF)

    Images are in /uploads/images/catalog/product/atx-m/{folder}/
    """
    urls: dict[str, list[str]] = {"mtf": [], "construction": []}

    # Named patterns: *_mtf.jpg, *_constr.jpg
    for m in re.finditer(r'(?:src|href)="([^"]*_constr[^"]*\.(?:jpg|png))', html, re.IGNORECASE):
        url = _resolve_tokina_url(m.group(1))
        if url not in urls["construction"]:
            urls["construction"].append(url)

    for m in re.finditer(r'(?:src|href)="([^"]*_mtf[^"]*\.(?:jpg|png))', html, re.IGNORECASE):
        url = _resolve_tokina_url(m.group(1))
        if url not in urls["mtf"]:
            urls["mtf"].append(url)

    # Numbered patterns (fallback for zoom lenses like 11-18mm):
    # Images in catalog/product/ with 05_N naming — 05_1 = construction, 05_2+ = MTF
    if not urls["construction"] and not urls["mtf"]:
        for m in re.finditer(
            r'(?:src|href)="([^"]*catalog/product/[^"]*05_(\d+)\.(?:jpg|png))',
            html, re.IGNORECASE,
        ):
            url = _resolve_tokina_url(m.group(1))
            idx = int(m.group(2))
            if idx == 1:
                if url not in urls["construction"]:
                    urls["construction"].append(url)
            else:
                if url not in urls["mtf"]:
                    urls["mtf"].append(url)

    return urls


def _resolve_tokina_url(src: str) -> str:
    """Resolve a potentially relative Tokina image URL to absolute."""
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
