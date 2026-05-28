"""TamronExtractor — the Tamron BrandExtractor strategy.

Tamron splits data across two pages: element/group counts and diagrams live
on a "spec.html" sub-page, while special elements and coating are on the main
page. The brandkit BrandTool concatenates both (via config.extra_paths), so
extract_optical sees the combined HTML. Image URLs are SVGs keyed by a
product code derived from the lens URL (.../lenses/b060/ -> b060), and appear
only on the spec page (harmless to match against the combined HTML).
"""

import re

from pagefetch import ContentMode, Transport

from brandkit import BrandConfig, BrandExtractor

BASE_URL = "https://www.tamron.com"

_TEXT_NUMS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
}

_SPECIAL_PATTERNS = [
    ("GM aspherical", [
        r"(\d+)\s*(?:x\s+)?GM\b",
        r"(\d+)\s*Glass\s+Molded\s+Aspherical",
    ]),
    ("hybrid aspherical", [
        r"(\d+)\s*(?:x\s+)?hybrid\s+aspherical",
        r"(\d+)\s*(?:x\s+)?aspherical\s+hybrid",
    ]),
    ("XLD", [
        r"(\d+)\s*(?:x\s+)?XLD\b",
        r"(\d+)\s*eXtra\s+Low\s+Dispersion",
    ]),
    ("LD", [
        r"(\d+)\s*(?:x\s+)?LD\s*\(Low\s+Dispersion\)",
        r"(\d+)\s*Low\s+Dispersion",
        r"(\d+)\s*(?:x\s+)?LD\b",
    ]),
]

_SPECIAL_FALLBACKS = {
    "GM aspherical": r"\bGM\s*\(Glass\s+Molded\s+Aspherical\)",
    "hybrid aspherical": r"\bhybrid\s+aspherical",
    "XLD": r"\bXLD\b",
    "LD": r"\bLD\s*\(Low\s+Dispersion\)",
}


def url_to_code(url: str) -> str:
    """Tamron model code is the last path segment:
    https://www.tamron.com/global/consumer/lenses/b060/ -> b060"""
    return url.rstrip("/").split("/")[-1]


class TamronExtractor(BrandExtractor):
    config = BrandConfig(
        name="Tamron",
        slug_prefix="tamron",
        content_mode=ContentMode.HTML,
        transport=Transport.AUTO,
        has_diagrams=True,
        extra_paths=("spec.html",),
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
        specs["coating"] = self._coating(text)
        return specs

    def extract_physical(self, content: str) -> dict:
        """Parse physical specs from Tamron's spec.html th/td table (#779).

        The spec sub-page (fetched + concatenated via config.extra_paths) has
        clean <th>label</th><td>value</td> rows. Multi-mount lenses list
        per-mount values ('86.2mm / ... (for Sony E-mount)'); the first value
        wins. Magnification 'N:M' -> decimal; MOD metres -> mm."""
        rows = self._spec_rows(content)
        out: dict = {}

        if ft := self._num(rows.get("Filter Size"), r"([\d.]+)\s*mm"):
            out["filterThread"] = ft
        if dia := self._num(rows.get("Maximum Diameter"), r"([\d.]+)\s*mm"):
            out["diameter"] = dia
        for key in ("Length", "Length *", "Overall Length"):
            if length := self._num(rows.get(key), r"([\d.]+)\s*mm"):
                out["length"] = length
                break
        if w := self._num(rows.get("Weight"), r"([\d.]+)\s*g"):
            out["weight"] = w
        if blades := self._num(rows.get("Aperture Blades"), r"(\d+)"):
            out["apertureBlades"] = blades
        # MOD: first value (WIDE) in "0.15m (5.9 in) (WIDE) / 0.24m (TELE)".
        if (mod := self._num(rows.get("Minimum Object Distance"), r"([\d.]+)\s*m")) is not None:
            out["minFocusDistance"] = round(mod * 1000)
        mag = re.search(r"1\s*:\s*([\d.]+)", rows.get("Maximum Magnification Ratio", ""))
        if mag:
            out["maxMagnification"] = round(1 / float(mag.group(1)), 3)
        return out

    @staticmethod
    def _spec_rows(content: str) -> dict[str, str]:
        rows: dict[str, str] = {}
        for m in re.finditer(r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>", content, re.DOTALL):
            label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip()
            value = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
            if label and value and label not in rows:
                rows[label] = value
        return rows

    @staticmethod
    def _num(value: str | None, pattern: str) -> float | None:
        if not value:
            return None
        m = re.search(pattern, value)
        return float(m.group(1)) if m else None

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

    @staticmethod
    def _coating(text: str) -> list[str]:
        coating: list[str] = []
        if re.search(r"BBAR\s+G2", text, re.IGNORECASE):
            coating.append("BBAR G2")
        elif re.search(r"BBAR\b", text, re.IGNORECASE):
            coating.append("BBAR")
        if re.search(r"\bfluorine\b", text, re.IGNORECASE):
            coating.append("fluorine")
        return coating

    def extract_image_urls(self, content: str, url: str = "") -> dict[str, list[str]]:
        urls: dict[str, list[str]] = {"mtf": [], "construction": []}
        code = url_to_code(url)
        if not code:
            return urls
        mtf = re.compile(
            r'(?:src|href)="([^"]*' + re.escape(code) + r'_mtf[^"]*\.svg)"',
            re.IGNORECASE,
        )
        for m in mtf.finditer(content):
            resolved = self._resolve(m.group(1))
            if resolved not in urls["mtf"]:
                urls["mtf"].append(resolved)
        con = re.compile(
            r'(?:src|href)="([^"]*' + re.escape(code) + r'_lens-construction[^"]*\.svg)"',
            re.IGNORECASE,
        )
        for m in con.finditer(content):
            resolved = self._resolve(m.group(1))
            if resolved not in urls["construction"]:
                urls["construction"].append(resolved)
        return urls

    @staticmethod
    def _resolve(src: str) -> str:
        if src.startswith("http"):
            return src
        return BASE_URL + (src if src.startswith("/") else "/" + src)
