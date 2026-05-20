"""Shared utilities for Fujifilm lens data tools.

Provides lens extraction from lenses.ts, slug generation, file caching,
image downloading, and Playwright browser management.
"""

import hashlib
import re
import urllib.request
from contextlib import contextmanager
from pathlib import Path

from playwright.sync_api import sync_playwright, BrowserContext, Page

ROOT = Path(__file__).resolve().parent.parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"
OPTICAL_CONSTRUCTION_DIR = ROOT / "docs" / "optical-construction"
MTF_CHARTS_DIR = ROOT / "docs" / "mtf-charts"
CACHE_DIR = ROOT / ".cache" / "fetch"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


# --- Lens extraction ---


def extract_fujifilm_lenses() -> list[dict]:
    """Extract Fujifilm lens model + officialUrl from lenses.ts."""
    content = LENSES_TS.read_text(encoding="utf-8")
    pattern = re.compile(
        r'brand:\s*"Fujifilm"[\s\S]*?'
        r'model:\s*"([^"]+)"[\s\S]*?'
        r'officialUrl:\s*"([^"]+)"'
    )
    return [{"model": m.group(1), "url": m.group(2)} for m in pattern.finditer(content)]


def model_to_slug(model: str) -> str:
    """Convert model name to file slug: XF 14mm f/2.8 R -> fujifilm-xf-14mm-f2-8-r"""
    slug = model.lower().replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return f"fujifilm-{slug}"


def url_to_slug(url: str) -> str:
    """Extract the URL slug from an official Fujifilm product URL."""
    return url.rstrip("/").split("/")[-1]


def specs_url(official_url: str) -> str:
    """Derive specifications page URL from official product URL."""
    return official_url.rstrip("/") + "/specifications/"


# --- File existence checks ---


def has_construction_image(slug: str) -> bool:
    """Check if an optical construction image exists for the given slug."""
    return bool(list(OPTICAL_CONSTRUCTION_DIR.glob(f"{slug}.*")))


def has_mtf_charts(slug: str) -> bool:
    """Check if MTF charts exist in either mtf-charts/ or optical-specs/ for the given slug."""
    in_mtf = bool(list(MTF_CHARTS_DIR.glob(f"{slug}-*lp.*")))
    specs_dir = OPTICAL_SPECS_DIR / slug
    if specs_dir.is_dir():
        # Check for standard *lp* pattern or any PNG/webp images (covers non-standard naming)
        mtf_images = [
            f for f in specs_dir.glob(f"{slug}-*.png")
            if "construction" not in f.name
        ]
        in_specs = bool(mtf_images)
    else:
        in_specs = False
    return in_mtf or in_specs


# --- Caching ---


def _cache_path(url: str, suffix: str) -> Path:
    h = hashlib.sha256(url.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{h}{suffix}"


def read_cache(url: str, html: bool = False) -> str | None:
    path = _cache_path(url, ".html" if html else ".txt")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def write_cache(url: str, content: str, html: bool = False) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(url, ".html" if html else ".txt")
    path.write_text(content, encoding="utf-8")


# --- Image downloading ---


def download_image(url: str, dest: Path, min_size: int = 500) -> bool:
    """Download an image to dest. Returns True on success."""
    if dest.exists():
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) < min_size:
                return False
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"    WARN: download failed for {dest.name}: {e}")
        return False


# --- Playwright browser ---


