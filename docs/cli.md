# CLI Reference

## Commands

### `score`

Get the 1–100 commonness score for a word (1 = most common, 100 = least common).

```bash
score computer
# Output: 18
# Exit code: 0

score xyznotaword
# Output: None
# Exit code: 1
```

### `exists`

Check if a word exists in the corpus.

```bash
exists computer
# Output: True
# Exit code: 0

exists xyznotaword
# Output: False
# Exit code: 1
```

Use in shell scripts:

```bash
if exists "$word"; then
    echo "$word is a real word"
fi
```

### `freq`

Get frequency data for a word.

```bash
freq computer
# Output:
# peak_tf_decade: 2000
# peak_df_decade: 2000
# sum_tf: 892451
# sum_df: 312876
```

Exit code is 1 if word not found:

```bash
freq xyznotaword
# Output: None
# Exit code: 1
```

### `pos`

Get all attested part-of-speech tags for a word. Tags are space-separated.

```bash
pos fast
# Output: ADJ ADV VERB
# Exit code: 0

pos sing
# Output: VERB
# Exit code: 0

pos xyznotaword
# Output: None
# Exit code: 1
```

Requires POS data to be installed first:

```bash
python -m gngram_lookup.download_pos_data
```

### `pos-freq`

Get all attested POS tags for a word along with their cumulative corpus frequencies.

```bash
pos-freq corn
# Output:
# ADJ: 1,433,642
# NOUN: 11,722,803
# VERB: 85,411
# Exit code: 0

pos-freq xyznotaword
# Output: None
# Exit code: 1
```

### `has-pos`

Check if a word is attested with a specific POS tag.

```bash
has-pos sing VERB
# Output: True
# Exit code: 0

has-pos fast NOUN
# Output: False
# Exit code: 1
```

Valid tags: `NOUN VERB ADJ ADV PRON DET ADP NUM CONJ PRT X`

Use in shell scripts:

```bash
if has-pos "$word" VERB; then
    echo "$word can be a verb"
fi
```

### `scripts/cluster.py`

Show all corpus words sharing a prefix with a given root word. Output is written to a file; the path is printed to stdout on completion.

```bash
poetry run python scripts/cluster.py <word> [--sort alpha|freq] [--with-freq] [--min-tf N] [--output PATH]
```

**Options**

| Option | Default | Description |
|--------|---------|-------------|
| `--sort alpha` | default | Alphabetical order |
| `--sort freq` | | Descending corpus frequency |
| `--with-freq` | off | Write frequency alongside each word |
| `--min-tf N` | `0` | Skip words with corpus frequency below N |
| `--output PATH` | `/tmp/cluster_<word>.txt` | Output file or directory |

If `--output` points to a directory (or ends with `/`), the file `cluster_<word>.txt` is created inside it. If omitted, output goes to `/tmp/cluster_<word>.txt`.

**Examples**

```bash
# Alphabetical, default output location
poetry run python scripts/cluster.py drink
# 47 results written to /tmp/cluster_drink.txt

# Ranked by frequency, with counts, noise filtered
poetry run python scripts/cluster.py happy --sort freq --with-freq --min-tf 100000
# 4 results written to /tmp/cluster_happy.txt

# Custom output file
poetry run python scripts/cluster.py happy --output /tmp/my-output.txt

# Custom output directory
poetry run python scripts/cluster.py happy --output /tmp/mydir/
# 47 results written to /tmp/mydir/cluster_happy.txt
```

The output file for `--sort freq --with-freq` looks like:

```
happiness    31,414,547
happily       9,336,058
happier       4,460,678
happiest      2,393,091
```

The y-drop allomorphic alternation is handled automatically. For a root ending in `-y`, the script also scans the stem and accepts continuations with `y` or `i`:

```bash
poetry run python scripts/cluster.py mercy --sort freq --with-freq --min-tf 10000
# 4 results written to /tmp/cluster_mercy.txt
```

### `python -m gngram_lookup.download_data`

Download frequency data files (~110 MB). Required before first use of frequency/exists functions.

```bash
python -m gngram_lookup.download_data
```

Data is stored in `~/.gngram-lookup/data/`.

### `python -m gngram_lookup.download_pos_data`

Download POS tag data files. Required before first use of `pos`/`has-pos` functions.

```bash
python -m gngram_lookup.download_pos_data
```

Data is stored in `~/.gngram-lookup/pos-data/`.
