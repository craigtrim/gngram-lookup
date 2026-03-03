# Data Format

## Frequency Data

### Overview

The corpus is split into 256 parquet files (`00.parquet` to `ff.parquet`), bucketed by MD5 hash prefix. This enables O(1) lookups without loading the entire dataset.

### File Structure

```
~/.gngram-lookup/data/
├── 00.parquet
├── 01.parquet
├── ...
├── ff.parquet
└── wordlist.parquet
```

Each hash bucket file contains ~19,500 words (~430 KB per file). `wordlist.parquet` contains all 5,001,090 unique words sorted alphabetically — see [wordlist.md](wordlist.md) for details.

### Schema

| Column | Type | Description |
|--------|------|-------------|
| `hash` | `str` | 30-char MD5 suffix (prefix is the filename) |
| `peak_tf` | `int` | Decade with highest term frequency |
| `peak_df` | `int` | Decade with highest document frequency |
| `sum_tf` | `int` | Total term frequency across all decades |
| `sum_df` | `int` | Total document frequency across all decades |

### Lookup Process

1. Compute MD5 hash of lowercase word
2. Use first 2 hex chars as bucket (filename)
3. Search for remaining 30 chars in that file

```python
import hashlib

word = "computer"
h = hashlib.md5(word.lower().encode()).hexdigest()
# h = "df53ca268240ca76670c8566ee54568a"
# bucket = "df" -> df.parquet
# search for hash = "53ca268240ca76670c8566ee54568a"
```

---

## POS Data

### Overview

Part-of-speech tags are stored in a parallel set of 256 parquet files under a separate directory, using the same hash-bucketing scheme. POS data must be downloaded independently from frequency data.

### File Structure

```
~/.gngram-lookup/pos-data/
├── 00.parquet
├── 01.parquet
├── ...
└── ff.parquet
```

### Schema

| Column | Type | Description |
|--------|------|-------------|
| `hash` | `str` | 30-char MD5 suffix (prefix is the filename) |
| `pos` | `str` | Pipe-separated POS tags, e.g. `"ADJ\|ADV\|VERB"` |

### Tag Set

Google Books Ngram uses its own tag set (not Penn Treebank):

| Tag | Description |
|-----|-------------|
| `NOUN` | Noun |
| `VERB` | Verb |
| `ADJ` | Adjective |
| `ADV` | Adverb |
| `PRON` | Pronoun |
| `DET` | Determiner |
| `ADP` | Adposition |
| `NUM` | Numeral |
| `CONJ` | Conjunction |
| `PRT` | Particle |
| `X` | Other / foreign |

Words with multiple attested uses (e.g. "fast" as adjective, adverb, and verb) have all tags stored pipe-separated in a single row.

---

## Why Hash-Bucketed?

Words are distributed by MD5 hash to create uniformly-sized files. Looking up a word requires reading only one file, making lookups fast regardless of corpus size. Both frequency and POS data use the same bucketing scheme, so the same hash computation applies to both.

---

## Data Source

Data is derived from the Google Books Ngram dataset:

- 500 years of published text (1500s to 2000s)
- Over 5 million books scanned and indexed
- 5+ million unique words

The data represents a processed snapshot and is not automatically updated.
