"""Tests for colocalisation domain queries."""

from gest.sql.colocalisation import ColocalisationQuery


class TestColocalisationQueries:
    def test_total_count_of_colocalisations(self, db_path: str) -> None:
        df = ColocalisationQuery.TOTAL_COUNT_OF_COLOCALISATIONS.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) == 1
        assert df["total_count_of_colocalisations"][0] == 3

    def test_number_of_significant_clpp(self, db_path: str) -> None:
        df = ColocalisationQuery.NUMBER_OF_SIGNIFICANT_CLPP.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) == 1
        assert df["number_of_significant_clpp"][0] == 2  # clpp >= 0.01: 0.02, 0.05

    def test_number_of_significant_h4(self, db_path: str) -> None:
        df = ColocalisationQuery.NUMBER_OF_SIGNIFICANT_H4.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) == 1
        assert df["number_of_significant_h4"][0] == 2  # h4 >= 0.8: 0.9, 0.85

    def test_number_of_unique_pairs_significant_clpp(self, db_path: str) -> None:
        df = (
            ColocalisationQuery.NUMBER_OF_UNIQUE_PAIRS_SIGNIFICANT_CLPP.value.to_metric(
                "test"
            ).resolve_query(db_path)
        )
        assert len(df) == 1
        assert df["number_of_unique_pairs_significant_clpp"][0] == 2

    def test_number_of_unique_pairs_significant_h4(self, db_path: str) -> None:
        df = ColocalisationQuery.NUMBER_OF_UNIQUE_PAIRS_SIGNIFICANT_H4.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) == 1

    def test_number_of_significant_clpp_per_study_type(self, db_path: str) -> None:
        df = ColocalisationQuery.NUMBER_OF_SIGNIFICANT_CLPP_PER_STUDY_TYPE.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert "rightStudyType" in df.columns

    def test_number_of_unique_pairs_significant_clpp_per_study_type(
        self, db_path: str
    ) -> None:
        df = ColocalisationQuery.NUMBER_OF_UNIQUE_PAIRS_SIGNIFICANT_CLPP_PER_STUDY_TYPE.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert "rightStudyType" in df.columns

    def test_number_of_significant_h4_per_study_type(self, db_path: str) -> None:
        df = (
            ColocalisationQuery.NUMBER_OF_SIGNIFICANT_H4_PER_STUDY_TYPE.value.to_metric(
                "test"
            ).resolve_query(db_path)
        )
        assert "rightStudyType" in df.columns

    def test_number_of_unique_pairs_significant_h4_per_study_type(
        self, db_path: str
    ) -> None:
        df = ColocalisationQuery.NUMBER_OF_UNIQUE_PAIRS_SIGNIFICANT_H4_PER_STUDY_TYPE.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert "rightStudyType" in df.columns
