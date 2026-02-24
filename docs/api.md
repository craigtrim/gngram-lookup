# API Reference

## Functions

### `exists(word: str) -> bool`

Check if a word exists in the corpus.

```python
import gngram_lookup as ng

ng.exists('THE')           # True (case-insensitive)
ng.exists('hello')         # True
ng.exists('asdfgh')        # False
```

### `frequency(word: str) -> FrequencyData | None`

Get frequency data for a word. Returns `None` if not found.

```python
import gngram_lookup as ng

freq = ng.frequency('algorithm')
if freq:
    print(f"Peak decade (TF): {freq['peak_tf']}")   # When it was used most
    print(f"Peak decade (DF): {freq['peak_df']}")   # When it appeared in most books
    print(f"Total TF: {freq['sum_tf']}")            # Total occurrences
    print(f"Total DF: {freq['sum_df']}")            # Total books containing it
```

### `batch_frequency(words: list[str]) -> dict[str, FrequencyData | None]`

Efficient batch lookup. Words are grouped by hash prefix to minimize file reads.

```python
import gngram_lookup as ng

results = ng.batch_frequency(['apple', 'banana', 'notaword'])
for word, freq in results.items():
    if freq:
        print(f"{word}: peaked in {freq['peak_tf']}")
    else:
        print(f"{word}: not found")
```

### `word_score(word: str) -> int | None`

Return a 1–100 commonness score. **1 = most common, 100 = least common.** Returns `None` if the word is not in the corpus.

Score is log-normalized against the most frequent word in the corpus ("the"), so the Zipfian spike at the top is compressed into the first few numbers and the rest of the vocabulary gets meaningful resolution.

```python
import gngram_lookup as ng

ng.word_score('the')          # 1
ng.word_score('computer')     # 18
ng.word_score('algorithm')    # 40
ng.word_score('rucksack')     # 58
ng.word_score('xyznotaword')  # None
```

### `pos(word: str, min_tf: int | None = None) -> list[str]`

Return all part-of-speech tags attested for a word in the Google Books Ngram corpus. Tags use Google's own tag set. Returns an empty list if the word is not found.

```python
import gngram_lookup as ng

ng.pos('sing')                # ['VERB']
ng.pos('fast')                # ['ADJ', 'ADV', 'VERB']
ng.pos('the')                 # ['DET']
ng.pos('xyzabc')              # []
ng.pos('corn', min_tf=10000)  # ['ADJ', 'NOUN']  — only tags with tf >= 10000
```

Raises `FileNotFoundError` if POS data has not been downloaded.

### `pos_freq(word: str, min_tf: int | None = None) -> dict[str, int]`

Return all attested POS tags and their cumulative corpus frequencies. Useful for inspecting raw counts before choosing a `min_tf` threshold.

```python
import gngram_lookup as ng

ng.pos_freq('corn')
# {'NOUN': 11722803, 'ADJ': 1433642, 'VERB': 85411, ...}

ng.pos_freq('corn', min_tf=100000)
# {'NOUN': 11722803, 'ADJ': 1433642}
```

Raises `FileNotFoundError` if POS data has not been downloaded.

### `has_pos(word: str, tag: PosTag, min_tf: int | None = None) -> bool`

Return `True` if the word is attested with the given POS tag.

```python
import gngram_lookup as ng

ng.has_pos('sing', ng.PosTag.VERB)                  # True
ng.has_pos('fast', ng.PosTag.ADJ)                   # True
ng.has_pos('corn', ng.PosTag.VERB, min_tf=100000)   # False (85k < 100k)
ng.has_pos('corn', ng.PosTag.NOUN, min_tf=100000)   # True (11.7M >= 100k)
```

Raises `FileNotFoundError` if POS data has not been downloaded.

### `is_data_installed() -> bool`

Check if frequency data files have been downloaded.

```python
import gngram_lookup as ng

if not ng.is_data_installed():
    print("Run: python -m gngram_lookup.download_data")
```

### `is_pos_data_installed() -> bool`

Check if POS data files have been downloaded.

```python
import gngram_lookup as ng

if not ng.is_pos_data_installed():
    print("Run: python -m gngram_lookup.download_pos_data")
```

### `get_hash_file(prefix: str) -> Path`

Return path to a specific frequency hash bucket parquet file. For direct file access.

```python
from gngram_lookup import get_hash_file
import polars as pl
import hashlib

word = "example"
h = hashlib.md5(word.lower().encode()).hexdigest()
df = pl.read_parquet(get_hash_file(h[:2]))
rows = df.filter(pl.col("hash") == h[2:])
```

### `get_data_dir() -> Path`

Return the frequency data directory path (`~/.gngram-lookup/data/`).

## Types

### `FrequencyData`

A TypedDict with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `peak_tf` | `int` | Decade with highest term frequency (e.g., 1990) |
| `peak_df` | `int` | Decade with highest document frequency |
| `sum_tf` | `int` | Total term frequency across all decades |
| `sum_df` | `int` | Total document frequency across all decades |

### `PosTag`

An enum of Google Books Ngram part-of-speech tags:

| Tag | Description |
|-----|-------------|
| `PosTag.NOUN` | Noun |
| `PosTag.VERB` | Verb |
| `PosTag.ADJ` | Adjective |
| `PosTag.ADV` | Adverb |
| `PosTag.PRON` | Pronoun |
| `PosTag.DET` | Determiner |
| `PosTag.ADP` | Adposition (preposition/postposition) |
| `PosTag.NUM` | Numeral |
| `PosTag.CONJ` | Conjunction |
| `PosTag.PRT` | Particle |
| `PosTag.X` | Other / foreign words |
