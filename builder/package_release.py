"""
Package parquet-hash directory for GitHub release.

Usage:
    python -m builder.package_release

Creates parquet-hash.tar.gz in the current directory.
Upload this file to a GitHub release for distribution.
"""

import sys
import tarfile
from pathlib import Path


def main() -> None:
    parquet_dir = Path("parquet-hash")
    output_file = Path("parquet-hash.tar.gz")

    if not parquet_dir.is_dir():
        print(f"Error: {parquet_dir} not found")
        print("Run build_hash_files first to generate the parquet files.")
        sys.exit(1)

    files = list(parquet_dir.glob("*.parquet"))
    if not files:
        print(f"Error: No parquet files found in {parquet_dir}")
        sys.exit(1)

    print(f"Packaging {len(files)} parquet files...")

    with tarfile.open(output_file, "w:gz") as tar:
        for f in sorted(files):
            tar.add(f, arcname=f"parquet-hash/{f.name}")

    size_mb = output_file.stat().st_size / 1024 / 1024
    print(f"Created: {output_file} ({size_mb:.1f} MB)")
    print()
    print("To release:")
    print(f"  1. Create a GitHub release tagged as v1.0.0")
    print(f"  2. Upload {output_file} to the release")
    print(f"  3. Update DATA_VERSION in gngram_counter/download_data.py if needed")


if __name__ == "__main__":
    main()
