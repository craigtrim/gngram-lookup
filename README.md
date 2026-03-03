# gngram-lookup

[![PyPI version](https://badge.fury.io/py/gngram-lookup.svg)](https://badge.fury.io/py/gngram-lookup)
[![Downloads](https://pepy.tech/badge/gngram-lookup)](https://pepy.tech/project/gngram-lookup)
[![Downloads/Month](https://pepy.tech/badge/gngram-lookup/month)](https://pepy.tech/project/gngram-lookup)
[![Tests](https://img.shields.io/badge/tests-194-brightgreen)](https://github.com/craigtrim/gngram-lookup/tree/main/tests)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**How common is this word? O(1) answer. 500 years of books. 5 million words.**

Word frequency, commonness scores, and part-of-speech tags derived from the Google Books Ngram corpus, the largest longitudinal word-frequency dataset ever compiled.

## Quick Start

```bash
pip install gngram-lookup
python -m gngram_lookup.download_data       # frequency data, ~110 MB
python -m gngram_lookup.download_pos_data   # POS tag data, optional
```

```python
import gngram_lookup as ng

# Does this word exist in 500 years of print?
ng.exists('computer')        # True
ng.exists('xyznotaword')     # False

# How common is it? (1=most common, 100=least common)
ng.word_score('the')         # 1
ng.word_score('computer')    # 18
ng.word_score('rucksack')    # 58
ng.word_score('xyznotaword') # None

# Full frequency data
ng.frequency('computer')
# {'peak_tf': 2000, 'peak_df': 2000, 'sum_tf': 892451, 'sum_df': 312876}

# Part-of-speech tags
ng.pos('fast')                        # ['.', 'ADJ', 'ADP', 'ADV', 'CONJ', 'DET', ...]
ng.pos('fast', min_tf=1_000_000)      # ['ADJ', 'ADV', 'NOUN']  — dominant tags only
ng.has_pos('sing', ng.PosTag.VERB)    # True
```

## Features

- **O(1) Lookups** - Hash-bucketed parquet files, no full scan
- **5 Million Words** - Broadest vocabulary coverage of any static lookup package
- **500 Years of Data** - 1500s through 2000s, decade-by-decade
- **Word Score** - 1–100 commonness scale, log-normalized against the corpus
- **Peak Decade** - Know when a word was most used in print
- **POS Tags** - Part-of-speech tags from Google's own tag set
- **Batch Lookup** - Efficient multi-word queries grouped by hash prefix
- **Prefix Clustering** - Find all corpus words sharing a prefix; handles y-drop allomorphs
- **Possessive & Hyphen Fallback** - `ship's` → `ship`, `north-west` → `north`
- **Unicode Normalization** - Smart quotes, accents, and Unicode apostrophes handled

## Word Score Zones

Words are scored 1–100 based on their total corpus frequency, log-normalized against `the` (the most frequent word). The scale compresses the Zipfian spike at the top and gives meaningful resolution across the rest of the vocabulary.

![gngram-lookup Word Score Zones](https://raw.githubusercontent.com/craigtrim/gngram-lookup/main/docs/images/word_score_zones_v7.png)

| Score | Zone | Description | Examples |
|-------|------|-------------|----------|
| 1–5 | ![Zipf](https://img.shields.io/badge/Zipf-3498db?style=flat-square) | Function words dominating millions of books | the, of, and, to, a |
| 6–20 | ![Core](https://img.shields.io/badge/Core-2ecc71?style=flat-square) | Everyday words known by all speakers | computer, walk, beautiful |
| 21–40 | ![Literary](https://img.shields.io/badge/Literary-f39c12?style=flat-square) | Vocabulary of books, not everyday speech | algorithm, philosophy, synthesis |
| 41–60 | ![Specialized](https://img.shields.io/badge/Specialized-e74c3c?style=flat-square) | Domain-specific but attested | rucksack, carbonate, heliotrope |
| 61–80 | ![Rare](https://img.shields.io/badge/Rare-9b59b6?style=flat-square) | Infrequent but legitimate | arcane technical and literary terms |
| 81–100 | ![Long Tail](https://img.shields.io/badge/Long_Tail-e67e22?style=flat-square) | Extremely low frequency | niche, archaic, or highly specialized |

```python
import gngram_lookup as ng

# "the data philosopher defenestrated eigenvalues into petrichor"
ng.word_score('the')            # 1   → Zipf
ng.word_score('data')           # 19  → Core
ng.word_score('philosopher')    # 32  → Literary
ng.word_score('eigenvalue')     # 43  → Specialized
ng.word_score('defenestrated')  # 67  → Rare
ng.word_score('petrichor')      # 82  → Long Tail

# Filter to common words only
def is_common(word):
    score = ng.word_score(word)
    return score is not None and score <= 30
```

## The Problem This Solves

In NLP, you frequently need to know not just whether a token is a word, but **how common it is**.

Not "what does it mean?" Not "what's its etymology?" Just: is this a word real people actually write, and how often?

No other static lookup package gives you this from a corpus spanning 500 years of print at 5 million word coverage with O(1) access.

## Why Google Books Ngrams?

The Google Books Ngram corpus isn't a dictionary (too narrow). It isn't a web crawl (too noisy). It isn't limited to a single decade or language register.

It's **a statistical analysis of over 8 million books** spanning the 1500s to the 2000s, one of the largest datasets ever assembled for studying how language changes over time. The frequency data captures real written usage at a scale no other freely available corpus matches.

If a word appears in this corpus with meaningful frequency, it's a word that real writers actually used.

## When to Use This

- **Vocabulary filtering** - Score words to keep common ones, discard rare ones
- **NLP preprocessing** - Filter candidates before expensive model calls
- **Content analysis** - Measure the reading level or register of a text
- **Spell-check pre-filtering** - Reject low-scoring tokens before fuzzy matching
- **Temporal analysis** - Find when a word peaked in usage
- **POS disambiguation** - Resolve ambiguous tokens using corpus-attested tags

## What This Doesn't Do

- No definitions, synonyms, or semantic relationships (use spaCy or WordNet for that)
- No spell-checking or suggestions (just existence and frequency)
- No real-time or web data (this is a static corpus snapshot)

## CLI

```bash
exists computer       # True, exit 0
exists xyznotaword    # False, exit 1

score computer        # 18
score xyznotaword     # None, exit 1

freq computer
# peak_tf_decade: 2000
# peak_df_decade: 2000
# sum_tf: 892451
# sum_df: 312876

pos fast              # ADJ ADV VERB
pos-freq corn         # ADJ: 1,433,642 / NOUN: 11,722,803 / VERB: 85,411
has-pos sing VERB     # True, exit 0
has-pos fast NOUN     # False, exit 1
```

### Prefix Cluster Script

Show all corpus words sharing a prefix with a given word, ranked by frequency:

```bash
poetry run python scripts/cluster.py happy --sort freq --with-freq --min-tf 100000
# 4 results written to /tmp/cluster_happy.txt
```

## Documentation

- [API Reference](https://github.com/craigtrim/gngram-lookup/blob/main/docs/api.md)
- [CLI Reference](https://github.com/craigtrim/gngram-lookup/blob/main/docs/cli.md)
- [Wordlist and Prefix Clustering](https://github.com/craigtrim/gngram-lookup/blob/main/docs/wordlist.md)
- [Data Format](https://github.com/craigtrim/gngram-lookup/blob/main/docs/data-format.md)
- [Use Cases](https://github.com/craigtrim/gngram-lookup/blob/main/docs/use-cases.md)
- [Development](https://github.com/craigtrim/gngram-lookup/blob/main/docs/development.md)

## Development

```bash
git clone https://github.com/craigtrim/gngram-lookup.git
cd gngram-lookup
make install   # Install dependencies
make test      # Run tests
make all       # Full pipeline
```

## See Also

- **[bnc-lookup](https://pypi.org/project/bnc-lookup/)** - O(1) lookup for British National Corpus (669k words, zero setup)
- **[wordnet-lookup](https://pypi.org/project/wordnet-lookup/)** - O(1) lookup for WordNet

## Attribution

Data derived from the [Google Books Ngram](https://books.google.com/ngrams) dataset.

## License

This package is dual-licensed:
- **Software**: MIT License
- **Ngram Data**: Creative Commons Attribution 3.0 Unported (CC BY 3.0)

See [LICENSE](https://github.com/craigtrim/gngram-lookup/blob/main/LICENSE) for complete terms.

## Links

- **Repository**: [github.com/craigtrim/gngram-lookup](https://github.com/craigtrim/gngram-lookup)
- **PyPI**: [pypi.org/project/gngram-lookup](https://pypi.org/project/gngram-lookup)
- **Author**: Craig Trim ([craigtrim@gmail.com](mailto:craigtrim@gmail.com))
