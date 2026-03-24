"""Tests for credible set domain queries."""

from gest.sql.credible_set import CredibleSetQuery


class TestCredibleSetQueries:
    def test_number_of_credible_sets(self, db_path: str) -> None:
        df = CredibleSetQuery.NUMBER_OF_CREDIBLE_SETS.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) == 1
        assert df["number_of_credible_sets"][0] == 3  # sl1, sl2, sl3

    def test_total_count_of_credible_sets(self, db_path: str) -> None:
        df = CredibleSetQuery.TOTAL_COUNT_OF_CREDIBLE_SETS.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) == 1
        assert df["total_count_of_credible_sets"][0] == 4  # 4 rows

    def test_number_of_credible_sets_per_study_type(self, db_path: str) -> None:
        df = CredibleSetQuery.NUMBER_OF_CREDIBLE_SETS_PER_STUDY_TYPE.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) == 2  # gwas, eqtl
        assert "studyType" in df.columns

    def test_number_of_credible_sets_per_project(self, db_path: str) -> None:
        df = CredibleSetQuery.NUMBER_OF_CREDIBLE_SETS_PER_PROJECT.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) >= 1
        assert "projectId" in df.columns

    def test_locus_size_stats(self, db_path: str) -> None:
        df = CredibleSetQuery.LOCUS_SIZE_STATS.value.to_metric("test").resolve_query(
            db_path
        )
        assert len(df) == 1
        assert "min_locus_size" in df.columns
        assert "max_locus_size" in df.columns

    def test_unique_lead_variants_per_study_type(self, db_path: str) -> None:
        df = CredibleSetQuery.UNIQUE_LEAD_VARIANTS_PER_STUDY_TYPE.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) >= 1
        assert "unique_lead_variants" in df.columns

    def test_unique_lead_variants_per_project(self, db_path: str) -> None:
        df = CredibleSetQuery.UNIQUE_LEAD_VARIANTS_PER_PROJECT.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) >= 1
        assert "projectId" in df.columns
