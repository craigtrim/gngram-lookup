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

    def test_siblings_do_not_start_with_input(self):
        # Siblings are not extensions of the input word
        word = "generate"
        for w in erosion_cluster(word):
            assert not w.startswith(word), f"{w!r} starts with {word!r} — should be excluded"

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
