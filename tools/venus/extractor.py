"""VenusExtractor — the Venus Laowa BrandExtractor strategy.

venuslens.net sits behind Cloudflare Turnstile, so the page needs UC-mode
Chrome to fetch (config.transport = UC). The extractor pulls element/group
counts (the "in" between is required) and special-glass counts, taking the
parenthetical after the structure line as the most reliable source and only
matching special-element patterns that carry a qualifying noun
(element/lens/glass) — bare "\\dED" would otherwise false-match CSS hex
colours like #8ed1fc. Image filenames may be English or URL-encoded Chinese,
and use lazy-load attributes.

Brand string in lenses.ts is "Venus Laowa"; slug prefix is "venus-laowa".
"""

import re

from pagefetch import ContentMode, Transport

from brandkit import BrandConfig, BrandExtractor

BASE_URL = "https://www.venuslens.net"

_TEXT_NUMS = {
    "a pair of": "2", "one": "1", "two": "2", "three": "3",
    "four": "4", "five": "5", "six": "6",
}

# Each pattern REQUIRES a qualifying noun, to dodge CSS-hex false positives.
_SPECIAL_PATTERNS = [
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

# Construction-diagram filename markers (English + URL-encoded/decoded Chinese).
_CONSTRUCTION_MARKER = re.compile(
    r"lens[_-]?structure|optical[_-]?design|construction|cross[_-]?section"
    r"|%E5%85%89%E8%B7%AF%E5%9B%BE"  # 光路图 optical path diagram (encoded)
    r"|%E7%BB%93%E6%9E%84"  # 结构 structure (encoded)
    r"|%E9%95%9C%E7%BB%84"  # 镜组 lens group (encoded)
    r"|光路图"  # 光路图 (decoded)
    r"|结构"  # 结构 (decoded)
    r"|镜组",  # 镜组 (decoded)
    re.IGNORECASE,
)


class VenusExtractor(BrandExtractor):
    config = BrandConfig(
        name="Venus Laowa",
        slug_prefix="venus-laowa",
        content_mode=ContentMode.HTML,
        transport=Transport.UC,  # Cloudflare Turnstile needs UC-mode Chrome
        has_diagrams=True,
    )

    def extract_optical(self, content: str) -> dict:
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", content))
        specs: dict = {}
        m = re.search(r"(\d+)\s*elements?\s+in\s+(\d+)\s*groups?", text, re.IGNORECASE)
        if m:
            specs["elements"] = int(m.group(1))
            specs["groups"] = int(m.group(2))
        specs["special"] = self._special(text)
        specs["coating"] = self._coating(text)
        return specs

    @staticmethod
    def _special(text: str) -> list[str]:
        # Parenthetical right after the structure line is the most reliable.
        paren = re.search(
            r"elements?\s+in\s+\d+\s*groups?\s*\(([^)]+)\)", text, re.IGNORECASE
        )
        paren_text = paren.group(1) if paren else ""

        normalized = text
        for word, digit in _TEXT_NUMS.items():
            normalized = re.sub(rf"\b{word}\b", digit, normalized, flags=re.IGNORECASE)
        search_text = (paren_text + " " + normalized) if paren_text else normalized

        special: list[str] = []
        for label, patterns in _SPECIAL_PATTERNS:
            for pat in patterns:
                m = re.search(pat, search_text, re.IGNORECASE)
                if m:
                    special.append(f"{m.group(1)} {label}")
                    break
        return special

    @staticmethod
    def _coating(text: str) -> list[str]:
        coating: list[str] = []
        if re.search(r"Frog\s+Eye\s+Coating", text, re.IGNORECASE):
            coating.append("Frog Eye Coating")
        if re.search(r"multi[- ]?coating", text, re.IGNORECASE):
            coating.append("Multi-Coating")
        return coating

    def extract_image_urls(self, content: str, url: str = "") -> dict[str, list[str]]:
        urls: dict[str, list[str]] = {"mtf": [], "construction": []}
        for m in re.finditer(
            r'(?:src|data-src|data-lazy-src)="([^"]+\.(?:jpg|png|webp|svg)[^"]*)"',
            content, re.IGNORECASE,
        ):
            src = m.group(1)
            lower = src.lower()
            if "150x" in lower or "100x" in lower or "icon" in lower:
                continue
            full = src if src.startswith("http") else BASE_URL + src
            if re.search(r"mtf|mft", lower):  # MFT is a frequent typo on these pages
                if full not in urls["mtf"]:
                    urls["mtf"].append(full)
            elif _CONSTRUCTION_MARKER.search(lower):
                if full not in urls["construction"]:
                    urls["construction"].append(full)
        return urls
