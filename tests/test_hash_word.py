from gngram_lookup.lookup import _hash_word


class TestHashWord:
    def test_hash_word_returns_tuple(self):
        prefix, suffix = _hash_word("test")
        assert isinstance(prefix, str)
        assert isinstance(suffix, str)

    def test_hash_word_prefix_length(self):
        prefix, suffix = _hash_word("example")
        assert len(prefix) == 2

    def test_hash_word_suffix_length(self):
        prefix, suffix = _hash_word("example")
        assert len(suffix) == 30

    def test_hash_word_lowercase(self):
        assert _hash_word("TEST") == _hash_word("test")
        assert _hash_word("TeSt") == _hash_word("test")

    def test_hash_word_consistent(self):
        assert _hash_word("hello") == _hash_word("hello")

    def test_hash_word_different_words(self):
        assert _hash_word("hello") != _hash_word("world")

    def test_hash_word_curly_apostrophe_normalizes(self):
        assert _hash_word("don't") == _hash_word("don\u2019t")

    def test_hash_word_whitespace_stripped(self):
        assert _hash_word("  hello  ") == _hash_word("hello")
