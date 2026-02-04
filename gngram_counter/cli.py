"""CLI entry points for gngram-counter."""

import sys

from gngram_counter.lookup import exists, frequency


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
