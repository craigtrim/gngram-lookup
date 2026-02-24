"""CLI entry points for gngram-lookup."""

import sys

from gngram_lookup.lookup import exists, frequency
from gngram_lookup.pos import has_pos, pos, pos_freq, PosTag


def gngram_exists() -> None:
    """Check if a word exists in the ngram data."""
    if len(sys.argv) != 2:
        print("Usage: gngram-exists <word>")
        sys.exit(1)

    word = sys.argv[1]
    result = exists(word)
    print(result)
    sys.exit(0 if result else 1)


def gngram_freq() -> None:
    """Get frequency data for a word."""
    if len(sys.argv) != 2:
        print("Usage: gngram-freq <word>")
        sys.exit(1)

    word = sys.argv[1]
    result = frequency(word)
    if result is None:
        print("None")
        sys.exit(1)

    print(f"peak_tf_decade: {result['peak_tf']}")
    print(f"peak_df_decade: {result['peak_df']}")
    print(f"sum_tf: {result['sum_tf']}")
    print(f"sum_df: {result['sum_df']}")
    sys.exit(0)


def gngram_pos() -> None:
    """Get POS tags for a word."""
    if len(sys.argv) != 2:
        print("Usage: gngram-pos <word>")
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
        print("Usage: gngram-pos-freq <word>")
        sys.exit(1)

    word = sys.argv[1]
    result = pos_freq(word)
    if not result:
        print("None")
        sys.exit(1)

    for tag, freq in sorted(result.items()):
        print(f"{tag}: {freq:,}")
    sys.exit(0)


def gngram_has_pos() -> None:
    """Check if a word has a specific POS tag."""
    if len(sys.argv) != 3:
        print("Usage: gngram-has-pos <word> <tag>")
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
