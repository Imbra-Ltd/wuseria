"""MitakonExtractor — the Mitakon (Zhongyi Optics) BrandExtractor strategy.

zyoptics.net blocks plain urllib and Playwright, so the page needs UC-mode
Chrome (config.transport = UC). It is a WooCommerce store: element/group
counts live in the spec table (tab panel 1), special glass is described in
prose, and the gallery holds product photos only (no MTF/construction
diagrams, so has_diagrams is False).

HRI handling: pages list "extra-high refractive index" and plain "high
refractive index" elements separately; both are HRI glass, so distinct
counts are summed into one HRI total.
"""

import re

from pagefetch import ContentMode, Transport

from brandkit import BrandConfig, BrandExtractor

_TEXT_NUMS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "sixteen": "16",
}

_SINGLE_PATTERNS = [
    ("aspherical", [
        r"(\d+)\s*(?:aspherical|asph\.?)\s*(?:lens|element|glass)",
        r"(\d+)\s*pcs?\s+(?:of\s+)?aspherical",
    ]),
    ("ED", [
        r"(\d+)\s*(?:extra[- ]low[- ]dispersion|ED)\s*(?:\([^)]*\)\s*)?(?:lens|element|glass)",
        r"(\d+)\s*pcs?\s+(?:of\s+)?(?:extra[- ]low[- ]dispersion|ED)",
    ]),
    ("UD", [
        r"(\d+)\s*(?:ultra[- ]low[- ]dispersion|UD)\s*(?:\([^)]*\)\s*)?(?:lens|element|glass)",
        r"(\d+)\s*pcs?\s+(?:of\s+)?(?:ultra[- ]low[- ]dispersion|UD)",
        r"(\d+)\s*pcs?\s+(?:of\s+)?UD\s*\(",
    ]),
    ("LD", [
        r"(\d+)\s*(?:low[- ]dispersion|LD)\s*(?:lens|element|glass)",
        r"(\d+)\s*pcs?\s+(?:of\s+)?(?:low[- ]dispersion|LD)",
    ]),
]

_HRI_EXTRA = [
    r"(\d+)\s*(?:extra[- ]high[- ]refract(?:ive|ion)[- ]?(?:index)?)\s*(?:\([^)]*\)\s*)?(?:lens|element|glass)e?s?",
    r"(\d+)\s*pcs?\s+(?:of\s+)?(?:extra[- ]high[- ]refract(?:ive|ion)[- ]?(?:index)?)",
]
_HRI_PLAIN = [
    r"(\d+)\s*(?:high[- ]?refract(?:ive|ion)[- ]?(?:index)?|HRI)\s*(?:\([^)]*\)\s*)?(?:lens|element|glass)",
    r"(\d+)\s*pcs?\s+(?:of\s+)?(?:high[- ]?refract(?:ive|ion)[- ]?(?:index)?|HRI)",
]


def _first_count(text: str, patterns: list[str]) -> int:
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return 0


