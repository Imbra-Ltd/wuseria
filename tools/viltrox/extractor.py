"""ViltroxExtractor — the Viltrox BrandExtractor strategy.

Viltrox runs a Shopify storefront: specs live in the product JSON API at
/products/{handle}.json, inside product.body_html. So this extractor's
"content" is the raw JSON text — it json.loads it itself, then parses the
embedded HTML. normalize_url appends ".json" so brandkit fetches the API
endpoint. Viltrox publishes no MTF/construction diagrams (has_diagrams
False), and every AF lens uses the same "HD Nano multilayer coating" — when
a page omits it, the coating is inferred (flagged via coating_inferred).
"""

import json
import re

from pagefetch import ContentMode, Transport

from brandkit import BrandConfig, BrandExtractor

VILTROX_COATING = "HD Nano multilayer coating"

_SPECIAL_PATTERNS = [
    ("aspherical", r"(\d+)\s*(?:aspherical|asph)\b"),
    ("ED", r"(\d+)\s*ED\b"),
    ("HR", r"(\d+)\s*(?:HR|HRI|High[- ]Refract(?:ive|ion)(?:\s+(?:Index|index))?)\b"),
    ("LD", r"(\d+)\s*(?:LD|Low[- ]Dispersion)\b"),
]


def url_to_handle(url: str) -> str:
    """Shopify product handle: https://viltrox.com/products/af-9mm-f2-8-xf
    -> af-9mm-f2-8-xf"""
    return url.rstrip("/").split("/products/")[-1]


class ViltroxExtractor(BrandExtractor):
    config = BrandConfig(
        name="Viltrox",
        slug_prefix="viltrox",
        content_mode=ContentMode.HTML,  # the JSON endpoint returns raw text
        transport=Transport.AUTO,
        has_diagrams=False,
    )

    def normalize_url(self, url: str) -> str:
        """Fetch the Shopify product JSON, not the HTML page."""
        return url.rstrip("/") + ".json"

    def extract_optical(self, content: str) -> dict:
        body = self._body_html(content)
        if body is None:
            return {}
        text = re.sub(r"\s+", " ", re.sub(r"&nbsp;", " ", re.sub(r"<[^>]+>", " ", body))).strip()

        specs: dict = {}
        self._elements_groups(text, specs)
        specs["special"] = [
            f"{m.group(1)} {label}"
            for label, pat in _SPECIAL_PATTERNS
            if (m := re.search(pat, text, re.IGNORECASE))
        ]
        self._coating(text, specs)
        return specs

    @staticmethod
    def _body_html(content: str) -> str | None:
        """Pull product.body_html out of the Shopify JSON text."""
        try:
            data = json.loads(content)
        except (ValueError, TypeError):
            return None
        return data.get("product", {}).get("body_html", "")

    @staticmethod
    def _elements_groups(text: str, specs: dict) -> None:
        # Pattern 1: "N elements in M groups".
        m = re.search(r"(\d+)\s*elements?\s+(?:in\s+)?(\d+)\s*groups?", text, re.IGNORECASE)
        if m:
            specs["elements"], specs["groups"] = int(m.group(1)), int(m.group(2))
            return
        # Pattern 2: "N/M Elements" / "N/M Optical Design" (elements/groups order).
        m = re.search(r"(\d+)/(\d+)\s*(?:Elements|Optical\s+Design)", text, re.IGNORECASE)
        if m:
            specs["elements"], specs["groups"] = int(m.group(1)), int(m.group(2))
            return
        # Pattern 3: "N/M Elements" where the larger number is elements.
        m = re.search(r"(\d+)/(\d+)\s*Elements?", text, re.IGNORECASE)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            specs["elements"], specs["groups"] = (a, b) if a > b else (b, a)

    @staticmethod
    def _coating(text: str, specs: dict) -> None:
        if re.search(r"(?:HD\s+)?[Nn]ano\s*(?:multi[- ]?layer\s+)?coat", text, re.IGNORECASE) or \
           re.search(r"nano[- ]?coat", text, re.IGNORECASE):
            specs["coating"] = [VILTROX_COATING]
            return
        # Brand-level default: every Viltrox AF lens uses this coating.
        specs["coating"] = [VILTROX_COATING]
        specs["coating_inferred"] = True
