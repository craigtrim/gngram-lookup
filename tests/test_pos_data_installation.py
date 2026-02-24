from gngram_lookup import is_pos_data_installed


class TestPosDataInstallation:
    def test_pos_data_is_installed(self):
        assert is_pos_data_installed(), (
            "POS data files not installed. "
            "Run: python -m gngram_lookup.download_pos_data"
        )
