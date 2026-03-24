"""Tests for Streamlit data source resolution."""

from datetime import datetime, timezone

from app import data
from gest import MetricResult, ReleaseReport


def _write_report(metrics_dir: str) -> None:
    report = ReleaseReport(
        release="26.03",
        computed_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
        metrics=[
            MetricResult(
                domain="study",
                name="total_count_of_studies",
                title="Total count of studies",
                description="Count of studies.",
                result=[{"total_count_of_studies": 1, "release": "26.03"}],
            )
        ],
    )
    report_path = f"{metrics_dir}/26_03.json"
    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report.model_dump_json())


def test_extract_hf_dataset_id() -> None:
    assert data._extract_hf_dataset_id("owner/repo") == "owner/repo"
    assert data._extract_hf_dataset_id("hf://datasets/owner/repo") == "owner/repo"
    assert (
        data._extract_hf_dataset_id("https://huggingface.co/datasets/owner/repo")
        == "owner/repo"
    )
    assert data._extract_hf_dataset_id("./metrics") is None
    assert data._extract_hf_dataset_id("/tmp/metrics") is None


def test_load_all_reports_uses_metrics_path_env(tmp_path, monkeypatch) -> None:
    metrics_dir = tmp_path / "metrics"
    metrics_dir.mkdir()
    _write_report(str(metrics_dir))

    monkeypatch.setenv(data.METRICS_PATH_ENV, str(metrics_dir))
    data.load_all_reports.clear()

    reports = data.load_all_reports()

    assert len(reports) == 1
    assert reports[0].release == "26.03"


def test_resolve_metrics_path_downloads_hf_dataset(monkeypatch, tmp_path) -> None:
    expected_dir = tmp_path / "hf_snapshot"
    expected_dir.mkdir()

    monkeypatch.setenv(data.METRICS_PATH_ENV, "org/release-metrics")

    captured: dict[str, object] = {}

    def _fake_snapshot_download(**kwargs: object) -> str:
        captured.update(kwargs)
        return str(expected_dir)

    monkeypatch.setattr(data, "snapshot_download", _fake_snapshot_download)

    resolved = data._resolve_metrics_path()

    assert resolved == expected_dir
    assert captured["repo_id"] == "org/release-metrics"
    assert captured["repo_type"] == "dataset"
