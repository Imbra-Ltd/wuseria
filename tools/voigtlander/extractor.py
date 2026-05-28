"""VoigtlanderExtractor — the Voigtlander BrandExtractor strategy.

Voigtlander (Cosina) uses a Divi/JS theme, so the page needs a real browser
to render (config.transport = PLAYWRIGHT). The extractor itself is the
simplest of all brands: only elements/groups (Voigtlander publishes no
special-glass counts or coating data, and no MTF charts — only construction
diagrams, named in German: Linsenaufbau / Linsenschnitt).
"""

import re

from pagefetch import ContentMode, Transport

from brandkit import BrandConfig, BrandExtractor

BASE_URL = "https://www.voigtlaender.de"


class VoigtlanderExtractor(BrandExtractor):
    config = BrandConfig(
        name="Voigtlander",
        slug_prefix="voigtlander",
        content_mode=ContentMode.HTML,
        transport=Transport.PLAYWRIGHT,  # Divi theme renders via JS
        has_diagrams=True,
    )

    def extract_optical(self, content: str) -> dict:
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", content))
        m = re.search(
            r"(\d+)\s*(?:lenses?|elements?)\s+in\s+(\d+)\s*groups?", text, re.IGNORECASE
        )
        if m:
            return {"elements": int(m.group(1)), "groups": int(m.group(2))}
        return {}

    def extract_physical(self, content: str) -> dict:
        """Parse physical specs from Voigtlander's inline label-value run
        (#779). Specs appear as 'Label value' in the rendered Divi text, e.g.
        'Aperture blades 12 Close focusing distance 0.18 m Max. Diameter
        59.3 mm Length 43.8 mm Weight 214 g Filter size diameter 46 mm'."""
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", content))
        text = text.replace("&nbsp;", " ")
        text = re.sub(r"&#\d+;", " ", text)  # drop entity digits (diameter sign)
        out: dict = {}

        if blades := self._num(text, r"Aperture blades\s*(\d+)"):
            out["apertureBlades"] = blades
        if (mfd := self._num(text, r"Close focusing distance\s*([\d.]+)\s*m")) is not None:
            out["minFocusDistance"] = round(mfd * 1000)  # metres -> mm
        # Diameter and length: the page gives them adjacently ("Maximum
        # diameter 59.3 mm Length 43.8 mm"). Anchor length to the diameter so
        # the focal-length prose elsewhere ("35mm lens ... Length") can't match.
        dl = re.search(
            r"(?:Max\.?\s*|Maximum\s*)Diameter\s*([\d.]+)\s*mm\s*Length\s*([\d.]+)\s*mm",
            text, re.IGNORECASE,
        )
        if dl:
            out["diameter"] = float(dl.group(1))
            out["length"] = float(dl.group(2))
        if w := self._num(text, r"Weight\s*([\d.]+)\s*g"):
            out["weight"] = w
        # "Filter size diameter 46 mm" or "Filter size ? 46 mm".
        if ft := self._num(text, r"Filter size(?:\s*diameter)?\s*([\d.]+)\s*mm"):
            out["filterThread"] = ft
        # "Largest magnification 1:N" or a decimal, when present with a value.
        mag = re.search(r"Largest magnification\s*1\s*:\s*([\d.]+)", text, re.IGNORECASE)
        if mag:
            out["maxMagnification"] = round(1 / float(mag.group(1)), 3)
        return out

    @staticmethod
    def _num(text: str, pattern: str) -> float | None:
        m = re.search(pattern, text, re.IGNORECASE)
        return float(m.group(1)) if m else None

    def extract_image_urls(self, content: str, url: str = "") -> dict[str, list[str]]:
        # Voigtlander publishes construction diagrams only (no MTF charts);
        # filenames use English or German terms.
        urls: dict[str, list[str]] = {"mtf": [], "construction": []}
        for m in re.finditer(
            r'src="([^"]*(?:lens[-_]?construction|Linsenaufbau|Linsenschnitt)[^"]*\.(?:jpg|png|webp))',
            content, re.IGNORECASE,
        ):
            resolved = self._resolve(m.group(1))
            if resolved not in urls["construction"]:
                urls["construction"].append(resolved)
        return urls

    @staticmethod
    def _resolve(src: str) -> str:
        if src.startswith("http"):
            return src
        return BASE_URL + (src if src.startswith("/") else "/" + src)
