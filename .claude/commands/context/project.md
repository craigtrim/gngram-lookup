# gngram-counter - Project Context

Use this context when starting work on the gngram-counter project to understand the architecture, goals, and available components.

**IMPORTANT:** Do not commit changes to git unless explicitly instructed to do so by the user.

## Overview

A Python utility for working with Google Ngram frequency data. Provides hash-bucketed parquet files for efficient word frequency lookups and tools to build/distribute the data.

## Package Structure

```
gngram-counter/
├── gngram_counter/          # Main package (distributed via pip)
│   ├── __init__.py          # Public API exports
│   ├── data.py              # Data path utilities
│   └── download_data.py     # Download data from GitHub releases
├── builder/                 # Build scripts (excluded from package)
│   ├── build_unigrams.py    # Process raw Google Books 1-gram data
│   ├── build_hash_files.py  # Create hash-bucketed parquet files
│   ├── report_stats.py      # Report stats on parquet files
│   └── package_release.py   # Package for GitHub release
└── tests/                   # Test suite
```

## Data Architecture

### Hash Bucketing

Words are stored in 256 parquet files named by MD5 hash prefix:
- `00.parquet`, `01.parquet`, ..., `ff.parquet`
- Each file contains words whose MD5 hash starts with that prefix
- Enables O(1) lookup: hash the word, read one file

### Data Schema

Each parquet file contains:
| Column | Type | Description |
|--------|------|-------------|
| hash | str | MD5 hash suffix (30 chars, minus 2-char prefix) |
| peak_tf | int | Decade with highest term frequency |
| peak_df | int | Decade with highest document frequency |
| sum_tf | int | Total term frequency across all decades |
| sum_df | int | Total document frequency across all decades |

### Data Location

Data files are stored at: `~/.gngram-counter/data/`

## Public API

```python
from gngram_counter import get_data_dir, get_hash_file, is_data_installed

# Check if data is installed
if not is_data_installed():
    print("Run: python -m gngram_counter.download_data")

# Get path to data directory
data_dir = get_data_dir()  # ~/.gngram-counter/data/

# Get path to specific hash bucket
hash_file = get_hash_file("ab")  # ~/.gngram-counter/data/ab.parquet
```

## Build Pipeline

The build pipeline processes raw Google Books 1-gram data:

1. **build_unigrams** - Process raw TSV files into decade-aggregated parquet
   ```bash
   python -m builder.build_unigrams <input_dir> <output_dir>
   ```

2. **build_hash_files** - Convert to hash-bucketed parquet files
   ```bash
   python -m builder.build_hash_files <parquet_dir> <output_dir>
   ```

3. **package_release** - Create tarball for GitHub release
   ```bash
   python -m builder.package_release
   ```

4. **download_data** - End users download pre-built data
   ```bash
   python -m gngram_counter.download_data
   ```

## Makefile Targets

```bash
make install          # Install dependencies
make test             # Run tests
make lint             # Run ruff linter
make clean            # Remove cache files
make build-hash       # Build hash files from source
make package-release  # Package for GitHub release
make download-data    # Download data files
```

## Dependencies

- `polars>=1.0` - DataFrame operations
- `pyarrow>=18.0` - Parquet file support
- Python 3.11+

## Key Design Principles

1. **Efficient lookups** - Hash bucketing enables fast single-word lookups
2. **Minimal dependencies** - Only polars and pyarrow
3. **Offline-first** - Download once, query locally
4. **Simple API** - Just path utilities, users handle parquet reading

## Project Repository

GitHub: https://github.com/craigtrim/gngram-counter
