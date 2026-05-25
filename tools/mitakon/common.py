"""Shared utilities for Mitakon (Zhongyi Optics) lens data tools.

Provides lens extraction from lenses.ts, slug generation, page fetching
via SeleniumBase UC mode (zyoptics.net blocks urllib and Playwright),
optical spec parsing, and image downloading.

zyoptics.net page structure (WooCommerce):
- Panel 0: product description (contains special elements in prose)
- Panel 1: spec table (elements/groups, aperture, focus, weight, etc.)
- Panel 3+: embedded videos, FAQ
- Gallery: product photos only (no MTF charts or construction diagrams)
"""

import hashlib
import re
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"
CACHE_DIR = ROOT / ".cache" / "fetch"


# --- Lens extraction ---


def extract_mitakon_lenses() -> list[dict]:
    """Extract Mitakon lens model + officialUrl from lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    blocks = re.split(r"(?=\{\s*\n\s*brand:)", content)
    lenses = []
    for block in blocks:
        if 'brand: "Mitakon"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        url_m = re.search(r'officialUrl:\s*\n?\s*"([^"]+)"', block)
        mount_m = re.search(r'mount:\s*"([^"]+)"', block)
        if model_m and url_m:
            lenses.append({
                "model": model_m.group(1),
                "url": url_m.group(1),
                "mount": mount_m.group(1) if mount_m else "X",
            })
    return lenses


def model_to_slug(model: str) -> str:
    """Convert model name to file slug: Speedmaster 35mm f/0.95 Mk II -> mitakon-speedmaster-35mm-f0-95-mk-ii"""
    slug = model.lower().replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return f"mitakon-{slug}"


# --- Caching ---


def _cache_path(url: str, html: bool = False) -> Path:
    h = hashlib.sha256(url.encode()).hexdigest()[:16]
    suffix = ".html" if html else ".txt"
    return CACHE_DIR / f"mitakon-{h}{suffix}"


def read_cache(url: str, html: bool = False) -> str | None:
    path = _cache_path(url, html)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def write_cache(url: str, content: str, html: bool = False) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(url, html)
    path.write_text(content, encoding="utf-8")


# --- Page fetching (SeleniumBase UC mode) ---


@contextmanager
def browser_session():
    """Context manager yielding a SeleniumBase UC session."""
    from seleniumbase import SB

    with SB(uc=True, headless=True) as sb:
        yield sb


def fetch_page(sb, url: str, wait_s: int = 5) -> tuple[str, str]:
    """Fetch a page via SeleniumBase UC mode. Returns (text, html). Uses cache."""
    cached_text = read_cache(url)
    cached_html = read_cache(url, html=True)
    if cached_text and cached_html:
        return cached_text, cached_html

    sb.open(url)
    sb.sleep(wait_s)
    sb.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    sb.sleep(2)

    html = sb.get_page_source()
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()

    write_cache(url, text)
    write_cache(url, html, html=True)
    return text, html


# --- Spec extraction ---


TEXT_NUMS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
}


def _normalize_nums(text: str) -> str:
    result = text
    for word, digit in TEXT_NUMS.items():
        result = re.sub(rf"\b{word}\b", digit, result, flags=re.IGNORECASE)
    return result


def extract_specs(html: str) -> dict:
    """Extract optical specs from zyoptics.net product page HTML.

    Returns dict with keys: elements, groups, special, coating.

    zyoptics.net uses WooCommerce tabs:
    - Panel 0 (description): prose with special element mentions
    - Panel 1 (specs): structured spec table with elements/groups
    """
    specs: dict = {}

    # Extract text from WooCommerce panels
    panels = re.findall(
        r'class="woocommerce-Tabs-panel[^"]*"[^>]*>(.*?)</div>',
        html, re.DOTALL,
    )

    full_text = re.sub(r"<[^>]+>", " ", html)
    full_text = re.sub(r"\s+", " ", full_text)

    # Elements/groups: prefer spec table (panel 1) over description prose
    eg_pattern = r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?"
    m = None
    if len(panels) > 1:
        panel1_text = re.sub(r"<[^>]+>", " ", panels[1])
        panel1_text = re.sub(r"\s+", " ", panel1_text)
        m = re.search(eg_pattern, panel1_text, re.IGNORECASE)
    if not m:
        m = re.search(eg_pattern, full_text, re.IGNORECASE)
    if m:
        specs["elements"] = int(m.group(1))
        specs["groups"] = int(m.group(2))

    # Special elements from description panel (panel 0) + full text
    normalized = _normalize_nums(full_text)
    specs["special"] = _extract_special_elements(normalized)

    # Coating
    specs["coating"] = _extract_coating(full_text)

    return specs


def _first_match_count(text: str, patterns: list[str]) -> int:
    """Return the count from the first regex match, or 0 if none."""
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return 0


def _extract_special_elements(text: str) -> list[str]:
    """Extract special element types from product description text.

    Mitakon uses:
    - ED / extra-low dispersion
    - UD / ultra-low dispersion
    - HRI / high-refractive index (also "extra-high refractive index")
    - LD / low dispersion
    - aspherical
    - APO / apochromatic

    The 35mm f/0.95 page lists "Two Extra-High Refractive Index Elements"
    and "One High Refractive Index Element" separately — both are HRI glass,
    so we sum all HRI matches into a single count.
    """
    special = []

    # Patterns that yield a single match per type
    single_patterns = [
        ("aspherical", [
            r"(\d+)\s*(?:aspherical|asph\.?)\s*(?:lens|element|glass)",
            r"(\d+)\s*pcs?\s+(?:of\s+)?aspherical",
        ]),
        ("ED", [
            r"(\d+)\s*(?:extra[- ]low[- ]dispersion|ED)\s*(?:\([^)]*\)\s*)?(?:lens|element|glass)",
            r"(\d+)\s*pcs?\s+(?:of\s+)?(?:extra[- ]low[- ]dispersion|ED)",
        ]),
        ("UD", [
            r"(\d+)\s*(?:ultra[- ]low[- ]dispersion|UD)\s*(?:\([^)]*\)\s*)?(?:lens|element|glass)",
            r"(\d+)\s*pcs?\s+(?:of\s+)?(?:ultra[- ]low[- ]dispersion|UD)",
            r"(\d+)\s*pcs?\s+(?:of\s+)?UD\s*\(",
        ]),
        ("LD", [
            r"(\d+)\s*(?:low[- ]dispersion|LD)\s*(?:lens|element|glass)",
            r"(\d+)\s*pcs?\s+(?:of\s+)?(?:low[- ]dispersion|LD)",
        ]),
    ]

    for label, patterns in single_patterns:
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                special.append(f"{m.group(1)} {label}")
                break

    # HRI: sum distinct variants ("extra-high refractive" + "high refractive")
    # Pages repeat the same data in key features, description, and JSON-LD,
    # so we deduplicate by count value — same count = same data repeated.
    # Different counts (e.g. "2 Extra-High RI" + "1 High RI") = distinct types.
    hri_extra = _first_match_count(text, [
        r"(\d+)\s*(?:extra[- ]high[- ]refract(?:ive|ion)[- ]?(?:index)?)\s*(?:\([^)]*\)\s*)?(?:lens|element|glass)e?s?",
        r"(\d+)\s*pcs?\s+(?:of\s+)?(?:extra[- ]high[- ]refract(?:ive|ion)[- ]?(?:index)?)",
    ])
    hri_plain = _first_match_count(text, [
        r"(\d+)\s*(?:high[- ]?refract(?:ive|ion)[- ]?(?:index)?|HRI)\s*(?:\([^)]*\)\s*)?(?:lens|element|glass)",
        r"(\d+)\s*pcs?\s+(?:of\s+)?(?:high[- ]?refract(?:ive|ion)[- ]?(?:index)?|HRI)",
    ])
    # If both "extra-high" and plain "high" are found with different counts,
    # they are distinct element types — sum them.
    # If only plain "high" is found, it covers all HRI.
    if hri_extra > 0 and hri_plain > 0:
        special.append(f"{hri_extra + hri_plain} HRI")
    elif hri_plain > 0:
        special.append(f"{hri_plain} HRI")
    elif hri_extra > 0:
        special.append(f"{hri_extra} HRI")

    return special


def _extract_coating(text: str) -> list[str]:
    """Extract coating information from page text."""
    coating: list[str] = []
    if re.search(r"nano[- ]?coat", text, re.IGNORECASE):
        coating.append("Nano coating")
    elif re.search(r"super[- ]?multi[- ]?coat", text, re.IGNORECASE):
        coating.append("Super multi-coating")
    elif re.search(r"MC\s+Multi[- ]?Layer", text, re.IGNORECASE):
        coating.append("MC Multi-Layer")
    elif re.search(r"multi[- ]?layer\s+coat", text, re.IGNORECASE):
        coating.append("Multi-layer coating")
    elif re.search(r"multi[- ]?coat", text, re.IGNORECASE):
        coating.append("Multi-coating")
    return coating


# --- Image downloading ---


def download_image(url: str, dest: Path, min_size: int = 500) -> bool:
    """Download an image to dest. Returns True on success."""
    import urllib.request

    if dest.exists():
        return True

    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": user_agent})
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
