"""
Download gngram data files from GitHub.

Usage:
    python -m gngram_counter.download_data

Downloads parquet hash files to ~/.gngram-counter/data/
"""

import sys
import tarfile
import urllib.request
from io import BytesIO
from pathlib import Path

GITHUB_REPO = "craigtrim/gngram-counter"
DATA_VERSION = "v1.0.0"
DATA_FILENAME = "parquet-hash.tar.gz"

DATA_DIR = Path.home() / ".gngram-counter" / "data"


def get_download_url() -> str:
    return f"https://github.com/{GITHUB_REPO}/releases/download/{DATA_VERSION}/{DATA_FILENAME}"


def download_and_extract() -> None:
    url = get_download_url()
    print(f"Downloading gngram data from {url}")
    print(f"Destination: {DATA_DIR}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

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
                tar.extractall(DATA_DIR, filter="data")

    except urllib.error.HTTPError as e:
        print(f"Error: Failed to download ({e.code} {e.reason})")
        print(f"URL: {url}")
        print("Make sure the release exists and the file is attached.")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Network error ({e.reason})")
        sys.exit(1)

    parquet_files = list(DATA_DIR.glob("**/*.parquet"))
    print(f"Done: {len(parquet_files)} parquet files installed to {DATA_DIR}")


def main() -> None:
    if DATA_DIR.exists() and any(DATA_DIR.glob("**/*.parquet")):
        print(f"Data already exists at {DATA_DIR}")
        response = input("Re-download and overwrite? [y/N]: ").strip().lower()
        if response != "y":
            print("Cancelled.")
            return

    download_and_extract()


if __name__ == "__main__":
    main()
