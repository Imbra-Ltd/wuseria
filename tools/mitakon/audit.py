"""Audit Mitakon lenses for missing optical specs.

Shows which lenses have optical construction data populated in lenses.ts
and which are missing.

Usage:
    py tools/mitakon/audit.py
"""

import re
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent.parent
LENSES_TS = ROOT / "src" / "data" / "lenses.ts"
OPTICAL_SPECS_DIR = ROOT / "docs" / "optical-specs"

OPTICAL_FIELDS = [
    "opticalElements",
    "opticalGroups",
    "specialElements",
    "coating",
]


def main() -> None:
    content = LENSES_TS.read_text(encoding="utf-8")
    blocks = re.split(r"(?=\{\s*\n\s*brand:)", content)

    lenses = []
    for block in blocks:
        if 'brand: "Mitakon"' not in block:
            continue
        model_m = re.search(r'model:\s*"([^"]+)"', block)
        mount_m = re.search(r'mount:\s*"([^"]+)"', block)
        if not model_m:
            continue

        model = model_m.group(1)
        mount = mount_m.group(1) if mount_m else "?"
        fields = {f: f in block for f in OPTICAL_FIELDS}
        lenses.append({"model": model, "mount": mount, "fields": fields})

    print(f"Mitakon: {len(lenses)} lenses\n")
    print(f"{'Model':<45} {'Mount':<5} {'El':>3} {'Gr':>3} {'Sp':>3} {'Co':>3} {'Folder'}")
    print("-" * 80)

    for lens in lenses:
        model = lens["model"]
        mount = lens["mount"]
        slug = model.lower().replace("f/", "f")
        slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
        slug = f"mitakon-{slug}"

        folder = OPTICAL_SPECS_DIR / slug
        has_folder = "Y" if folder.is_dir() else "-"

        def mark(field: str) -> str:
            return "Y" if lens["fields"][field] else "-"

        print(
            f"{model:<45} {mount:<5} "
            f"{mark('opticalElements'):>3} {mark('opticalGroups'):>3} "
            f"{mark('specialElements'):>3} {mark('coating'):>3} "
            f"{has_folder:>3}"
        )


if __name__ == "__main__":
    main()
