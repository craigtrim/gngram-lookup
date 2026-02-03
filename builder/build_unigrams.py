"""
Process Google Books 1-gram data into a decade-aggregated Parquet file.

Input:  Tab-delimited file with columns: ngram, year, tf, df
Output: Parquet file with columns: word, decade, tf, df

Words are lowercased, stripped of POS tags, and filtered to pure alpha [a-z].
TF and DF are summed per (word, decade).
"""

import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import polars as pl

ALPHA_RE = re.compile(r"^[a-zA-Z]+$")


def extract_word(ngram: str) -> str | None:
    """Extract the bare word from an ngram token like 'accrued.8_ADP' or 'Adlman'."""
    part = ngram.split("_")[0]
    part = part.split(".")[0]
    if not part or not ALPHA_RE.match(part):
        return None
    return part.lower()


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: python -m builder.build_unigrams <input_dir> <output_dir>")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not input_dir.is_dir():
        print(f"Input directory not found: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    input_files = sorted(f for f in input_dir.iterdir() if f.is_file())
    if not input_files:
        print(f"No files found in {input_dir}")
        sys.exit(1)

    for input_path in input_files:
        output_path = output_dir / (input_path.name + ".parquet")
        process_file(input_path, output_path)


def process_file(input_path: Path, output_path: Path) -> None:
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return

    print(f"Reading {input_path} ...")

    # (word, decade) -> [tf_sum, df_sum]
    agg: dict[tuple[str, int], list[int]] = defaultdict(lambda: [0, 0])

    total = 0
    kept = 0
    skipped = 0
    t0 = time.time()

    with open(input_path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            total += 1
            if total % 5_000_000 == 0:
                elapsed = time.time() - t0
                print(f"  Processing line {total - 4_999_999:,} - {total:,}  [{elapsed:.1f}s elapsed]")

            parts = line.rstrip("\n").split("\t")
            if len(parts) != 4:
                skipped += 1
                continue

            ngram_raw, year_raw, tf_raw, df_raw = parts

            word = extract_word(ngram_raw)
            if word is None:
                skipped += 1
                continue

            try:
                year = int(year_raw)
                tf = int(tf_raw)
                df = int(df_raw)
            except ValueError:
                skipped += 1
                continue

            decade = (year // 10) * 10
            bucket = agg[(word, decade)]
            bucket[0] += tf
            bucket[1] += df
            kept += 1

    print(f"  {total:,} lines total, {kept:,} kept, {skipped:,} skipped")

    words = []
    decades = []
    tfs = []
    dfs = []
    for (word, decade), (tf, df) in sorted(agg.items()):
        words.append(word)
        decades.append(decade)
        tfs.append(tf)
        dfs.append(df)

    df_out = pl.DataFrame({
        "word": words,
        "decade": decades,
        "tf": tfs,
        "df": dfs,
    })

    unique_words = df_out["word"].n_unique()
    print(f"  {df_out.height:,} rows after aggregation")
    print(f"  {unique_words:,} unique words")

    df_out.write_parquet(output_path)

    print(f"Written to {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
