"""Command-line interface for pagefetch.

Thin wrapper over NetworkFetcher that preserves the original
fetch-page.py CLI surface exactly.

Usage:
    py -m pagefetch <url>                          # single URL, auto mode
    py -m pagefetch <url> --html                   # raw HTML output
    py -m pagefetch <url> --js                     # force Playwright
    py -m pagefetch <url> --nodriver               # force Nodriver (headed)
    py -m pagefetch <url> --uc                     # force SeleniumBase UC
    py -m pagefetch <url> --wait 5000              # extra wait (ms)
    py -m pagefetch <url> --no-cache               # bypass cache

    py -m pagefetch --batch urls.txt               # batch from file
    py -m pagefetch --batch urls.txt --nodriver    # batch with Nodriver
    py -m pagefetch --batch urls.txt --output-dir out/  # save to files
    py -m pagefetch url1 url2 url3                 # batch from args
    echo url | py -m pagefetch --batch -           # batch from stdin

    py -m pagefetch --clean-cache                  # purge junk cache entries
    py -m pagefetch --clean-cache --dry-run        # list junk, delete nothing
"""

import sys
from pathlib import Path

from .detection import is_bot_blocked, is_error_page
from .network import NetworkFetcher
from .source import ContentMode, FetchOptions, Transport

_VALUE_FLAGS = {"--wait", "--batch", "--output-dir"}
_BARE_FLAGS = {
    "--html",
    "--no-cache",
    "--js",
    "--nodriver",
    "--uc",
    "--clean-cache",
    "--dry-run",
}


def _parse_transport(argv: list[str]) -> Transport:
    if "--uc" in argv:
        return Transport.UC
    if "--nodriver" in argv:
        return Transport.NODRIVER
    if "--js" in argv:
        return Transport.PLAYWRIGHT
    return Transport.AUTO


def _flag_value(argv: list[str], flag: str) -> str | None:
    if flag in argv:
        idx = argv.index(flag)
        if idx + 1 < len(argv):
            return argv[idx + 1]
    return None


def _collect_urls(argv: list[str], batch_file: str | None) -> list[str]:
    urls: list[str] = []
    skip_next = False
    for arg in argv[1:]:
        if skip_next:
            skip_next = False
            continue
        if arg in _VALUE_FLAGS:
            skip_next = True
            continue
        if arg.startswith("--"):
            continue
        urls.append(arg)

    if batch_file:
        if batch_file == "-":
            lines = sys.stdin
        else:
            batch_path = Path(batch_file)
            if not batch_path.exists():
                print(f"Batch file not found: {batch_file}", file=sys.stderr)
                sys.exit(1)
            lines = batch_path.read_text(encoding="utf-8").splitlines()
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def _classify_junk(body: str) -> str | None:
    """Reason a cached body is junk, or None to keep it. Order matters only
    for the label — a page that is both is reported as bot-blocked."""
    if is_bot_blocked(body):
        return "bot-blocked"
    if is_error_page(body):
        return "404/error"
    return None


def _clean_cache(dry_run: bool) -> None:
    """Sweep the cache of bot-blocked / 404 entries, printing a summary."""
    from .cache import FileCache

    report = FileCache().clean(_classify_junk, dry_run=dry_run)
    verb = "would remove" if dry_run else "removed"
    if report.removed:
        print(f"{verb} {len(report.removed)} junk entries:", file=sys.stderr)
        for path, reason in report.removed:
            print(f"    {path.name}  ({reason})", file=sys.stderr)
    print(
        f"{verb} {len(report.removed)} junk entries, kept {report.kept}",
        file=sys.stderr,
    )


def main() -> None:
    argv = sys.argv
    if len(argv) < 2:
        print(__doc__)
        sys.exit(1)

    if "--clean-cache" in argv:
        _clean_cache(dry_run="--dry-run" in argv)
        return

    mode = ContentMode.HTML if "--html" in argv else ContentMode.TEXT
    transport = _parse_transport(argv)
    use_cache = "--no-cache" not in argv
    wait_ms = int(_flag_value(argv, "--wait") or 500)
    output_dir = _flag_value(argv, "--output-dir")
    batch_file = _flag_value(argv, "--batch")

    urls = _collect_urls(argv, batch_file)
    if not urls:
        print(__doc__)
        sys.exit(1)

    opts = FetchOptions(
        mode=mode, transport=transport, wait_ms=wait_ms, use_cache=use_cache
    )
    fetcher = NetworkFetcher()

    if len(urls) == 1 and not output_dir:
        result = fetcher.fetch(urls[0], opts)
        sys.stdout.buffer.write(result.content.encode("utf-8", errors="replace"))
        sys.stdout.buffer.write(b"\n")
        return

    results = fetcher.fetch_batch(urls, opts)
    _write_batch_output(results, output_dir, mode)


def _write_batch_output(results, output_dir: str | None, mode: ContentMode) -> None:
    """Reproduce the original batch output: one file per URL to a
    directory (hash-named), or delimited blocks to stdout."""
    from .cache import FileCache

    out_path = Path(output_dir) if output_dir else None
    if out_path:
        out_path.mkdir(parents=True, exist_ok=True)

    suffix = ".html" if mode is ContentMode.HTML else ".txt"
    for result in results:
        if not result.content:
            continue
        if out_path:
            fname = FileCache.url_hash(result.url) + suffix
            (out_path / fname).write_text(result.content, encoding="utf-8")
            print(f"[batch]   -> {fname} ({len(result.content)} bytes)", file=sys.stderr)
        else:
            sys.stdout.buffer.write(f"--- {result.url} ---\n".encode())
            sys.stdout.buffer.write(result.content.encode("utf-8", errors="replace"))
            sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
