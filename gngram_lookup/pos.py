"""
POS tag lookup for gngram-lookup.

Returns all part-of-speech tags attested for a word in the Google Books
Ngram corpus (2012 edition). Tags use Google's own tag set:

    NOUN  VERB  ADJ  ADV  PRON  DET  ADP  NUM  CONJ  PRT  X  .

Words with multiple attested tags (e.g. "fast": ADJ, ADV, VERB) return
all of them. Unknown words return an empty list.

Usage:
    from gngram_lookup import pos, has_pos, PosTag
    pos("sing")                         # ["VERB"]
    pos("fast")                         # ["ADJ", "ADV", "VERB"]
    pos("fast", min_tf=1000)            # tags with cumulative freq >= 1000
    has_pos("sing", PosTag.VERB)        # True
    has_pos("sing", PosTag.VERB, min_tf=1000)  # True if tf >= 1000
"""

from __future__ import annotations

import hashlib
from enum import Enum
from functools import lru_cache

import polars as pl

from gngram_lookup.data import get_pos_hash_file, is_pos_data_installed
from gngram_lookup.normalize import normalize


class PosTag(str, Enum):
    """Google Books Ngram part-of-speech tags."""
    NOUN = "NOUN"
    VERB = "VERB"
    ADJ  = "ADJ"
    ADV  = "ADV"
    PRON = "PRON"
    DET  = "DET"
    ADP  = "ADP"
    NUM  = "NUM"
    CONJ = "CONJ"
    PRT  = "PRT"
    X    = "X"


@lru_cache(maxsize=256)
def _load_pos_bucket(prefix: str) -> pl.DataFrame:
    """Load and cache a POS parquet bucket file."""
    return pl.read_parquet(get_pos_hash_file(prefix))


def _lookup_raw(word: str) -> dict[str, int]:
    """Return {tag: cumulative_tf} for a word, or {} if not found."""
    if not is_pos_data_installed():
        raise FileNotFoundError(
            "POS data files not installed. Run: python -m gngram_lookup.download_pos_data"
        )

    word = normalize(word)
    if not word:
        return {}

    h = hashlib.md5(word.encode("utf-8")).hexdigest()
    prefix, suffix = h[:2], h[2:]

    try:
        df = _load_pos_bucket(prefix)
    except FileNotFoundError:
        return {}

    row = df.filter(pl.col("hash") == suffix)
    if row.is_empty():
        return {}

    result: dict[str, int] = {}
    for part in row["pos"][0].split("|"):
        tag, _, freq_str = part.partition(":")
        result[tag] = int(freq_str) if freq_str else 0
    return result


def pos(word: str, min_tf: int | None = None) -> list[str]:
    """Return attested POS tags for a word, or [] if not found.

    Args:
        word:   Any word. Normalized before lookup (lowercased, accent-stripped).
        min_tf: If given, only return tags with cumulative corpus frequency >= min_tf.

    Returns:
        Sorted list of POS tag strings, e.g. ["ADJ", "VERB"]. Empty list if
        the word is absent from the corpus (or no tags meet the threshold).

    Raises:
        FileNotFoundError: If POS data files have not been downloaded.
    """
    tag_freqs = _lookup_raw(word)
    if min_tf is not None:
        tag_freqs = {t: f for t, f in tag_freqs.items() if f >= min_tf}
    return sorted(tag_freqs)


def has_pos(word: str, tag: PosTag, min_tf: int | None = None) -> bool:
    """Return True if the word is attested with the given POS tag.

    Args:
        word:   Any word.
        tag:    A PosTag enum value, e.g. PosTag.VERB.
        min_tf: If given, only return True if the tag's cumulative corpus
                frequency is >= min_tf.

    Returns:
        True if the tag appears in the word's attested POS set (and meets
        the frequency threshold if specified).

    Raises:
        FileNotFoundError: If POS data files have not been downloaded.
    """
    tag_freqs = _lookup_raw(word)
    if tag.value not in tag_freqs:
        return False
    if min_tf is not None:
        return tag_freqs[tag.value] >= min_tf
    return True
