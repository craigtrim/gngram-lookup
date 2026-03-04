"""
Show prefix cluster variations for a given word.

Output is printed to stdout. If --output is given, results are also written to a file.

Usage:
    poetry run python scripts/cluster.py <word> [--sort freq|alpha] [--with-freq] [--output PATH]

Examples:
    poetry run python scripts/cluster.py happy
    poetry run python scripts/cluster.py happy --sort freq
    poetry run python scripts/cluster.py happy --sort freq --with-freq
    poetry run python scripts/cluster.py happy --sort freq --with-freq --min-tf 100000
    poetry run python scripts/cluster.py happy --output /tmp/gngrams-lookup/my-output.txt
    poetry run python scripts/cluster.py happy --output /tmp/gngrams-lookup/
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from gngram_lookup import prefix_cluster


def main() -> None:
    parser = argparse.ArgumentParser(description="Show prefix cluster variations for a word.")
    parser.add_argument("word", help="Root word to cluster from")
    parser.add_argument(
        "--sort",
        choices=["alpha", "freq"],
        default="alpha",
        help="Sort order: alphabetical (default) or by corpus frequency",
    )
    parser.add_argument(
        "--with-freq",
        action="store_true",
        help="Show corpus frequency alongside each word",
    )
    parser.add_argument(
        "--min-tf",
        type=int,
        default=0,
        metavar="N",
        help="Minimum corpus frequency to include a word (default: 0 = all)",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        help="Write results to this file or directory (optional; stdout always printed)",
    )
    args = parser.parse_args()

    # Always fetch with_freq=True so we have freq data for alignment
    results = prefix_cluster(args.word, sort_by=args.sort, with_freq=True, min_tf=args.min_tf)

    if not results:
        print(f"No cluster found for {args.word!r}")
        return

    color = sys.stdout.isatty()
    RESET = "\033[0m"    if color else ""
    WORD  = "\033[36m"   if color else ""   # cyan          — word entries
    VAL   = "\033[1;33m" if color else ""   # bold yellow   — frequencies

    def _fmt(word: str, tf: int, col: int) -> tuple[str, str]:
        """Return (plain_line, colored_line) for one result row."""
        plain = f"{word:<{col}}  {tf:>12,}"
        colored = f"{WORD}{word}{RESET}{' ' * (col - len(word))}  {VAL}{tf:>12,}{RESET}"
        return plain, colored

    col = max(len(w) for w, _ in results)

    plain_lines: list[str] = []
    color_lines: list[str] = []

    if args.with_freq:
        for word, tf in results:
            plain, colored = _fmt(word, tf, col)
            plain_lines.append(plain)
            color_lines.append(colored)
    else:
        for word, _ in results:
            plain_lines.append(word)
            color_lines.append(f"{WORD}{word}{RESET}" if color else word)

    print("\n".join(color_lines))

    if args.output:
        filename = f"cluster_{args.word.lower()}.txt"
        out = Path(args.output)
        if out.is_dir() or str(args.output).endswith("/"):
            out.mkdir(parents=True, exist_ok=True)
            out = out / filename
        out.write_text("\n".join(plain_lines) + "\n")
        print(f"\n{len(results)} results written to {out}")


if __name__ == "__main__":
    main()
