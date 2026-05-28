"""TokinaExtractor — the Tokina BrandExtractor strategy.

Ports the Tokina-specific parsing (optical specs from spec text + image
alt attributes, MTF/construction image URLs, the hyphen-to-underscore URL
quirk) onto the brandkit BrandExtractor contract. The shared scaffolding
(slug, lenses.ts parsing, caching, image download) now lives in brandkit;
only the brand-specific parsing remains here.

Tokina pages serve underscored product slugs, use plain urllib, embed
special-element names in image alt text, and label coating "Multi-coating".
"""

import re

from pagefetch import ContentMode, Transport

from brandkit import BrandConfig, BrandExtractor

BASE_URL = "https://tokinalens.com"

_TEXT_NUMS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
}

_SPECIAL_PATTERNS = [
    ("aspherical", [r"(\d+)\s*aspherical\s*(?:lens|element)", r"(\d+)\s*aspherical\b"]),
    ("SD", [
        r"(\d+)\s*(?:Super\s+)?Low[- ]Dispersion\s*\(SD\)",
        r"(\d+)\s*SD\s+glass",
        r"(\d+)\s*SD\b",
    ]),
    ("ED", [r"(\d+)\s*ED\s+(?:glass|element|lens)", r"(\d+)\s*ED\b"]),
]

_SPECIAL_FALLBACKS = {
    "aspherical": r"\baspherical\s+(?:lens|element)",
    "SD": r"\b(?:Super\s+)?Low[- ]Dispersion\b|\bSD\s+glass|\bSuper\s+Low\s+Dispersion\s+Glass\b",
    "ED": r"\bED\s+(?:glass|element|lens)",
}


class TokinaExtractor(BrandExtractor):
    config = BrandConfig(
        name="Tokina",
        slug_prefix="tokina",
        content_mode=ContentMode.HTML,
        transport=Transport.AUTO,
        has_diagrams=True,
    )

    def normalize_url(self, url: str) -> str:
        """Tokina serves underscored product slugs; lenses.ts uses hyphens."""
        prefix = BASE_URL + "/product/"
        if not url.startswith(prefix):
            return url
        return prefix + url[len(prefix):].replace("-", "_")

    def extract_optical(self, content: str) -> dict:
        # Tokina puts special-element names in image alt text, so fold alt
        # attributes into the searchable text before stripping tags.
        alt_text = " ".join(re.findall(r'alt="([^"]*)"', content))
        text = re.sub(r"<[^>]+>", " ", content) + " " + alt_text
        text = re.sub(r"\s+", " ", text)
        for word, digit in _TEXT_NUMS.items():
            text = re.sub(rf"\b{word}\b", digit, text, flags=re.IGNORECASE)

        specs: dict = {}
        m = re.search(r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?", text, re.IGNORECASE)
        if m:
            specs["elements"] = int(m.group(1))
            specs["groups"] = int(m.group(2))

        specs["special"] = self._extract_special(text)

        coating = []
        if re.search(r"Multi[- ]?coating", text, re.IGNORECASE):
            coating.append("Multi-coating")
        specs["coating"] = coating
        return specs

    @staticmethod
    def _extract_special(text: str) -> list[str]:
        special: list[str] = []
        for label, patterns in _SPECIAL_PATTERNS:
            matched = next(
                (re.search(p, text, re.IGNORECASE) for p in patterns
                 if re.search(p, text, re.IGNORECASE)),
                None,
            )
            if matched:
                special.append(f"{matched.group(1)} {label}")
            elif re.search(_SPECIAL_FALLBACKS[label], text, re.IGNORECASE):
                special.append(f"~1 {label}")
        return special

    def extract_image_urls(self, content: str, url: str = "") -> dict[str, list[str]]:
        # Tokina matches on image filenames in the page; url is unused.
        urls: dict[str, list[str]] = {"mtf": [], "construction": []}

        for m in re.finditer(
            r'(?:src|href)="([^"]*_constr[^"]*\.(?:jpg|png))', content, re.IGNORECASE
        ):
            url = self._resolve(m.group(1))
            if url not in urls["construction"]:
                urls["construction"].append(url)

        for m in re.finditer(
            r'(?:src|href)="([^"]*_mtf[^"]*\.(?:jpg|png))', content, re.IGNORECASE
        ):
            url = self._resolve(m.group(1))
            if url not in urls["mtf"]:
                urls["mtf"].append(url)

        # Numbered fallback for zoom lenses: 05_1 = construction, 05_2+ = MTF.
        if not urls["construction"] and not urls["mtf"]:
            for m in re.finditer(
                r'(?:src|href)="([^"]*catalog/product/[^"]*05_(\d+)\.(?:jpg|png))',
                content, re.IGNORECASE,
            ):
                url = self._resolve(m.group(1))
                bucket = "construction" if int(m.group(2)) == 1 else "mtf"
                if url not in urls[bucket]:
                    urls[bucket].append(url)
        return urls

    @staticmethod
    def _resolve(src: str) -> str:
        if src.startswith("http"):
            return src
        return BASE_URL + (src if src.startswith("/") else "/" + src)
