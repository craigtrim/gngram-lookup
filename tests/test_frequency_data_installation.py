from gngram_lookup import is_data_installed


class TestFrequencyDataInstallation:
    def test_data_is_installed(self):
        assert is_data_installed(), (
            "Data files not installed. "
            "Run: python -m gngram_lookup.download_data"
        )
