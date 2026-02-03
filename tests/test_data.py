"""
Tests for gngram_counter.data module.
"""

import pytest
from pathlib import Path

from gngram_counter import is_data_installed, get_data_dir, get_hash_file


class TestDataDir:
    """Tests for get_data_dir()."""

    def test_get_data_dir_returns_path(self):
        result = get_data_dir()
        assert isinstance(result, Path)

    def test_get_data_dir_is_in_home(self):
        result = get_data_dir()
        assert str(Path.home()) in str(result)

    def test_get_data_dir_consistent(self):
        result1 = get_data_dir()
        result2 = get_data_dir()
        assert result1 == result2


class TestIsDataInstalled:
    """Tests for is_data_installed()."""

    def test_is_data_installed_returns_bool(self):
        result = is_data_installed()
        assert isinstance(result, bool)


# Only run these if data is installed
DATA_INSTALLED = is_data_installed()
requires_data = pytest.mark.skipif(
    not DATA_INSTALLED,
    reason="Data files not installed",
)


@requires_data
class TestGetHashFile:
    """Tests for get_hash_file() when data is installed."""

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
        # Test a few different prefixes
        for prefix in ["00", "0f", "a0", "ff"]:
            result = get_hash_file(prefix)
            assert result.exists(), f"File for prefix {prefix} should exist"


class TestGetHashFileNotInstalled:
    """Tests for get_hash_file() error handling."""

    @pytest.mark.skipif(DATA_INSTALLED, reason="Data is installed")
    def test_get_hash_file_raises_when_not_installed(self):
        with pytest.raises(FileNotFoundError):
            get_hash_file("00")
