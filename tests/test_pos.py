from gngram_lookup import pos


class TestPos:
    def test_unambiguous_verb(self):
        result = pos("sing")
        assert "VERB" in result

    def test_unambiguous_noun(self):
        result = pos("corn")
        assert "NOUN" in result

    def test_ambiguous_word_returns_multiple(self):
        result = pos("fast")
        assert len(result) > 1
        assert "ADJ" in result
        assert "VERB" in result

    def test_unknown_word_returns_empty(self):
        assert pos("zzzzqqqq") == []

    def test_empty_string_returns_empty(self):
        assert pos("") == []

    def test_returns_sorted_list(self):
        result = pos("fast")
        assert result == sorted(result)

    def test_min_tf_filters_low_freq_tags(self):
        # With a high threshold, rare/noisy tags should be filtered out
        result_unfiltered = pos("corn")
        result_filtered = pos("corn", min_tf=100)
        # Filtered result should be a subset
        assert set(result_filtered).issubset(set(result_unfiltered))
        # NOUN should survive a high threshold for a common word
        assert "NOUN" in result_filtered

    def test_min_tf_extreme_returns_empty(self):
        # An impossibly high threshold returns nothing
        assert pos("corn", min_tf=10_000_000_000) == []
