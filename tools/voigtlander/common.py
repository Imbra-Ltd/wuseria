"""Shared utilities for Voigtlander lens data tools.

Provides lens extraction from lenses.ts, slug generation, page fetching,
optical spec parsing, and image downloading for Voigtlander product pages.

Voigtlander (Cosina) uses a Divi theme with JavaScript-rendered content.
Pages require Playwright for full rendering, but cached HTML from
pagefetch can be parsed with plain urllib for spec extraction.
"""

import hashlib
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"
CACHE_DIR = ROOT / ".cache" / "fetch"

BASE_URL = "https://www.voigtlaender.de"

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


def extract_voigtlander_lenses() -> list[dict]:
    """Extract Voigtlander lens model + officialUrl from lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    blocks = re.split(r"(?=\{\s*\n\s*(?://[^\n]*\n\s*)*brand:)", content)
    lenses = []
    for block in blocks:
        if 'brand: "Voigtlander"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        url_m = re.search(r'officialUrl:\s*\n?\s*"([^"]+)"', block)
        if model_m and url_m:
            lenses.append({"model": model_m.group(1), "url": url_m.group(1)})
    return lenses


def model_to_slug(model: str) -> str:
    """Convert model name to file slug: Nokton 23mm f/1.2 -> voigtlander-nokton-23mm-f1-2"""
    slug = model.lower().replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return f"voigtlander-{slug}"


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


def fetch_page_playwright(url: str, wait_ms: int = 3000) -> str:
    """Fetch a page using Playwright (headless Chromium). Returns rendered HTML.

    Voigtlander uses Divi theme with JS-rendered content, so Playwright
    is required to get the full page including spec tables and images.
    """
    cached = read_cache(url)
    if cached:
        return cached

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium")
        raise

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=USER_AGENT,
        )
        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(wait_ms)

        # Scroll to trigger lazy-loaded content, then expand Divi toggles
        page.evaluate("""async () => {
            const delay = ms => new Promise(r => setTimeout(r, ms));
            const height = document.body.scrollHeight;
            const step = window.innerHeight;
            for (let y = 0; y < height; y += step) {
                window.scrollTo(0, y);
                await delay(200);
            }
            window.scrollTo(0, 0);
            await delay(500);

            // Expand all closed Divi accordion/toggle sections
            document.querySelectorAll('.et_pb_toggle_close').forEach(el => {
                el.classList.remove('et_pb_toggle_close');
                el.classList.add('et_pb_toggle_open');
                const content = el.querySelector('.et_pb_toggle_content');
                if (content) {
                    content.style.display = 'block';
                    content.style.height = 'auto';
                    content.style.overflow = 'visible';
                }
            });
            await delay(300);
        }""")

        html = page.content()
        browser.close()

    write_cache(url, html)
    return html


# --- Spec extraction ---


def extract_specs(html: str) -> dict:
    """Extract optical specs from Voigtlander product page HTML.

    Voigtlander uses varying HTML structures across pages:
    - Some use <td> table pairs (older pages)
    - Some use <p> paragraphs (newer pages)

    Searches the full HTML text for element/group patterns.
    Returns dict with keys: elements, groups.
    """
    specs: dict = {}

    # Strip HTML tags for text-based search
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    m = re.search(
        r"(\d+)\s*(?:lenses?|elements?)\s+in\s+(\d+)\s*groups?",
        text, re.IGNORECASE,
    )
    if m:
        specs["elements"] = int(m.group(1))
        specs["groups"] = int(m.group(2))

    return specs


# --- Image extraction ---


def extract_image_urls(html: str) -> dict[str, list[str]]:
    """Extract construction diagram URLs from Voigtlander product page.

    Voigtlander does not publish MTF charts on their website.
    Construction diagrams use naming patterns like:
    - lens-construction-*.png/jpg
    - Lens-Construction-*.jpg
    - Linsenaufbau-*.jpg
    - Linsenschnitt-*.png
    """
    urls: dict[str, list[str]] = {"mtf": [], "construction": []}

    construction_patterns = [
        r'src="([^"]*(?:lens[-_]?construction|Linsenaufbau|Linsenschnitt)[^"]*\.(?:jpg|png|webp))',
    ]

    for pattern in construction_patterns:
        for m in re.finditer(pattern, html, re.IGNORECASE):
            url = _resolve_url(m.group(1))
            if url not in urls["construction"]:
                urls["construction"].append(url)

    return urls


def _resolve_url(src: str) -> str:
    """Resolve a potentially relative URL to absolute."""
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
