from pathlib import Path

from gngram_lookup import get_data_dir


class TestFrequencyDataDir:
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
