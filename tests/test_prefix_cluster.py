from gngram_lookup import prefix_cluster


class TestPrefixCluster:
    def test_returns_list(self):
        assert isinstance(prefix_cluster("drink"), list)

    def test_standard_prefix_match(self):
        result = prefix_cluster("drink")
        assert "drinking" in result
        assert "drinks" in result

    def test_results_are_longer_than_input(self):
        word = "drink"
        for w in prefix_cluster(word):
            assert len(w) > len(word)

    def test_results_share_prefix(self):
        word = "nation"
        for w in prefix_cluster(word):
            assert w.startswith(word) or w.startswith(word[:-1])

    def test_y_drop_allomorph(self):
        result = prefix_cluster("happy")
        assert "happiness" in result
        assert "happier" in result

    def test_y_drop_no_false_matches(self):
        # "mercantile" should not appear in mercy cluster (doesn't continue with y or i)
        result = prefix_cluster("mercy")
        for w in result:
            stem = "merc"
            if not w.startswith("mercy"):
                assert w[len(stem)] in ("y", "i"), f"unexpected continuation in {w!r}"

    def test_min_len_guard(self):
        # Words shorter than min_len return empty
        assert prefix_cluster("go", min_len=5) == []
        assert prefix_cluster("run", min_len=5) == []

    def test_min_len_boundary(self):
        # A 5-char word with min_len=5 should attempt clustering
        result = prefix_cluster("drink", min_len=5)
        assert isinstance(result, list)

    def test_unknown_word_returns_empty_or_list(self):
        result = prefix_cluster("zzzzqqqq")
        assert isinstance(result, list)

    def test_results_sorted(self):
        result = prefix_cluster("drink")
        assert result == sorted(result)

    def test_min_tf_filters_rare_words(self):
        all_results = prefix_cluster("drink")
        filtered = prefix_cluster("drink", min_tf=1_000_000)
        assert len(filtered) <= len(all_results)

    def test_case_insensitive(self):
        assert prefix_cluster("DRINK") == prefix_cluster("drink")

    def test_sort_by_freq_returns_list_str(self):
        result = prefix_cluster("drink", sort_by="freq")
        assert isinstance(result, list)
        assert all(isinstance(w, str) for w in result)

    def test_sort_by_freq_descending(self):
        result = prefix_cluster("drink", sort_by="freq", with_freq=True)
        tfs = [tf for _, tf in result]
        assert tfs == sorted(tfs, reverse=True)

    def test_with_freq_returns_tuples(self):
        result = prefix_cluster("drink", with_freq=True)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
        assert all(isinstance(w, str) and isinstance(tf, int) for w, tf in result)

    def test_with_freq_alpha_sorted(self):
        result = prefix_cluster("drink", with_freq=True, sort_by="alpha")
        words = [w for w, _ in result]
        assert words == sorted(words)

    def test_with_freq_freq_sorted(self):
        result = prefix_cluster("drink", with_freq=True, sort_by="freq")
        tfs = [tf for _, tf in result]
        assert tfs == sorted(tfs, reverse=True)

    def test_sort_by_alpha_default(self):
        # default sort_by="alpha" matches explicit call
        assert prefix_cluster("drink") == prefix_cluster("drink", sort_by="alpha")
