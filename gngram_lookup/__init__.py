"""gngram-lookup: Google Ngram frequency lookup."""

from gngram_lookup.data import get_data_dir, get_hash_file, is_data_installed, is_pos_data_installed
from gngram_lookup.find_suffixes import get_suffixes
from gngram_lookup.find_inflections import get_inflections
from gngram_lookup.morphology import Morphology, get_morphology
from gngram_lookup.lookup import FrequencyData, batch_frequency, erosion_cluster, exists, frequency, prefix_cluster, word_score, wordlist
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
    "wordlist",
    "prefix_cluster",
    "erosion_cluster",
    "pos",
    "pos_freq",
    "has_pos",
    "PosTag",
    "get_suffixes",
    "get_inflections",
    "Morphology",
    "get_morphology",
]
