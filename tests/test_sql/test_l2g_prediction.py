"""Tests for L2G prediction domain queries."""

from gest.sql.l2g_prediction import L2GPredictionQuery


class TestL2GPredictionQueries:
    def test_total_count_of_predictions(self, db_path: str) -> None:
        df = L2GPredictionQuery.TOTAL_COUNT_OF_PREDICTIONS.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) == 1
        assert df["total_count_of_predictions"][0] == 4

    def test_number_of_significant_predictions(self, db_path: str) -> None:
        df = L2GPredictionQuery.NUMBER_OF_SIGNIFICANT_PREDICTIONS.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) == 1
        assert (
            df["number_of_significant_predictions"][0] == 2
        )  # score >= 0.05: 0.1, 0.06

    def test_gene_count_per_study_locus(self, db_path: str) -> None:
        df = L2GPredictionQuery.GENE_COUNT_PER_STUDY_LOCUS.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) >= 1
        assert "gene_count" in df.columns
        assert "number_of_study_loci" in df.columns
