from gngram_lookup.normalize import normalize, normalize_apostrophes, strip_accents


class TestNormalize:
    def test_normalize_ascii_apostrophe(self):
        assert normalize("don't") == "don't"

    def test_normalize_curly_right(self):
        assert normalize("don\u2019t") == "don't"

    def test_normalize_curly_left(self):
        assert normalize("don\u2018t") == "don't"

    def test_normalize_grave_accent(self):
        assert normalize("don\u0060t") == "don't"

    def test_normalize_acute_accent(self):
        assert normalize("don\u00B4t") == "don't"

    def test_normalize_prime(self):
        assert normalize("don\u2032t") == "don't"

    def test_normalize_reversed_prime(self):
        assert normalize("don\u2035t") == "don't"

    def test_normalize_modifier_letter_apostrophe(self):
        assert normalize("don\u02BCt") == "don't"

    def test_normalize_fullwidth_apostrophe(self):
        assert normalize("don\uFF07t") == "don't"

    def test_normalize_high_reversed_9(self):
        assert normalize("don\u201Bt") == "don't"

    def test_normalize_modifier_letter_prime(self):
        assert normalize("don\u02B9t") == "don't"

    def test_normalize_lowercase(self):
        assert normalize("DON'T") == "don't"

    def test_normalize_strip(self):
        assert normalize("  hello  ") == "hello"

    def test_normalize_combined_curly_upper_whitespace(self):
        assert normalize("  DON\u2019T  ") == "don't"

    def test_normalize_empty_string(self):
        assert normalize("") == ""

    def test_normalize_no_apostrophes_passthrough(self):
        assert normalize("hello") == "hello"

    def test_normalize_apostrophes_only(self):
        result = normalize_apostrophes("we\u2019ll")
        assert result == "we'll"

    def test_normalize_apostrophes_preserves_case(self):
        result = normalize_apostrophes("DON\u2019T")
        assert result == "DON'T"

    def test_normalize_apostrophes_no_change(self):
        result = normalize_apostrophes("don't")
        assert result == "don't"

    def test_normalize_apostrophes_empty(self):
        assert normalize_apostrophes("") == ""

    def test_strip_accents_acute(self):
        assert strip_accents("protégé") == "protege"

    def test_strip_accents_mixed(self):
        assert strip_accents("phaéton") == "phaeton"

    def test_strip_accents_grave(self):
        assert strip_accents("outré") == "outre"

    def test_strip_accents_no_change(self):
        assert strip_accents("hello") == "hello"

    def test_strip_accents_empty(self):
        assert strip_accents("") == ""

    def test_strip_accents_preserves_apostrophe(self):
        assert strip_accents("don't") == "don't"

    def test_normalize_accent_full_pipeline(self):
        assert normalize("  Protégé  ") == "protege"

    def test_normalize_accent_with_apostrophe(self):
        assert normalize("café\u2019s") == "cafe's"
