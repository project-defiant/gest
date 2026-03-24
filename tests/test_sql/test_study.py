"""Tests for study domain queries."""

from gest.sql.study import StudyQuery


class TestStudyQueries:
    def test_number_of_studies(self, db_path: str) -> None:
        df = StudyQuery.NUMBER_OF_STUDIES.value.to_metric("test").resolve_query(db_path)
        assert len(df) == 1
        assert df["number_of_studies"][0] == 4

    def test_total_count_of_studies(self, db_path: str) -> None:
        df = StudyQuery.TOTAL_COUNT_OF_STUDIES.value.to_metric("test").resolve_query(
            db_path
        )
        assert len(df) == 1
        assert df["total_count_of_studies"][0] == 4

    def test_number_of_studies_per_study_type(self, db_path: str) -> None:
        df = StudyQuery.NUMBER_OF_STUDIES_PER_STUDY_TYPE.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) == 3
        assert "studyType" in df.columns
        assert "number_of_studies" in df.columns
