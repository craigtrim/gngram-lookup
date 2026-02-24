from gngram_lookup.lookup import _split_hyphenated


class TestSplitHyphenated:
    def test_split_simple(self):
        assert _split_hyphenated("quarter-deck") == ["quarter", "deck"]

    def test_split_three_parts(self):
        assert _split_hyphenated("man-of-war") == ["man", "of", "war"]

    def test_split_no_hyphen(self):
        assert _split_hyphenated("hello") is None

    def test_split_empty(self):
        assert _split_hyphenated("") is None

    def test_split_lone_hyphen(self):
        assert _split_hyphenated("-") is None

    def test_split_leading_hyphen(self):
        assert _split_hyphenated("-foo") is None

    def test_split_trailing_hyphen(self):
        assert _split_hyphenated("foo-") is None

    def test_split_double_hyphen(self):
        assert _split_hyphenated("foo--bar") == ["foo", "bar"]
