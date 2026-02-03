# Development Context

Development guidelines for gngram-counter.

**User Instructions:** $ARGUMENTS

## Git Discipline

**Do NOT commit until explicitly asked.** Work on code, run tests, iterate - but wait for the user to request a commit. Never proactively commit changes.

## Code Style

Keep code simple and focused:
- Clear, descriptive function and variable names
- Type hints for function signatures
- Brief docstrings explaining purpose and usage
- Minimal inline comments (only for non-obvious logic)

## Project Structure

```
gngram-counter/
├── gngram_counter/          # Main package (distributed)
│   ├── __init__.py          # Public API exports
│   ├── data.py              # Data path utilities
│   └── download_data.py     # Download from GitHub releases
├── builder/                 # Build scripts (not distributed)
│   ├── build_unigrams.py    # Process raw 1-gram data
│   ├── build_hash_files.py  # Create hash-bucketed files
│   ├── report_stats.py      # Report parquet stats
│   └── package_release.py   # Package for release
└── tests/                   # Test suite
```

## Development Workflow

```bash
# Install dependencies
make install

# Run linter
make lint

# Run tests
make test

# All checks
make all
```

## Build Pipeline (for maintainers)

Building data files from raw Google Books data:

```bash
# 1. Process raw 1-gram TSV files to parquet
python -m builder.build_unigrams <raw_input_dir> <parquet_output_dir>

# 2. Build hash-bucketed parquet files
python -m builder.build_hash_files <parquet_dir> parquet-hash

# 3. Report stats on generated files
python -m builder.report_stats parquet-hash

# 4. Package for GitHub release
python -m builder.package_release
```

Or use Makefile shortcuts:
```bash
make build-hash       # Steps 1-2 (expects ~/Desktop/gngram-parquet)
make package-release  # Step 4
```

## Testing Data Downloads

```bash
# Download data files (as an end user would)
make download-data

# Or directly
python -m gngram_counter.download_data
```

## Data Distribution Strategy

The package is split between PyPI and GitHub releases due to size constraints:

**PyPI Wheel (~50KB)** - installed via `pip install gngram-counter`:
- `gngram_counter/` - Core package with lookup utilities
- `gngram_counter/download_data.py` - Script to fetch data from GitHub
- `gngram_counter/data.py` - Data path helpers

**GitHub Release (~110MB)** - downloaded via `python -m gngram_counter.download_data`:
- `parquet-hash.tar.gz` - 256 parquet files (00.parquet to ff.parquet)
- Contains hash-bucketed word frequency data
- Installed to `~/.gngram-counter/data/`

**Excluded from PyPI** (via `pyproject.toml exclude`):
- `builder/` - Build scripts for maintainers only
- `parquet-hash/` - Data files (too large for PyPI, distributed via GitHub)

**Release Workflow**:
1. `make build-hash` - Generate parquet files from source data
2. `make package-release` - Create `parquet-hash.tar.gz`
3. Create GitHub release (e.g., `v1.0.0`), upload tarball
4. Update `DATA_VERSION` in `download_data.py` to match release tag

## Instructions

Follow the user's instructions in `$ARGUMENTS`. Apply these development guidelines throughout your work.
