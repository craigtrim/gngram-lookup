"""gngram-lookup: Google Ngram frequency lookup."""

from gngram_lookup.data import get_data_dir, get_hash_file, is_data_installed, is_pos_data_installed
from gngram_lookup.lookup import FrequencyData, batch_frequency, exists, frequency, word_score
from gngram_lookup.pos import PosTag, has_pos, pos, pos_freq

__all__ = [
    "get_data_dir",
    "get_hash_file",
    "is_data_installed",
    "is_pos_data_installed",
    "exists",
    "frequency",
    "batch_frequency",
    "FrequencyData",
    "word_score",
    "pos",
    "pos_freq",
    "has_pos",
    "PosTag",
]
