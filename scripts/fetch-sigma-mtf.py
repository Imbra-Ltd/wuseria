"""Fetch MTF chart images from the official Sigma product pages.

Usage:
    py scripts/fetch-sigma-mtf.py                     # fetch missing charts only
    py scripts/fetch-sigma-mtf.py --lens c017_16_14   # fetch one by lens code
    py scripts/fetch-sigma-mtf.py --force              # re-download existing charts
    py scripts/fetch-sigma-mtf.py --dry-run            # list URLs without downloading
    py scripts/fetch-sigma-mtf.py --temp               # fetch to temp dir (for testing)

Sigma hosts MTF chart images at predictable URLs. Two patterns exist:
    /lenses/{code}_specification_02_{nn}.png          (most lenses)
    /lenses/images/{code}_specification_02_{n}.png    (newer pages)

Primes have 2 charts (diffraction + geometrical), zooms have 4
(diffraction + geometrical at wide and tele ends). The script probes
both URL patterns and stops on the first 404.

Images are saved to docs/mtf-charts/ as sigma-{slug}-mtf-{nn}.png.
"""

import sys
import urllib.request
import urllib.error
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "mtf-charts"
MAX_CHARTS = 4

# Two URL patterns exist on sigma-global.com
URL_PATTERNS = [
    "https://www.sigma-global.com/lenses/{code}_specification_02_{idx:02d}.png",
    "https://www.sigma-global.com/lenses/images/{code}_specification_02_{idx}.png",
]

# Map: lens code -> output slug
# Codes are from the officialUrl field in src/data/lenses.ts
LENSES = {
    "c023_10_18_28": "sigma-10-18mm-f2-8-dc-dn-c",
    "c025_12_14": "sigma-12mm-f1-4-dc-dn-c",
    "c026_15_14": "sigma-15mm-f1-4-dc-dn-c",
    "c017_16_14": "sigma-16mm-f1-4-dc-dn-c",
    "c025_16_300_35_67": "sigma-16-300mm-f3-5-6-7-dc-os-c",
    "a025_17_40_18": "sigma-17-40mm-f1-8-dc-art",
    "c021_18_50_28": "sigma-18-50mm-f2-8-dc-dn-c",
    "c023_23_14": "sigma-23mm-f1-4-dc-dn-c",
    "c016_30_14": "sigma-30mm-f1-4-dc-dn-c",
    "c018_56_14": "sigma-56mm-f1-4-dc-dn-c",
    "c020_100_400_5_63": "sigma-100-400mm-f5-6-3-dg-dn-os-c",
}


def out_path(output_dir: Path, slug: str, index: int) -> Path:
    """Build the output file path."""
    return output_dir / f"{slug}-mtf-{index:02d}.png"


def _head_ok(url: str) -> bool:
    """Return True if a HEAD request returns 200."""
    req = urllib.request.Request(url, method="HEAD", headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except urllib.error.HTTPError:
        return False


def resolve_pattern(code: str) -> str | None:
    """Find which URL pattern works for this lens by probing chart 01/1."""
    for pattern in URL_PATTERNS:
        url = pattern.format(code=code, idx=1)
        if _head_ok(url):
            return pattern
    return None


def probe_chart_count(pattern: str, code: str) -> int:
    """Probe how many MTF charts exist for a lens (1-4)."""
    count = 0
    for i in range(1, MAX_CHARTS + 1):
        url = pattern.format(code=code, idx=i)
        if _head_ok(url):
            count = i
        else:
            break
    return count


def all_exist(output_dir: Path, slug: str, expected: int) -> bool:
    """Check if all expected chart files already exist."""
    for count in range(expected, 0, -1):
        if all(out_path(output_dir, slug, i).exists() for i in range(1, count + 1)):
            return True
    return False


def fetch_lens(
    code: str, slug: str, output_dir: Path,
    dry_run: bool = False, force: bool = False,
) -> int:
    """Fetch all MTF charts for one lens. Returns number of new files saved."""
    # Skip network probing entirely when all charts exist and not forcing
    if not force and not dry_run:
        for count in (4, 2):
            if all(out_path(output_dir, slug, i).exists() for i in range(1, count + 1)):
                print(f"  SKIP (all {count} charts exist)")
                return 0

    pattern = resolve_pattern(code)
    if pattern is None:
        print(f"  WARN: no MTF charts found for {slug} ({code})")
        return 0

    count = probe_chart_count(pattern, code)
    if count == 0:
        print(f"  WARN: no MTF charts found for {slug} ({code})")
        return 0

    if dry_run:
        for i in range(1, count + 1):
            path = out_path(output_dir, slug, i)
            exists = "exists" if path.exists() else "missing"
            print(f"  {path.name} <- chart {i:02d} ({exists})")
        return 0

    saved = 0
    for i in range(1, count + 1):
        path = out_path(output_dir, slug, i)
        if path.exists() and not force:
            print(f"  SKIP {path.name} (already exists)")
            continue

        url = pattern.format(code=code, idx=i)
        print(f"  Downloading {url}...")
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": f"https://www.sigma-global.com/en/lenses/{code}/",
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()

        output_dir.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print(f"  SAVED {path.name} ({len(data)} bytes)")
        saved += 1

    return saved


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv
    use_temp = "--temp" in sys.argv
    lens_filter = None

    if "--lens" in sys.argv:
        idx = sys.argv.index("--lens")
        if idx + 1 < len(sys.argv):
            lens_filter = sys.argv[idx + 1]

    if use_temp:
        output_dir = Path(__file__).resolve().parent.parent / "temp"
        output_dir.mkdir(exist_ok=True)
        print(f"Output: {output_dir}\n")
    else:
        output_dir = OUTPUT_DIR

    targets = LENSES
    if lens_filter:
        if lens_filter not in LENSES:
            print(f"Unknown lens code: {lens_filter}")
            print(f"Known: {', '.join(LENSES.keys())}")
            sys.exit(1)
        targets = {lens_filter: LENSES[lens_filter]}

    mode = "DRY RUN" if dry_run else ("FETCH (force)" if force else "FETCH")
    print(f"[{mode}] {len(targets)} Sigma MTF charts\n")

    saved = 0
    for code, slug in targets.items():
        print(f"{slug}:")
        saved += fetch_lens(code, slug, output_dir, dry_run, force)
        print()

    print(f"Done. {saved} new images saved.")


if __name__ == "__main__":
    main()
