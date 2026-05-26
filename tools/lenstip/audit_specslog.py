"""Audit specs-logs for false LensTip "Not covered" entries.

Cross-references specs-log.md files that claim LensTip has no coverage
against the local LensTip index to find lenses that ARE covered but
were missed during research.

Usage:
    py tools/lenstip/audit_specslog.py           # check all specs-logs
    py tools/lenstip/audit_specslog.py --fix      # also print the correct URLs
"""

import argparse
import json
import re
import sys
from pathlib import Path

OPTICAL_SPECS_DIR = Path("docs/optical-specs")
INDEX_FILE = Path(__file__).parent / "lenstip-index.json"

# Import search from sibling module
sys.path.insert(0, str(Path(__file__).parent))
from search import search


def extract_lens_name_from_slug(slug: str) -> str:
    """Convert a directory slug back to a searchable lens name.

    e.g. "viltrox-af-56mm-f1-4" → "Viltrox 56mm f/1.4"
    """
    name = slug.replace("-", " ")
    # Restore f/ prefix: "f1.4" or "f1 4" → "f/1.4"
    name = re.sub(r"\bf(\d)", r"f/\1", name)
    # Restore decimal: "f/1 4" → "f/1.4"
    name = re.sub(r"(f/\d+) (\d+)", r"\1.\2", name)
    return name


def has_lenstip_not_covered(specs_log_path: Path) -> bool:
    """Check if a specs-log says LensTip is not covered."""
    text = specs_log_path.read_text(encoding="utf-8").lower()
    # Look for LensTip mentioned near "not covered/found" indicators
    lines = text.split("\n")
    for line in lines:
        if "lenstip" not in line:
            continue
        if any(neg in line for neg in [
            "not covered", "not found", "no coverage", "no results",
            "no page", "no entry", "n/a", "not listed", "not in database",
            "no lenstip", "not available",
        ]):
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit specs-logs for false LensTip 'Not covered' entries"
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="Print the correct LensTip URLs for false negatives",
    )
    args = parser.parse_args()

    if not INDEX_FILE.exists():
        print("Index not found. Run: py tools/lenstip/build_index.py")
        sys.exit(1)

    false_negatives = []
    checked = 0

    for specs_dir in sorted(OPTICAL_SPECS_DIR.iterdir()):
        if not specs_dir.is_dir():
            continue
        specs_log = specs_dir / "specs-log.md"
        if not specs_log.exists():
            continue

        if not has_lenstip_not_covered(specs_log):
            continue

        checked += 1
        slug = specs_dir.name
        lens_name = extract_lens_name_from_slug(slug)

        results = search(lens_name, limit=3)
        if not results or results[0]["score"] < 0.8:
            continue

        # Verify the brand actually matches — prevent cross-brand false positives
        # Extract brand from slug (first token before the model number)
        slug_brand = slug.split("-")[0].lower()
        # Brand aliases
        brand_aliases = {
            "kamlan": ["sainsonic", "kamlan"],
            "handevision": ["handevision", "kipon", "iberit"],
            "mitakon": ["mitakon", "zhongyi"],
            "pergear": ["pergear"],
        }
        allowed = brand_aliases.get(slug_brand, [slug_brand])
        match = results[0]
        match_brand = match["brand"].lower()
        match_name = match["name"].lower()

        brand_matches = any(
            alias in match_brand or alias in match_name
            for alias in allowed
        )
        if not brand_matches:
            continue

        false_negatives.append({
            "slug": slug,
            "search_query": lens_name,
            "lenstip_match": match["name"],
            "lenstip_url": match["url"],
            "score": match["score"],
            "specs_log": str(specs_log),
        })

    print(f"Checked {checked} specs-logs with LensTip 'not covered' entries")
    print(f"Found {len(false_negatives)} probable false negative(s)\n")

    if not false_negatives:
        print("All 'not covered' entries appear correct.")
        return

    for fn in false_negatives:
        print(f"  {fn['slug']}")
        print(f"    Searched: {fn['search_query']}")
        print(f"    Match:    {fn['lenstip_match']} (score: {fn['score']:.2f})")
        if args.fix:
            print(f"    URL:      {fn['lenstip_url']}")
        print(f"    File:     {fn['specs_log']}")
        print()


if __name__ == "__main__":
    main()
