"""Search the local LensTip lens index.

Finds LensTip spec page URLs by fuzzy-matching lens names against
the local index built by build_index.py.

Usage:
    py tools/lenstip/search.py "Viltrox 56mm"
    py tools/lenstip/search.py "XF 90mm f/2"
    py tools/lenstip/search.py "Sigma 56mm" --brand Sigma
    py tools/lenstip/search.py "TTartisan 50mm" --limit 5

Requires: tools/lenstip/lenstip-index.json (run build_index.py first)
"""

import argparse
import json
import re
import sys
from pathlib import Path

INDEX_FILE = Path(__file__).parent / "lenstip-index.json"


def normalize(text: str) -> str:
    """Normalize a lens name for fuzzy matching."""
    t = text.lower()
    # Normalize common variants
    t = t.replace("f/", "f").replace("f /", "f")
    t = t.replace("-", " ").replace("_", " ")
    # Split number+unit clusters: "56mm" → "56 mm", "f1.4" → "f 1.4"
    t = re.sub(r"(\d)(mm|cm)\b", r"\1 \2", t)
    t = re.sub(r"(f)([\d])", r"\1 \2", t)
    # Remove extra whitespace
    t = " ".join(t.split())
    return t


def tokenize(text: str) -> list[str]:
    """Split normalized text into word-boundary tokens."""
    return text.split()


def score_match(query_terms: list[str], name_normalized: str) -> float:
    """Score how well query terms match a lens name. Higher is better.

    Uses word-boundary matching: "56" matches the token "56" in
    "viltrox af 56 mm f1.4 xf" but not "156" or "560".
    """
    name_tokens = tokenize(name_normalized)
    matched = 0
    for term in query_terms:
        # Exact token match (word boundary) scores higher
        if term in name_tokens:
            matched += 1.0
        # Substring match (e.g. "56mm" in "56") scores partial
        elif term in name_normalized:
            matched += 0.5
    if matched == 0:
        return 0.0
    coverage = matched / len(query_terms)
    # Bonus for shorter names (more specific match)
    brevity = 1.0 / (1.0 + len(name_normalized) / 100)
    return coverage + brevity * 0.1


def search(
    query: str,
    *,
    brand_filter: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Search the index for lenses matching the query."""
    if not INDEX_FILE.exists():
        print(
            "Index not found. Run: py tools/lenstip/build_index.py",
            file=sys.stderr,
        )
        sys.exit(1)

    index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    query_normalized = normalize(query)
    query_terms = query_normalized.split()

    results = []
    for brand_name, lenses in index.get("brands", {}).items():
        if brand_filter and brand_filter.lower() not in brand_name.lower():
            continue
        for lens in lenses:
            name_normalized = normalize(lens["name"])
            # Also match against brand + name combined
            full_normalized = normalize(f"{brand_name} {lens['name']}")
            score = max(
                score_match(query_terms, name_normalized),
                score_match(query_terms, full_normalized),
            )
            if score > 0:
                results.append({
                    "brand": brand_name,
                    "name": lens["name"],
                    "url": lens["url"],
                    "id": lens["id"],
                    "score": score,
                })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search the LensTip lens index"
    )
    parser.add_argument("query", help="Lens name to search for")
    parser.add_argument(
        "--brand", type=str, help="Filter to a single brand"
    )
    parser.add_argument(
        "--limit", type=int, default=10, help="Max results (default: 10)"
    )
    args = parser.parse_args()

    results = search(args.query, brand_filter=args.brand, limit=args.limit)

    if not results:
        print(f"No matches for: {args.query}")
        sys.exit(1)

    print(f"Results for: {args.query}\n")
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r['brand']}] {r['name']}")
        print(f"     {r['url']}")
        if i < len(results):
            print()


if __name__ == "__main__":
    main()
