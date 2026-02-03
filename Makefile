.PHONY: all install test lint clean build-hash package-release download-data

all: install test

install:
	poetry install

test:
	poetry run pytest tests/ --no-header -rN || test $$? -eq 5

lint:
	poetry run ruff check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Build hash files from source parquet (requires ~/Desktop/gngram-parquet)
build-hash:
	rm -rf parquet-hash
	poetry run python -m builder.build_hash_files ~/Desktop/gngram-parquet parquet-hash

# Package hash files for GitHub release
package-release:
	poetry run python -m builder.package_release

# Download data files (for end users)
download-data:
	poetry run python -m gngram_counter.download_data
