"""Text normalization utilities for gngram-counter.

Handles normalization of Unicode apostrophe variants and other text
transformations to ensure consistent matching against the ngram corpus.

Ported from bnc-lookup normalize.py.
"""

# Unicode characters that should normalize to ASCII apostrophe (U+0027)
# Ordered by likelihood of occurrence in English text
APOSTROPHE_VARIANTS = (
    '\u2019'  # RIGHT SINGLE QUOTATION MARK (most common smart quote)
    '\u2018'  # LEFT SINGLE QUOTATION MARK
    '\u0060'  # GRAVE ACCENT
    '\u00B4'  # ACUTE ACCENT
    '\u201B'  # SINGLE HIGH-REVERSED-9 QUOTATION MARK
    '\u2032'  # PRIME
    '\u2035'  # REVERSED PRIME
    '\u02B9'  # MODIFIER LETTER PRIME
    '\u02BC'  # MODIFIER LETTER APOSTROPHE
    '\u02C8'  # MODIFIER LETTER VERTICAL LINE
    '\u0313'  # COMBINING COMMA ABOVE
    '\u0315'  # COMBINING COMMA ABOVE RIGHT
    '\u055A'  # ARMENIAN APOSTROPHE
    '\u05F3'  # HEBREW PUNCTUATION GERESH
    '\u07F4'  # NKO HIGH TONE APOSTROPHE
    '\u07F5'  # NKO LOW TONE APOSTROPHE
    '\uFF07'  # FULLWIDTH APOSTROPHE
    '\u1FBF'  # GREEK PSILI
    '\u1FBD'  # GREEK KORONIS
    '\uA78C'  # LATIN SMALL LETTER SALTILLO
)

# Pre-compiled translation table for fast apostrophe normalization
_APOSTROPHE_TABLE = str.maketrans({char: "'" for char in APOSTROPHE_VARIANTS})


def normalize_apostrophes(text: str) -> str:
    """Normalize Unicode apostrophe variants to ASCII apostrophe."""
    return text.translate(_APOSTROPHE_TABLE)


def normalize(text: str) -> str:
    """Normalize text for ngram lookup.

    Applies: apostrophe variant conversion, lowercase, strip whitespace.
    """
    return normalize_apostrophes(text).lower().strip()
