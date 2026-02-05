"""
Comprehensive tests for gngram_counter lookup functions.

Tests cover:
- Positive outcomes (found words, valid data)
- Negative outcomes (missing words)
- Edge cases (empty strings, special chars, unicode)
"""

from gngram_counter import (
    batch_frequency,
    exists,
    frequency,
    is_data_installed,
)
from gngram_counter.lookup import (
    S_CONTRACTION_STEMS,
    _hash_word,
    _split_contraction,
)
from gngram_counter.normalize import normalize, normalize_apostrophes


class TestDataInstallation:
    """First test: verify data is installed."""

    def test_data_is_installed(self):
        """Data must be installed to run tests."""
        assert is_data_installed(), (
            "Data files not installed. "
            "Run: python -m gngram_counter.download_data"
        )


class TestHashWord:
    """Tests for the internal _hash_word function."""

    def test_hash_word_returns_tuple(self):
        prefix, suffix = _hash_word("test")
        assert isinstance(prefix, str)
        assert isinstance(suffix, str)

    def test_hash_word_prefix_length(self):
        prefix, suffix = _hash_word("example")
        assert len(prefix) == 2

    def test_hash_word_suffix_length(self):
        prefix, suffix = _hash_word("example")
        assert len(suffix) == 30

    def test_hash_word_lowercase(self):
        """Hash should be case-insensitive."""
        assert _hash_word("TEST") == _hash_word("test")
        assert _hash_word("TeSt") == _hash_word("test")

    def test_hash_word_consistent(self):
        """Same word should always produce same hash."""
        assert _hash_word("hello") == _hash_word("hello")

    def test_hash_word_different_words(self):
        """Different words should produce different hashes."""
        assert _hash_word("hello") != _hash_word("world")

    def test_hash_word_curly_apostrophe_normalizes(self):
        """Curly apostrophe should hash identically to ASCII apostrophe."""
        assert _hash_word("don't") == _hash_word("don\u2019t")

    def test_hash_word_whitespace_stripped(self):
        """Leading/trailing whitespace should be stripped before hashing."""
        assert _hash_word("  hello  ") == _hash_word("hello")


class TestExists:
    """Tests for the exists() function."""

    def test_exists_common_word(self):
        assert exists("the") is True

    def test_exists_another_common_word(self):
        assert exists("and") is True

    def test_exists_case_insensitive_upper(self):
        assert exists("THE") is True

    def test_exists_case_insensitive_mixed(self):
        assert exists("ThE") is True

    def test_exists_nonexistent_word(self):
        assert exists("xyznotarealword123") is False

    def test_exists_gibberish(self):
        # Use a truly random string unlikely to be in corpus
        assert exists("qzxjkvwpy") is False

    def test_exists_empty_string(self):
        assert exists("") is False

    def test_exists_whitespace_only(self):
        assert exists("   ") is False

    def test_exists_with_numbers(self):
        # Pure numbers shouldn't be in word corpus
        assert exists("12345") is False

    def test_exists_special_chars(self):
        assert exists("!@#$%") is False


class TestFrequency:
    """Tests for the frequency() function."""

    def test_frequency_common_word_returns_dict(self):
        result = frequency("the")
        assert result is not None
        assert isinstance(result, dict)

    def test_frequency_has_required_keys(self):
        result = frequency("the")
        assert result is not None
        assert "peak_tf" in result
        assert "peak_df" in result
        assert "sum_tf" in result
        assert "sum_df" in result

    def test_frequency_values_are_integers(self):
        result = frequency("the")
        assert result is not None
        assert isinstance(result["peak_tf"], int)
        assert isinstance(result["peak_df"], int)
        assert isinstance(result["sum_tf"], int)
        assert isinstance(result["sum_df"], int)

    def test_frequency_values_are_positive(self):
        result = frequency("the")
        assert result is not None
        assert result["sum_tf"] > 0
        assert result["sum_df"] > 0

    def test_frequency_peak_decades_are_valid(self):
        result = frequency("the")
        assert result is not None
        # Decades should be in a reasonable range
        assert 1500 <= result["peak_tf"] <= 2020
        assert 1500 <= result["peak_df"] <= 2020

    def test_frequency_case_insensitive(self):
        result_lower = frequency("hello")
        result_upper = frequency("HELLO")
        assert result_lower == result_upper

    def test_frequency_nonexistent_word_returns_none(self):
        result = frequency("xyznotarealword123")
        assert result is None

    def test_frequency_empty_string_returns_none(self):
        result = frequency("")
        assert result is None

    def test_frequency_whitespace_returns_none(self):
        result = frequency("   ")
        assert result is None

    def test_frequency_special_chars_returns_none(self):
        result = frequency("!@#$%^&*()")
        assert result is None


