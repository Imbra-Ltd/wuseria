"""Shared utilities for Tamron lens data tools.

Provides lens extraction from lenses.ts, slug generation, page fetching,
optical spec parsing, and image downloading for Tamron product pages.
"""

import hashlib
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"
CACHE_DIR = ROOT / ".cache" / "fetch"

BASE_URL = "https://www.tamron.com"

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
    return bool([f for f in specs_dir.glob(f"{slug}-mtf*") if f.suffix in (".png", ".jpg", ".svg")])


def has_construction_image(slug: str) -> bool:
    """Check if an optical construction diagram exists in optical-specs/{slug}/."""
    specs_dir = OPTICAL_SPECS_DIR / slug
    if not specs_dir.is_dir():
        return False
    return bool([f for f in specs_dir.glob(f"{slug}-construction*") if f.suffix in (".png", ".jpg", ".svg")])


# --- Lens extraction ---


def extract_tamron_lenses() -> list[dict]:
    """Extract Tamron lens model + officialUrl from lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    blocks = re.split(r"(?=\{\s*\n\s*brand:)", content)
    lenses = []
    for block in blocks:
        if 'brand: "Tamron"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        url_m = re.search(r'officialUrl:\s*\n?\s*"([^"]+)"', block)
        if model_m and url_m:
            lenses.append({"model": model_m.group(1), "url": url_m.group(1)})
    return lenses


def model_to_slug(model: str) -> str:
    """Convert model name to file slug: 11-20mm f/2.8 Di III-A RXD -> tamron-11-20mm-f2-8-di-iii-a-rxd"""
    slug = model.lower().replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return f"tamron-{slug}"


def url_to_code(url: str) -> str:
    """Extract the model code from a Tamron URL.

    https://www.tamron.com/global/consumer/lenses/b060/ -> b060
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
    """Extract optical specs from Tamron product page HTML.

    Tamron pages have specs on two pages:
    - Main page: special elements (LD, XLD, GM aspherical, hybrid aspherical),
      coating (BBAR G2, etc.)
    - Spec page (/spec.html): elements/groups count

    This function parses both — call it with concatenated HTML from both pages.

    Returns dict with keys: elements, groups, special, coating.
    """
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    # Normalize text numbers to digits
    for word, digit in TEXT_NUMS.items():
        text = re.sub(rf"\b{word}\b", digit, text, flags=re.IGNORECASE)

    specs: dict = {}

    # Elements and groups
    m = re.search(
        r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?",
        text, re.IGNORECASE,
    )
    if m:
        specs["elements"] = int(m.group(1))
        specs["groups"] = int(m.group(2))

    # Special elements — Tamron uses LD, XLD, GM (Glass Molded Aspherical),
    # hybrid aspherical
    special = []

    type_patterns = [
        ("GM aspherical", [
            r"(\d+)\s*(?:x\s+)?GM\b",
            r"(\d+)\s*Glass\s+Molded\s+Aspherical",
        ]),
        ("hybrid aspherical", [
            r"(\d+)\s*(?:x\s+)?hybrid\s+aspherical",
            r"(\d+)\s*(?:x\s+)?aspherical\s+hybrid",
        ]),
        ("XLD", [
            r"(\d+)\s*(?:x\s+)?XLD\b",
            r"(\d+)\s*eXtra\s+Low\s+Dispersion",
        ]),
        ("LD", [
            r"(\d+)\s*(?:x\s+)?LD\s*\(Low\s+Dispersion\)",
            r"(\d+)\s*Low\s+Dispersion",
            r"(\d+)\s*(?:x\s+)?LD\b",
        ]),
    ]

    for label, patterns in type_patterns:
        for pat in patterns:
            m3 = re.search(pat, text, re.IGNORECASE)
            if m3:
                special.append(f"{m3.group(1)} {label}")
                break
        else:
            # Fallback: mentioned without count
            fallback_patterns = {
                "GM aspherical": r"\bGM\s*\(Glass\s+Molded\s+Aspherical\)",
                "hybrid aspherical": r"\bhybrid\s+aspherical",
                "XLD": r"\bXLD\b",
                "LD": r"\bLD\s*\(Low\s+Dispersion\)",
            }
            pat = fallback_patterns.get(label)
            if pat and re.search(pat, text, re.IGNORECASE):
                special.append(f"~1 {label}")

    specs["special"] = special

    # Coating — Tamron uses BBAR G2, BBAR, fluorine
    coating = []
    if re.search(r"BBAR\s+G2", text, re.IGNORECASE):
        coating.append("BBAR G2")
    elif re.search(r"BBAR\b", text, re.IGNORECASE):
        coating.append("BBAR")
    if re.search(r"\bfluorine\b", text, re.IGNORECASE):
        coating.append("fluorine")

    specs["coating"] = coating

    return specs


# --- Image extraction ---


def extract_image_urls(html: str, code: str) -> dict[str, list[str]]:
    """Extract MTF chart and construction diagram URLs from Tamron spec page.

    Tamron uses SVG format for technical diagrams:
    - MTF: {code}_mtf_{focal}_en.svg
    - Construction: {code}_lens-construction_en.svg

    URLs may be relative or on S3 (s3-ap-northeast-1.amazonaws.com/tamron-docs/).
    """
    urls: dict[str, list[str]] = {"mtf": [], "construction": []}

    # Match MTF chart SVGs
    mtf_pattern = re.compile(
        r'(?:src|href)="([^"]*' + re.escape(code) + r'_mtf[^"]*\.svg)"',
        re.IGNORECASE,
    )
    for m in mtf_pattern.finditer(html):
        url = _resolve_tamron_url(m.group(1))
        if url not in urls["mtf"]:
            urls["mtf"].append(url)

    # Match construction diagram SVGs
    constr_pattern = re.compile(
        r'(?:src|href)="([^"]*' + re.escape(code) + r'_lens-construction[^"]*\.svg)"',
        re.IGNORECASE,
    )
    for m in constr_pattern.finditer(html):
        url = _resolve_tamron_url(m.group(1))
        if url not in urls["construction"]:
            urls["construction"].append(url)

    return urls


def _resolve_tamron_url(src: str) -> str:
    """Resolve a potentially relative Tamron image URL to absolute."""
    if src.startswith("http"):
        return src
    if src.startswith("/"):
        return BASE_URL + src
    return BASE_URL + "/" + src


def download_image(url: str, dest: Path, min_size: int = 200) -> bool:
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
