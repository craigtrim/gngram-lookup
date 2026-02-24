from gngram_lookup import exists, frequency


class TestFrequencyEdgeCases:
    def test_accented_word_resolves_to_ascii(self):
        assert exists("café") is True
        assert exists("protégé") is True
        assert exists("outré") is True
        assert exists("phaéton") is True

    def test_very_long_word(self):
        long_word = "a" * 1000
        assert exists(long_word) is False
        assert frequency(long_word) is None

    def test_single_character(self):
        result_a = exists("a")
        result_i = exists("i")
        assert result_a or result_i

    def test_hyphenated_word(self):
        assert exists("self-aware") is True

    def test_word_with_apostrophe(self):
        assert exists("don't") is True
        assert exists("we'll") is True
        assert exists("they're") is True

    def test_word_with_curly_apostrophe(self):
        assert exists("don\u2019t") is True
        assert exists("we\u2019ll") is True

    def test_numeric_string(self):
        assert exists("123") is False
        assert frequency("456") is None

    def test_mixed_alphanumeric(self):
        result = exists("test123")
        assert isinstance(result, bool)
