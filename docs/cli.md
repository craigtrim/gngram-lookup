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
