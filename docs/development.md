# Development

## Setup

```bash
git clone https://github.com/craigtrim/gngram-lookup.git
cd gngram-lookup
make install
```

## Commands

### General

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make test` | Run tests |
| `make lint` | Run linter |

### Frequency Data

| Command | Description |
|---------|-------------|
| `make build-hash` | Build hash files from source parquet |
| `make package-release` | Create `parquet-hash.tar.gz` |
| `make release VERSION=v1.1.0` | Create GitHub release with frequency data |
| `make download-data` | Download frequency data (prompts before overwrite) |
| `make ensure-data` | Download frequency data if not installed (no prompts) |

### POS Data

| Command | Description |
|---------|-------------|
| `make build-pos` | Build POS hash files from raw Google Ngram source |
| `make package-pos-release` | Create `parquet-pos.tar.gz` |
| `make release-pos VERSION=v1.1.0` | Upload POS tarball to an existing GitHub release |
| `make download-pos-data` | Download POS data (prompts before overwrite) |
| `make ensure-pos-data` | Download POS data if not installed (no prompts) |

## Building Frequency Data

To rebuild the hash-bucketed parquet files from source:

```bash
make build-hash
```

This processes the raw ngram data and creates the 256 bucket files.

## Building POS Data

To rebuild POS hash files from the raw Google Ngram unigram source files:

```bash
make build-pos
```

Source files are expected at `/Volumes/WD06-6/Misc Output/Google Unigrams/txt`.

## Creating a Release

### Frequency data

```bash
make package-release
make release VERSION=v1.2.0
```

After releasing, update `DATA_VERSION` in [gngram_lookup/download_data.py](../gngram_lookup/download_data.py).

### POS data

```bash
make package-pos-release
make release-pos VERSION=v1.2.0
```

After releasing, update `POS_DATA_VERSION` in [gngram_lookup/download_pos_data.py](../gngram_lookup/download_pos_data.py).

Both tarballs can be attached to the same GitHub release.