class TestBatchFrequency:
    """Tests for the batch_frequency() function."""

    def test_batch_frequency_returns_dict(self):
        result = batch_frequency(["the", "and"])
        assert isinstance(result, dict)

    def test_batch_frequency_contains_all_words(self):
        words = ["the", "and", "notaword123"]
        result = batch_frequency(words)
        for word in words:
            assert word in result

    def test_batch_frequency_found_words_have_data(self):
        result = batch_frequency(["the", "and"])
        assert result["the"] is not None
        assert result["and"] is not None

    def test_batch_frequency_missing_words_are_none(self):
        result = batch_frequency(["xyznotarealword123"])
        assert result["xyznotarealword123"] is None

    def test_batch_frequency_mixed_results(self):
        result = batch_frequency(["the", "xyznotarealword123", "and"])
        assert result["the"] is not None
        assert result["xyznotarealword123"] is None
        assert result["and"] is not None

    def test_batch_frequency_empty_list(self):
        result = batch_frequency([])
        assert result == {}

    def test_batch_frequency_single_word(self):
        result = batch_frequency(["the"])
        assert len(result) == 1
        assert "the" in result

    def test_batch_frequency_duplicate_words(self):
        result = batch_frequency(["the", "the", "the"])
        # Should handle duplicates (last wins or deduped)
        assert "the" in result

    def test_batch_frequency_case_preserved_in_keys(self):
        result = batch_frequency(["THE", "And", "hello"])
        # Keys should match input case
        assert "THE" in result
        assert "And" in result
        assert "hello" in result

    def test_batch_frequency_large_batch(self):
        # Test with a larger batch
        words = ["word" + str(i) for i in range(100)]
        words.extend(["the", "and", "is", "a"])
        result = batch_frequency(words)
        assert len(result) == len(words)

    def test_batch_frequency_data_structure(self):
        result = batch_frequency(["the"])
        data = result["the"]
        assert data is not None
        assert "peak_tf" in data
        assert "peak_df" in data
        assert "sum_tf" in data
        assert "sum_df" in data


class TestEdgeCases:
    """Tests for edge cases and unusual inputs."""

    def test_unicode_word(self):
        # Unicode characters - may or may not exist
        result = exists("café")
        assert isinstance(result, bool)
        freq = frequency("café")
        assert freq is None or isinstance(freq, dict)

    def test_very_long_word(self):
        long_word = "a" * 1000
        assert exists(long_word) is False
        assert frequency(long_word) is None

    def test_single_character(self):
        # Single letters like 'a' and 'i' should exist
        result_a = exists("a")
        result_i = exists("i")
        # At least one of these common single-letter words should exist
        assert result_a or result_i

    def test_hyphenated_word(self):
        # Hyphenated words may or may not be in corpus
        result = exists("self-aware")
        assert isinstance(result, bool)

    def test_word_with_apostrophe(self):
        # Contractions resolve via fallback (split into components)
        assert exists("don't") is True
        assert exists("we'll") is True
        assert exists("they're") is True

    def test_word_with_curly_apostrophe(self):
        # Unicode RIGHT SINGLE QUOTATION MARK (U+2019) should normalize
        assert exists("don\u2019t") is True
        assert exists("we\u2019ll") is True

    def test_numeric_string(self):
        assert exists("123") is False
        assert frequency("456") is None

    def test_mixed_alphanumeric(self):
        result = exists("test123")
        assert isinstance(result, bool)


class TestCaching:
    """Tests to verify caching behavior works correctly."""

    def test_repeated_lookups_same_result(self):
        result1 = frequency("the")
        result2 = frequency("the")
        assert result1 == result2

    def test_multiple_words_same_bucket(self):
        # Multiple lookups should work consistently
        result1 = batch_frequency(["the", "and", "is"])
        result2 = batch_frequency(["the", "and", "is"])
        assert result1 == result2

    def test_alternating_exists_and_frequency(self):
        # Mixing function calls should work correctly
        assert exists("the") is True
        freq = frequency("the")
        assert freq is not None
        assert exists("the") is True


