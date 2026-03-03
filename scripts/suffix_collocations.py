"""
Build a suffix collocation matrix from the Google Books corpus.

Two suffixes are "collocated" if they both appear as extensions of the same root word.

    beauty -> [beautiful, beautifully, beautician, beautification]
    suffixes: [ful, fully, cian, fication]
    pairs: (ful, fully), (ful, cian), (ful, fication), (fully, cian), ...

The y->i allomorphic alternation is handled identically to suffix_analysis.py:
    beauty -> modified root "beauti", so beautiful -> suffix "ful" (not "iful")

Output:
    scripts/suffix_collocations.csv  (suffix_a, suffix_b, count, example_roots)

    count = number of distinct roots on which both suffixes co-occur.

Usage:
    poetry run python scripts/suffix_collocations.py
"""

import csv
import itertools
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from gngram_lookup import prefix_cluster, wordlist

MIN_ROOT_LEN = 5
MIN_TF = 100_000        # applied to both root words and cluster members
OUTPUT_PATH = Path(__file__).parent / "suffix_collocations.csv"


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
    print(f"Loading wordlist (min_tf={MIN_TF:,}) ...")
    roots = [w for w in wordlist(min_tf=MIN_TF) if len(w) >= MIN_ROOT_LEN]
    print(f"  {len(roots):,} root words to process")

    pair_counter: Counter[tuple[str, str]] = Counter()
    pair_examples: defaultdict[tuple[str, str], list[str]] = defaultdict(list)

    t0 = time.time()
    for i, root in enumerate(roots):
        if i % 50_000 == 0 and i > 0:
            elapsed = time.time() - t0
            rate = i / elapsed
            remaining = (len(roots) - i) / rate
            print(f"  {i:>8,} / {len(roots):,}  [{elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining]")

        cluster = prefix_cluster(root, min_len=MIN_ROOT_LEN, min_tf=MIN_TF)
        suffixes = sorted({
            s for m in cluster
            if (s := extract_suffix(root, m)) is not None
        })

        # Every unordered pair of suffixes that share this root
        for s_a, s_b in itertools.combinations(suffixes, 2):
            pair = (s_a, s_b)
            pair_counter[pair] += 1
            if len(pair_examples[pair]) < 3:
                pair_examples[pair].append(root)

    elapsed = time.time() - t0
    print(f"\nProcessed {len(roots):,} roots in {elapsed:.1f}s")
    print(f"Found {len(pair_counter):,} distinct suffix pairs")
    print(f"Writing to {OUTPUT_PATH} ...")

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["suffix_a", "suffix_b", "count", "example_roots"])
        for (s_a, s_b), count in pair_counter.most_common():
            writer.writerow([s_a, s_b, count, " | ".join(pair_examples[(s_a, s_b)])])

    print("Done.\n")
    print("Top 30 suffix collocations:")
    print(f"  {'suffix_a':20s}  {'suffix_b':20s}  {'count':>8s}  example roots")
    print(f"  {'-'*20}  {'-'*20}  {'-'*8}  ------------")
    for (s_a, s_b), count in pair_counter.most_common(30):
        examples = ", ".join(pair_examples[(s_a, s_b)])
        print(f"  {s_a:20s}  {s_b:20s}  {count:>8,}  {examples}")


if __name__ == "__main__":
    main()
