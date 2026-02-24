"""
High-level lookup API for gngram-lookup.

The ngram corpus contains only pure alphabetic words, so contractions,
possessives, and hyphenated compounds are absent. Fallback strategies:

1. Contractions: "don't" -> stem "do" looked up
2. Possessives: "ship's" -> stem "ship" looked up
3. Hyphenated: "quarter-deck" -> all parts checked ("quarter", "deck")
"""

from __future__ import annotations

import hashlib
import math
from functools import lru_cache
from typing import TypedDict

import polars as pl

from gngram_lookup.data import get_hash_file, is_data_installed
from gngram_lookup.normalize import normalize


class FrequencyData(TypedDict):
    """Frequency data for a word."""

    peak_tf: int  # Decade with highest term frequency
    peak_df: int  # Decade with highest document frequency
    sum_tf: int  # Total term frequency across all decades
    sum_df: int  # Total document frequency across all decades


# Contraction suffixes stored as separate tokens in the ngram corpus
# Order matters: longer suffixes must be checked before shorter ones
CONTRACTION_SUFFIXES = ("n't", "'ll", "'re", "'ve", "'m", "'d")


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
    """Split a contraction or possessive into (stem, suffix).

    Handles standard contractions (n't, 'll, etc.) and possessives ('s).
    The ngram corpus only has pure alpha words, so both contractions and
    possessives need stem-based fallback.

    Returns:
        Tuple of (stem, suffix) or None if no pattern matches.
    """
    for suffix in CONTRACTION_SUFFIXES:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            if stem:
                return (stem, suffix)

    # Any 's — covers both contractions ("it's") and possessives ("ship's")
    if word.endswith("'s"):
        stem = word[:-2]
        if stem:
            return (stem, "'s")

    return None


def _split_hyphenated(word: str) -> list[str] | None:
    """Split a hyphenated word into its component parts.

    Returns:
        List of parts if the word contains hyphens and has at least 2
        non-empty parts, or None otherwise.
    """
    if "-" not in word:
        return None
    parts = [p for p in word.split("-") if p]
    if len(parts) < 2:
        return None
    return parts


def exists(word: str) -> bool:
    """Check if a word exists in the ngram data.

    Fallback chain:
    1. Direct lookup
    2. Contraction/possessive: check stem ("don't" -> "do", "ship's" -> "ship")
    3. Hyphenated: check all parts ("quarter-deck" -> "quarter" + "deck")

    Args:
        word: The word to check (case-insensitive)

    Returns:
        True if the word exists, False otherwise

    Raises:
        FileNotFoundError: If data files are not installed
    """
    if not is_data_installed():
        raise FileNotFoundError(
            "Data files not installed. Run: python -m gngram_lookup.download_data"
        )

    word = normalize(word)

    if _lookup_frequency(word) is not None:
        return True

    # Contraction/possessive fallback
    parts = _split_contraction(word)
    if parts:
        stem, _ = parts
        if _lookup_frequency(stem) is not None:
            return True

    # Hyphenated fallback: all parts must exist
    hyp_parts = _split_hyphenated(word)
    if hyp_parts:
        if all(_lookup_frequency(p) is not None for p in hyp_parts):
            return True

    return False


def frequency(word: str) -> FrequencyData | None:
    """Get frequency data for a word.

    Fallback chain:
    1. Direct lookup
    2. Contraction/possessive: return stem's frequency
    3. Hyphenated: return first component's frequency

    Args:
        word: The word to look up (case-insensitive)

    Returns:
        FrequencyData dict with peak_tf, peak_df, sum_tf, sum_df, or None if not found

    Raises:
        FileNotFoundError: If data files are not installed
    """
    if not is_data_installed():
        raise FileNotFoundError(
            "Data files not installed. Run: python -m gngram_lookup.download_data"
        )

    word = normalize(word)

    result = _lookup_frequency(word)
    if result is not None:
        return result

    # Contraction/possessive fallback: return the stem's frequency
    parts = _split_contraction(word)
    if parts:
        stem, _ = parts
        stem_freq = _lookup_frequency(stem)
        if stem_freq is not None:
            return stem_freq

    # Hyphenated fallback: return first component's frequency
    hyp_parts = _split_hyphenated(word)
    if hyp_parts:
        if all(_lookup_frequency(p) is not None for p in hyp_parts):
            return _lookup_frequency(hyp_parts[0])

    return None


_MAX_TF = 26_500_000_000  # approximate sum_tf for "the"


def word_score(word: str) -> int | None:
    """Return a 1-100 commonness score (1 = most common, 100 = least common).

    Uses log-normalized sum_tf against the most frequent word in the corpus.
    Returns None if the word is not found.
    """
    freq = frequency(word)
    if not freq:
        return None
    tf = freq["sum_tf"]
    if tf <= 0:
        return 100
    log_score = math.log10(tf) / math.log10(_MAX_TF)
    return max(1, round(100 * (1 - log_score)))


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
            "Data files not installed. Run: python -m gngram_lookup.download_data"
        )

    # Group words by bucket prefix for efficient batch lookups
    by_prefix: dict[str, list[tuple[str, str, str]]] = {}
    fallback_words: list[str] = []

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
                results[word] = None
                fallback_words.append(word)

    # Fallback for words not found directly
    for word in fallback_words:
        normalized = normalize(word)

        # Contraction/possessive fallback
        parts = _split_contraction(normalized)
        if parts:
            stem, _ = parts
            stem_freq = _lookup_frequency(stem)
            if stem_freq is not None:
                results[word] = stem_freq
                continue

        # Hyphenated fallback
        hyp_parts = _split_hyphenated(normalized)
        if hyp_parts:
            if all(_lookup_frequency(p) is not None for p in hyp_parts):
                results[word] = _lookup_frequency(hyp_parts[0])

    return results
