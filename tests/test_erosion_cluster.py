from gngram_lookup import erosion_cluster


class TestErosionCluster:
    def test_returns_list(self):
        assert isinstance(erosion_cluster("generate"), list)

    def test_min_len_guard(self):
        # Words at or below min_len cannot be eroded
        assert erosion_cluster("drink", min_len=5) == []
        assert erosion_cluster("run", min_len=5) == []

    def test_finds_siblings(self):
        # "generate" erodes to "generat" -> finds "generation", "generations", etc.
        result = erosion_cluster("generate")
        assert len(result) > 0

    def test_generation_is_sibling_of_generate(self):
        result = erosion_cluster("generate")
        assert "generation" in result

    def test_extensions_excluded(self):
        # Words that extend the input (e.g. "generates") are excluded; the word itself is not
        word = "generate"
        for w in erosion_cluster(word):
            assert w == word or not w.startswith(word), f"{w!r} is an extension of {word!r} — should be excluded"

    def test_input_word_included_in_results(self):
        # The searched word itself appears in results so it shows in context within the tree
        assert "generate" in erosion_cluster("generate")
        assert "simplification" in erosion_cluster("simplification")

    def test_siblings_share_prefix_with_input(self):
        # Every sibling must share at least min_len chars with the input
        word = "generate"
        min_len = 5
        for w in erosion_cluster(word, min_len=min_len):
            shared = sum(1 for a, b in zip(word, w) if a == b)
            assert shared >= min_len, f"{w!r} shares fewer than {min_len} chars with {word!r}"

    def test_unknown_word_returns_empty(self):
        assert erosion_cluster("zzzzqqqq") == []

    def test_case_insensitive(self):
        assert erosion_cluster("GENERATE") == erosion_cluster("generate")

    def test_min_tf_filters_rare_words(self):
        all_results = erosion_cluster("generate")
        filtered = erosion_cluster("generate", min_tf=1_000_000)
        assert len(filtered) <= len(all_results)

    def test_sort_by_alpha_default(self):
        result = erosion_cluster("generate")
        assert result == sorted(result)

    def test_sort_by_alpha_explicit(self):
        assert erosion_cluster("generate", sort_by="alpha") == erosion_cluster("generate")

    def test_sort_by_freq_returns_list_str(self):
        result = erosion_cluster("generate", sort_by="freq")
        assert isinstance(result, list)
        assert all(isinstance(w, str) for w in result)

    def test_sort_by_freq_descending(self):
        result = erosion_cluster("generate", sort_by="freq", with_freq=True)
        tfs = [tf for _, tf in result]
        assert tfs == sorted(tfs, reverse=True)

    def test_with_freq_returns_tuples(self):
        result = erosion_cluster("generate", with_freq=True)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
        assert all(isinstance(w, str) and isinstance(tf, int) for w, tf in result)

    def test_with_freq_alpha_sorted(self):
        result = erosion_cluster("generate", with_freq=True, sort_by="alpha")
        words = [w for w, _ in result]
        assert words == sorted(words)

    def test_with_freq_freq_sorted(self):
        result = erosion_cluster("generate", with_freq=True, sort_by="freq")
        tfs = [tf for _, tf in result]
        assert tfs == sorted(tfs, reverse=True)

    def test_no_duplicates(self):
        result = erosion_cluster("generate")
        assert len(result) == len(set(result))

    def test_prefix_erosion_finds_derived_forms(self):
        # "beauty" (6 chars) erodes to "beaut" -> finds "beautiful", "beautification", etc.
        result = erosion_cluster("beauty")
        assert "beautiful" in result

    def test_min_tf_filters_input_word_when_below_threshold(self):
        # min_tf applies uniformly — word itself is excluded if its frequency is too low
        result = erosion_cluster("generate", min_tf=1_000_000_000)
        assert "generate" not in result

    def test_input_word_only_when_high_min_tf_applied(self):
        # Without min_tf, the word is in results; with absurd min_tf it is not
        without_filter = erosion_cluster("generate")
        with_filter = erosion_cluster("generate", min_tf=1_000_000_000)
        assert "generate" in without_filter
        assert "generate" not in with_filter

    def test_sort_by_freq_does_not_include_extensions(self):
        word = "generate"
        for w in erosion_cluster(word, sort_by="freq"):
            assert w == word or not w.startswith(word)

    def test_with_freq_input_word_has_positive_tf(self):
        result = erosion_cluster("generate", with_freq=True)
        tf_map = dict(result)
        assert "generate" in tf_map
        assert tf_map["generate"] > 0

    def test_long_word_included_in_results(self):
        # Multi-syllable words are found in their own erosion cluster
        result = erosion_cluster("simplification")
        assert "simplification" in result

    def test_all_results_are_lowercase(self):
        result = erosion_cluster("Generate")
        assert all(w == w.lower() for w in result)
