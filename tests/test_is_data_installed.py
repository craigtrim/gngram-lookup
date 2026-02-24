from gngram_lookup import is_data_installed


class TestIsFrequencyDataInstalled:
    def test_is_data_installed_returns_bool(self):
        result = is_data_installed()
        assert isinstance(result, bool)

    def test_is_data_installed_is_true(self):
        assert is_data_installed() is True
