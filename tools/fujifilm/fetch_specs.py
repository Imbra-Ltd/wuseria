"""Fetch optical specs, MTF charts, construction diagrams, and coatings from Fujifilm pages.

Combines the functionality of the old fetch-fujifilm-specs.py,
fetch-fujifilm-images.py, and fetch-fujifilm-coatings.py scripts.

Usage:
    py tools/fujifilm/fetch_specs.py                    # fetch all missing data
    py tools/fujifilm/fetch_specs.py --dry-run           # list what would be fetched
    py tools/fujifilm/fetch_specs.py --limit 5           # fetch first N lenses only
    py tools/fujifilm/fetch_specs.py --all               # re-fetch all, not just missing
    py tools/fujifilm/fetch_specs.py --filter gf         # filter by model substring
    py tools/fujifilm/fetch_specs.py --specs-only        # only extract specs text, no images
    py tools/fujifilm/fetch_specs.py --images-only       # only download images
    py tools/fujifilm/fetch_specs.py --coatings-only     # only extract coatings
"""

import argparse
import sys
import time
from pathlib import Path

from common import (
    ROOT,
    OPTICAL_CONSTRUCTION_DIR,
    MTF_CHARTS_DIR,
    extract_fujifilm_lenses,
    model_to_slug,
    url_to_slug,
    specs_url,
    browser_context,
    fetch_page_content,
    scroll_page,
    extract_specs,
    extract_coatings,
    extract_image_urls_by_position,
    download_image,
    read_cache,
    has_construction_image,
    has_mtf_charts,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Fujifilm optical specs and images")
    parser.add_argument("--dry-run", action="store_true", help="List what would be fetched")
    parser.add_argument("--all", action="store_true", help="Re-check all lenses, not just missing")
    parser.add_argument("--limit", type=int, help="Fetch first N lenses only")
    parser.add_argument("--filter", type=str, help="Filter by model substring (case-insensitive)")
    parser.add_argument("--specs-only", action="store_true", help="Only extract specs text")
    parser.add_argument("--images-only", action="store_true", help="Only download images")
    parser.add_argument("--coatings-only", action="store_true", help="Only extract coatings")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    lenses = extract_fujifilm_lenses()
    print(f"Found {len(lenses)} Fujifilm lenses with official URLs")

    if args.filter:
        lenses = [l for l in lenses if args.filter.lower() in l["model"].lower()]
        print(f"  Filtered to {len(lenses)} matching '{args.filter}'")

    # Build work list
    work = []
    for lens in lenses:
        slug = model_to_slug(lens["model"])
        needs_construction = not has_construction_image(slug)
        needs_mtf = not has_mtf_charts(slug)
        needs_any = needs_construction or needs_mtf

        if args.all or needs_any:
            work.append({
                **lens,
                "slug": slug,
                "needs_construction": needs_construction,
                "needs_mtf": needs_mtf,
            })

    if not args.all:
        print(f"{len(work)}/{len(lenses)} lenses need data")
    if args.limit:
        work = work[:args.limit]

    if args.dry_run:
        for lens in work:
            needs = []
            if lens["needs_construction"]:
                needs.append("construction")
            if lens["needs_mtf"]:
                needs.append("MTF")
            if not needs:
                needs.append("(re-check)")
            print(f"  {lens['model']}: {', '.join(needs)}")
        return

    OPTICAL_CONSTRUCTION_DIR.mkdir(parents=True, exist_ok=True)
    MTF_CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    do_specs = not args.images_only and not args.coatings_only
    do_images = not args.specs_only and not args.coatings_only
    do_coatings = not args.specs_only and not args.images_only

    stats = {"specs": 0, "construction": 0, "mtf": 0, "coatings": 0, "failed": 0}
    results = []

    with browser_context() as ctx:
        for i, lens in enumerate(work):
            model = lens["model"]
            slug = lens["slug"]
            u_slug = url_to_slug(lens["url"])
            spec_url = specs_url(lens["url"])

            print(f"\n[{i + 1}/{len(work)}] {model}")

            # Fetch specs page (for specs text + images)
            if do_specs or do_images:
                text, html = fetch_page_content(ctx, spec_url)

                if do_specs:
                    specs = extract_specs(text)
                    el = specs.get("elements", "?")
                    gr = specs.get("groups", "?")
                    sp = specs.get("special", [])
                    print(f"  Specs: {el} elements, {gr} groups, special: {sp}")
                    if el != "?":
                        stats["specs"] += 1
                    results.append({"model": model, "slug": slug, **specs})

                if do_images:
                    # Use positional extraction (opens a new page for JS evaluation)
                    page = ctx.new_page()
                    try:
                        page.goto(spec_url, wait_until="networkidle", timeout=30000)
                        page.wait_for_timeout(3000)
                        scroll_page(page)
                        img_urls = extract_image_urls_by_position(page, u_slug)
                    except Exception as e:
                        print(f"  WARN: page error: {e}")
                        img_urls = {}
                    finally:
                        page.close()

                    found = False

                    if "construction" in img_urls:
                        ext = img_urls["construction"].rsplit(".", 1)[-1]
                        dest = OPTICAL_CONSTRUCTION_DIR / f"{slug}.{ext}"
                        if download_image(img_urls["construction"], dest):
                            print(f"  Construction: {dest.name}")
                            stats["construction"] += 1
                            found = True

                    for key, label, suffix in [
                        ("mtf_15", "MTF 15lp", "-15lp"),
                        ("mtf_45", "MTF 45lp", "-45lp"),
                    ]:
                        if key in img_urls:
                            ext = img_urls[key].rsplit(".", 1)[-1]
                            dest = MTF_CHARTS_DIR / f"{slug}{suffix}.{ext}"
                            if download_image(img_urls[key], dest):
                                print(f"  {label}: {dest.name}")
                                stats["mtf"] += 1
                                found = True

                    if not found and (lens["needs_construction"] or lens["needs_mtf"]):
                        print(f"  No images found on page")
                        stats["failed"] += 1

            # Fetch overview page for coatings
            if do_coatings:
                overview_text = read_cache(lens["url"])
                if overview_text is None:
                    page = ctx.new_page()
                    try:
                        page.goto(lens["url"], wait_until="networkidle", timeout=30000)
                        page.wait_for_timeout(2000)
                        overview_text = page.inner_text("body")
                        from common import write_cache
                        write_cache(lens["url"], overview_text)
                    except Exception as e:
                        print(f"  WARN: coating page error: {e}")
                        overview_text = ""
                    finally:
                        page.close()

                coatings = extract_coatings(overview_text)
                print(f"  Coatings: {', '.join(coatings)}")
                stats["coatings"] += 1

    # Print summary
    print(f"\n{'=' * 40}")
    print(f"Done: {stats['specs']} specs, {stats['construction']} construction diagrams, "
          f"{stats['mtf']} MTF charts, {stats['coatings']} coatings")
    if stats["failed"]:
        print(f"{stats['failed']} lenses with no images found")

    # Write specs summary
    if do_specs and results:
        summary_dir = ROOT / ".cache" / "fujifilm-specs"
        summary_dir.mkdir(parents=True, exist_ok=True)
        summary_path = summary_dir / "fujifilm-specs.txt"
        with open(summary_path, "w", encoding="utf-8") as f:
            for r in results:
                special_str = ", ".join(r.get("special", [])) or "none"
                f.write(f"{r['model']}|{r.get('elements', '?')}|"
                        f"{r.get('groups', '?')}|{special_str}\n")
        print(f"Specs summary: {summary_path}")


if __name__ == "__main__":
    main()
