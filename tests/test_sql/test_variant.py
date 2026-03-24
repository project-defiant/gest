"""Tests for variant domain queries."""

from gest.sql.variant import VariantQuery


class TestVariantQueries:
    def test_number_of_variants(self, db_path: str) -> None:
        df = VariantQuery.NUMBER_OF_VARIANTS.value.to_metric("test").resolve_query(
            db_path
        )
        assert len(df) == 1
        assert df["number_of_variants"][0] == 3

    def test_total_count_of_variants(self, db_path: str) -> None:
        df = VariantQuery.TOTAL_COUNT_OF_VARIANTS.value.to_metric("test").resolve_query(
            db_path
        )
        assert len(df) == 1
        assert df["total_count_of_variants"][0] == 3

    def test_variants_per_max_effect_assessment(self, db_path: str) -> None:
        df = VariantQuery.VARIANTS_PER_MAX_EFFECT_ASSESSMENT.value.to_metric(
            "test"
        ).resolve_query(db_path)
        assert len(df) >= 1
        assert "max_assessment" in df.columns
        assert "number_of_variants" in df.columns
