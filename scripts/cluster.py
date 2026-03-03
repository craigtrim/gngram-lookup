"""
Show prefix cluster variations for a given word.

Output is written to a file. Default location is /tmp/cluster_<word>.txt.

Usage:
    poetry run python scripts/cluster.py <word> [--sort freq|alpha] [--with-freq] [--output PATH]

Examples:
    poetry run python scripts/cluster.py happy
    poetry run python scripts/cluster.py happy --sort freq
    poetry run python scripts/cluster.py happy --sort freq --with-freq
    poetry run python scripts/cluster.py happy --sort freq --with-freq --min-tf 100000
    poetry run python scripts/cluster.py happy --output /tmp/my-output.txt
    poetry run python scripts/cluster.py happy --output /tmp/mydir/
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
        help="Output file or directory (default: /tmp/cluster_<word>.txt)",
    )
    args = parser.parse_args()

    results = prefix_cluster(args.word, sort_by=args.sort, with_freq=args.with_freq, min_tf=args.min_tf)

    # Resolve output path
    filename = f"cluster_{args.word.lower()}.txt"
    if args.output:
        out = Path(args.output)
        if out.is_dir() or str(args.output).endswith("/"):
            out.mkdir(parents=True, exist_ok=True)
            out = out / filename
    else:
        out = Path("/tmp") / filename

    if not results:
        out.write_text(f"No cluster found for {args.word!r}\n")
        print(f"No cluster found for {args.word!r}")
        print(f"Written to {out}")
        return

    lines = []
    if args.with_freq:
        width = max(len(w) for w, _ in results)
        for word, tf in results:
            lines.append(f"{word:<{width}}  {tf:>12,}")
    else:
        for word in results:
            lines.append(word)

    out.write_text("\n".join(lines) + "\n")
    print(f"{len(results)} results written to {out}")


if __name__ == "__main__":
    main()
