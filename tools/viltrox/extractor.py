"""ViltroxExtractor — the Viltrox BrandExtractor strategy.

Viltrox runs a Shopify storefront. Historically specs lived in the product
JSON API (/products/{handle}.json, inside product.body_html), but Viltrox
moved them into a spec table rendered in the theme HTML of the product page
(#901). So this extractor fetches the HTML page (normalize_url is identity)
and parses a <table> whose rows are 'Label | per-mount values...'.

The table lists one value column per mount the lens ships in, in no fixed
order (e.g. E, Z, XF on one lens; E, X, EF-M, Z on another). The X-mount
column is selected from the 'Mount Type' row; for a single-value row the one
value is used. Labels and units drift across product generations ('Lens
Size' vs 'Outer Diameter Size', 'Filter Size' φ67mm vs Φ52, 'Aperture
Blades' vs 'Number of Aperture Blades'), so lookups use synonym sets and the
numeric parse ignores the Φ/φ diameter sign.

Viltrox publishes no MTF/construction diagrams (has_diagrams False), and
every AF lens uses the same 'HD Nano multilayer coating' — when a page omits
it, the coating is inferred (flagged via coating_inferred).
"""

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

# Label synonyms across product generations -> canonical spec key.
_FILTER_LABELS = ("Filter Size",)
_DIM_LABELS = ("Lens Size", "Outer Diameter Size", "Dimensions")
_WEIGHT_LABELS = ("Weight",)
_BLADES_LABELS = ("Number of Aperture Blades", "Aperture Blades")
_MAG_LABELS = ("Max.Magnification", "Maximum Magnification", "Magnification")
_MFD_LABELS = ("Shooting Distance", "Focus Range", "Focusing Range")
_ELEMENTS_LABELS = ("Lens Elements", "Lens Structure", "Optical Design")
_MOTOR_LABELS = ("Focus Motor",)


