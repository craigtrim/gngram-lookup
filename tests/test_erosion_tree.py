import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from erosion import _build_tree_lines, _lcp_len

# Shared fake results used across multiple tests
_SIMPLIFICATION_RESULTS = [
    ("simplified", 7_432_361),
    ("simplification", 2_762_457),
    ("simplify", 3_594_130),
]
_GENERATE_RESULTS = [
    ("generation", 50_000_000),
    ("generator", 10_000_000),
    ("generate", 25_000_000),
]


class TestBuildTreeLines:
    def test_anchor_word_always_first_line(self):
        lines = _build_tree_lines("simplification", _SIMPLIFICATION_RESULTS, with_freq=False, anchor_tf=2_762_457)
        assert lines[0] == "simplification"

    def test_anchor_shown_without_with_freq(self):
        lines = _build_tree_lines("generate", _GENERATE_RESULTS, with_freq=False, anchor_tf=25_000_000)
        assert lines[0] == "generate"
        assert "25,000,000" not in lines[0]

    def test_anchor_frequency_shown_with_with_freq(self):
        lines = _build_tree_lines("generate", _GENERATE_RESULTS, with_freq=True, anchor_tf=25_000_000)
        assert "generate" in lines[0]
        assert "25,000,000" in lines[0]

    def test_no_word_dash_label_when_word_in_results(self):
        # "simplification" in results must not create a "simplification-" group label
        lines = _build_tree_lines("simplification", _SIMPLIFICATION_RESULTS, with_freq=True, anchor_tf=2_762_457)
        assert "simplification-" not in lines

    def test_intermediate_prefix_labels_still_present(self):
        # "simplifi-" label should still appear for the depth-8 group
        lines = _build_tree_lines("simplification", _SIMPLIFICATION_RESULTS, with_freq=True, anchor_tf=2_762_457)
        assert any(line.strip() == "simplifi-" for line in lines)

    def test_input_word_appears_in_tree_body(self):
        # "simplification" should appear both as anchor (line 0) and inside the tree
        lines = _build_tree_lines("simplification", _SIMPLIFICATION_RESULTS, with_freq=True, anchor_tf=2_762_457)
        occurrences = [i for i, line in enumerate(lines) if "simplification" in line and "simplification-" not in line]
        assert len(occurrences) >= 2

    def test_blank_separator_after_anchor(self):
        lines = _build_tree_lines("generate", _GENERATE_RESULTS, with_freq=False, anchor_tf=25_000_000)
        assert lines[1] == ""

    def test_returns_list_of_strings(self):
        lines = _build_tree_lines("generate", _GENERATE_RESULTS, with_freq=False)
        assert isinstance(lines, list)
        assert all(isinstance(line, str) for line in lines)

    def test_frequencies_right_aligned_to_common_column(self):
        lines = _build_tree_lines("generate", _GENERATE_RESULTS, with_freq=True, anchor_tf=25_000_000)
        freq_lines = [line for line in lines if "," in line and any(c.isdigit() for c in line)]
        # All frequency numbers should end at the same column
        end_positions = [len(line) for line in freq_lines]
        assert len(set(end_positions)) == 1, f"Frequencies not aligned: {end_positions}"

    def test_anchor_tf_none_still_shows_anchor(self):
        lines = _build_tree_lines("generate", _GENERATE_RESULTS, with_freq=True, anchor_tf=None)
        assert lines[0] == "generate"

    def test_input_word_absent_from_results_still_shows_at_top(self):
        # Classic pre-fix behavior: word not in siblings, but anchor still renders at top
        results_without_self = [("generation", 50_000_000), ("generator", 10_000_000)]
        lines = _build_tree_lines("generate", results_without_self, with_freq=True, anchor_tf=25_000_000)
        assert lines[0].startswith("generate")

    def test_no_frequencies_when_with_freq_false(self):
        # No comma-separated number sequences should appear anywhere in output
        lines = _build_tree_lines("generate", _GENERATE_RESULTS, with_freq=False, anchor_tf=25_000_000)
        for line in lines:
            assert not any(c.isdigit() for c in line), f"Unexpected digits in: {line!r}"

    def test_group_labels_end_with_dash(self):
        # Every section header (prefix group label) ends with "-"
        lines = _build_tree_lines("simplification", _SIMPLIFICATION_RESULTS, with_freq=False, anchor_tf=0)
        label_lines = [line.strip() for line in lines if line.strip().endswith("-")]
        assert len(label_lines) > 0
        for label in label_lines:
            assert label.endswith("-")

    def test_single_result_no_crash(self):
        lines = _build_tree_lines("generate", [("generation", 50_000_000)], with_freq=True, anchor_tf=25_000_000)
        assert isinstance(lines, list)
        assert len(lines) > 0

    def test_single_result_anchor_at_top(self):
        lines = _build_tree_lines("generate", [("generation", 50_000_000)], with_freq=False, anchor_tf=0)
        assert lines[0] == "generate"


class TestLcpLen:
    def test_identical_strings(self):
        assert _lcp_len("generate", "generate") == 8

    def test_partial_match(self):
        # "generate" vs "generation": g-e-n-e-r-a-t match, then 'e' vs 'i' differ → 7
        assert _lcp_len("generate", "generation") == 7

    def test_partial_match_longer(self):
        # "simplification" vs "simplified": share "simplifi" (8 chars), then 'c' vs 'e'
        assert _lcp_len("simplification", "simplified") == 8

    def test_no_common_prefix(self):
        assert _lcp_len("abc", "xyz") == 0

    def test_one_char_match(self):
        assert _lcp_len("apple", "ant") == 1

    def test_shorter_string_limits_result(self):
        assert _lcp_len("ab", "abcde") == 2

    def test_symmetric(self):
        assert _lcp_len("generate", "generation") == _lcp_len("generation", "generate")

    def test_empty_string(self):
        assert _lcp_len("", "generate") == 0
        assert _lcp_len("generate", "") == 0
