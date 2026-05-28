"""SigmaExtractor — the Sigma BrandExtractor strategy.

Ports the Sigma-specific parsing onto the brandkit contract. Sigma labels
special glass FLD / SLD / ELD / aspherical (with a "~1" fallback when a type
is mentioned in a diagram legend without a count), and coats lenses "Super
Multi-Layer Coating". Image URLs are keyed by a product code derived from
the lens URL (e.g. .../lenses/c019_30_14/ -> c019_30_14).
"""

import re

from pagefetch import ContentMode, Transport

from brandkit import BrandConfig, BrandExtractor

BASE_URL = "https://www.sigma-global.com"

_TEXT_NUMS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
}

_SPECIAL_PATTERNS = [
    ("aspherical", [
        r"(\d+)\s*(?:molded\s+glass\s+)?aspherical\s+(?:lens|element)",
        r"(\d+)\s*aspherical\b",
    ]),
    ("FLD", [r"(\d+)\s*FLD\b"]),
    ("SLD", [r"(\d+)\s*SLD\b"]),
    ("ELD", [r"(\d+)\s*ELD\b"]),
]

_SPECIAL_FALLBACKS = {
    "aspherical": r"\b(?:aspherical\s+(?:lens|element)|aspherical\b)",
    "FLD": r"\bFLD\s+(?:glass|element|lens)",
    "SLD": r"\bSLD\s+(?:glass|element|lens)",
    "ELD": r"\bELD\s+(?:glass|element|lens)",
}


def url_to_code(url: str) -> str:
    """Sigma product code is the last path segment:
    https://www.sigma-global.com/en/lenses/c017_16_14/ -> c017_16_14"""
    return url.rstrip("/").split("/")[-1]


class SigmaExtractor(BrandExtractor):
    config = BrandConfig(
        name="Sigma",
        slug_prefix="sigma",
        content_mode=ContentMode.HTML,
        transport=Transport.AUTO,
        has_diagrams=True,
    )

    def extract_optical(self, content: str) -> dict:
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", content))
        for word, digit in _TEXT_NUMS.items():
            text = re.sub(rf"\b{word}\b", digit, text, flags=re.IGNORECASE)

        specs: dict = {}
        m = re.search(
            r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?", text, re.IGNORECASE
        )
        if m:
            specs["elements"] = int(m.group(1))
            specs["groups"] = int(m.group(2))
        specs["special"] = self._special(text)
        specs["coating"] = (
            ["Super Multi-Layer Coating"]
            if re.search(r"Super\s+Multi[- ]Layer\s+Coating", text, re.IGNORECASE)
            else []
        )
        return specs

    @staticmethod
    def _special(text: str) -> list[str]:
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
        urls: dict[str, list[str]] = {"mtf": [], "construction": []}
        code = url_to_code(url)
        if not code:
            return urls
        pattern = re.compile(
            r'(?:src|href)="([^"]*' + re.escape(code) + r'_specification[^"]*\.png)"',
            re.IGNORECASE,
        )
        for m in pattern.finditer(content):
            src = m.group(1)
            full = src if src.startswith("http") else BASE_URL + src
            # _specification_01 / _2 are construction; _specification_02_ is MTF.
            if re.search(r"_specification_(?:01(?:_\d+)?|[12])\.png$", src, re.IGNORECASE):
                if full not in urls["construction"]:
                    urls["construction"].append(full)
            elif "_specification_02_" in src:
                if full not in urls["mtf"]:
                    urls["mtf"].append(full)
        return urls
