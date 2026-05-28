"""SamyangExtractor — the Samyang BrandExtractor strategy.

Ports the Samyang-specific parsing from the old common.py onto the brandkit
contract. Samyang isolates the spec table between "Optical Construction" and
"Minimum Focusing Distance" (avoiding navigation false positives), supports
both "N type" and "type N" special-element formats, and labels coating
NCS / UMC / MC. Image URLs are extensionless (served as JPEG).
"""

import re

from pagefetch import ContentMode, Transport

from brandkit import BrandConfig, BrandExtractor

BASE_URL = "https://www.lksamyang.com"

_TEXT_NUMS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
}

# (label, [patterns]) — first matching pattern's count wins; same label sums.
_SPECIAL_PATTERNS = [
    ("aspherical", [
        r"(\d+)\s*(?:glass\s+)?(?:aspherical|ASP)\s+(?:lens|element)",
        r"(\d+)\s*(?:glass\s+)?(?:aspherical|ASP)\b",
        r"\b(?:ASP)\s+(\d+)",
    ]),
    ("aspherical", [
        r"(\d+)\s*(?:hybrid\s+aspherical|H-ASP)\b",
        r"\bH-ASP\s+(\d+)",
    ]),
    ("ED", [
        r"(\d+)\s*(?:extra[- ]?low[- ]?dispersion|ED)\s+(?:lens|element)",
        r"(\d+)\s*(?:extra[- ]?low[- ]?dispersion|ED)\b",
        r"\bED\s+(\d+)",
    ]),
    ("HR", [
        r"(\d+)\s*(?:high[- ]?refractive|HR)\s+(?:lens|element)",
        r"(\d+)\s*(?:high[- ]?refractive|HR)\b",
        r"\bHR\s+(\d+)",
    ]),
]


class SamyangExtractor(BrandExtractor):
    config = BrandConfig(
        name="Samyang",
        slug_prefix="samyang",
        content_mode=ContentMode.HTML,
        transport=Transport.AUTO,
        has_diagrams=True,
    )

    def extract_optical(self, content: str) -> dict:
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", content))
        block = self._spec_block(text)
        if not block:
            return {}
        for word, digit in _TEXT_NUMS.items():
            block = re.sub(rf"\b{word}\b", digit, block, flags=re.IGNORECASE)

        specs: dict = {}
        m = re.search(
            r"(\d+)\s*(?:lenses|elements?)\s+(?:in\s+)?(\d+)\s*groups?",
            block, re.IGNORECASE,
        )
        if m:
            specs["elements"] = int(m.group(1))
            specs["groups"] = int(m.group(2))
        specs["special"] = self._special(block)
        specs["coating"] = self._coating(block, text)
        return specs

    def extract_physical(self, content: str) -> dict:
        """Parse physical specs from Samyang's th2/td2 spec rows (#779).

        Rows are <td class="th2">Label</td><td class="td2">value</td>. The
        same lens ships in several mounts, so some rows (Weight) list a value
        per mount — we take the first numeric value (mount-specific weights
        differ slightly; --verify surfaces any real divergence)."""
        rows = self._spec_rows(content)
        out: dict = {}

        if ft := self._num(rows.get("Filter Size"), r"([\d.]+)\s*mm"):
            out["filterThread"] = ft
        if dia := self._num(rows.get("Maximum Diameter"), r"([\d.]+)\s*mm"):
            out["diameter"] = dia
        if length := self._num(rows.get("Length"), r"([\d.]+)\s*mm"):
            out["length"] = length
        if blades := self._num(rows.get("Number of Diaphragm Blades"), r"(\d+)"):
            out["apertureBlades"] = blades
        if (mfd := self._num(rows.get("Minimum Focusing Distance"), r"([\d.]+)\s*m")) is not None:
            out["minFocusDistance"] = round(mfd * 1000)
        # Weight: first numeric (mounts listed left-to-right).
        if w := self._num(rows.get("Weight"), r"([\d.]+)\s*g"):
            out["weight"] = w
        # "Aperture Range" reads "F2.0 ~ 22" — the first value is max aperture.
        if ap := self._num(rows.get("Aperture Range"), r"F/?([\d.]+)"):
            out["maxAperture"] = ap
        if (mag := self._num(rows.get("Maximum Magnification Ratio"), r"([\d.]+)")) is not None:
            out["maxMagnification"] = mag
        return out

    @staticmethod
    def _spec_rows(content: str) -> dict[str, str]:
        """Label -> value from the th2/td2 spec table. First value per label
        wins (mount columns trail the first value)."""
        rows: dict[str, str] = {}
        for m in re.finditer(
            r'<td[^>]*class="th2"[^>]*>(.*?)</td>\s*<td[^>]*class="td2"[^>]*>(.*?)</td>',
            content, re.DOTALL,
        ):
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
    def _spec_block(text: str) -> str:
        """The spec table sits between these two headings; isolate it to
        avoid matching navigation and marketing copy."""
        m = re.search(
            r"Optical Construction\s+(.*?)Minimum Focusing",
            text, re.IGNORECASE | re.DOTALL,
        )
        return m.group(1) if m else ""

    @staticmethod
    def _special(block: str) -> list[str]:
        special: list[str] = []
        seen: dict[str, int] = {}
        for label, patterns in _SPECIAL_PATTERNS:
            count = 0
            for pat in patterns:
                m = re.search(pat, block, re.IGNORECASE)
                if m:
                    count = int(m.group(1))
                    break
            if count > 0:
                if label in seen:
                    idx = seen[label]
                    existing = int(special[idx].split()[0])
                    special[idx] = f"{existing + count} {label}"
                else:
                    seen[label] = len(special)
                    special.append(f"{count} {label}")
        return special

    @staticmethod
    def _coating(block: str, text: str) -> list[str]:
        if re.search(r"Coating\s+NCS\b|Nano\s*Coating\s*System", block, re.IGNORECASE):
            return ["NCS"]
        if re.search(r"Coating\s+UMC\b|Ultra\s*Multi\s*Coat", block, re.IGNORECASE):
            return ["UMC"]
        if re.search(r"Coating\s+MC\b", block, re.IGNORECASE):
            return ["MC"]
        # Fallback: a "Coating <VAL>" elsewhere on the page.
        cm = re.search(r"Coating\s+(\w+)", text)
        if cm and cm.group(1).upper() in ("NCS", "UMC", "MC"):
            return [cm.group(1).upper()]
        return []

    def extract_image_urls(self, content: str, url: str = "") -> dict[str, list[str]]:
        # Samyang matches on heading-adjacent <img>; url is unused.
        urls: dict[str, list[str]] = {"mtf": [], "construction": []}
        mtf = re.search(
            r"MTF\s*(?:Chart|CHART)\s*</strong>[^<]*<img\s+src=\"([^\"]+)\"",
            content, re.IGNORECASE,
        )
        if mtf:
            urls["mtf"].append(self._resolve(mtf.group(1)))
        con = re.search(
            r"Optical\s*Construction\s*</strong>[^<]*<img\s+src=\"([^\"]+)\"",
            content, re.IGNORECASE,
        )
        if con:
            urls["construction"].append(self._resolve(con.group(1)))
        return urls

    @staticmethod
    def _resolve(src: str) -> str:
        return src if src.startswith("http") else BASE_URL + src
