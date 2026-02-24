from gngram_lookup import PosTag


class TestPosTag:
    def test_enum_values_are_strings(self):
        assert PosTag.VERB == "VERB"
        assert PosTag.NOUN == "NOUN"

    def test_all_tags_present(self):
        tags = {t.value for t in PosTag}
        assert tags == {"NOUN", "VERB", "ADJ", "ADV", "PRON", "DET", "ADP", "NUM", "CONJ", "PRT", "X"}
