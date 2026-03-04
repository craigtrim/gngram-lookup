import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from suffix_fingerprint import extract_suffix


class TestExtractSuffix:
    def test_simple_suffix(self):
        # "nation" + "al" = "national"
        assert extract_suffix("nation", "national") == "al"

    def test_ize_suffix(self):
        assert extract_suffix("modern", "modernize") == "ize"

    def test_ization_suffix(self):
        assert extract_suffix("modern", "modernization") == "ization"

    def test_ly_suffix(self):
        assert extract_suffix("quick", "quickly") == "ly"

    def test_ness_suffix(self):
        assert extract_suffix("happy", "happiness") == "ness"  # via y->i allomorph

    def test_y_allomorph_fication(self):
        # "beauty" -> "beauti" -> "beautification"[7:] = "fication"
        assert extract_suffix("beauty", "beautification") == "fication"

    def test_y_allomorph_ful(self):
        assert extract_suffix("beauty", "beautiful") == "ful"

    def test_no_match_unrelated_word(self):
        assert extract_suffix("nation", "generate") is None

    def test_no_match_non_prefix(self):
        # "tion" does not start with "nation"
        assert extract_suffix("nation", "tion") is None

    def test_exact_match_returns_empty_string(self):
        # member == root → suffix is ""
        assert extract_suffix("nation", "nation") == ""

    def test_y_root_but_no_match(self):
        # "happy" -> "happi" doesn't match "happening" (unrelated)
        assert extract_suffix("happy", "happening") is None

    def test_non_y_root_no_allomorph_tried(self):
        # "quick" doesn't end in y; only direct prefix match is tried
        assert extract_suffix("quick", "quicken") == "en"
        assert extract_suffix("quick", "quickness") == "ness"

    def test_classi_stem(self):
        # corpus stem "classi" + "fication" = "classification"
        assert extract_suffix("classi", "classification") == "fication"

    def test_justi_stem(self):
        assert extract_suffix("justi", "justification") == "fication"

    def test_ism_suffix(self):
        assert extract_suffix("nation", "nationalism") == "alism"

    def test_ist_suffix(self):
        assert extract_suffix("nation", "nationalist") == "alist"

    def test_returns_none_not_false(self):
        result = extract_suffix("nation", "generate")
        assert result is None

    def test_returns_str_on_match(self):
        result = extract_suffix("nation", "national")
        assert isinstance(result, str)
