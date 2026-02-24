# Word Score Band Analysis

Computed across all 5,001,090 words in the corpus (256 hash-bucketed parquet files).

Total corpus TF: 762,749,334,921

## Band Distribution

| Score | Zone | Unique Words | % of Words | Corpus TF | % of TF |
|-------|------|-------------|------------|-----------|---------|
| 1–5 | Zipf | 8 | 0.0% | 175,023,776,288 | 22.9% |
| 6–20 | Core | 376 | 0.0% | 262,455,213,676 | 34.4% |
| 21–40 | Literary | 21,381 | 0.4% | 282,877,391,975 | 37.1% |
| 41–60 | Specialized | 285,077 | 5.7% | 37,531,627,154 | 4.9% |
| 61–80 | Rare | 3,864,358 | 77.3% | 4,804,176,600 | 0.6% |
| 81–100 | Long Tail | 829,890 | 16.6% | 57,149,228 | 0.0% |

## Key Findings

**21,765 words account for 94.4% of all corpus token frequency.**

That is: Zipf + Core + Literary combined — 0.4% of the vocabulary — covers nearly all of what you will ever read in print.

**The Rare band contains 77.3% of unique word types but only 0.6% of TF.**

Most of the vocabulary by headcount is words that almost nobody ever writes. This is the long tail of the Zipfian distribution playing out at scale.

**The 8 Zipf words alone account for 22.9% of everything ever printed** (in the Google Books corpus). They are: `the`, `of`, `and`, `to`, `a`, `in`, `is`, `that` (approximate — exact set depends on lowercase normalization).

## Implications for Filtering

If you are filtering NLP tokens and want to keep only "real" vocabulary:

- **Score ≤ 40** catches 94.4% of corpus TF with just 21,765 word types
- **Score ≤ 20** catches 57.3% of corpus TF with just 384 word types
- **Score ≤ 60** catches 99.3% of corpus TF, covering 306,842 word types

The cutoff at 40 (Literary boundary) is a natural inflection point — below it, you have the high-frequency working vocabulary of print; above it, you have the long tail.