class ViltroxExtractor(BrandExtractor):
    config = BrandConfig(
        name="Viltrox",
        slug_prefix="viltrox",
        content_mode=ContentMode.HTML,
        transport=Transport.AUTO,
        has_diagrams=False,
    )

    def extract_optical(self, content: str) -> dict:
        rows = self._spec_rows(content)
        specs: dict = {}
        for label in _ELEMENTS_LABELS:
            m = re.search(r"(\d+)\s*/\s*(\d+)", rows.get(label, ""))
            if m:
                specs["elements"], specs["groups"] = int(m.group(1)), int(m.group(2))
                break
        # Special elements, when named at all, appear in the product
        # description prose — never the spec table. Scan only that block: the
        # full theme page is full of CSS/JS hex (e.g. a color-scheme UUID
        # '...b953ed' would otherwise read as '953 ED'). Most pages name no
        # counts, so [] is the common, correct result.
        desc = self._description(content)
        specs["special"] = [
            f"{m.group(1)} {label}"
            for label, pat in _SPECIAL_PATTERNS
            if (m := re.search(pat, desc, re.IGNORECASE))
        ]
        self._coating(desc, specs)
        return specs

    @staticmethod
    def _description(content: str) -> str:
        """The product description prose (the .rte / product__description
        block), tags stripped. Empty string if not found."""
        m = re.search(
            r'<div[^>]*class="[^"]*(?:product__description|rte)[^"]*"[^>]*>(.*?)</div>',
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if not m:
            return ""
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip()

    def extract_physical(self, content: str) -> dict:
        """Parse physical specs from Viltrox's theme spec table (#901).

        Picks the X-mount column per row. Filter/dimensions ignore the Φ/φ
        sign; dimensions are 'φDIAxLENmm' (x or ×); weight drops the ≈/=
        prefix; magnification drops a trailing 'X'; MFD ('0.28m-∞') is metres
        -> mm. afMotor is the focus-motor cell verbatim."""
        rows = self._spec_rows(content)
        out: dict = {}

        if ft := self._num(self._first(rows, _FILTER_LABELS), r"([\d.]+)"):
            out["filterThread"] = ft
        dims = self._first(rows, _DIM_LABELS)
        if dims:
            dm = re.search(r"([\d.]+)\s*[x×]\s*([\d.]+)\s*mm", dims)
            if dm:
                out["diameter"] = float(dm.group(1))
                out["length"] = float(dm.group(2))
        if w := self._num(self._first(rows, _WEIGHT_LABELS), r"([\d,]+\.?\d*)\s*g"):
            out["weight"] = w
        if blades := self._num(self._first(rows, _BLADES_LABELS), r"(\d+)"):
            out["apertureBlades"] = blades
        if (mag := self._num(self._first(rows, _MAG_LABELS), r"([\d.]+)")) is not None:
            out["maxMagnification"] = mag
        mfd = self._first(rows, _MFD_LABELS)
        if mfd and (mm := re.search(r"([\d.]+)\s*m\b", mfd)):
            out["minFocusDistance"] = round(float(mm.group(1)) * 1000)
        if motor := self._first(rows, _MOTOR_LABELS):
            out["afMotor"] = motor
        return out

    @staticmethod
    def _spec_rows(content: str) -> dict[str, str]:
        """Parse the spec <table> into {label: x-mount value}.

        Each <tr> is 'Label | mount-1 value | mount-2 value | ...'. The
        X-mount column index comes from the 'Mount Type' row (the cell
        containing 'X-mount'); rows with a single value use it directly,
        and when no Mount Type row is found the last value wins."""
        table = ViltroxExtractor._spec_table(content)
        if not table:
            return {}
        parsed: list[tuple[str, list[str]]] = []
        for tr in re.finditer(r"<tr[^>]*>(.*?)</tr>", table, re.DOTALL):
            cells = [
                re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip()
                for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr.group(1), re.DOTALL)
            ]
            if cells and cells[0]:
                parsed.append((cells[0], cells[1:]))

        col = ViltroxExtractor._x_mount_col(parsed)
        rows: dict[str, str] = {}
        for label, values in parsed:
            if not values:
                continue
            value = values[col] if col is not None and col < len(values) else values[-1]
            if label not in rows:
                rows[label] = value
        return rows

    @staticmethod
    def _spec_table(content: str) -> str | None:
        """The product spec table — the one containing the elements row."""
        for labels in (_ELEMENTS_LABELS,):
            for label in labels:
                i = content.find(label)
                if i < 0:
                    continue
                start = content.rfind("<table", 0, i)
                end = content.find("</table>", i)
                if start >= 0 and end >= 0:
                    return content[start : end + len("</table>")]
        return None

    @staticmethod
    def _x_mount_col(parsed: list[tuple[str, list[str]]]) -> int | None:
        for label, values in parsed:
            if label.strip().lower() == "mount type":
                for idx, val in enumerate(values):
                    if re.search(r"\bX[- ]?mount\b", val, re.IGNORECASE):
                        return idx
        return None

    @staticmethod
    def _first(rows: dict[str, str], labels: tuple[str, ...]) -> str | None:
        for label in labels:
            if label in rows:
                return rows[label]
        return None

    @staticmethod
    def _num(value: str | None, pattern: str) -> float | None:
        if not value:
            return None
        m = re.search(pattern, value)
        return float(m.group(1).replace(",", "")) if m else None

    @staticmethod
    def _coating(text: str, specs: dict) -> None:
        if re.search(r"(?:HD\s+)?[Nn]ano\s*(?:multi[- ]?layer\s+)?coat", text, re.IGNORECASE) or \
           re.search(r"nano[- ]?coat", text, re.IGNORECASE):
            specs["coating"] = [VILTROX_COATING]
            return
        # Brand-level default: every Viltrox AF lens uses this coating.
        specs["coating"] = [VILTROX_COATING]
        specs["coating_inferred"] = True
