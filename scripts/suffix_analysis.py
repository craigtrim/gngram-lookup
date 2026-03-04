"""
Extract and count morphological suffixes across the Google Books corpus.

For each WordNet root word with sufficient corpus frequency, finds all longer
words sharing the same prefix and records the suffix that was appended.
The y->i allomorphic alternation is handled: "beauty" -> "beautification"
yields suffix "fication" (not "ification"), since the modified root is "beauti".

Usage:
    poetry run python scripts/suffix_analysis.py

Output:
    scripts/suffix_counts.csv  (suffix, count)
"""

import argparse
import csv
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from gngram_lookup import prefix_cluster, wordlist

MIN_ROOT_LEN = 5


def extract_suffix(root: str, member: str) -> str | None:
    """Return the suffix appended to root to produce member, or None."""
    if member.startswith(root):
        return member[len(root):]
    if root.endswith("y"):
        modified = root[:-1] + "i"   # beauty -> beauti
        if member.startswith(modified):
            return member[len(modified):]   # beautification -> fication
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract suffix counts from corpus using WordNet roots.")
    parser.add_argument(
        "--min-tf",
        type=int,
        default=100_000,
        metavar="N",
        help="Minimum corpus frequency for root words (default: 100,000)",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        help="Output directory (default: /tmp/gngrams-lookup)",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=1,
        metavar="N",
        help="Minimum number of roots a suffix must appear on to be included (default: 1)",
    )
    args = parser.parse_args()

    TMP_DIR = Path("/tmp/gngrams-lookup")
    out_dir = Path(args.output_dir) if args.output_dir else TMP_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / "suffix_counts.csv"

    print(f"Loading wordlist (min_tf={args.min_tf:,}) ...")
    roots = [w for w in wordlist(min_tf=args.min_tf) if len(w) >= MIN_ROOT_LEN]
    print(f"  {len(roots):,} root words to process")

    suffix_counter: Counter[str] = Counter()

    t0 = time.time()
    for i, root in enumerate(roots):
        if i % 10_000 == 0 and i > 0:
            elapsed = time.time() - t0
            rate = i / elapsed
            remaining = (len(roots) - i) / rate
            print(f"  {i:>8,} / {len(roots):,}  [{elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining]")

        for member in prefix_cluster(root, min_len=MIN_ROOT_LEN):
            suffix = extract_suffix(root, member)
            if suffix:
                suffix_counter[suffix] += 1

    elapsed = time.time() - t0
    print(f"\nProcessed {len(roots):,} roots in {elapsed:.1f}s")
    print(f"Found {len(suffix_counter):,} distinct suffixes")
    print(f"Writing to {output_path} ...")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["suffix", "count"])
        for suffix, count in suffix_counter.most_common():
            if count >= args.min_count:
                writer.writerow([suffix, count])

    print("Done.\n")
    top = [(s, c) for s, c in suffix_counter.most_common(30) if c >= args.min_count]
    print(f"Top {len(top)} suffixes (min_count={args.min_count:,}):")
    print(f"  {'suffix':20s}  {'count':>8s}")
    print(f"  {'-'*20}  {'-'*8}")
    for suffix, count in top:
        print(f"  {repr(suffix):20s}  {count:>8,}")


if __name__ == "__main__":
    main()
