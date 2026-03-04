import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from suffix_query import _candidate_forms, _levenshtein


class TestLevenshtein:
    def test_identical_strings(self):
        assert _levenshtein("ification", "ification") == 0

    def test_single_substitution(self):
        assert _levenshtein("cat", "bat") == 1

    def test_single_insertion(self):
        assert _levenshtein("cat", "cats") == 1

    def test_single_deletion(self):
        assert _levenshtein("cats", "cat") == 1

    def test_classic_example(self):
        assert _levenshtein("kitten", "sitting") == 3

    def test_empty_string(self):
        assert _levenshtein("", "abc") == 3
        assert _levenshtein("abc", "") == 3

    def test_symmetric(self):
        assert _levenshtein("ification", "fication") == _levenshtein("fication", "ification")

    def test_suffix_variants_ranked_correctly(self):
        # "fication" is closer to "ification" than "ation" is
        assert _levenshtein("ification", "fication") < _levenshtein("ification", "ation")

    def test_prefix_relationship(self):
        # "ation" vs "ification": differ by 4 chars at the start
        assert _levenshtein("ation", "ication") == 2


class TestCandidateForms:
    def test_basic_form(self):
        assert _candidate_forms("class", "ify") == ["classify"]

    def test_non_y_root_returns_one_form(self):
        forms = _candidate_forms("nation", "al")
        assert forms == ["national"]

    def test_y_root_returns_two_forms(self):
        # "happy" -> ["happyness", "happiness"]
        forms = _candidate_forms("happy", "ness")
        assert "happyness" in forms
        assert "happiness" in forms
        assert len(forms) == 2

    def test_y_allomorph_drops_y_adds_i(self):
        forms = _candidate_forms("beauty", "ful")
        assert "beautiful" in forms
        assert "beautyful" in forms

    def test_non_y_does_not_produce_allomorph(self):
        forms = _candidate_forms("work", "ing")
        assert forms == ["working"]

    def test_returns_list(self):
        assert isinstance(_candidate_forms("simple", "ify"), list)

    def test_first_form_is_always_direct_concatenation(self):
        # The direct root+suffix form is always first
        forms = _candidate_forms("happy", "ness")
        assert forms[0] == "happyness"

    def test_y_allomorph_is_second_form(self):
        forms = _candidate_forms("beauty", "fication")
        assert forms[1] == "beautification"

    def test_empty_suffix(self):
        # Empty suffix is an edge case — still produces root itself
        forms = _candidate_forms("class", "")
        assert "class" in forms

    def test_classi_stem_produces_classification(self):
        # "classi" (corpus stem) + "fication" = "classification" via direct concatenation
        # "classi" does not end in "y" so no allomorph
        forms = _candidate_forms("classi", "fication")
        assert forms == ["classification"]

    def test_no_allomorph_when_root_ends_in_i(self):
        # Roots ending in "i" are not treated as y-drop allomorphs
        forms = _candidate_forms("justi", "fication")
        assert forms == ["justification"]
        assert len(forms) == 1
