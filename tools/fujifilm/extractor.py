"""FujifilmExtractor — the Fujifilm BrandExtractor strategy.

Fujifilm pages are JS-rendered (config.transport = PLAYWRIGHT) and specs live
on a "/specifications/" sub-path (normalize_url appends it). The extractor
folds the old extract_specs + extract_coatings into extract_optical: every
Fujifilm lens has Super EBC, plus optional Nano-GI / HT-EBC.

Image URLs come from named CDN patterns (extract_image_urls) where possible.
Newer pages use generic CDN filenames the regex can't match; for those,
extract_images_live resolves URLs from on-page geometry (image position
relative to "Lens Configurations" / "MTF Chart" / "Spatial frequency"
markers). brandkit opens the live Playwright page and calls it — this is the
one documented place the content->dict contract bends (ADR-035).

The old code returned image keys construction / mtf_15 / mtf_45; here they
normalize to the standard {"mtf": [...], "construction": [...]} shape, with
the 15 lp/mm chart first and 45 lp/mm second.
"""

import re

from pagefetch import ContentMode, Transport

from brandkit import BrandConfig, BrandExtractor

_TEXT_NUMS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
}

_SPECIAL_PATTERNS = [
    (r"(\d+)\s*aspherical", "aspherical"),
    (r"(\d+)\s*(?:extra[- ]low[- ]dispersion|anomalous[- ]dispersion|ED)\b", "ED"),
    (r"(\d+)\s*(?:Super\s?ED|super\s?ED|superED|super\s+extra[- ]low[- ]dispersion)", "Super ED"),
    (r"(\d+)\s*fluorite", "fluorite"),
]


def url_to_slug(url: str) -> str:
    """The CDN-filename slug is the last path segment of the product URL.
    Strips a trailing /specifications/ if normalize_url added it."""
    cleaned = url.rstrip("/")
    if cleaned.endswith("/specifications"):
        cleaned = cleaned[: -len("/specifications")]
    return cleaned.rstrip("/").split("/")[-1]


