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
from gngram_counter.lookup import _hash_word


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
        assert exists("asdfghjkl") is False

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
        # Words with apostrophes may or may not be in corpus
        result = exists("don't")
        assert isinstance(result, bool)

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
