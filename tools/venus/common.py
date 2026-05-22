"""Shared utilities for Venus Laowa lens data tools.

Provides lens extraction from lenses.ts, slug generation, page fetching,
optical spec parsing, and image downloading for Venus Laowa product pages.

Venus Laowa (venuslens.net) uses WordPress/WooCommerce with Avada theme
behind Cloudflare Turnstile. Plain urllib is blocked (403). SeleniumBase
UC mode is required for fetching; cached HTML is parsed with plain regex.
"""

import hashlib
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"
CACHE_DIR = ROOT / ".cache" / "fetch"

BASE_URL = "https://www.venuslens.net"

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
    return bool([f for f in specs_dir.glob(f"{slug}-construction*") if f.suffix in (".png", ".jpg", ".webp", ".svg")])


# --- Lens extraction ---


def extract_venus_lenses() -> list[dict]:
    """Extract Venus Laowa lens model + officialUrl from lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    blocks = re.split(r"(?=\{\s*\n\s*(?://[^\n]*\n\s*)*brand:)", content)
    lenses = []
    for block in blocks:
        if 'brand: "Venus Laowa"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        url_m = re.search(r'officialUrl:\s*\n?\s*"([^"]+)"', block)
        if model_m and url_m:
            lenses.append({"model": model_m.group(1), "url": url_m.group(1)})
    return lenses


def model_to_slug(model: str) -> str:
    """Convert model name to file slug: Argus 33mm f/0.95 CF APO -> venus-laowa-argus-33mm-f0-95-cf-apo"""
    slug = model.lower().replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return f"venus-laowa-{slug}"


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


def fetch_page_seleniumbase(url: str, wait_s: int = 4) -> str:
    """Fetch a page using SeleniumBase UC mode to bypass Cloudflare.

    venuslens.net uses Cloudflare Turnstile which blocks plain urllib and
    standard Playwright. SeleniumBase UC (Undetected Chrome) mode suppresses
    automation indicators and typically passes the challenge automatically.
    """
    cached = read_cache(url)
    if cached:
        return cached

    try:
        from seleniumbase import Driver
    except ImportError:
        print("ERROR: seleniumbase not installed. Run: py -m pip install seleniumbase")
        raise

    import time

    driver = Driver(uc=True, headless=False)
    try:
        driver.uc_open_with_reconnect(url, wait_s)
        time.sleep(3)

        html = driver.page_source

        # Check if still on Cloudflare challenge
        if "_cf_chl" in html or "security verification" in html.lower():
            print("  Cloudflare challenge detected, attempting uc_gui_click_captcha...")
            try:
                driver.uc_gui_click_captcha()
                time.sleep(5)
                html = driver.page_source
            except Exception:
                pass

        if "_cf_chl" in html or "security verification" in html.lower():
            print("  WARNING: Could not bypass Cloudflare for this page")
            return html

        # Scroll to trigger lazy-loaded images
        driver.execute_script("""
            const delay = ms => new Promise(r => setTimeout(r, ms));
            (async () => {
                const height = document.body.scrollHeight;
                const step = window.innerHeight;
                for (let y = 0; y < height; y += step) {
                    window.scrollTo(0, y);
                    await delay(200);
                }
                window.scrollTo(0, 0);
                await delay(500);
            })();
        """)
        time.sleep(2)

        html = driver.page_source
    finally:
        driver.quit()

    write_cache(url, html)
    return html


# --- Spec extraction ---


def extract_specs(html: str) -> dict:
    """Extract optical specs from Venus Laowa product page HTML.

    Venus Laowa pages embed specs in prose text and in a Specifications
    tab section. Patterns found:
    - "12 elements in 8 groups" (in Lens Structure row or prose)
    - "(4 ED elements)" or "(2 aspherical + 3 ED)" as parenthetical
    - Coating mentioned in prose (e.g. "Frog Eye Coating")

    Returns dict with keys: elements, groups, special, coating.
    """
    # Strip HTML tags for text matching
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    specs: dict = {}

    # Elements and groups
    m = re.search(
        r"(\d+)\s*elements?\s+in\s+(\d+)\s*groups?",
        text, re.IGNORECASE,
    )
    if m:
        specs["elements"] = int(m.group(1))
        specs["groups"] = int(m.group(2))

    # Special elements — Venus Laowa uses ED, aspherical, UHR in parentheses
    # after the structure line, or in descriptive prose nearby.
    # IMPORTANT: Do NOT search the full page text for short patterns like
    # "\dED" — CSS hex colors like #8ed1fc produce false matches.
    special = []

    # Extract the parenthetical after "X elements in Y groups (...)".
    # This is the most reliable source, e.g. "(4 ED elements)" or
    # "(2pcs of Aspherical Elements+ 2 pcs of Extra-low Dispersion Elements)"
    paren_m = re.search(
        r"elements?\s+in\s+\d+\s*groups?\s*\(([^)]+)\)",
        text, re.IGNORECASE,
    )
    paren_text = paren_m.group(1) if paren_m else ""

    # Also extract prose text — Venus Laowa mentions special elements in
    # product descriptions far from the spec table. Use the full text BUT
    # only match patterns that include a qualifying noun (element/glass/lens)
    # to avoid CSS hex color false positives like #8ed1fc.
    #
    # Also handle text numbers: "a pair of" = 2, "three" = 3, etc.
    TEXT_NUMS = {
        "a pair of": "2", "one": "1", "two": "2", "three": "3",
        "four": "4", "five": "5", "six": "6",
    }
    normalized = text
    for word, digit in TEXT_NUMS.items():
        normalized = re.sub(rf"\b{word}\b", digit, normalized, flags=re.IGNORECASE)

    # Combine parenthetical (highest priority) + full normalized text
    search_text = (paren_text + " " + normalized) if paren_text else normalized

    type_patterns = [
        ("aspherical", [
            r"(\d+)\s*(?:pcs?\s+(?:of\s+)?)?aspherical\s*(?:elements?|lens(?:es)?|glass(?:es)?)",
        ]),
        ("ED", [
            r"(\d+)\s*(?:pcs?\s+(?:of\s+)?)?ED\s*(?:elements?|lens(?:es)?|glass(?:es)?)",
            r"(\d+)\s*(?:pcs?\s+(?:of\s+)?)?extra[- ]low\s+dispersion\s*(?:elements?|lens(?:es)?|glass(?:es)?)",
        ]),
        ("UHR", [
            r"(\d+)\s*(?:pcs?\s+(?:of\s+)?)?(?:UHR|ultra\s+high\s+refraction)\s*(?:elements?|lens(?:es)?|glass(?:es)?)",
        ]),
        ("HR", [
            r"(\d+)\s*(?:highly\s+refractive)\s*(?:elements?|lens(?:es)?|glass(?:es)?)",
        ]),
    ]

    for label, patterns in type_patterns:
        for pat in patterns:
            m2 = re.search(pat, search_text, re.IGNORECASE)
            if m2:
                special.append(f"{m2.group(1)} {label}")
                break

    specs["special"] = special

    # Coating — Venus Laowa uses "Frog Eye Coating" (FEC) on some lenses
    coating = []
    if re.search(r"Frog\s+Eye\s+Coating", text, re.IGNORECASE):
        coating.append("Frog Eye Coating")
    if re.search(r"multi[- ]?coating", text, re.IGNORECASE):
        coating.append("Multi-Coating")

    specs["coating"] = coating

    return specs


# --- Image extraction ---


def extract_image_urls(html: str) -> dict[str, list[str]]:
    """Extract MTF chart and construction diagram URLs from page HTML.

    Venus Laowa pages use naming patterns like:
    - *_MTF.png or *_MTF_*.png for MTF charts
    - *_Lens-Structure.png or *_Lens_Structure.png for construction diagrams
    - *_Optical-Design.png or *_optical*.png variants
    - URL-encoded Chinese: %E5%85%89%E8%B7%AF%E5%9B%BE (光路图 = optical path diagram)
    """
    urls: dict[str, list[str]] = {"mtf": [], "construction": []}

    # Match all image src attributes
    for m in re.finditer(r'(?:src|data-src|data-lazy-src)="([^"]+\.(?:jpg|png|webp|svg)[^"]*)"', html, re.IGNORECASE):
        src = m.group(1)
        lower = src.lower()

        # Skip tiny thumbnails and unrelated images
        if "150x" in lower or "100x" in lower or "icon" in lower:
            continue

        full_url = src if src.startswith("http") else BASE_URL + src

        if re.search(r"mtf", lower):
            if full_url not in urls["mtf"]:
                urls["mtf"].append(full_url)
        elif re.search(
            r"lens[_-]?structure|optical[_-]?design|construction|cross[_-]?section"
            r"|%E5%85%89%E8%B7%AF%E5%9B%BE"  # 光路图 = optical path diagram (URL-encoded)
            r"|%E7%BB%93%E6%9E%84"  # 结构 = structure (URL-encoded)
            r"|%E9%95%9C%E7%BB%84"  # 镜组 = lens group (URL-encoded)
            r"|\u5149\u8DEF\u56FE"  # 光路图 = optical path diagram (decoded)
            r"|\u7ED3\u6784"  # 结构 = structure (decoded)
            r"|\u955C\u7EC4",  # 镜组 = lens group (decoded)
            lower,
        ):
            if full_url not in urls["construction"]:
                urls["construction"].append(full_url)

    return urls


def _encode_url(url: str) -> str:
    """Percent-encode non-ASCII characters in a URL path."""
    from urllib.parse import quote, urlparse, urlunparse

    parsed = urlparse(url)
    encoded_path = quote(parsed.path, safe="/:@!$&'()*+,;=-._~")
    return urlunparse(parsed._replace(path=encoded_path))


def download_image(url: str, dest: Path, min_size: int = 500) -> bool:
    """Download an image to dest. Returns True on success.

    First tries plain urllib (fast). Falls back to SeleniumBase if blocked
    by Cloudflare (403).
    """
    if dest.exists():
        return True
    url = _encode_url(url)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if len(data) < min_size:
                return False
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        return True
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return _download_image_via_browser(url, dest, min_size)
        print(f"    WARN: download failed for {dest.name}: {e}")
        return False
    except Exception as e:
        print(f"    WARN: download failed for {dest.name}: {e}")
        return False


def _download_image_via_browser(url: str, dest: Path, min_size: int = 500) -> bool:
    """Download an image via SeleniumBase when Cloudflare blocks direct access."""
    try:
        from seleniumbase import Driver
    except ImportError:
        print(f"    WARN: seleniumbase not available for fallback download")
        return False

    import base64
    import time

    driver = Driver(uc=True, headless=False)
    try:
        driver.uc_open_with_reconnect(url, 4)
        time.sleep(2)

        # Use JavaScript to fetch the image as base64 via canvas
        data_url = driver.execute_script("""
            return new Promise((resolve, reject) => {
                const img = new Image();
                img.crossOrigin = 'anonymous';
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    canvas.width = img.naturalWidth;
                    canvas.height = img.naturalHeight;
                    canvas.getContext('2d').drawImage(img, 0, 0);
                    resolve(canvas.toDataURL('image/png'));
                };
                img.onerror = () => reject('failed');
                img.src = arguments[0];
            });
        """, url)

        if not data_url or not data_url.startswith("data:"):
            return False

        # Strip the data URL prefix and decode
        b64_data = data_url.split(",", 1)[1]
        img_bytes = base64.b64decode(b64_data)

        if len(img_bytes) < min_size:
            return False

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(img_bytes)
        return True
    except Exception as e:
        print(f"    WARN: browser download failed for {dest.name}: {e}")
        return False
    finally:
        driver.quit()