class FujifilmExtractor(BrandExtractor):
    config = BrandConfig(
        name="Fujifilm",
        slug_prefix="fujifilm",
        content_mode=ContentMode.HTML,
        transport=Transport.PLAYWRIGHT,
        has_diagrams=True,
        needs_live_page=True,
    )

    def normalize_url(self, url: str) -> str:
        """Specs live on the /specifications/ sub-page."""
        base = url.rstrip("/")
        if base.endswith("/specifications"):
            return base + "/"
        return base + "/specifications/"

    def extract_optical(self, content: str) -> dict:
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", content))
        specs: dict = {}
        m = re.search(r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?", text, re.IGNORECASE)
        if m:
            specs["elements"] = int(m.group(1))
            specs["groups"] = int(m.group(2))

        # Special elements: search a short window after the construction line.
        block_m = re.search(
            r"\d+\s*elements?\s+(?:in\s+)?\d+\s*groups?.{0,400}", text, re.IGNORECASE
        )
        block = block_m.group(0) if block_m else ""
        for word, digit in _TEXT_NUMS.items():
            block = re.sub(rf"\b{word}\b", digit, block, flags=re.IGNORECASE)
        special = []
        for pat, label in _SPECIAL_PATTERNS:
            m2 = re.search(pat, block, re.IGNORECASE)
            if m2:
                special.append(f"{m2.group(1)} {label}")
        specs["special"] = special

        specs["coating"] = self._coating(text)
        return specs

    def extract_physical(self, content: str) -> dict:
        """Parse physical specs from the Fujifilm specifications page (#779).

        The spec table's two-column layout shifts on multi-value rows, so
        these use targeted patterns over the de-tagged text rather than
        cell-pairing. minFocusDistance takes the closer of the Normal/Macro
        focus ranges (Macro = the lens's true minimum)."""
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", content))
        text = text.replace("&#8211;", "-").replace("&nbsp;", " ")
        # Drop other HTML numeric entities (e.g. &#8709; diameter sign, &#8734;
        # infinity) so their digits don't get mistaken for spec values.
        text = re.sub(r"&#\d+;", " ", text)
        out: dict = {}

        # focal length: "f=14mm" or "f=10-24mm"
        fl = re.search(r"f=\s*([\d.]+)(?:\s*-\s*([\d.]+))?\s*mm", text, re.IGNORECASE)
        if fl:
            out["focalLengthMin"] = float(fl.group(1))
            out["focalLengthMax"] = float(fl.group(2) or fl.group(1))
        if ap := self._num(text, r"Max\.?\s*aperture\s*F/?([\d.]+)"):
            out["maxAperture"] = ap
        if blades := self._num(text, r"(\d+)\s*\(rounded diaphragm"):
            out["apertureBlades"] = blades
        if (mag := self._num(text, r"Max\.?\s*magnification\s*([\d.]+)\s*x")) is not None:
            out["maxMagnification"] = mag
        # Weights >=1000g are printed with a comma thousands separator
        # ("2,265g"); capture commas and strip them before parsing so the
        # leading digits are not dropped.
        if wm := re.search(r"Weight[^=g]*?([\d,.]+)\s*g", text, re.IGNORECASE):
            out["weight"] = float(wm.group(1).replace(",", ""))
        if ft := self._num(text, r"Filter size[^\d]*([\d.]+)\s*mm"):
            out["filterThread"] = ft
        # dimensions: "Diameter x Length ... 65mm x 58.4mm"
        dims = re.search(r"Diameter x Length[^\d]*?([\d.]+)\s*mm\s*x\s*([\d.]+)\s*mm", text, re.IGNORECASE)
        if dims:
            out["diameter"] = float(dims.group(1))
            out["length"] = float(dims.group(2))
        # focus range: take the closer of Normal/Macro (cm -> mm).
        ranges = [float(x) for x in re.findall(r"(?:Normal|Macro)\s*([\d.]+)\s*cm", text, re.IGNORECASE)]
        if ranges:
            out["minFocusDistance"] = round(min(ranges) * 10)  # cm -> mm
        return out

    @staticmethod
    def _num(text: str, pattern: str) -> float | None:
        m = re.search(pattern, text, re.IGNORECASE)
        return float(m.group(1)) if m else None

    @staticmethod
    def _coating(text: str) -> list[str]:
        # Every Fujifilm lens has Super EBC; Nano-GI / HT-EBC are optional.
        coatings = ["Super EBC"]
        if re.search(r"Nano[- ]GI", text, re.IGNORECASE):
            coatings.append("Nano-GI")
        if re.search(r"HT[- ]EBC", text, re.IGNORECASE):
            coatings.append("HT-EBC")
        return coatings

    def extract_image_urls(self, content: str, url: str = "") -> dict[str, list[str]]:
        named = self._named_image_urls(content, url_to_slug(url))
        urls: dict[str, list[str]] = {"mtf": [], "construction": []}
        if named.get("construction"):
            urls["construction"].append(named["construction"])
        # Old keys mtf_15 / mtf_45 normalize to an ordered mtf list.
        for key in ("mtf_15", "mtf_45"):
            if named.get(key):
                urls["mtf"].append(named[key])
        return urls

    @staticmethod
    def _named_image_urls(html: str, url_slug: str) -> dict[str, str]:
        """Named-CDN-pattern image URLs (the static path). Mirrors the old
        extract_image_urls_from_html."""
        urls: dict[str, str] = {}
        slug_prefix = url_slug[: len(url_slug) - 2] if len(url_slug) > 4 else url_slug
        m = None
        for slug_pat in [re.escape(url_slug), re.escape(slug_prefix)]:
            if not slug_pat:
                continue
            m = re.search(
                r'src="([^"]*' + slug_pat + r'[^"]*_c(?:ro|or)ss[^"]*\.[^"]+)"',
                html, re.IGNORECASE,
            )
            if m:
                break
        if not m:
            m = re.search(
                r'src="([^"]*b-cdn[^"]*_c(?:ro|or)ss[^"]*\.(?:webp|png|jpg|jpeg))[^"]*"',
                html, re.IGNORECASE,
            )
        if m:
            urls["construction"] = m.group(1).split("?")[0]

        for suffix_pat, key in [(r"0*2", "mtf_15"), (r"0*3", "mtf_45")]:
            if not url_slug:
                break
            m2 = re.search(
                r'src="([^"]*' + re.escape(url_slug)
                + r'[^"]*Specifications-images' + suffix_pat + r'\.[^"]+)"',
                html, re.IGNORECASE,
            )
            if m2:
                urls[key] = m2.group(1).split("?")[0]
        return urls

    def extract_images_live(self, page, url: str) -> dict[str, list[str]]:
        """Position-based fallback for newer pages with generic CDN filenames.
        Reads image Y-positions relative to text markers via page.evaluate."""
        url_slug = url_to_slug(url)
        named = self._named_image_urls(page.content(), url_slug)
        if named:
            return self._normalize(named)

        markers = page.evaluate(
            """() => {
                const r = {};
                const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
                while (w.nextNode()) {
                    const t = w.currentNode.textContent.trim();
                    const el = w.currentNode.parentElement;
                    if (!el) continue;
                    const top = el.getBoundingClientRect().top;
                    if (t === 'Lens Configurations' && !r.lensConfig) r.lensConfig = top;
                    if (t === 'MTF Chart' && !r.mtfChart) r.mtfChart = top;
                    if (/^Spatial frequency 15/.test(t) && !r.freq15) r.freq15 = top;
                    if (/^Spatial frequency 45/.test(t) && !r.freq45) r.freq45 = top;
                }
                return r;
            }"""
        )
        if not markers.get("lensConfig") and not markers.get("mtfChart"):
            return {"mtf": [], "construction": []}

        imgs = page.evaluate(
            """() => Array.from(document.querySelectorAll('img'))
                .map(img => ({src: img.src.split('?')[0], top: img.getBoundingClientRect().top,
                              w: img.naturalWidth || img.width, h: img.naturalHeight || img.height}))
                .filter(i => i.src.includes('b-cdn') && !i.src.includes('thum')
                    && !i.src.includes('flag') && !i.src.includes('logo')
                    && !i.src.includes('fujifilmX') && i.h > 50 && i.w > 50);"""
        )

        named = self._from_positions(markers, imgs)
        return self._normalize(named)

    @staticmethod
    def _from_positions(markers: dict, imgs: list) -> dict[str, str]:
        lc, mtf = markers.get("lensConfig", 0), markers.get("mtfChart", 0)
        f15, f45 = markers.get("freq15", 0), markers.get("freq45", 0)
        out: dict[str, str] = {}
        for img in imgs:
            top, src = img["top"], img["src"]
            if lc and mtf and lc < top < mtf and "construction" not in out:
                out["construction"] = src
            if f15 and abs(top - f15) < 300 and "mtf_15" not in out:
                out["mtf_15"] = src
            if f45 and abs(top - f45) < 300 and "mtf_45" not in out:
                out["mtf_45"] = src
        if mtf and "mtf_15" not in out and "mtf_45" not in out:
            after = [i for i in imgs if i["top"] > mtf and i["w"] > 100]
            if len(after) >= 2:
                out["mtf_15"], out["mtf_45"] = after[0]["src"], after[1]["src"]
            elif len(after) == 1:
                out["mtf_15"] = after[0]["src"]
        return out

    @staticmethod
    def _normalize(named: dict[str, str]) -> dict[str, list[str]]:
        urls: dict[str, list[str]] = {"mtf": [], "construction": []}
        if named.get("construction"):
            urls["construction"].append(named["construction"])
        for key in ("mtf_15", "mtf_45"):
            if named.get(key):
                urls["mtf"].append(named[key])
        return urls
