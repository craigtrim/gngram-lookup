from gngram_lookup import batch_frequency, exists, frequency


class TestContractionFallback:
    def test_exists_dont(self):
        assert exists("don't") is True

    def test_exists_wont(self):
        assert exists("won't") is True

    def test_exists_cant(self):
        assert exists("can't") is True

    def test_exists_well(self):
        assert exists("we'll") is True

    def test_exists_theyre(self):
        assert exists("they're") is True

    def test_exists_ive(self):
        assert exists("i've") is True

    def test_exists_im(self):
        assert exists("i'm") is True

    def test_exists_id(self):
        assert exists("i'd") is True

    def test_exists_thats(self):
        assert exists("that's") is True

    def test_exists_its(self):
        assert exists("it's") is True

    def test_exists_hes(self):
        assert exists("he's") is True

    def test_exists_shes(self):
        assert exists("she's") is True

    def test_exists_theres(self):
        assert exists("there's") is True

    def test_exists_whats(self):
        assert exists("what's") is True

    def test_exists_lets(self):
        assert exists("let's") is True

    def test_exists_possessive_resolves_via_stem(self):
        assert exists("dog's") is True
        assert exists("king's") is True
        assert exists("ship's") is True

    def test_exists_uppercase_contraction(self):
        assert exists("DON'T") is True

    def test_exists_mixed_case_contraction(self):
        assert exists("Don't") is True

    def test_exists_uppercase_s_contraction(self):
        assert exists("THAT'S") is True

    def test_exists_curly_thats(self):
        assert exists("that\u2019s") is True

    def test_exists_curly_its(self):
        assert exists("it\u2019s") is True

    def test_frequency_dont(self):
        result = frequency("don't")
        assert result is not None
        assert result["sum_tf"] > 0

    def test_frequency_well(self):
        result = frequency("we'll")
        assert result is not None
        assert result["sum_tf"] > 0

    def test_frequency_thats(self):
        result = frequency("that's")
        assert result is not None
        assert result["sum_tf"] > 0

    def test_frequency_its(self):
        result = frequency("it's")
        assert result is not None
        assert result["sum_tf"] > 0

    def test_frequency_curly_apostrophe(self):
        result = frequency("don\u2019t")
        assert result is not None
        assert result["sum_tf"] > 0

    def test_frequency_contraction_has_valid_structure(self):
        result = frequency("don't")
        assert result is not None
        assert "peak_tf" in result
        assert "peak_df" in result
        assert "sum_tf" in result
        assert "sum_df" in result
        assert isinstance(result["peak_tf"], int)
        assert isinstance(result["sum_tf"], int)

    def test_frequency_possessive_returns_stem_data(self):
        result = frequency("dog's")
        assert result is not None
        assert result == frequency("dog")

    def test_frequency_contraction_equals_stem(self):
        assert frequency("don't") == frequency("do")

    def test_frequency_s_contraction_equals_stem(self):
        assert frequency("that's") == frequency("that")

    def test_frequency_curly_equals_ascii(self):
        assert frequency("don\u2019t") == frequency("don't")

    def test_exists_frequency_agree_for_contraction(self):
        for word in ("don't", "we'll", "that's", "it's"):
            e = exists(word)
            f = frequency(word)
            if e:
                assert f is not None, f"exists=True but frequency=None for {word!r}"
            else:
                assert f is None, f"exists=False but frequency!=None for {word!r}"

    def test_batch_frequency_contractions(self):
        words = ["don't", "we'll", "the", "xyznotaword"]
        result = batch_frequency(words)
        assert result["don't"] is not None
        assert result["we'll"] is not None
        assert result["the"] is not None
        assert result["xyznotaword"] is None

    def test_batch_frequency_curly_apostrophe(self):
        result = batch_frequency(["don\u2019t", "we\u2019ll"])
        assert result["don\u2019t"] is not None
        assert result["we\u2019ll"] is not None

    def test_batch_frequency_s_contractions(self):
        result = batch_frequency(["that's", "it's", "where's"])
        assert result["that's"] is not None
        assert result["it's"] is not None
        assert result["where's"] is not None

    def test_batch_frequency_case_preserved_for_contractions(self):
        result = batch_frequency(["DON'T", "That's"])
        assert "DON'T" in result
        assert "That's" in result
        assert result["DON'T"] is not None
        assert result["That's"] is not None

    def test_batch_frequency_matches_individual_frequency(self):
        words = ["don't", "that's", "we'll"]
        batch_result = batch_frequency(words)
        for word in words:
            assert batch_result[word] == frequency(word), (
                f"batch != individual for {word!r}"
            )