class MitakonExtractor(BrandExtractor):
    config = BrandConfig(
        name="Mitakon",
        slug_prefix="mitakon",
        content_mode=ContentMode.HTML,
        transport=Transport.UC,  # zyoptics.net blocks urllib + Playwright
        has_diagrams=False,  # gallery is product photos only
    )

    def extract_optical(self, content: str) -> dict:
        specs: dict = {}
        self._elements_groups(content, specs)
        full_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", content))
        specs["special"] = self._special(self._normalize(full_text))
        specs["coating"] = self._coating(full_text)
        return specs

    def extract_physical(self, content: str) -> dict:
        """Parse physical specs from a zyoptics.net (GFX) product page (#779).

        Inline label-value spec run, e.g. 'Filter Thread 72 mm
        Dimensions (DxL) 82x 96mm Weight 1,050 g', plus 'Maximum
        Magnification 0.25x', 'Minimum Focus Distance 70 cm', an
        'Eleven-Bladed Diaphragm' (text number), and 'Aperture range f/1.4'.
        Dimensions are (DxL) = diameter x length; weight carries a comma."""
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", content)).replace("&nbsp;", " ")
        out: dict = {}

        if ft := self._num(text, r"Filter Thread\s*([\d.]+)\s*mm"):
            out["filterThread"] = ft
        # Dimensions "(DxL) 82x 96mm" -> diameter x length.
        dims = re.search(r"Dimensions\s*\(?D\s*x\s*L\)?\s*([\d.]+)\s*x\s*([\d.]+)\s*mm", text, re.IGNORECASE)
        if dims:
            out["diameter"] = float(dims.group(1))
            out["length"] = float(dims.group(2))
        # Weight carries a thousands comma ("1,050 g").
        wm = re.search(r"Weight\s*([\d,]+(?:\.\d+)?)\s*g", text, re.IGNORECASE)
        if wm:
            out["weight"] = float(wm.group(1).replace(",", ""))
        if (mag := self._num(text, r"Maximum Magnification\s*([\d.]+)\s*x")) is not None:
            out["maxMagnification"] = mag
        if (mfd := self._num(text, r"Minimum Focus(?:ing)?\s*Distance\s*([\d.]+)\s*cm")) is not None:
            out["minFocusDistance"] = round(mfd * 10)  # cm -> mm
        if ap := self._num(text, r"Aperture range\s*f/?([\d.]+)"):
            out["maxAperture"] = ap
        # Blades: "Eleven-Bladed Diaphragm" (text number) or "11 blades".
        bm = re.search(r"(\w+)[- ]Bladed", text, re.IGNORECASE)
        if bm:
            n = _TEXT_NUMS.get(bm.group(1).lower())
            if n:
                out["apertureBlades"] = float(n)
        elif blades := self._num(text, r"(\d+)\s*(?:aperture\s*)?blades?"):
            out["apertureBlades"] = blades
        return out

    @staticmethod
    def _num(text: str, pattern: str) -> float | None:
        m = re.search(pattern, text, re.IGNORECASE)
        return float(m.group(1)) if m else None

    @staticmethod
    def _normalize(text: str) -> str:
        for word, digit in _TEXT_NUMS.items():
            text = re.sub(rf"\b{word}\b", digit, text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def _elements_groups(html: str, specs: dict) -> None:
        """Prefer the spec table (WooCommerce tab panel 1) over description prose."""
        pat = r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?"
        panels = re.findall(
            r'class="woocommerce-Tabs-panel[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL
        )
        m = None
        if len(panels) > 1:
            panel1 = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", panels[1]))
            m = re.search(pat, panel1, re.IGNORECASE)
        if not m:
            full = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
            m = re.search(pat, full, re.IGNORECASE)
        if m:
            specs["elements"] = int(m.group(1))
            specs["groups"] = int(m.group(2))

    @staticmethod
    def _special(text: str) -> list[str]:
        special: list[str] = []
        for label, patterns in _SINGLE_PATTERNS:
            for pat in patterns:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    special.append(f"{m.group(1)} {label}")
                    break
        # HRI: sum distinct "extra-high" + plain "high" counts into one total.
        hri_extra = _first_count(text, _HRI_EXTRA)
        hri_plain = _first_count(text, _HRI_PLAIN)
        if hri_extra and hri_plain:
            special.append(f"{hri_extra + hri_plain} HRI")
        elif hri_plain:
            special.append(f"{hri_plain} HRI")
        elif hri_extra:
            special.append(f"{hri_extra} HRI")
        return special

    @staticmethod
    def _coating(text: str) -> list[str]:
        if re.search(r"nano[- ]?coat", text, re.IGNORECASE):
            return ["Nano coating"]
        if re.search(r"super[- ]?multi[- ]?coat", text, re.IGNORECASE):
            return ["Super multi-coating"]
        if re.search(r"MC\s+Multi[- ]?Layer", text, re.IGNORECASE):
            return ["MC Multi-Layer"]
        if re.search(r"multi[- ]?layer\s+coat", text, re.IGNORECASE):
            return ["Multi-layer coating"]
        if re.search(r"multi[- ]?coat", text, re.IGNORECASE):
            return ["Multi-coating"]
        return []
