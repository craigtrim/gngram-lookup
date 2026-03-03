"""
High-level lookup API for gngram-lookup.

The ngram corpus contains only pure alphabetic words, so contractions,
possessives, and hyphenated compounds are absent. Fallback strategies:

1. Contractions: "don't" -> stem "do" looked up
2. Possessives: "ship's" -> stem "ship" looked up
3. Hyphenated: "quarter-deck" -> all parts checked ("quarter", "deck")
"""

from __future__ import annotations

import bisect
import hashlib
import math
from functools import lru_cache
from typing import Literal, TypedDict

import polars as pl

from gngram_lookup.data import get_hash_file, get_wordlist_file, is_data_installed
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


@lru_cache(maxsize=1)
def _load_wordlist() -> tuple[list[str], list[int]]:
    """Load and cache the sorted wordlist. Returns (words, sum_tfs)."""
    df = pl.read_parquet(get_wordlist_file())
    return df["word"].to_list(), df["sum_tf"].to_list()


def wordlist(min_tf: int = 0) -> list[str]:
    """Return the full sorted vocabulary list.

    Args:
        min_tf: Minimum sum_tf to include a word (0 = all words).

    Returns:
        Sorted list of words.

    Raises:
        FileNotFoundError: If data files are not installed.
    """
    if not is_data_installed():
        raise FileNotFoundError(
            "Data files not installed. Run: python -m gngram_lookup.download_data"
        )
    words, tfs = _load_wordlist()
    if min_tf <= 0:
        return list(words)
    return [w for w, tf in zip(words, tfs) if tf >= min_tf]


def prefix_cluster(
    word: str,
    min_len: int = 5,
    min_tf: int = 0,
    sort_by: Literal["alpha", "freq"] = "alpha",
    with_freq: bool = False,
) -> list[str] | list[tuple[str, int]]:
    """Return all corpus words that share the same prefix as `word`.

    Handles two cases:
    1. Standard prefix match: all words longer than `word` that start with `word`.
    2. y-drop allomorphic variant: for words ending in -y, drops the y and
       clusters on the stem, accepting only continuations with y or i.

    Args:
        word: The root word to cluster from.
        min_len: Minimum word length to attempt clustering (default 5).
        min_tf: Minimum sum_tf for candidate words (0 = all).
        sort_by: Sort order — "alpha" (alphabetical) or "freq" (descending frequency).
        with_freq: If True, return list[tuple[str, int]] with (word, sum_tf) pairs.

    Returns:
        list[str] by default, or list[tuple[str, int]] when with_freq=True.

    Raises:
        FileNotFoundError: If data files are not installed.
    """
    if not is_data_installed():
        raise FileNotFoundError(
            "Data files not installed. Run: python -m gngram_lookup.download_data"
        )

    word = normalize(word)
    if len(word) < min_len:
        return []

    words, tfs = _load_wordlist()

    def _scan_prefix(prefix: str, accept: set[str] | None = None) -> list[tuple[str, int]]:
        """Return (word, sum_tf) pairs that start with prefix and are longer than word."""
        lo = bisect.bisect_left(words, prefix)
        results = []
        for i in range(lo, len(words)):
            w = words[i]
            if not w.startswith(prefix):
                break
            if len(w) <= len(word):
                continue
            if accept is not None and w[len(prefix)] not in accept:
                continue
            if min_tf > 0 and tfs[i] < min_tf:
                continue
            results.append((w, tfs[i]))
        return results

    # Standard prefix match
    candidates = _scan_prefix(word)

    # y-drop allomorphic variant: "happy" -> stem "happ", accept y or i continuations
    if word.endswith("y"):
        stem = word[:-1]
        y_candidates = _scan_prefix(stem, accept={"y", "i"})
        seen = {w for w, _ in candidates}
        for pair in y_candidates:
            if pair[0] not in seen:
                candidates.append(pair)
                seen.add(pair[0])

    if sort_by == "freq":
        candidates.sort(key=lambda x: x[1], reverse=True)
    else:
        candidates.sort(key=lambda x: x[0])

    if with_freq:
        return candidates
    return [w for w, _ in candidates]


def erosion_cluster(
    word: str,
    min_len: int = 5,
    min_tf: int = 0,
    sort_by: Literal["alpha", "freq"] = "alpha",
    with_freq: bool = False,
) -> list[str] | list[tuple[str, int]]:
    """Return corpus words that are morphological siblings of `word` via suffix erosion.

    Progressively strips characters from the right of `word`, scanning the corpus
    at each prefix length down to `min_len`. Words that share a prefix with `word`
    but are not extensions of it are siblings — e.g. "homogenous" finds
    "homogeneous", "homogeneity", "homogenize" via the common stem "homogen".

    Args:
        word: The root word to find siblings for.
        min_len: Minimum prefix length to erode down to (default 5).
        min_tf: Minimum sum_tf for candidate words (0 = all).
        sort_by: Sort order — "alpha" (alphabetical) or "freq" (descending frequency).
        with_freq: If True, return list[tuple[str, int]] with (word, sum_tf) pairs.

    Returns:
        list[str] by default, or list[tuple[str, int]] when with_freq=True.

    Raises:
        FileNotFoundError: If data files are not installed.
    """
    if not is_data_installed():
        raise FileNotFoundError(
            "Data files not installed. Run: python -m gngram_lookup.download_data"
        )

    word = normalize(word)
    if len(word) <= min_len:
        return []

    words, tfs = _load_wordlist()

    seen: set[str] = set()
    candidates: list[tuple[str, int]] = []

    for length in range(len(word) - 1, min_len - 1, -1):
        prefix = word[:length]
        lo = bisect.bisect_left(words, prefix)
        for i in range(lo, len(words)):
            w = words[i]
            if not w.startswith(prefix):
                break
            if w == word or w.startswith(word):
                continue
            if min_tf > 0 and tfs[i] < min_tf:
                continue
            if w not in seen:
                seen.add(w)
                candidates.append((w, tfs[i]))

    if sort_by == "freq":
        candidates.sort(key=lambda x: x[1], reverse=True)
    else:
        candidates.sort(key=lambda x: x[0])

    if with_freq:
        return candidates
    return [w for w, _ in candidates]
