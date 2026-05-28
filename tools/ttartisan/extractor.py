"""TTArtisanExtractor — the TTartisan BrandExtractor strategy.

TTartisan keeps element/group counts in a spec table (class="specification",
falling back to any table, then full-page text) and names special glass in
prose (ED / HR / LD / UD / aspherical / achromatic doublet). Coating is rare.
Image filenames vary by page age (Specification-MTF / -OD / -1 / -2, with
-M/-EN segment suffixes); SLR-mount variant images are skipped.

Brand name in lenses.ts is "TTartisan" (lowercase 'a').
"""

import re

from pagefetch import ContentMode, Transport

from brandkit import BrandConfig, BrandExtractor

BASE_URL = "https://www.ttartisan.com"

_TEXT_NUMS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
}

_SPECIAL_PATTERNS = [
    ("aspherical", [r"(\d+)\s*(?:aspherical|asph\.?)\s*(?:lens|element|glass)"]),
    ("ED", [
        r"(\d+)\s*(?:extra[- ]low[- ]dispersion|ED)\s*(?:\([^)]*\)\s*)?(?:lens|element|glass)",
        r"(\d+)\s*ED\s*\(",
    ]),
    ("HR", [r"(\d+)\s*(?:high[- ]?refract(?:ive|ion)|high[- ]?index)\s*(?:lens|element|glass)"]),
    ("LD", [r"(\d+)\s*(?:low[- ]dispersion)\s*(?:lens|element|glass)"]),
    ("UD", [r"(\d+)\s*(?:ultra[- ]low[- ]dispersion)\s*(?:\([^)]*\)\s*)?(?:lens|element|glass)"]),
]


def _strip(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


class TTArtisanExtractor(BrandExtractor):
    config = BrandConfig(
        name="TTartisan",
        slug_prefix="ttartisan",
        content_mode=ContentMode.HTML,
        transport=Transport.AUTO,
        has_diagrams=True,
    )

    def extract_optical(self, content: str) -> dict:
        specs: dict = {}
        eg = self._elements_groups(content)
        if eg:
            specs["elements"], specs["groups"] = eg
        specs["special"] = self._special(_strip(content))
        specs["coating"] = self._coating(_strip(content))
        return specs

    @staticmethod
    def _elements_groups(html: str) -> tuple[int, int] | None:
        """Counts: spec table first, then any table mentioning elements/groups,
        then full-page text."""
        candidates = []
        table = re.search(
            r'<table[^>]*class="specification"[^>]*>(.*?)</table>',
            html, re.DOTALL | re.IGNORECASE,
        )
        if table:
            candidates.append(_strip(table.group(1)))
        else:
            for t in re.finditer(r"<table[^>]*>(.*?)</table>", html, re.DOTALL | re.IGNORECASE):
                t_text = _strip(t.group(1))
                if re.search(r"elements?\s+(?:in\s+)?\d+\s*groups?", t_text, re.IGNORECASE):
                    candidates.append(t_text)
                    break
        candidates.append(_strip(html))  # last resort

        for text in candidates:
            m = re.search(r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?", text, re.IGNORECASE)
            if m:
                return int(m.group(1)), int(m.group(2))
        return None

    @staticmethod
    def _special(text: str) -> list[str]:
        normalized = text
        for word, digit in _TEXT_NUMS.items():
            normalized = re.sub(rf"\b{word}\b", digit, normalized, flags=re.IGNORECASE)

        special: list[str] = []
        for label, patterns in _SPECIAL_PATTERNS:
            for pat in patterns:
                m = re.search(pat, normalized, re.IGNORECASE)
                if m:
                    special.append(f"{m.group(1)} {label}")
                    break
        achro = re.search(
            r"(\d+)\s*(?:sets?\s+of\s+)?achromatic\s+doublets?", normalized, re.IGNORECASE
        )
        if achro:
            special.append(f"{achro.group(1)} achromatic doublet")
        return special

    @staticmethod
    def _coating(text: str) -> list[str]:
        if re.search(r"MC\s+Multi[- ]?Layer", text, re.IGNORECASE):
            return ["MC Multi-Layer"]
        if re.search(r"multi[- ]?layer\s+coat", text, re.IGNORECASE):
            return ["Multi-layer coating"]
        if re.search(r"multi[- ]?coat", text, re.IGNORECASE):
            return ["Multi-coating"]
        return []

    def extract_image_urls(self, content: str, url: str = "") -> dict[str, list[str]]:
        urls: dict[str, list[str]] = {"mtf": [], "construction": []}
        for img in re.findall(r'(?:src|href)="([^"]+\.(?:webp|jpg|png))"', content, re.IGNORECASE):
            lower = img.lower()
            if "-slr" in lower:  # skip SLR-mount variants
                continue
            resolved = self._resolve(img)
            if "specification-mtf" in lower:
                self._add(urls["mtf"], resolved)
            elif "specification-od" in lower:
                self._add(urls["construction"], resolved)
            elif re.search(r"specification-1(?:-[a-z]+)*\.(?:webp|jpg|png)", lower):
                self._add(urls["mtf"], resolved)
            elif re.search(r"specification-2(?:-[a-z]+)*\.(?:webp|jpg|png)", lower):
                self._add(urls["construction"], resolved)
        return urls

    @staticmethod
    def _add(bucket: list[str], url: str) -> None:
        if url not in bucket:
            bucket.append(url)

    @staticmethod
    def _resolve(src: str) -> str:
        if src.startswith("http"):
            return src
        return BASE_URL + (src if src.startswith("/") else "/" + src)
