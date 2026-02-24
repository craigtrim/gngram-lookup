from gngram_lookup import exists


class TestExists:
    def test_exists_common_word(self):
        assert exists("the") is True

    def test_exists_another_common_word(self):
        assert exists("and") is True

    def test_exists_case_insensitive_upper(self):
        assert exists("THE") is True

    def test_exists_case_insensitive_mixed(self):
        assert exists("ThE") is True

    def test_exists_nonexistent_word(self):
        assert exists("xyznotarealword123") is False

    def test_exists_gibberish(self):
        assert exists("qzxjkvwpy") is False

    def test_exists_empty_string(self):
        assert exists("") is False

    def test_exists_whitespace_only(self):
        assert exists("   ") is False

    def test_exists_with_numbers(self):
        assert exists("12345") is False

    def test_exists_special_chars(self):
        assert exists("!@#$%") is False
