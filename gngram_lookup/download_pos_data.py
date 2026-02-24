"""
Download gngram POS data files from GitHub.

Usage:
    python -m gngram_lookup.download_pos_data

Downloads parquet-pos files to ~/.gngram-lookup/pos-data/
"""

import sys
import tarfile
import urllib.request
from io import BytesIO
from pathlib import Path

GITHUB_REPO = "craigtrim/gngram-lookup"
POS_DATA_VERSION = "v1.1.0"
POS_DATA_FILENAME = "parquet-pos.tar.gz"

POS_DATA_DIR = Path.home() / ".gngram-lookup" / "pos-data"


def get_download_url() -> str:
    return f"https://github.com/{GITHUB_REPO}/releases/download/{POS_DATA_VERSION}/{POS_DATA_FILENAME}"


def download_and_extract() -> None:
    url = get_download_url()
    print(f"Downloading gngram POS data from {url}")
    print(f"Destination: {POS_DATA_DIR}")

    POS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with urllib.request.urlopen(url) as response:
            total_size = response.headers.get("Content-Length")
            if total_size:
                total_size = int(total_size)
                print(f"Size: {total_size / 1024 / 1024:.1f} MB")

            data = BytesIO()
            downloaded = 0
            chunk_size = 1024 * 1024  # 1MB chunks

            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                data.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    pct = downloaded / total_size * 100
                    print(f"\r  {downloaded / 1024 / 1024:.1f} MB ({pct:.0f}%)", end="", flush=True)
                else:
                    print(f"\r  {downloaded / 1024 / 1024:.1f} MB", end="", flush=True)

            print()
            data.seek(0)

            print("Extracting...")
            with tarfile.open(fileobj=data, mode="r:gz") as tar:
                tar.extractall(POS_DATA_DIR, filter="data")

    except urllib.error.HTTPError as e:
        print(f"Error: Failed to download ({e.code} {e.reason})")
        print(f"URL: {url}")
        print("Make sure the release exists and the file is attached.")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Network error ({e.reason})")
        sys.exit(1)

    parquet_files = list(POS_DATA_DIR.glob("**/*.parquet"))
    print(f"Done: {len(parquet_files)} parquet files installed to {POS_DATA_DIR}")


def ensure_pos_data() -> None:
    """Download POS data if not already installed. No prompts."""
    if POS_DATA_DIR.exists() and any(POS_DATA_DIR.glob("**/*.parquet")):
        print(f"POS data already installed at {POS_DATA_DIR}")
        return
    download_and_extract()


def main() -> None:
    if POS_DATA_DIR.exists() and any(POS_DATA_DIR.glob("**/*.parquet")):
        print(f"POS data already exists at {POS_DATA_DIR}")
        response = input("Re-download and overwrite? [y/N]: ").strip().lower()
        if response != "y":
            print("Cancelled.")
            return

    download_and_extract()


if __name__ == "__main__":
    main()
