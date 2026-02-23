.PHONY: all install test lint clean build-hash package-release release download-data build-pos package-pos-release release-pos download-pos-data

all: install test

install:
	poetry install

test:
	poetry run pytest tests/ --no-header -rN

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

# Create GitHub release (usage: make release VERSION=v1.1.0)
release: package-release
	@if [ -z "$(VERSION)" ]; then echo "Usage: make release VERSION=v1.1.0"; exit 1; fi
	gh release create $(VERSION) parquet-hash.tar.gz --title "$(VERSION)" --notes "Data release $(VERSION)"
	@echo "Update DATA_VERSION in gngram_lookup/download_data.py to $(VERSION)"

# Download data files (for end users)
download-data:
	poetry run python -m gngram_lookup.download_data

# Build POS hash files from raw Google Ngram source files
build-pos:
	rm -rf pos-hash
	poetry run python -m builder.build_pos_files \
		"/Volumes/WD06-6/Misc Output/Google Unigrams/txt" \
		pos-hash

# Package POS hash files for GitHub release
package-pos-release:
	poetry run python -m builder.package_pos_release

# Create GitHub POS release (usage: make release-pos VERSION=v1.1.0)
release-pos: package-pos-release
	@if [ -z "$(VERSION)" ]; then echo "Usage: make release-pos VERSION=v1.1.0"; exit 1; fi
	gh release upload $(VERSION) parquet-pos.tar.gz
	@echo "Update POS_DATA_VERSION in gngram_lookup/download_pos_data.py to $(VERSION)"

# Download POS data files (for end users)
download-pos-data:
	poetry run python -m gngram_lookup.download_pos_data
