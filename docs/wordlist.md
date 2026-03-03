# Wordlist

## Overview

`wordlist.parquet` is a flat, alphabetically sorted vocabulary file distributed as part of the `v1.1.0` data release. It contains every unique word in the Google Books corpus that passed the pure-alpha filter (lowercased, POS tags stripped, `[a-z]` only).

Unlike the 256 hash-bucket files — which are optimised for O(1) point lookups — the wordlist supports sequential and prefix-range scans, enabling morphological analysis techniques that require iterating over related word forms.

## File Location

```
~/.gngram-lookup/data/parquet-hash/wordlist.parquet
```

Downloaded automatically by `python -m gngram_lookup.download_data` as part of `parquet-hash.tar.gz`.

## Schema

| Column | Type | Description |
|--------|------|-------------|
| `word` | `str` | Lowercase alphabetic word, sorted ascending |
| `sum_tf` | `int` | Total term frequency across all decades |

## Descriptive Statistics

### Vocabulary size by frequency threshold

| Filter | Word count |
|--------|------------|
| All entries (no filter) | 5,001,090 |
| `min_tf >= 100` | 4,257,990 |
| `min_tf >= 1,000` | 1,409,730 |
| `min_tf >= 10,000` | 360,023 |
| `min_tf >= 100,000` | 97,599 |
| `min_tf >= 1,000,000` | 28,448 |
| `min_tf >= 10,000,000` | 6,594 |
| `min_tf >= 100,000,000` | 801 |
| `min_tf >= 1,000,000,000` | 71 |

The full 5M corpus includes significant OCR noise and hapax legomena. For most NLP applications `min_tf=10_000` (~360k words) is a reasonable starting point; `min_tf=1_000_000` (~28k words) approximates a clean general-vocabulary lexicon.

### Word length distribution

| Statistic | Value |
|-----------|-------|
| Minimum length | 1 |
| Maximum length | 133 |
| Mean length | 8.6 |
| Median length | 8 |

## API

```python
from gngram_lookup import wordlist, prefix_cluster

# Full vocabulary
words = wordlist()                      # 5,001,090 words

# Filtered by frequency
words = wordlist(min_tf=10_000)         # ~360k words
words = wordlist(min_tf=1_000_000)      # ~28k words

# Prefix cluster — alphabetical, strings only (default)
prefix_cluster("drink")                 # ['drinker', 'drinking', 'drinks', ...]
prefix_cluster("happy")                 # ['happier', 'happiest', 'happiness', ...]

# y-drop allomorphic variant is handled automatically:
# "happy" -> stem "happ", accept continuations with y or i
prefix_cluster("mercy")                 # ['merciful', 'merciless', 'mercilessly', ...]

# Filter clusters by frequency to suppress OCR noise
prefix_cluster("drink", min_tf=10_000)
prefix_cluster("happy", min_tf=10_000)

# Suppress short root words (default min_len=5)
prefix_cluster("go")                    # [] — too short
prefix_cluster("go", min_len=2)         # ['going', 'gone', 'goes', ...]

# Sort by descending corpus frequency
prefix_cluster("happy", sort_by="freq")
# ['happiness', 'happily', 'happier', 'happiest', ...]

# Return (word, sum_tf) tuples
prefix_cluster("happy", sort_by="freq", with_freq=True)
# [('happiness', 31414547), ('happily', 9336058), ('happier', 4460678), ...]

# Combine all options: frequency-ranked, with counts, noise filtered
prefix_cluster("happy", sort_by="freq", with_freq=True, min_tf=100_000)
# [('happiness', 31414547), ('happily', 9336058), ('happier', 4460678), ('happiest', 2393091)]
```

## Use Case: Morphological Prefix Clustering

Prefix clustering is an unsupervised technique for discovering inflectional and derivational families. Given a root word of length >= N, all longer words sharing the same prefix are candidate inflections:

```
drink  -> [drinker, drinking, drinks, drinkable]
settle -> [settled, settlement, settler, settles]
nation -> [national, nationalism, nationalist, nationality]
```

The y-drop variant handles the most common English allomorphic alternation. For words ending in `-y`, the stem (word minus `y`) is scanned and only continuations with `y` or `i` are accepted, eliminating false matches like `mercantile` from the `mercy` cluster:

```
happy  -> [happier, happiest, happiness]
beauty -> [beautician, beautification, beautiful, beautifully]
mercy  -> [merciful, mercifulness, merciless, mercilessly]
```

This covers roughly 60–70% of English derivational forms with zero configuration.
