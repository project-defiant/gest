"""Tests for core gest models."""

from datetime import datetime, timezone

from gest import Metadata, MetricResult, ReleaseReport


class TestMetadata:
    def test_creation(self) -> None:
        m = Metadata(title="Test", description="A test metric.")
        assert m.title == "Test"
        assert m.description == "A test metric."


class TestQueryFile:
    def test_to_metric(self, db_path: str) -> None:
        from gest.sql.study import StudyQuery

        qf = StudyQuery.NUMBER_OF_STUDIES.value
        metric = qf.to_metric("24.12")
        assert metric.release == "24.12"
        assert metric.view == "number_of_studies"
        assert "{release}" in metric.query  # placeholder preserved until resolve_query

    def test_resolve_query(self, db_path: str) -> None:
        from gest.sql.study import StudyQuery

        qf = StudyQuery.NUMBER_OF_STUDIES.value
        metric = qf.to_metric("24.12")
        df = metric.resolve_query(db_path)
        assert len(df) == 1
        assert "number_of_studies" in df.columns
        assert "release" in df.columns


class TestMetricResult:
    def test_creation(self) -> None:
        mr = MetricResult(
            domain="study",
            name="number_of_studies",
            title="Number of studies",
            description="Count of distinct studies.",
            result=[{"number_of_studies": 4, "release": "24.12"}],
        )
        assert mr.domain == "study"
        assert len(mr.result) == 1


class TestReleaseReport:
    def test_serialization(self) -> None:
        report = ReleaseReport(
            release="24.12",
            computed_at=datetime(2024, 12, 1, tzinfo=timezone.utc),
            metrics=[
                MetricResult(
                    domain="study",
                    name="test",
                    title="Test",
                    description="Test metric.",
                    result=[{"value": 1}],
                )
            ],
        )
        json_str = report.model_dump_json()
        restored = ReleaseReport.model_validate_json(json_str)
        assert restored.release == "24.12"
        assert len(restored.metrics) == 1
