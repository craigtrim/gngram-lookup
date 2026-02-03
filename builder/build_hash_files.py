"""
Build hash-bucketed parquet files from source parquet files.

Streams rows from sorted parquet files and writes to consolidated parquet files:

    <output_dir>/xx.parquet

Where xx = first 2 hex chars of MD5 (256 files total).
Each row contains: hash_suffix, peak_tf_decade, peak_df_decade, sum_tf, sum_df

Usage:
    python -m builder.build_hash_files <parquet_dir> <output_dir>
"""

import hashlib
import sys
import time
from collections import defaultdict
from pathlib import Path

import polars as pl


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python -m builder.build_hash_files <parquet_dir> <output_dir>")
        sys.exit(1)

    parquet_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not parquet_dir.is_dir():
        print(f"Directory not found: {parquet_dir}")
        sys.exit(1)

    files = sorted(parquet_dir.glob("*.parquet"))
    if not files:
        print(f"No parquet files found in {parquet_dir}")
        sys.exit(1)

    t0 = time.time()

    # bucket (first 2 hex chars) -> list of (hash_suffix, peak_tf_decade, peak_df_decade, sum_tf, sum_df)
    buckets: dict[str, list[tuple[str, int, int, int, int]]] = defaultdict(list)

    word_count = 0
    current_word: str | None = None
    peak_tf_decade = 0
    peak_tf_value = 0
    peak_df_decade = 0
    peak_df_value = 0
    sum_tf = 0
    sum_df = 0

    for i, f in enumerate(files, 1):
        print(f"  Reading {f.name} ({i}/{len(files)})  [{time.time() - t0:.1f}s elapsed]")
        df = pl.read_parquet(f)

        for row in df.iter_rows():
            word, decade, tf, doc_freq = row

            if word != current_word:
                if current_word is not None:
                    h = hashlib.md5(current_word.encode("utf-8")).hexdigest()
                    prefix, suffix = h[:2], h[2:]
                    buckets[prefix].append((suffix, peak_tf_decade, peak_df_decade, sum_tf, sum_df))
                    word_count += 1
                    if word_count % 500_000 == 0:
                        print(f"    {word_count:,} words processed  [{time.time() - t0:.1f}s elapsed]")

                current_word = word
                peak_tf_decade = decade
                peak_tf_value = tf
                peak_df_decade = decade
                peak_df_value = doc_freq
                sum_tf = 0
                sum_df = 0
            else:
                if tf > peak_tf_value:
                    peak_tf_decade = decade
                    peak_tf_value = tf
                if doc_freq > peak_df_value:
                    peak_df_decade = decade
                    peak_df_value = doc_freq

            sum_tf += tf
            sum_df += doc_freq

    # flush last word
    if current_word is not None:
        h = hashlib.md5(current_word.encode("utf-8")).hexdigest()
        prefix, suffix = h[:2], h[2:]
        buckets[prefix].append((suffix, peak_tf_decade, peak_df_decade, sum_tf, sum_df))
        word_count += 1

    print(f"  {word_count:,} words processed  [{time.time() - t0:.1f}s elapsed]")
    print(f"  Writing {len(buckets):,} bucket files ...")

    output_dir.mkdir(parents=True, exist_ok=True)

    for prefix, entries in buckets.items():
        sorted_entries = sorted(entries)
        df = pl.DataFrame({
            "hash": [e[0] for e in sorted_entries],
            "peak_tf": [e[1] for e in sorted_entries],
            "peak_df": [e[2] for e in sorted_entries],
            "sum_tf": [e[3] for e in sorted_entries],
            "sum_df": [e[4] for e in sorted_entries],
        })
        df.write_parquet(output_dir / f"{prefix}.parquet")

    elapsed = time.time() - t0
    print()
    print(f"Done: {word_count:,} words -> {len(buckets):,} files in {output_dir}")
    print(f"  Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
