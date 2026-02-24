from gngram_lookup import word_score


class TestWordScore:
    def test_returns_int(self):
        result = word_score("computer")
        assert isinstance(result, int)

    def test_unknown_word_returns_none(self):
        assert word_score("zzzzqqqq") is None

    def test_empty_string_returns_none(self):
        assert word_score("") is None

    def test_range_is_1_to_100(self):
        for word in ("the", "computer", "algorithm", "rucksack"):
            score = word_score(word)
            if score is not None:
                assert 1 <= score <= 100, f"{word!r} score {score} out of range"

    def test_common_word_scores_lower_than_rare(self):
        common = word_score("the")
        rare = word_score("rucksack")
        assert common is not None
        assert rare is not None
        assert common < rare

    def test_very_common_word_scores_low(self):
        assert word_score("the") <= 10

    def test_case_insensitive(self):
        assert word_score("THE") == word_score("the")
