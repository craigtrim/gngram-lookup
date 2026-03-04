"""
Group corpus words by shared suffix morphology (derivational fingerprint).

For each root word with sufficient corpus frequency, compute its suffix
fingerprint: the frozenset of suffixes found in its prefix_cluster. Then
reverse the index to find all words that share the same fingerprint.

    international -> {ation, ise, ism, ist, ize, ly}
    rational      -> {ation, ise, ism, ist, ize, ly}   <- same paradigm

Words with an identical fingerprint belong to the same derivational class.

The y->i allomorphic alternation is handled identically to suffix_analysis.py.

Usage:
    poetry run python scripts/suffix_fingerprint.py

Output:
    /tmp/suffix_fingerprints.csv   (fingerprint, count)
    /tmp/suffix_word_index.json    (fingerprint -> [words])  for use by suffix_query.py
"""

import argparse
import csv
import json
import sys
import time
from collections import defaultdict
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
    parser = argparse.ArgumentParser(description="Group words by shared suffix morphology fingerprint.")
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
        help="Output directory (default: /tmp)",
    )
    parser.add_argument(
        "--min-group",
        type=int,
        default=2,
        metavar="N",
        help="Minimum number of words sharing a fingerprint to be included (default: 2)",
    )
    parser.add_argument(
        "--min-suffix-len",
        type=int,
        default=2,
        metavar="N",
        help="Minimum suffix length to count (default: 2, filters trivial s/e/n)",
    )
    parser.add_argument(
        "--min-fp-size",
        type=int,
        default=2,
        metavar="N",
        help="Minimum number of distinct suffixes in a fingerprint (default: 2)",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir) if args.output_dir else Path("/tmp")
    csv_path = out_dir / "suffix_fingerprints.csv"
    json_path = out_dir / "suffix_word_index.json"

    print(f"Loading wordlist (min_tf={args.min_tf:,}) ...")
    roots = [w for w in wordlist(min_tf=args.min_tf) if len(w) >= MIN_ROOT_LEN]
    print(f"  {len(roots):,} root words to process")

    # fingerprint (frozenset) -> list of root words
    fingerprint_index: defaultdict[frozenset, list[str]] = defaultdict(list)

    t0 = time.time()
    for i, root in enumerate(roots):
        if i % 10_000 == 0 and i > 0:
            elapsed = time.time() - t0
            rate = i / elapsed
            remaining = (len(roots) - i) / rate
            print(f"  {i:>8,} / {len(roots):,}  [{elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining]")

        suffixes = frozenset(
            s for member in prefix_cluster(root, min_len=MIN_ROOT_LEN, min_tf=args.min_tf)
            if (s := extract_suffix(root, member)) is not None
            and len(s) >= args.min_suffix_len
        )
        if len(suffixes) >= args.min_fp_size:
            fingerprint_index[suffixes].append(root)

    elapsed = time.time() - t0
    print(f"\nProcessed {len(roots):,} roots in {elapsed:.1f}s")

    # Sort groups by count descending, apply min_group filter
    groups = [(fp, words) for fp, words in fingerprint_index.items() if len(words) >= args.min_group]
    groups.sort(key=lambda x: len(x[1]), reverse=True)

    print(f"Found {len(fingerprint_index):,} distinct fingerprints")
    print(f"Found {len(groups):,} groups with >= {args.min_group} words")

    # CSV: fingerprint, count
    print(f"Writing {csv_path} ...")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["fingerprint", "count"])
        for fp, words in groups:
            writer.writerow(["|".join(sorted(fp)), len(words)])

    # JSON: fingerprint_str -> [words]  (for suffix_query.py)
    print(f"Writing {json_path} ...")
    word_index = {"|".join(sorted(fp)): words for fp, words in groups}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(word_index, f)

    print("Done.\n")
    print(f"Top 20 fingerprint groups (min_group={args.min_group:,}):")
    print(f"  {'count':>6s}  fingerprint")
    print(f"  {'------':>6s}  ----------")
    for fp, words in groups[:20]:
        print(f"  {len(words):>6,}  {' | '.join(sorted(fp))}")


if __name__ == "__main__":
    main()