class TestNormalize:
    """Tests for text normalization."""

    def test_normalize_ascii_apostrophe(self):
        assert normalize("don't") == "don't"

    def test_normalize_curly_right(self):
        assert normalize("don\u2019t") == "don't"

    def test_normalize_curly_left(self):
        assert normalize("don\u2018t") == "don't"

    def test_normalize_grave_accent(self):
        assert normalize("don\u0060t") == "don't"

    def test_normalize_acute_accent(self):
        assert normalize("don\u00B4t") == "don't"

    def test_normalize_prime(self):
        assert normalize("don\u2032t") == "don't"

    def test_normalize_reversed_prime(self):
        assert normalize("don\u2035t") == "don't"

    def test_normalize_modifier_letter_apostrophe(self):
        assert normalize("don\u02BCt") == "don't"

    def test_normalize_fullwidth_apostrophe(self):
        assert normalize("don\uFF07t") == "don't"

    def test_normalize_high_reversed_9(self):
        assert normalize("don\u201Bt") == "don't"

    def test_normalize_modifier_letter_prime(self):
        assert normalize("don\u02B9t") == "don't"

    def test_normalize_lowercase(self):
        assert normalize("DON'T") == "don't"

    def test_normalize_strip(self):
        assert normalize("  hello  ") == "hello"

    def test_normalize_combined_curly_upper_whitespace(self):
        assert normalize("  DON\u2019T  ") == "don't"

    def test_normalize_empty_string(self):
        assert normalize("") == ""

    def test_normalize_no_apostrophes_passthrough(self):
        assert normalize("hello") == "hello"

    def test_normalize_apostrophes_only(self):
        result = normalize_apostrophes("we\u2019ll")
        assert result == "we'll"

    def test_normalize_apostrophes_preserves_case(self):
        result = normalize_apostrophes("DON\u2019T")
        assert result == "DON'T"

    def test_normalize_apostrophes_no_change(self):
        result = normalize_apostrophes("don't")
        assert result == "don't"

    def test_normalize_apostrophes_empty(self):
        assert normalize_apostrophes("") == ""


class TestSplitContraction:
    """Tests for _split_contraction."""

    def test_split_nt(self):
        assert _split_contraction("don't") == ("do", "n't")

    def test_split_ll(self):
        assert _split_contraction("we'll") == ("we", "'ll")

    def test_split_re(self):
        assert _split_contraction("they're") == ("they", "'re")

    def test_split_ve(self):
        assert _split_contraction("i've") == ("i", "'ve")

    def test_split_m(self):
        assert _split_contraction("i'm") == ("i", "'m")

    def test_split_d(self):
        assert _split_contraction("i'd") == ("i", "'d")

    def test_split_s_all_allowlist_stems(self):
        # Every stem in S_CONTRACTION_STEMS should split
        for stem in S_CONTRACTION_STEMS:
            word = f"{stem}'s"
            result = _split_contraction(word)
            assert result == (stem, "'s"), f"Failed for {word!r}"

    def test_split_s_possessive_rejected(self):
        # Possessives should NOT split
        for possessive in ("dog's", "john's", "cat's", "king's", "mother's"):
            assert _split_contraction(possessive) is None, (
                f"{possessive!r} should not split"
            )

    def test_split_regular_word(self):
        assert _split_contraction("hello") is None

    def test_split_empty(self):
        assert _split_contraction("") is None

    def test_split_suffix_only_no_stem(self):
        # Suffix alone should return None (empty stem)
        assert _split_contraction("'ll") is None
        assert _split_contraction("'re") is None
        assert _split_contraction("'ve") is None
        assert _split_contraction("'m") is None
        assert _split_contraction("'d") is None
        assert _split_contraction("n't") is None

    def test_split_nt_various_stems(self):
        assert _split_contraction("won't") == ("wo", "n't")
        assert _split_contraction("can't") == ("ca", "n't")
        assert _split_contraction("isn't") == ("is", "n't")
        assert _split_contraction("wasn't") == ("was", "n't")

    def test_split_ll_various_stems(self):
        assert _split_contraction("i'll") == ("i", "'ll")
        assert _split_contraction("they'll") == ("they", "'ll")
        assert _split_contraction("she'll") == ("she", "'ll")


