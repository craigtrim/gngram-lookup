"""
POS tag lookup for gngram-lookup.

Returns all part-of-speech tags attested for a word in the Google Books
Ngram corpus (2012 edition). Tags use Google's own tag set:

    NOUN  VERB  ADJ  ADV  PRON  DET  ADP  NUM  CONJ  PRT  X  .

Words with multiple attested tags (e.g. "fast": ADJ, ADV, VERB) return
all of them. Unknown words return an empty list.

Usage:
    from gngram_lookup import pos
    pos("sing")   # ["VERB"]
    pos("corn")   # ["NOUN"]
    pos("fast")   # ["ADJ", "ADV", "VERB"]
    pos("zzz")    # []
"""

from __future__ import annotations

import hashlib
from functools import lru_cache

import polars as pl

from gngram_lookup.data import get_pos_hash_file, is_pos_data_installed
from gngram_lookup.normalize import normalize


@lru_cache(maxsize=256)
def _load_pos_bucket(prefix: str) -> pl.DataFrame:
    """Load and cache a POS parquet bucket file."""
    return pl.read_parquet(get_pos_hash_file(prefix))


def pos(word: str) -> list[str]:
    """Return attested POS tags for a word, or [] if not found.

    Args:
        word: Any word. Normalized before lookup (lowercased, accent-stripped).

    Returns:
        Sorted list of POS tags, e.g. ["ADJ", "VERB"]. Empty list if the word
        is absent from the corpus or POS data is not installed.

    Raises:
        FileNotFoundError: If POS data files have not been downloaded.
    """
    if not is_pos_data_installed():
        raise FileNotFoundError(
            "POS data files not installed. Run: python -m gngram_lookup.download_pos_data"
        )

    word = normalize(word)
    if not word:
        return []

    h = hashlib.md5(word.encode("utf-8")).hexdigest()
    prefix, suffix = h[:2], h[2:]

    try:
        df = _load_pos_bucket(prefix)
    except FileNotFoundError:
        return []

    row = df.filter(pl.col("hash") == suffix)
    if row.is_empty():
        return []

    return row["pos"][0].split("|")
