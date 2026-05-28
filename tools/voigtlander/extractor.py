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