class TestContractionFallback:
    """Tests for contraction fallback in exists() and frequency()."""

    def test_exists_dont(self):
        assert exists("don't") is True

    def test_exists_wont(self):
        assert exists("won't") is True

    def test_exists_cant(self):
        assert exists("can't") is True

    def test_exists_well(self):
        assert exists("we'll") is True

    def test_exists_theyre(self):
        assert exists("they're") is True

    def test_exists_ive(self):
        assert exists("i've") is True

    def test_exists_im(self):
        assert exists("i'm") is True

    def test_exists_id(self):
        assert exists("i'd") is True

    def test_exists_thats(self):
        # The original reported issue
        assert exists("that's") is True

    def test_exists_its(self):
        assert exists("it's") is True

    def test_exists_hes(self):
        assert exists("he's") is True

    def test_exists_shes(self):
        assert exists("she's") is True

    def test_exists_theres(self):
        assert exists("there's") is True

    def test_exists_whats(self):
        assert exists("what's") is True

    def test_exists_lets(self):
        assert exists("let's") is True

    def test_exists_possessive_not_split(self):
        # Possessives should NOT be split — "dog's" stays as-is
        # (will be False since "dog's" isn't in the corpus directly)
        result = exists("dog's")
        assert isinstance(result, bool)

    # --- Case-insensitive contractions ---

    def test_exists_uppercase_contraction(self):
        assert exists("DON'T") is True

    def test_exists_mixed_case_contraction(self):
        assert exists("Don't") is True

    def test_exists_uppercase_s_contraction(self):
        assert exists("THAT'S") is True

    # --- Curly apostrophe through 's contractions ---

    def test_exists_curly_thats(self):
        assert exists("that\u2019s") is True

    def test_exists_curly_its(self):
        assert exists("it\u2019s") is True

    # --- frequency() for contractions ---

    def test_frequency_dont(self):
        result = frequency("don't")
        assert result is not None
        assert result["sum_tf"] > 0

    def test_frequency_well(self):
        result = frequency("we'll")
        assert result is not None
        assert result["sum_tf"] > 0

    def test_frequency_thats(self):
        result = frequency("that's")
        assert result is not None
        assert result["sum_tf"] > 0

    def test_frequency_its(self):
        result = frequency("it's")
        assert result is not None
        assert result["sum_tf"] > 0

    def test_frequency_curly_apostrophe(self):
        result = frequency("don\u2019t")
        assert result is not None
        assert result["sum_tf"] > 0

    def test_frequency_contraction_has_valid_structure(self):
        result = frequency("don't")
        assert result is not None
        assert "peak_tf" in result
        assert "peak_df" in result
        assert "sum_tf" in result
        assert "sum_df" in result
        assert isinstance(result["peak_tf"], int)
        assert isinstance(result["sum_tf"], int)

    def test_frequency_possessive_returns_none(self):
        # "dog's" is not in allowlist, not a recognized contraction
        assert frequency("dog's") is None

    # --- Consistency: contraction frequency == stem frequency ---

    def test_frequency_contraction_equals_stem(self):
        # "don't" fallback returns "do" frequency
        assert frequency("don't") == frequency("do")

    def test_frequency_s_contraction_equals_stem(self):
        # "that's" fallback returns "that" frequency
        assert frequency("that's") == frequency("that")

    def test_frequency_curly_equals_ascii(self):
        # Normalization equivalence
        assert frequency("don\u2019t") == frequency("don't")

    # --- exists/frequency agreement ---

    def test_exists_frequency_agree_for_contraction(self):
        for word in ("don't", "we'll", "that's", "it's"):
            e = exists(word)
            f = frequency(word)
            if e:
                assert f is not None, f"exists=True but frequency=None for {word!r}"
            else:
                assert f is None, f"exists=False but frequency!=None for {word!r}"

    # --- batch_frequency ---

    def test_batch_frequency_contractions(self):
        words = ["don't", "we'll", "the", "xyznotaword"]
        result = batch_frequency(words)
        assert result["don't"] is not None
        assert result["we'll"] is not None
        assert result["the"] is not None
        assert result["xyznotaword"] is None

    def test_batch_frequency_curly_apostrophe(self):
        result = batch_frequency(["don\u2019t", "we\u2019ll"])
        assert result["don\u2019t"] is not None
        assert result["we\u2019ll"] is not None

    def test_batch_frequency_s_contractions(self):
        result = batch_frequency(["that's", "it's", "where's"])
        assert result["that's"] is not None
        assert result["it's"] is not None
        assert result["where's"] is not None

    def test_batch_frequency_case_preserved_for_contractions(self):
        result = batch_frequency(["DON'T", "That's"])
        assert "DON'T" in result
        assert "That's" in result
        assert result["DON'T"] is not None
        assert result["That's"] is not None

    def test_batch_frequency_matches_individual_frequency(self):
        words = ["don't", "that's", "we'll"]
        batch_result = batch_frequency(words)
        for word in words:
            assert batch_result[word] == frequency(word), (
                f"batch != individual for {word!r}"
            )
