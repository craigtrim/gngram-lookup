"""
Data path utilities for gngram-counter.
"""

from pathlib import Path

DATA_DIR = Path.home() / ".gngram-counter" / "data"


def get_data_dir() -> Path:
    """Return the data directory path."""
    return DATA_DIR


def get_hash_file(prefix: str) -> Path:
    """Return path to a specific hash bucket parquet file.

    Args:
        prefix: Two hex characters (00-ff)

    Returns:
        Path to the parquet file (may be in subdirectory from tar extraction)
    """
    # Handle both flat structure and nested (from tar extraction)
    direct = DATA_DIR / f"{prefix}.parquet"
    if direct.exists():
        return direct

    nested = DATA_DIR / "parquet-hash" / f"{prefix}.parquet"
    if nested.exists():
        return nested

    raise FileNotFoundError(
        f"Data file not found for prefix '{prefix}'. "
        "Run 'python -m gngram_counter.download_data' to download the data files."
    )


def is_data_installed() -> bool:
    """Check if data files are installed."""
    if not DATA_DIR.exists():
        return False
    return any(DATA_DIR.glob("**/*.parquet"))
