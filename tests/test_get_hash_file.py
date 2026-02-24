from pathlib import Path

from gngram_lookup import get_hash_file


class TestGetFrequencyHashFile:
    def test_get_hash_file_returns_path(self):
        result = get_hash_file("00")
        assert isinstance(result, Path)

    def test_get_hash_file_exists(self):
        result = get_hash_file("00")
        assert result.exists()

    def test_get_hash_file_is_parquet(self):
        result = get_hash_file("00")
        assert result.suffix == ".parquet"

    def test_get_hash_file_various_prefixes(self):
        for prefix in ["00", "0f", "a0", "ff"]:
            result = get_hash_file(prefix)
            assert result.exists(), f"File for prefix {prefix} should exist"

    def test_get_hash_file_all_256_buckets(self):
        for i in range(256):
            prefix = f"{i:02x}"
            result = get_hash_file(prefix)
            assert result.exists(), f"File for prefix {prefix} should exist"
