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

    def extract_physical(self, content: str) -> dict:
        """Parse physical specs from Sigma's l-grid spec rows (#779).

        Each spec is a <li> with a <p>label</p> then a <div> of value <p>s.
        Multi-mount lenses prefix each value with 'Mount：'/'Mount:' (older
        pages use a fullwidth colon, newer ones ASCII); the first value wins,
        matching Tamron. Weights carry thousands separators ('1,135g'). Sigma
        quotes MFD in cm — a single value ('30cm') or a zoom range
        ('112(W) - 160(T)cm'), where the wide (first) figure wins. Dimensions
        are 'φDIAmm × LENmm' (× or lowercase x). 'Rounded diaphragm' on the
        blade count confirms a circular aperture."""
        rows = self._spec_rows(content)
        out: dict = {}

        if ft := self._num(rows.get("Filter Size"), r"([\d.]+)\s*mm"):
            out["filterThread"] = ft
        dims = self._first_value(rows.get("Dimensions (Diameter × Length)"))
        if dims:
            dm = re.search(r"([\d.]+)\s*mm\s*[×x]\s*([\d.]+)\s*mm", dims)
            if dm:
                out["diameter"] = float(dm.group(1))
                out["length"] = float(dm.group(2))
        if w := self._num(self._first_value(rows.get("Weight")), r"([\d,]+\.?\d*)\s*g"):
            out["weight"] = w
        blades_raw = rows.get("Number of Diaphragm Blades", "")
        if blades := self._num(blades_raw, r"(\d+)"):
            out["apertureBlades"] = blades
        if re.search(r"round", blades_raw, re.IGNORECASE):
            out["hasCircularAperture"] = True
        # MFD in cm -> mm; a zoom range gives the wide (first) figure.
        if (mfd := self._num(rows.get("Minimum Focusing Distance"), r"([\d.]+)")) is not None:
            if re.search(r"cm", rows.get("Minimum Focusing Distance", "")):
                out["minFocusDistance"] = round(mfd * 10)
        mag = re.search(r"1\s*:\s*([\d.]+)", rows.get("Maximum Magnification Ratio", ""))
        if mag:
            out["maxMagnification"] = round(1 / float(mag.group(1)), 3)
        return out

    @staticmethod
    def _spec_rows(content: str) -> dict[str, str]:
        rows: dict[str, str] = {}
        pattern = re.compile(
            r'l-grid --panel-2">\s*<p>(.*?)</p>\s*<div>(.*?)</div>\s*</div>\s*</li>',
            re.DOTALL,
        )
        for m in pattern.finditer(content):
            label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip()
            value = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
            if label and value and label not in rows:
                rows[label] = value
        return rows

    @staticmethod
    def _first_value(value: str | None) -> str | None:
        """First per-mount value. Mount labels use a fullwidth colon on older
        pages ('L-Mount：280g') and an ASCII colon on newer ones
        ('Canon RF Mount: 250g'). Returns the value after the first colon, up
        to the next 'Mount:' label."""
        if not value:
            return None
        m = re.search(r"[：:]", value)
        if not m:
            return value
        after = value[m.end():]
        # The next mount value starts at the next 'Word(s) Mount[：:]' run.
        return re.split(r"\s+[\w-]+(?:\s+[\w-]+)*\s*[：:]", after, maxsplit=1)[0].strip()

    @staticmethod
    def _num(value: str | None, pattern: str) -> float | None:
        if not value:
            return None
        m = re.search(pattern, value)
        return float(m.group(1).replace(",", "")) if m else None

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
