from gngram_lookup import PosTag, has_pos


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