@contextmanager
def browser_context():
    """Context manager yielding a Playwright BrowserContext."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=USER_AGENT)
        try:
            yield ctx
        finally:
            browser.close()


def scroll_page(page: Page) -> None:
    """Scroll through a page to trigger lazy-loaded content."""
    page.evaluate("""async () => {
        const delay = ms => new Promise(r => setTimeout(r, ms));
        for (let y = 0; y < document.body.scrollHeight; y += window.innerHeight) {
            window.scrollTo(0, y); await delay(300);
        }
        window.scrollTo(0, 0); await delay(500);
    }""")
    page.wait_for_timeout(2000)


def fetch_page_content(ctx: BrowserContext, url: str, wait_ms: int = 3000) -> tuple[str, str]:
    """Fetch a page, return (text_content, html_content). Uses cache."""
    cached_text = read_cache(url)
    cached_html = read_cache(url, html=True)
    if cached_text and cached_html:
        return cached_text, cached_html

    page = ctx.new_page()
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(wait_ms)
        scroll_page(page)
        text = page.inner_text("body")
        html = page.content()
        write_cache(url, text)
        write_cache(url, html, html=True)
        return text, html
    finally:
        page.close()


# --- Spec extraction ---


TEXT_NUMS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
}


def extract_specs(text: str) -> dict:
    """Extract optical specs (elements, groups, special elements) from page text."""
    specs: dict = {}

    m = re.search(r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?", text, re.IGNORECASE)
    if m:
        specs["elements"] = int(m.group(1))
        specs["groups"] = int(m.group(2))

    # Find the construction block for special element parsing (4-line window)
    m2 = re.search(
        r"\d+\s*elements?\s+(?:in\s+)?\d+\s*groups?[^\n]*(?:\n[^\n]*){0,4}",
        text, re.IGNORECASE,
    )
    block = m2.group(0) if m2 else ""

    # Normalize text numbers
    for word, digit in TEXT_NUMS.items():
        block = re.sub(rf"\b{word}\b", digit, block, flags=re.IGNORECASE)

    special = []
    for pat, label in [
        (r"(\d+)\s*aspherical", "aspherical"),
        (r"(\d+)\s*(?:extra[- ]low[- ]dispersion|anomalous[- ]dispersion|ED)\b", "ED"),
        (r"(\d+)\s*(?:Super\s?ED|super\s?ED|superED|super\s+extra[- ]low[- ]dispersion)", "Super ED"),
        (r"(\d+)\s*fluorite", "fluorite"),
    ]:
        m3 = re.search(pat, block, re.IGNORECASE)
        if m3:
            special.append(f"{m3.group(1)} {label}")
    specs["special"] = special

    return specs


def extract_coatings(text: str) -> list[str]:
    """Extract coating types from page text."""
    coatings = ["Super EBC"]  # all Fujifilm lenses have this
    if re.search(r"Nano[- ]GI", text, re.IGNORECASE):
        coatings.append("Nano-GI")
    if re.search(r"HT[- ]EBC", text, re.IGNORECASE):
        coatings.append("HT-EBC")
    return coatings


# --- Image URL extraction ---


def extract_image_urls_from_html(html: str, url_slug: str) -> dict[str, str]:
    """Extract construction + MTF image URLs from HTML using named URL patterns."""
    urls: dict[str, str] = {}

    # Try full slug match first, then partial (Fujifilm sometimes truncates CDN filenames)
    # Also match _corss (known Fujifilm typo) and case-insensitive CDN filenames
    slug_prefix = url_slug[:len(url_slug) - 2] if len(url_slug) > 4 else url_slug
    for slug_pat in [re.escape(url_slug), re.escape(slug_prefix)]:
        m = re.search(
            r'src="([^"]*' + slug_pat + r'[^"]*_c(?:ro|or)ss[^"]*\.[^"]+)"',
            html, re.IGNORECASE,
        )
        if m:
            break
    # Fallback: any b-cdn _cross image on the page (different naming conventions)
    if not m:
        m = re.search(
            r'src="([^"]*b-cdn[^"]*_c(?:ro|or)ss[^"]*\.(?:webp|png|jpg|jpeg))[^"]*"',
            html, re.IGNORECASE,
        )
    if m:
        urls["construction"] = m.group(1).split("?")[0]

    for suffix_pat, key in [(r"0*2", "mtf_15"), (r"0*3", "mtf_45")]:
        m2 = re.search(
            r'src="([^"]*' + re.escape(url_slug)
            + r'[^"]*Specifications-images' + suffix_pat + r'\.[^"]+)"',
            html, re.IGNORECASE,
        )
        if m2:
            urls[key] = m2.group(1).split("?")[0]

    return urls


def extract_image_urls_by_position(page: Page, url_slug: str) -> dict[str, str]:
    """Extract construction + MTF image URLs by page position relative to text markers.

    Falls back to this strategy when named URL patterns don't match
    (newer Fujifilm pages use generic image filenames).
    """
    urls: dict[str, str] = {}

    # First try named URLs from the page HTML
    html = page.content()
    urls = extract_image_urls_from_html(html, url_slug)
    if urls:
        return urls

    # Get text marker Y positions
    markers = page.evaluate("""() => {
        const result = {};
        const walk = document.createTreeWalker(
            document.body, NodeFilter.SHOW_TEXT, null
        );
        while (walk.nextNode()) {
            const text = walk.currentNode.textContent.trim();
            const el = walk.currentNode.parentElement;
            if (!el) continue;
            const rect = el.getBoundingClientRect();
            if (text === 'Lens Configurations' && !result.lensConfig)
                result.lensConfig = rect.top;
            if (text === 'MTF Chart' && !result.mtfChart)
                result.mtfChart = rect.top;
            if (/^Spatial frequency 15/.test(text) && !result.freq15)
                result.freq15 = rect.top;
            if (/^Spatial frequency 45/.test(text) && !result.freq45)
                result.freq45 = rect.top;
        }
        return result;
    }""")

    if not markers.get("lensConfig") and not markers.get("mtfChart"):
        return urls

    # Get content image positions
    imgs = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('img'))
            .map(img => ({
                src: img.src.split('?')[0],
                top: img.getBoundingClientRect().top,
                w: img.naturalWidth || img.width,
                h: img.naturalHeight || img.height,
            }))
            .filter(i => i.src.includes('b-cdn')
                && !i.src.includes('thum') && !i.src.includes('flag')
                && !i.src.includes('logo') && !i.src.includes('fujifilmX')
                && i.h > 50 && i.w > 50);
    }""")

    lc_y = markers.get("lensConfig", 0)
    mtf_y = markers.get("mtfChart", 0)
    f15_y = markers.get("freq15", 0)
    f45_y = markers.get("freq45", 0)

    for img in imgs:
        top = img["top"]
        src = img["src"]

        if lc_y and mtf_y and lc_y < top < mtf_y:
            if "construction" not in urls:
                urls["construction"] = src

        if f15_y and abs(top - f15_y) < 300:
            if "mtf_15" not in urls:
                urls["mtf_15"] = src

        if f45_y and abs(top - f45_y) < 300:
            if "mtf_45" not in urls:
                urls["mtf_45"] = src

    # Fallback: first 2 images after "MTF Chart" heading
    if mtf_y and not urls.get("mtf_15") and not urls.get("mtf_45"):
        after_mtf = [i for i in imgs if i["top"] > mtf_y and i["w"] > 100]
        if len(after_mtf) >= 2:
            urls["mtf_15"] = after_mtf[0]["src"]
            urls["mtf_45"] = after_mtf[1]["src"]
        elif len(after_mtf) == 1:
            urls["mtf_15"] = after_mtf[0]["src"]

    return urls
