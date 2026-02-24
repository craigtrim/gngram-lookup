"""
Tests for gngram_lookup POS functions: pos(), has_pos(), PosTag.
"""

from gngram_lookup import PosTag, has_pos, is_pos_data_installed, pos


class TestPosDataInstallation:
    def test_pos_data_is_installed(self):
        assert is_pos_data_installed(), (
            "POS data files not installed. "
            "Run: python -m gngram_lookup.download_pos_data"
        )


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


class TestHasPos:
    def test_verb_positive(self):
        assert has_pos("sing", PosTag.VERB) is True

    def test_noun_positive(self):
        assert has_pos("corn", PosTag.NOUN) is True

    def test_unknown_word_returns_false(self):
        assert has_pos("zzzzqqqq", PosTag.NOUN) is False

    def test_min_tf_filters_noise(self):
        # With a very high threshold, even present tags return False
        assert has_pos("corn", PosTag.NOUN, min_tf=10_000_000_000) is False

    def test_min_tf_common_tag_passes(self):
        assert has_pos("corn", PosTag.NOUN, min_tf=100) is True


class TestPosTag:
    def test_enum_values_are_strings(self):
        assert PosTag.VERB == "VERB"
        assert PosTag.NOUN == "NOUN"

    def test_all_tags_present(self):
        tags = {t.value for t in PosTag}
        assert tags == {"NOUN", "VERB", "ADJ", "ADV", "PRON", "DET", "ADP", "NUM", "CONJ", "PRT", "X"}
