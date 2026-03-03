"""
Data path utilities for gngram-lookup.
"""

from pathlib import Path

DATA_DIR = Path.home() / ".gngram-lookup" / "data"
POS_DATA_DIR = Path.home() / ".gngram-lookup" / "pos-data"


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
        "Run 'python -m gngram_lookup.download_data' to download the data files."
    )


def is_data_installed() -> bool:
    """Check if data files are installed."""
    if not DATA_DIR.exists():
        return False
    return any(DATA_DIR.glob("**/*.parquet"))


def get_wordlist_file() -> Path:
    """Return path to the sorted wordlist parquet file.

    Returns:
        Path to wordlist.parquet (may be in subdirectory from tar extraction)
    """
    direct = DATA_DIR / "wordlist.parquet"
    if direct.exists():
        return direct

    nested = DATA_DIR / "parquet-hash" / "wordlist.parquet"
    if nested.exists():
        return nested

    raise FileNotFoundError(
        "wordlist.parquet not found. "
        "Run 'python -m gngram_lookup.download_data' to download the data files."
    )


def get_pos_hash_file(prefix: str) -> Path:
    """Return path to a specific POS hash bucket parquet file.

    Args:
        prefix: Two hex characters (00-ff)

    Returns:
        Path to the parquet file (may be in subdirectory from tar extraction)
    """
    direct = POS_DATA_DIR / f"{prefix}.parquet"
    if direct.exists():
        return direct

    nested = POS_DATA_DIR / "parquet-pos" / f"{prefix}.parquet"
    if nested.exists():
        return nested

    raise FileNotFoundError(
        f"POS data file not found for prefix '{prefix}'. "
        "Run 'python -m gngram_lookup.download_pos_data' to download the POS data files."
    )


def is_pos_data_installed() -> bool:
    """Check if POS data files are installed."""
    if not POS_DATA_DIR.exists():
        return False
    return any(POS_DATA_DIR.glob("**/*.parquet"))
