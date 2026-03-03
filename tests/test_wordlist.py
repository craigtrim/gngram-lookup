from gngram_lookup import wordlist


class TestWordlist:
    def test_returns_list(self):
        result = wordlist()
        assert isinstance(result, list)

    def test_nonempty(self):
        assert len(wordlist()) > 0

    def test_sorted(self):
        result = wordlist()
        assert result == sorted(result)

    def test_all_strings(self):
        for word in wordlist()[:100]:
            assert isinstance(word, str)

    def test_known_words_present(self):
        result = set(wordlist())
        for word in ("the", "computer", "language", "drink"):
            assert word in result

    def test_min_tf_reduces_list(self):
        all_words = wordlist()
        filtered = wordlist(min_tf=1_000_000)
        assert len(filtered) < len(all_words)
        assert len(filtered) > 0

    def test_min_tf_zero_returns_all(self):
        assert wordlist(min_tf=0) == wordlist()

    def test_high_min_tf_returns_only_common_words(self):
        result = wordlist(min_tf=1_000_000_000)
        assert "the" in result
