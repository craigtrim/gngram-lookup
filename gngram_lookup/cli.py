"""CLI entry points for gngram-lookup."""

import sys

from gngram_lookup.lookup import exists, frequency, word_score
from gngram_lookup.pos import has_pos, pos, pos_freq, PosTag


def gngram_exists() -> None:
    """Check if a word exists in the ngram data."""
    if len(sys.argv) != 2:
        print("Usage: exists <word>")
        sys.exit(1)

    word = sys.argv[1]
    result = exists(word)
    print(result)
    sys.exit(0 if result else 1)


def gngram_freq() -> None:
    """Get frequency data for a word."""
    if len(sys.argv) != 2:
        print("Usage: freq <word>")
        sys.exit(1)

    word = sys.argv[1]
    result = frequency(word)
    if result is None:
        print("None")
        sys.exit(1)

    color = sys.stdout.isatty()
    RESET = "\033[0m"   if color else ""
    KEY   = "\033[36m"  if color else ""   # cyan, no bold
    VAL   = "\033[1;33m" if color else ""  # bold yellow — all values

    rows = [
        ("peak_tf_decade", str(result["peak_tf"])),
        ("peak_df_decade", str(result["peak_df"])),
        ("sum_tf",         f"{result['sum_tf']:,}"),
        ("sum_df",         f"{result['sum_df']:,}"),
    ]

    key_w = max(len(k) for k, _ in rows)
    val_w = max(len(v) for _, v in rows)

    for key, val in rows:
        print(f"  {KEY}{key:>{key_w}}{RESET}   {VAL}{val:>{val_w}}{RESET}")

    sys.exit(0)


def gngram_score() -> None:
    """Get commonness score (1=most common, 100=least common) for a word."""
    if len(sys.argv) != 2:
        print("Usage: score <word>")
        sys.exit(1)

    word = sys.argv[1]
    result = word_score(word)
    if result is None:
        print("None")
        sys.exit(1)

    print(result)
    sys.exit(0)


def gngram_pos() -> None:
    """Get POS tags for a word."""
    if len(sys.argv) != 2:
        print("Usage: pos <word>")
        sys.exit(1)

    word = sys.argv[1]
    result = pos(word)
    if not result:
        print("None")
        sys.exit(1)

    print(" ".join(result))
    sys.exit(0)


def gngram_pos_freq() -> None:
    """Get POS tags and their corpus frequencies for a word."""
    if len(sys.argv) != 2:
        print("Usage: pos-freq <word>")
        sys.exit(1)

    word = sys.argv[1]
    result = pos_freq(word)
    if not result:
        print("None")
        sys.exit(1)

    color = sys.stdout.isatty()
    RESET = "\033[0m"    if color else ""
    KEY   = "\033[36m"   if color else ""   # cyan, no bold
    VAL   = "\033[1;33m" if color else ""   # bold yellow — all values

    rows = sorted(result.items(), key=lambda x: x[1], reverse=True)
    key_w = max(len(tag) for tag, _ in rows)
    val_w = max(len(f"{n:,}") for _, n in rows)

    for tag, n in rows:
        print(f"  {KEY}{tag:>{key_w}}{RESET}   {VAL}{n:>{val_w},}{RESET}")
    sys.exit(0)


def gngram_has_pos() -> None:
    """Check if a word has a specific POS tag."""
    if len(sys.argv) != 3:
        print("Usage: has-pos <word> <tag>")
        print(f"Tags: {' '.join(t.value for t in PosTag)}")
        sys.exit(1)

    word = sys.argv[1]
    tag_str = sys.argv[2].upper()

    try:
        tag = PosTag(tag_str)
    except ValueError:
        print(f"Unknown tag: {tag_str}")
        print(f"Valid tags: {' '.join(t.value for t in PosTag)}")
        sys.exit(1)

    result = has_pos(word, tag)
    print(result)
    sys.exit(0 if result else 1)
