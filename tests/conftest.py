"""
Pytest configuration for gngram_lookup tests.

Data must be installed to run tests. Either:
- Clone the repo with parquet-hash/ directory
- Run: python -m gngram_lookup.download_data
"""

import pytest

from gngram_lookup import is_data_installed


def pytest_configure(config):
    """Verify data is installed before running any tests."""
    if not is_data_installed():
        pytest.exit(
            "ERROR: Data files not installed.\n"
            "Run one of:\n"
            "  make download-data\n"
            "  python -m gngram_lookup.download_data\n"
            "Or ensure parquet-hash/ directory exists in repo root.",
            returncode=1,
        )
