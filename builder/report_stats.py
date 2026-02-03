"""Report unique word and row counts across all parquet files in a directory."""

import sys
from pathlib import Path

import polars as pl


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m builder.report_stats <parquet_dir>")
        sys.exit(1)

    parquet_dir = Path(sys.argv[1])
    if not parquet_dir.is_dir():
        print(f"Directory not found: {parquet_dir}")
        sys.exit(1)

    files = sorted(parquet_dir.glob("*.parquet"))
    if not files:
        print(f"No parquet files found in {parquet_dir}")
        sys.exit(1)

    total_rows = 0
    total_unique_words = 0

    all_words: set[str] = set()

    for f in files:
        df = pl.read_parquet(f)
        rows = df.height
        words = set(df["word"].to_list())
        unique = len(words)

        total_rows += rows
        total_unique_words += unique
        all_words.update(words)

        print(f"  {f.name:<60}  rows={rows:>10,}  unique_words={unique:>10,}")

    print()
    print(f"Files:              {len(files):,}")
    print(f"Total rows:         {total_rows:,}")
    print(f"Global unique words:{len(all_words):>10,}")


if __name__ == "__main__":
    main()
