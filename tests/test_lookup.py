"""
Comprehensive tests for gngram_counter lookup functions.

Tests cover:
- Positive outcomes (found words, valid data)
- Negative outcomes (missing words)
- Edge cases (empty strings, special chars, unicode)
- Error handling (data not installed)
"""

import pytest

from gngram_counter import is_data_installed
from gngram_counter.lookup import _hash_word


# Skip all data-dependent tests if data is not installed
DATA_INSTALLED = is_data_installed()
requires_data = pytest.mark.skipif(
    not DATA_INSTALLED,
    reason="Data files not installed. Run: python -m gngram_counter.download_data",
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


@requires_data
class TestExists:
    """Tests for the exists() function."""

    def test_exists_common_word(self):
        from gngram_counter import exists

        assert exists("the") is True

    def test_exists_another_common_word(self):
        from gngram_counter import exists

        assert exists("and") is True

    def test_exists_case_insensitive_upper(self):
        from gngram_counter import exists

        assert exists("THE") is True

    def test_exists_case_insensitive_mixed(self):
        from gngram_counter import exists

        assert exists("ThE") is True

    def test_exists_nonexistent_word(self):
        from gngram_counter import exists

        assert exists("xyznotarealword123") is False

    def test_exists_gibberish(self):
        from gngram_counter import exists

        assert exists("asdfghjkl") is False

    def test_exists_empty_string(self):
        from gngram_counter import exists

        assert exists("") is False

    def test_exists_whitespace_only(self):
        from gngram_counter import exists

        assert exists("   ") is False

    def test_exists_with_numbers(self):
        from gngram_counter import exists

        # Pure numbers shouldn't be in word corpus
        assert exists("12345") is False

    def test_exists_special_chars(self):
        from gngram_counter import exists

        assert exists("!@#$%") is False


@requires_data
class TestFrequency:
    """Tests for the frequency() function."""

    def test_frequency_common_word_returns_dict(self):
        from gngram_counter import frequency

        result = frequency("the")
        assert result is not None
        assert isinstance(result, dict)

    def test_frequency_has_required_keys(self):
        from gngram_counter import frequency

        result = frequency("the")
        assert result is not None
        assert "peak_tf" in result
        assert "peak_df" in result
        assert "sum_tf" in result
        assert "sum_df" in result

    def test_frequency_values_are_integers(self):
        from gngram_counter import frequency

        result = frequency("the")
        assert result is not None
        assert isinstance(result["peak_tf"], int)
        assert isinstance(result["peak_df"], int)
        assert isinstance(result["sum_tf"], int)
        assert isinstance(result["sum_df"], int)

    def test_frequency_values_are_positive(self):
        from gngram_counter import frequency

        result = frequency("the")
        assert result is not None
        assert result["sum_tf"] > 0
        assert result["sum_df"] > 0

    def test_frequency_peak_decades_are_valid(self):
        from gngram_counter import frequency

        result = frequency("the")
        assert result is not None
        # Decades should be in a reasonable range
        assert 1500 <= result["peak_tf"] <= 2020
        assert 1500 <= result["peak_df"] <= 2020

    def test_frequency_case_insensitive(self):
        from gngram_counter import frequency

        result_lower = frequency("hello")
        result_upper = frequency("HELLO")
        assert result_lower == result_upper

    def test_frequency_nonexistent_word_returns_none(self):
        from gngram_counter import frequency

        result = frequency("xyznotarealword123")
        assert result is None

    def test_frequency_empty_string_returns_none(self):
        from gngram_counter import frequency

        result = frequency("")
        assert result is None

    def test_frequency_whitespace_returns_none(self):
        from gngram_counter import frequency

        result = frequency("   ")
        assert result is None

    def test_frequency_special_chars_returns_none(self):
        from gngram_counter import frequency

        result = frequency("!@#$%^&*()")
        assert result is None


@requires_data
class TestBatchFrequency:
    """Tests for the batch_frequency() function."""

    def test_batch_frequency_returns_dict(self):
        from gngram_counter import batch_frequency

        result = batch_frequency(["the", "and"])
        assert isinstance(result, dict)

    def test_batch_frequency_contains_all_words(self):
        from gngram_counter import batch_frequency

        words = ["the", "and", "notaword123"]
        result = batch_frequency(words)
        for word in words:
            assert word in result

    def test_batch_frequency_found_words_have_data(self):
        from gngram_counter import batch_frequency

        result = batch_frequency(["the", "and"])
        assert result["the"] is not None
        assert result["and"] is not None

    def test_batch_frequency_missing_words_are_none(self):
        from gngram_counter import batch_frequency

        result = batch_frequency(["xyznotarealword123"])
        assert result["xyznotarealword123"] is None

    def test_batch_frequency_mixed_results(self):
        from gngram_counter import batch_frequency

        result = batch_frequency(["the", "xyznotarealword123", "and"])
        assert result["the"] is not None
        assert result["xyznotarealword123"] is None
        assert result["and"] is not None

    def test_batch_frequency_empty_list(self):
        from gngram_counter import batch_frequency

        result = batch_frequency([])
        assert result == {}

    def test_batch_frequency_single_word(self):
        from gngram_counter import batch_frequency

        result = batch_frequency(["the"])
        assert len(result) == 1
        assert "the" in result

    def test_batch_frequency_duplicate_words(self):
        from gngram_counter import batch_frequency

        result = batch_frequency(["the", "the", "the"])
        # Should handle duplicates (last wins or deduped)
        assert "the" in result

    def test_batch_frequency_case_preserved_in_keys(self):
        from gngram_counter import batch_frequency

        result = batch_frequency(["THE", "And", "hello"])
        # Keys should match input case
        assert "THE" in result
        assert "And" in result
        assert "hello" in result

    def test_batch_frequency_large_batch(self):
        from gngram_counter import batch_frequency

        # Test with a larger batch
        words = ["word" + str(i) for i in range(100)]
        words.extend(["the", "and", "is", "a"])
        result = batch_frequency(words)
        assert len(result) == len(words)

    def test_batch_frequency_data_structure(self):
        from gngram_counter import batch_frequency

        result = batch_frequency(["the"])
        data = result["the"]
        assert data is not None
        assert "peak_tf" in data
        assert "peak_df" in data
        assert "sum_tf" in data
        assert "sum_df" in data


class TestDataNotInstalled:
    """Tests for behavior when data is not installed."""

    def test_is_data_installed_returns_bool(self):
        result = is_data_installed()
        assert isinstance(result, bool)


@requires_data
class TestEdgeCases:
    """Tests for edge cases and unusual inputs."""

    def test_unicode_word(self):
        from gngram_counter import exists, frequency

        # Unicode characters - may or may not exist
        result = exists("café")
        assert isinstance(result, bool)
        freq = frequency("café")
        assert freq is None or isinstance(freq, dict)

    def test_very_long_word(self):
        from gngram_counter import exists, frequency

        long_word = "a" * 1000
        assert exists(long_word) is False
        assert frequency(long_word) is None

    def test_single_character(self):
        from gngram_counter import exists, frequency

        # Single letters like 'a' and 'i' should exist
        result_a = exists("a")
        result_i = exists("i")
        # At least one of these common single-letter words should exist
        assert result_a or result_i

    def test_hyphenated_word(self):
        from gngram_counter import exists

        # Hyphenated words may or may not be in corpus
        result = exists("self-aware")
        assert isinstance(result, bool)

    def test_word_with_apostrophe(self):
        from gngram_counter import exists

        # Words with apostrophes may or may not be in corpus
        result = exists("don't")
        assert isinstance(result, bool)

    def test_numeric_string(self):
        from gngram_counter import exists, frequency

        assert exists("123") is False
        assert frequency("456") is None

    def test_mixed_alphanumeric(self):
        from gngram_counter import exists

        result = exists("test123")
        assert isinstance(result, bool)


@requires_data
class TestCaching:
    """Tests to verify caching behavior works correctly."""

    def test_repeated_lookups_same_result(self):
        from gngram_counter import frequency

        result1 = frequency("the")
        result2 = frequency("the")
        assert result1 == result2

    def test_multiple_words_same_bucket(self):
        from gngram_counter import batch_frequency

        # Multiple lookups should work consistently
        result1 = batch_frequency(["the", "and", "is"])
        result2 = batch_frequency(["the", "and", "is"])
        assert result1 == result2

    def test_alternating_exists_and_frequency(self):
        from gngram_counter import exists, frequency

        # Mixing function calls should work correctly
        assert exists("the") is True
        freq = frequency("the")
        assert freq is not None
        assert exists("the") is True
