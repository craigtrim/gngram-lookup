from gngram_lookup import frequency


class TestFrequency:
    def test_frequency_common_word_returns_dict(self):
        result = frequency("the")
        assert result is not None
        assert isinstance(result, dict)

    def test_frequency_has_required_keys(self):
        result = frequency("the")
        assert result is not None
        assert "peak_tf" in result
        assert "peak_df" in result
        assert "sum_tf" in result
        assert "sum_df" in result

    def test_frequency_values_are_integers(self):
        result = frequency("the")
        assert result is not None
        assert isinstance(result["peak_tf"], int)
        assert isinstance(result["peak_df"], int)
        assert isinstance(result["sum_tf"], int)
        assert isinstance(result["sum_df"], int)

    def test_frequency_values_are_positive(self):
        result = frequency("the")
        assert result is not None
        assert result["sum_tf"] > 0
        assert result["sum_df"] > 0

    def test_frequency_peak_decades_are_valid(self):
        result = frequency("the")
        assert result is not None
        assert 1500 <= result["peak_tf"] <= 2020
        assert 1500 <= result["peak_df"] <= 2020

    def test_frequency_case_insensitive(self):
        result_lower = frequency("hello")
        result_upper = frequency("HELLO")
        assert result_lower == result_upper

    def test_frequency_nonexistent_word_returns_none(self):
        result = frequency("xyznotarealword123")
        assert result is None

    def test_frequency_empty_string_returns_none(self):
        result = frequency("")
        assert result is None

    def test_frequency_whitespace_returns_none(self):
        result = frequency("   ")
        assert result is None

    def test_frequency_special_chars_returns_none(self):
        result = frequency("!@#$%^&*()")
        assert result is None
