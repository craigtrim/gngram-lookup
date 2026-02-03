# gngram-counter

Google Ngram frequency lookup using hash-bucketed parquet files.

Based on the Google Books Ngram dataset, this library provides fast O(1) lookups for word frequency data across decades (1500s-2000s).

## Installation

```bash
pip install gngram-counter
```

After installing, download the data files (~110MB):

```bash
python -m gngram_counter.download_data
```

Data is stored in `~/.gngram-counter/data/`.

## Quick Start

```python
from gngram_counter import exists, frequency, batch_frequency

# Check if a word exists in the corpus
exists("example")      # True
exists("xyznotaword")  # False

# Get frequency data for a word
freq = frequency("example")
# Returns: {'peak_tf': 1990, 'peak_df': 1990, 'sum_tf': 12345, 'sum_df': 9876}
# Or None if word not found

# Batch lookup for multiple words (efficient for large lists)
results = batch_frequency(["the", "example", "xyznotaword"])
# Returns: {'the': {...}, 'example': {...}, 'xyznotaword': None}
```

## API Reference

### `exists(word: str) -> bool`

Check if a word exists in the ngram corpus.

- **word**: The word to check (case-insensitive)
- **Returns**: `True` if found, `False` otherwise
- **Raises**: `FileNotFoundError` if data not installed

```python
exists("THE")      # True (case-insensitive)
exists("hello")    # True
exists("asdfgh")   # False
```

### `frequency(word: str) -> FrequencyData | None`

Get frequency data for a single word.

- **word**: The word to look up (case-insensitive)
- **Returns**: `FrequencyData` dict or `None` if not found
- **Raises**: `FileNotFoundError` if data not installed

```python
freq = frequency("computer")
if freq:
    print(f"Peak usage decade (by TF): {freq['peak_tf']}")
    print(f"Peak usage decade (by DF): {freq['peak_df']}")
    print(f"Total term frequency: {freq['sum_tf']}")
    print(f"Total document frequency: {freq['sum_df']}")
```

### `batch_frequency(words: list[str]) -> dict[str, FrequencyData | None]`

Get frequency data for multiple words efficiently.

- **words**: List of words to look up (case-insensitive)
- **Returns**: Dict mapping each word to its `FrequencyData` or `None`
- **Raises**: `FileNotFoundError` if data not installed

Words are grouped by hash prefix for efficient batch lookups.

```python
results = batch_frequency(["apple", "banana", "notaword"])
for word, freq in results.items():
    if freq:
        print(f"{word}: TF={freq['sum_tf']}")
    else:
        print(f"{word}: not found")
```

### `FrequencyData`

TypedDict with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `peak_tf` | `int` | Decade (e.g., 1990) with highest term frequency |
| `peak_df` | `int` | Decade with highest document frequency |
| `sum_tf` | `int` | Total term frequency across all decades |
| `sum_df` | `int` | Total document frequency across all decades |

### `is_data_installed() -> bool`

Check if data files have been downloaded.

```python
from gngram_counter import is_data_installed

if not is_data_installed():
    print("Run: python -m gngram_counter.download_data")
```

## Low-level API

For direct parquet file access:

```python
from gngram_counter import get_hash_file
import polars as pl
import hashlib

word = "example"
h = hashlib.md5(word.encode()).hexdigest()
df = pl.read_parquet(get_hash_file(h[:2]))
rows = df.filter(pl.col("hash") == h[2:])
```

## Data Schema

The corpus is split into 256 parquet files (`00.parquet` to `ff.parquet`), bucketed by MD5 hash prefix.

Each file contains:

| Column | Type | Description |
|--------|------|-------------|
| `hash` | `str` | 30-char MD5 suffix (prefix is filename) |
| `peak_tf` | `int` | Decade with highest term frequency |
| `peak_df` | `int` | Decade with highest document frequency |
| `sum_tf` | `int` | Total term frequency across all decades |
| `sum_df` | `int` | Total document frequency across all decades |

## Development

```bash
make install          # Install dependencies
make test             # Run tests
make lint             # Run linter
make build-hash       # Build hash files from source parquet
make package-release  # Create parquet-hash.tar.gz
make release VERSION=v1.1.0  # Create GitHub release
```

## License

MIT
