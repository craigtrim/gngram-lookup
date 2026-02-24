# gngram-lookup

[![PyPI version](https://badge.fury.io/py/gngram-lookup.svg)](https://badge.fury.io/py/gngram-lookup)
[![Downloads](https://pepy.tech/badge/gngram-lookup)](https://pepy.tech/project/gngram-lookup)
[![Downloads/Month](https://pepy.tech/badge/gngram-lookup/month)](https://pepy.tech/project/gngram-lookup)
[![Tests](https://img.shields.io/badge/tests-194-brightgreen)](https://github.com/craigtrim/gngram-lookup/tree/main/tests)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

Word frequency and part-of-speech tags from 500 years of books. O(1) lookup. 5 million words.

## Install

```bash
pip install gngram-lookup
python -m gngram_lookup.download_data       # frequency data, ~110 MB
python -m gngram_lookup.download_pos_data   # POS tag data, separate download
```

## Python

```python
import gngram_lookup as ng

ng.exists('computer')       # True
ng.exists('xyznotaword')    # False

ng.frequency('computer')
# {'peak_tf': 2000, 'peak_df': 2000, 'sum_tf': 892451, 'sum_df': 312876}

ng.batch_frequency(['the', 'algorithm', 'xyznotaword'])
# {'the': {...}, 'algorithm': {...}, 'xyznotaword': None}

ng.word_score('the')                     # 1  (most common)
ng.word_score('computer')               # 18
ng.word_score('rucksack')               # 58
ng.word_score('xyznotaword')            # None

ng.pos('fast')                           # ['ADJ', 'ADV', 'VERB']
ng.pos('corn', min_tf=100000)            # ['ADJ', 'NOUN']
ng.pos_freq('corn')                      # {'NOUN': 11722803, 'ADJ': 1433642, ...}
ng.has_pos('sing', ng.PosTag.VERB)       # True
ng.has_pos('sing', ng.PosTag.VERB, min_tf=1000)  # True
```

## CLI

```bash
exists computer       # True, exit 0
exists xyznotaword    # False, exit 1

freq computer
# peak_tf_decade: 2000
# peak_df_decade: 2000
# sum_tf: 892451
# sum_df: 312876

score computer        # 18
pos fast              # ADJ ADV VERB
pos-freq corn         # ADJ: 1,433,642 / NOUN: 11,722,803 / VERB: 85,411
has-pos sing VERB     # True, exit 0
has-pos fast NOUN     # False, exit 1
```

## Docs

- [API Reference](https://github.com/craigtrim/gngram-lookup/blob/main/docs/api.md)
- [CLI Reference](https://github.com/craigtrim/gngram-lookup/blob/main/docs/cli.md)
- [Data Format](https://github.com/craigtrim/gngram-lookup/blob/main/docs/data-format.md)
- [Use Cases](https://github.com/craigtrim/gngram-lookup/blob/main/docs/use-cases.md)
- [Development](https://github.com/craigtrim/gngram-lookup/blob/main/docs/development.md)

## See Also

- [bnc-lookup](https://pypi.org/project/bnc-lookup/) - O(1) lookup for British National Corpus
- [wordnet-lookup](https://pypi.org/project/wordnet-lookup/) - O(1) lookup for WordNet

## Attribution

Data derived from the [Google Books Ngram](https://books.google.com/ngrams) dataset.

## License

Proprietary. See [LICENSE](https://github.com/craigtrim/gngram-lookup/blob/main/LICENSE).
