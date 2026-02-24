from gngram_lookup import batch_frequency, exists, frequency


class TestFrequencyCaching:
    def test_repeated_lookups_same_result(self):
        result1 = frequency("the")
        result2 = frequency("the")
        assert result1 == result2

    def test_multiple_words_same_bucket(self):
        result1 = batch_frequency(["the", "and", "is"])
        result2 = batch_frequency(["the", "and", "is"])
        assert result1 == result2

    def test_alternating_exists_and_frequency(self):
        assert exists("the") is True
        freq = frequency("the")
        assert freq is not None
        assert exists("the") is True
