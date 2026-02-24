from gngram_lookup.lookup import _split_contraction


class TestSplitContraction:
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

    def test_split_s_pronoun_contractions(self):
        for stem in ("it", "he", "she", "that", "what", "who", "where", "let"):
            word = f"{stem}'s"
            result = _split_contraction(word)
            assert result == (stem, "'s"), f"Failed for {word!r}"

    def test_split_s_possessives(self):
        for word, expected_stem in [
            ("dog's", "dog"), ("king's", "king"), ("ship's", "ship"),
            ("captain's", "captain"), ("mother's", "mother"),
        ]:
            result = _split_contraction(word)
            assert result == (expected_stem, "'s"), f"Failed for {word!r}"

    def test_split_regular_word(self):
        assert _split_contraction("hello") is None

    def test_split_empty(self):
        assert _split_contraction("") is None

    def test_split_suffix_only_no_stem(self):
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
