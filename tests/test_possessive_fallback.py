from gngram_lookup import batch_frequency, exists, frequency


class TestPossessiveFallback:
    def test_exists_common_possessives(self):
        for word in ("ship's", "king's", "captain's", "admiral's"):
            assert exists(word) is True, f"{word!r} should exist via stem"

    def test_exists_possessive_case_insensitive(self):
        assert exists("KING'S") is True
        assert exists("Ship's") is True

    def test_exists_possessive_curly_apostrophe(self):
        assert exists("ship\u2019s") is True

    def test_exists_nonsense_possessive(self):
        assert exists("xyznotaword's") is False

    def test_frequency_possessive_equals_stem(self):
        assert frequency("ship's") == frequency("ship")
        assert frequency("king's") == frequency("king")

    def test_frequency_nonsense_possessive(self):
        assert frequency("xyznotaword's") is None

    def test_batch_possessives(self):
        result = batch_frequency(["ship's", "king's", "xyznotaword's"])
        assert result["ship's"] is not None
        assert result["king's"] is not None
        assert result["xyznotaword's"] is None

    def test_batch_possessive_matches_individual(self):
        words = ["ship's", "captain's", "dog's"]
        batch_result = batch_frequency(words)
        for word in words:
            assert batch_result[word] == frequency(word), (
                f"batch != individual for {word!r}"
            )
