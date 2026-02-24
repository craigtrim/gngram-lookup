from gngram_lookup import batch_frequency, exists, frequency


class TestHyphenatedFallback:
    """Tests for hyphenated word fallback in exists() and frequency()."""

    def test_exists_common_hyphenated(self):
        for word in ("quarter-deck", "court-martial", "north-west", "twenty-five"):
            assert exists(word) is True, f"{word!r} should exist via parts"

    def test_exists_three_part(self):
        assert exists("man-of-war") is True

    def test_exists_hyphenated_case_insensitive(self):
        assert exists("QUARTER-DECK") is True
        assert exists("North-West") is True

    def test_exists_hyphenated_one_bad_part(self):
        # One component is nonsense — should be False
        assert exists("quarter-xyznotaword") is False

    def test_exists_hyphenated_all_bad_parts(self):
        assert exists("xyzfoo-xyzbar") is False

    def test_frequency_hyphenated_returns_first_part(self):
        result = frequency("quarter-deck")
        assert result is not None
        assert result == frequency("quarter")

    def test_frequency_hyphenated_three_part(self):
        result = frequency("man-of-war")
        assert result is not None
        assert result == frequency("man")

    def test_frequency_hyphenated_bad_part_returns_none(self):
        assert frequency("quarter-xyznotaword") is None

    def test_batch_hyphenated(self):
        result = batch_frequency(["quarter-deck", "north-west", "xyzfoo-xyzbar"])
        assert result["quarter-deck"] is not None
        assert result["north-west"] is not None
        assert result["xyzfoo-xyzbar"] is None

    def test_batch_hyphenated_matches_individual(self):
        words = ["quarter-deck", "court-martial", "man-of-war"]
        batch_result = batch_frequency(words)
        for word in words:
            assert batch_result[word] == frequency(word), (
                f"batch != individual for {word!r}"
            )

    def test_exists_frequency_agree_for_hyphenated(self):
        for word in ("quarter-deck", "north-west", "xyzfoo-xyzbar"):
            e = exists(word)
            f = frequency(word)
            if e:
                assert f is not None, f"exists=True but frequency=None for {word!r}"
            else:
                assert f is None, f"exists=False but frequency!=None for {word!r}"
