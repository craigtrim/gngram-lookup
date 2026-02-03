# Build Context

Build and package gngram data files from raw Google Books 1-gram data.

**User Instructions:** $ARGUMENTS

## Build Pipeline Overview

The build pipeline transforms raw Google Books 1-gram TSV files into hash-bucketed parquet files for efficient lookups.

```
Raw TSV files → Decade-aggregated parquet → Hash-bucketed parquet → Tar archive → GitHub release
```

## Step 1: Process Raw 1-grams

Convert raw Google Books 1-gram TSV files to decade-aggregated parquet:

```bash
python -m builder.build_unigrams <input_dir> <output_dir>
```

**Input format:** Tab-delimited with columns: ngram, year, tf, df
**Output:** Parquet files with columns: word, decade, tf, df

Processing:
- Lowercase all words
- Strip POS tags (e.g., `accrued_VERB` → `accrued`)
- Filter to pure alpha `[a-z]` only
- Aggregate TF and DF by (word, decade)

## Step 2: Build Hash Files

Convert decade-aggregated parquet to hash-bucketed parquet:

```bash
python -m builder.build_hash_files <parquet_dir> <output_dir>
```

**Output:** 256 parquet files named `00.parquet` through `ff.parquet`

Each file contains words whose MD5 hash starts with that 2-char prefix:
- `hash`: MD5 suffix (30 chars)
- `peak_tf`: Decade with highest term frequency
- `peak_df`: Decade with highest document frequency
- `sum_tf`: Total term frequency across all decades
- `sum_df`: Total document frequency across all decades

## Step 3: Report Stats

Verify the generated files:

```bash
python -m builder.report_stats <parquet_dir>
```

Reports row counts and unique word counts per file and total.

## Step 4: Package Release

Create a tarball for GitHub release:

```bash
python -m builder.package_release
```

Creates `parquet-hash.tar.gz` in the current directory.

## Makefile Shortcuts

```bash
make build-hash       # Steps 1-2 (expects ~/Desktop/gngram-parquet as source)
make package-release  # Step 4
```

## Releasing

Full release workflow:

```bash
# 1. Package the data
make package-release

# 2. Create GitHub release and upload tarball
gh release create v1.0.0 parquet-hash.tar.gz --title "v1.0.0" --notes "Release notes here"

# 3. If version changed, update download_data.py
# Edit DATA_VERSION in gngram_counter/download_data.py to match the tag
```

For subsequent releases, increment the version (e.g., `v1.1.0`, `v2.0.0`).

## Instructions

Follow the user's instructions in `$ARGUMENTS`. This may include:
- Running the full build pipeline
- Running individual build steps
- Debugging build issues
- Packaging for release
