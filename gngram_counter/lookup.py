"""
High-level lookup API for gngram-counter.

Provides simple functions for word frequency lookups similar to bnc-lookup.

Includes contraction fallback: if a contraction like "don't" is not found
directly, the stem ("do") is looked up instead. The ngram corpus only
contains pure alphabetic words, so contractions and their suffix parts
(n't, 'll, etc.) are absent — but the stems are present.
"""

import hashlib
from functools import lru_cache
from typing import TypedDict

import polars as pl

from gngram_counter.data import get_hash_file, is_data_installed
from gngram_counter.normalize import normalize


class FrequencyData(TypedDict):
    """Frequency data for a word."""

    peak_tf: int  # Decade with highest term frequency
    peak_df: int  # Decade with highest document frequency
    sum_tf: int  # Total term frequency across all decades
    sum_df: int  # Total document frequency across all decades


# Contraction suffixes stored as separate tokens in the ngram corpus
# Order matters: longer suffixes must be checked before shorter ones
CONTRACTION_SUFFIXES = ("n't", "'ll", "'re", "'ve", "'m", "'d")

# Specific stems that form 's contractions (where 's = "is" or "has").
# NOT generalized — 's is ambiguous with possessive, so only known
# contraction stems are listed here. Ported from bnc-lookup.
S_CONTRACTION_STEMS = frozenset({
    # Pronouns (unambiguously 's = "is" or "has", never possessive)
    'it', 'he', 'she', 'that', 'what', 'who',
    # Adverbs / demonstratives
    'where', 'how', 'here', 'there',
    # "let's" = "let us"
    'let',
    # Indefinite pronouns
    'somebody', 'everybody', 'everyone', 'nobody',
    'anywhere', 'nowhere',
})


@lru_cache(maxsize=256)
def _load_bucket(prefix: str) -> pl.DataFrame:
    """Load and cache a parquet bucket file."""
    return pl.read_parquet(get_hash_file(prefix))


def _hash_word(word: str) -> tuple[str, str]:
    """Hash a word and return (prefix, suffix)."""
    h = hashlib.md5(normalize(word).encode("utf-8")).hexdigest()
    return h[:2], h[2:]


def _lookup_frequency(word: str) -> FrequencyData | None:
    """Look up frequency data for a single word form (no fallbacks)."""
    if not word:
        return None
    prefix, suffix = _hash_word(word)
    try:
        df = _load_bucket(prefix)
    except FileNotFoundError:
        return None
    row = df.filter(pl.col("hash") == suffix)
    if len(row) == 0:
        return None
    return FrequencyData(
        peak_tf=row["peak_tf"][0],
        peak_df=row["peak_df"][0],
        sum_tf=row["sum_tf"][0],
        sum_df=row["sum_df"][0],
    )


def _split_contraction(word: str) -> tuple[str, str] | None:
    """Split a contraction into its component parts if possible.

    The ngram corpus tokenizes contractions separately (e.g., "we'll" -> "we" + "'ll").
    This function reverses that split for fallback lookup.

    Returns:
        Tuple of (stem, suffix) if the word matches a contraction pattern,
        or None if no contraction pattern matches.
    """
    for suffix in CONTRACTION_SUFFIXES:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            if stem:
                return (stem, suffix)

    # Specific 's contractions from curated allowlist (not possessives)
    if word.endswith("'s"):
        stem = word[:-2]
        if stem in S_CONTRACTION_STEMS:
            return (stem, "'s")

    return None


def exists(word: str) -> bool:
    """Check if a word exists in the ngram data.

    Performs case-insensitive lookup with automatic fallbacks:
    1. Direct lookup of the normalized word
    2. Contraction fallback: if word is a contraction, check if both
       components exist (e.g., "don't" -> "do" + "n't")

    Args:
        word: The word to check (case-insensitive)

    Returns:
        True if the word exists, False otherwise

    Raises:
        FileNotFoundError: If data files are not installed
    """
    if not is_data_installed():
        raise FileNotFoundError(
            "Data files not installed. Run: python -m gngram_counter.download_data"
        )

    word = normalize(word)

    if _lookup_frequency(word) is not None:
        return True

    # Contraction fallback: check if the stem exists
    parts = _split_contraction(word)
    if parts:
        stem, _ = parts
        if _lookup_frequency(stem) is not None:
            return True

    return False


def frequency(word: str) -> FrequencyData | None:
    """Get frequency data for a word.

    Performs case-insensitive lookup with contraction fallback.
    For contractions, returns the stem's frequency data.

    Args:
        word: The word to look up (case-insensitive)

    Returns:
        FrequencyData dict with peak_tf, peak_df, sum_tf, sum_df, or None if not found

    Raises:
        FileNotFoundError: If data files are not installed
    """
    if not is_data_installed():
        raise FileNotFoundError(
            "Data files not installed. Run: python -m gngram_counter.download_data"
        )

    word = normalize(word)

    result = _lookup_frequency(word)
    if result is not None:
        return result

    # Contraction fallback: return the stem's frequency
    parts = _split_contraction(word)
    if parts:
        stem, _ = parts
        stem_freq = _lookup_frequency(stem)
        if stem_freq is not None:
            return stem_freq

    return None


def batch_frequency(words: list[str]) -> dict[str, FrequencyData | None]:
    """Get frequency data for multiple words.

    Args:
        words: List of words to look up (case-insensitive)

    Returns:
        Dict mapping each word to its FrequencyData or None if not found

    Raises:
        FileNotFoundError: If data files are not installed
    """
    if not is_data_installed():
        raise FileNotFoundError(
            "Data files not installed. Run: python -m gngram_counter.download_data"
        )

    # Group words by bucket prefix for efficient batch lookups
    by_prefix: dict[str, list[tuple[str, str, str]]] = {}
    contraction_words: list[str] = []

    for word in words:
        normalized = normalize(word)
        prefix, suffix = _hash_word(normalized)
        if prefix not in by_prefix:
            by_prefix[prefix] = []
        by_prefix[prefix].append((word, normalized, suffix))

    results: dict[str, FrequencyData | None] = {}

    for prefix, entries in by_prefix.items():
        df = _load_bucket(prefix)
        suffixes = [s for _, _, s in entries]

        # Filter to all matching suffixes at once
        matches = df.filter(pl.col("hash").is_in(suffixes))
        match_dict = {row["hash"]: row for row in matches.iter_rows(named=True)}

        for word, normalized, suffix in entries:
            if suffix in match_dict:
                row = match_dict[suffix]
                results[word] = FrequencyData(
                    peak_tf=row["peak_tf"],
                    peak_df=row["peak_df"],
                    sum_tf=row["sum_tf"],
                    sum_df=row["sum_df"],
                )
            else:
                # Mark for contraction fallback
                results[word] = None
                contraction_words.append(word)

    # Contraction fallback for words not found directly
    for word in contraction_words:
        normalized = normalize(word)
        parts = _split_contraction(normalized)
        if parts:
            stem, _ = parts
            stem_freq = _lookup_frequency(stem)
            if stem_freq is not None:
                results[word] = stem_freq

    return results
