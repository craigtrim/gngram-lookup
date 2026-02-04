"""
Build hash-bucketed parquet files from source parquet files.

Streams rows from sorted parquet files and writes to consolidated parquet files:

    <output_dir>/xx.parquet

Where xx = first 2 hex chars of MD5 (256 files total).
Each row contains: hash_suffix, peak_tf_decade, peak_df_decade, sum_tf, sum_df

Peak decades are computed using NORMALIZED frequencies (tf/corpus_total) to account
for the larger corpus size in recent decades.

Usage:
    python -m builder.build_hash_files <parquet_dir> <output_dir>
"""

import hashlib
import sys
import time
from collections import defaultdict
from pathlib import Path

import polars as pl

# Minimum corpus size (pages) to consider a decade for peak calculation.
# Decades with fewer pages are skipped to avoid misleadingly high
# normalized frequencies from tiny corpora. 1M pages reached around 1800.
MIN_CORPUS_PAGES = 1_000_000


def load_decade_totals(totalcounts_path: Path) -> dict[int, tuple[int, int]]:
    """Load total corpus counts and aggregate by decade.

    Returns:
        Dict mapping decade -> (total_tf, total_df)
        where total_tf is sum of match_count and total_df is sum of page_count
    """
    decade_tf: dict[int, int] = defaultdict(int)
    decade_df: dict[int, int] = defaultdict(int)

    with open(totalcounts_path, "r") as f:
        content = f.read().strip()

    # Format: tab-separated entries like "year,match_count,page_count,volume_count"
    entries = content.split("\t")
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(",")
        if len(parts) != 4:
            continue
        try:
            year = int(parts[0])
            match_count = int(parts[1])
            page_count = int(parts[2])
        except ValueError:
            continue

        decade = (year // 10) * 10
        decade_tf[decade] += match_count
        decade_df[decade] += page_count

    return {d: (decade_tf[d], decade_df[d]) for d in decade_tf}


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python -m builder.build_hash_files <parquet_dir> <output_dir>")
        sys.exit(1)

    parquet_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not parquet_dir.is_dir():
        print(f"Directory not found: {parquet_dir}")
        sys.exit(1)

    # Load corpus totals for normalization
    totalcounts_path = Path(__file__).parent / "totalcounts.txt"
    if not totalcounts_path.exists():
        print(f"Total counts file not found: {totalcounts_path}")
        print("Download from: https://storage.googleapis.com/books/ngrams/books/20200217/eng/totalcounts-1")
        sys.exit(1)

    print("Loading corpus totals for normalization...")
    decade_totals = load_decade_totals(totalcounts_path)
    print(f"  Loaded totals for {len(decade_totals)} decades")
    for decade in sorted(decade_totals.keys())[-5:]:
        tf_total, df_total = decade_totals[decade]
        print(f"    {decade}: tf={tf_total:,}, df={df_total:,}")

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
    peak_tf_normalized = 0.0  # Normalized frequency for comparison
    peak_df_decade = 0
    peak_df_normalized = 0.0  # Normalized frequency for comparison
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
                # Get corpus totals for this decade
                corpus_tf, corpus_df = decade_totals.get(decade, (1, 1))
                # Skip decades with tiny corpus for peak calculation
                if corpus_df >= MIN_CORPUS_PAGES:
                    peak_tf_normalized = tf / corpus_tf if corpus_tf > 0 else 0
                    peak_df_normalized = doc_freq / corpus_df if corpus_df > 0 else 0
                    peak_tf_decade = decade
                    peak_df_decade = decade
                else:
                    peak_tf_normalized = 0.0
                    peak_df_normalized = 0.0
                    peak_tf_decade = 0
                    peak_df_decade = 0
                sum_tf = 0
                sum_df = 0
            else:
                # Get corpus totals for this decade
                corpus_tf, corpus_df = decade_totals.get(decade, (1, 1))
                # Only consider decades with sufficient corpus for peak calculation
                if corpus_df >= MIN_CORPUS_PAGES:
                    # Normalize and compare
                    tf_normalized = tf / corpus_tf if corpus_tf > 0 else 0
                    df_normalized = doc_freq / corpus_df if corpus_df > 0 else 0

                    if tf_normalized > peak_tf_normalized:
                        peak_tf_decade = decade
                        peak_tf_normalized = tf_normalized
                    if df_normalized > peak_df_normalized:
                        peak_df_decade = decade
                        peak_df_normalized = df_normalized

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
