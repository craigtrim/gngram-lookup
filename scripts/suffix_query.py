"""
Query the suffix word index built by suffix_fingerprint.py.

Given a suffix list, finds all words in the corpus that share exactly that
derivational fingerprint. Shows derived forms and their frequencies.

Usage:
    poetry run python scripts/suffix_query.py --suffixes ization --contains
    poetry run python scripts/suffix_query.py --suffixes ization,isation --contains --sort freq

Options:
    --suffixes    Comma-separated suffix list (required)
    --contains    Match any fingerprint that contains ALL given suffixes (not exact)
    --sort        freq (default) or alpha
    --min-tf      Minimum corpus frequency of the derived form (default: 0 = all)
    --index       Path to index file (auto-detected from /tmp/gngrams-lookup if omitted)
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from gngram_lookup import batch_frequency


def _levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    row = list(range(len(b) + 1))
    for c in a:
        new_row = [row[0] + 1]
        for j, d in enumerate(b):
            new_row.append(min(new_row[-1] + 1, row[j + 1] + 1, row[j] + (c != d)))
        row = new_row
    return row[-1]


def _candidate_forms(root: str, suffix: str) -> list[str]:
    """Return candidate derived forms for root+suffix, including y->i allomorph."""
    forms = [root + suffix]
    if root.endswith("y"):
        forms.append(root[:-1] + "i" + suffix)
    return forms


def main() -> None:
    parser = argparse.ArgumentParser(description="Query words by shared suffix fingerprint.")
    parser.add_argument(
        "--suffixes",
        required=True,
        metavar="SUFFIXES",
        help="Comma-separated suffix list, e.g. ization or ly,ism,ist",
    )
    parser.add_argument(
        "--sort",
        choices=["alpha", "freq"],
        default="freq",
        help="Sort order: by corpus frequency (default) or alphabetical",
    )
    parser.add_argument(
        "--contains",
        action="store_true",
        help="Match any fingerprint that contains ALL the given suffixes (not exact match)",
    )
    parser.add_argument(
        "--min-tf",
        type=int,
        default=0,
        metavar="N",
        help="Minimum corpus frequency of the derived form (default: 0 = all)",
    )
    parser.add_argument(
        "--index",
        metavar="PATH",
        default=None,
        help="Path to suffix_word_index-<N>.json (auto-detected from /tmp/gngrams-lookup if omitted)",
    )
    args = parser.parse_args()

    TMP_DIR = Path("/tmp/gngrams-lookup")
    if args.index:
        index_path = Path(args.index)
    else:
        candidates = sorted(TMP_DIR.glob("suffix_word_index-*.json"))
        if not candidates:
            print("No suffix word index found in /tmp/gngrams-lookup/.")
            print("Run suffix_fingerprint.py first to build the index.")
            sys.exit(1)
        elif len(candidates) == 1:
            index_path = candidates[0]
        else:
            print("Multiple indexes found:")
            for i, p in enumerate(candidates):
                print(f"  [{i}] {p.name}")
            choice = input("Select [0]: ").strip()
            idx = int(choice) if choice else 0
            index_path = candidates[idx]

    if not index_path.exists():
        print(f"Index not found: {index_path}")
        print("Run suffix_fingerprint.py first to build the index.")
        sys.exit(1)

    with open(index_path, encoding="utf-8") as f:
        word_index: dict[str, list[str]] = json.load(f)

    suffixes = sorted(s.strip() for s in args.suffixes.split(",") if s.strip())
    key = "|".join(suffixes)

    if args.contains:
        query_set = set(suffixes)
        roots = []
        for fp_key, fp_roots in word_index.items():
            if query_set.issubset(set(fp_key.split("|"))):
                roots.extend(fp_roots)
    else:
        roots = word_index.get(key) or []

    if not roots:
        print(f"No words found for fingerprint: {key}")
        # Suggest indexed suffixes that are trailing variants of the queried suffix
        all_indexed = {s for fp_key in word_index for s in fp_key.split("|")}
        suggestions: dict[str, list[str]] = {}
        for q in suffixes:
            candidates_set = {
                s for s in all_indexed
                if s != q and len(s) >= 3
                and (q.endswith(s) or s.endswith(q))
            }
            matches = sorted(candidates_set, key=lambda s: _levenshtein(q, s))
            if matches:
                suggestions[q] = matches
        if suggestions:
            print("\nDid you mean:")
            for q, matches in suggestions.items():
                print(f"  '{q}' -> {matches[:8]}")
        sys.exit(0)

    # Build all candidate derived forms: (derived_form, root, suffix)
    candidates: list[tuple[str, str, str]] = []
    for root in roots:
        for suffix in suffixes:
            for form in _candidate_forms(root, suffix):
                candidates.append((form, root, suffix))

    # Batch look up all derived forms
    all_forms = [form for form, _, _ in candidates]
    freq_map = batch_frequency(all_forms)

    # Group results by root: root -> [(suffix, tf)]
    seen: set[str] = set()
    root_map: dict[str, list[tuple[str, int]]] = {}
    for form, root, suffix in candidates:
        dedup_key = f"{root}|{suffix}"
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        tf = freq_map.get(form, {}).get("sum_tf", 0) if freq_map.get(form) else 0
        if tf >= args.min_tf:
            root_map.setdefault(root, []).append((suffix, tf))

    if not root_map:
        print(f"No derived forms found above min_tf={args.min_tf:,}")
        sys.exit(0)

    # Sort roots: by max derived tf (freq) or alphabetically
    def root_sort_key(r: str) -> int | str:
        return -max(tf for _, tf in root_map[r]) if args.sort == "freq" else r

    sorted_roots = sorted(root_map, key=root_sort_key)

    # Column width for aligning frequencies: max length of "+suffix" labels
    suffix_col = max(len(f"+{s}") for s in suffixes) + 2

    total_forms = sum(len(v) for v in root_map.values())
    print(f"Fingerprint: {key}")
    print(f"{len(root_map)} roots, {total_forms} derived forms\n")

    for root in sorted_roots:
        print(root)
        for suffix, tf in sorted(root_map[root], key=lambda x: x[1], reverse=True):
            label = f"+{suffix}"
            print(f"    {label}{' ' * (suffix_col - len(label))}{tf:>12,}")


if __name__ == "__main__":
    main()
