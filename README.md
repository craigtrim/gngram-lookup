# gngram-counter

Google Ngram frequency lookup using hash-bucketed parquet files.

## Installation

```bash
pip install gngram-counter
```

After installing, download the data files:

```bash
python -m gngram_counter.download_data
```

This downloads ~110MB of parquet files to `~/.gngram-counter/data/`.

## Usage

```python
from gngram_counter import get_hash_file, is_data_installed
import polars as pl
import hashlib

# Check if data is installed
if not is_data_installed():
    print("Run: python -m gngram_counter.download_data")

# Lookup a word
word = "example"
h = hashlib.md5(word.encode()).hexdigest()
prefix, suffix = h[:2], h[2:]

df = pl.read_parquet(get_hash_file(prefix))
row = df.filter(pl.col("hash") == suffix)

if len(row):
    print(f"peak_tf_decade: {row['peak_tf'][0]}")
    print(f"peak_df_decade: {row['peak_df'][0]}")
    print(f"sum_tf: {row['sum_tf'][0]}")
    print(f"sum_df: {row['sum_df'][0]}")
```

## Data Schema

Each parquet file contains:
- `hash`: 30-char MD5 suffix (prefix is the filename)
- `peak_tf`: decade with highest term frequency
- `peak_df`: decade with highest document frequency
- `sum_tf`: total term frequency across all decades
- `sum_df`: total document frequency across all decades

## Development

```bash
# Install dependencies
make install

# Run tests
make test

# Build hash files from source parquet
make build-hash

# Package for GitHub release
make package-release
```

## Release Workflow

1. Build hash files: `make build-hash`
2. Package: `make package-release` (creates `parquet-hash.tar.gz`)
3. Create GitHub release, upload `parquet-hash.tar.gz`
4. Update `DATA_VERSION` in `gngram_counter/download_data.py` if needed
