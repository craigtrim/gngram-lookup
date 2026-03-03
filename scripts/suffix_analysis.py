"""
Extract and count morphological suffixes across the Google Books corpus.

For each root word in the vocabulary, finds all longer words sharing the same
prefix and records the suffix that was appended. The y->i allomorphic alternation
is handled: "beauty" -> "beautification" yields suffix "fication" (not "ification"),
since the modified root is "beauti".

Usage:
    poetry run python scripts/suffix_analysis.py

Output:
    scripts/suffix_counts.csv  (suffix, count, examples)
"""

import csv
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from gngram_lookup import prefix_cluster, wordlist

MIN_ROOT_LEN = 5
OUTPUT_PATH = Path(__file__).parent / "suffix_counts.csv"


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
    print("Loading wordlist ...")
    roots = [w for w in wordlist() if len(w) >= MIN_ROOT_LEN]
    print(f"  {len(roots):,} root words to process")

    suffix_counter: Counter[str] = Counter()
    suffix_examples: defaultdict[str, list[str]] = defaultdict(list)

    t0 = time.time()
    for i, root in enumerate(roots):
        if i % 50_000 == 0 and i > 0:
            elapsed = time.time() - t0
            rate = i / elapsed
            remaining = (len(roots) - i) / rate
            print(f"  {i:>8,} / {len(roots):,}  [{elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining]")

        for member in prefix_cluster(root, min_len=MIN_ROOT_LEN):
            suffix = extract_suffix(root, member)
            if not suffix:
                continue
            suffix_counter[suffix] += 1
            if len(suffix_examples[suffix]) < 3:
                suffix_examples[suffix].append(f"{root}+{suffix}={member}")

    elapsed = time.time() - t0
    print(f"\nProcessed {len(roots):,} roots in {elapsed:.1f}s")
    print(f"Found {len(suffix_counter):,} distinct suffixes")
    print(f"Writing to {OUTPUT_PATH} ...")

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["suffix", "count", "examples"])
        for suffix, count in suffix_counter.most_common():
            writer.writerow([suffix, count, " | ".join(suffix_examples[suffix])])

    print("Done.\n")
    print("Top 30 suffixes:")
    print(f"  {'suffix':20s}  {'count':>8s}  example")
    print(f"  {'-'*20}  {'-'*8}  -------")
    for suffix, count in suffix_counter.most_common(30):
        example = suffix_examples[suffix][0] if suffix_examples[suffix] else ""
        print(f"  {repr(suffix):20s}  {count:>8,}  {example}")


if __name__ == "__main__":
    main()
