from gngram_lookup import batch_frequency


class TestBatchFrequency:
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
        assert "the" in result

    def test_batch_frequency_case_preserved_in_keys(self):
        result = batch_frequency(["THE", "And", "hello"])
        assert "THE" in result
        assert "And" in result
        assert "hello" in result

    def test_batch_frequency_large_batch(self):
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
