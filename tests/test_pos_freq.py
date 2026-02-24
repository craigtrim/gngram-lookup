from gngram_lookup import pos_freq


class TestPosFreq:
    def test_returns_dict(self):
        result = pos_freq("corn")
        assert isinstance(result, dict)
        assert "NOUN" in result
        assert isinstance(result["NOUN"], int)

    def test_unknown_word_returns_empty(self):
        assert pos_freq("zzzzqqqq") == {}

    def test_empty_string_returns_empty(self):
        assert pos_freq("") == {}

    def test_min_tf_filters(self):
        full = pos_freq("corn")
        filtered = pos_freq("corn", min_tf=100000)
        assert set(filtered).issubset(set(full))
        assert "NOUN" in filtered

    def test_min_tf_extreme_returns_empty(self):
        assert pos_freq("corn", min_tf=10_000_000_000) == {}
