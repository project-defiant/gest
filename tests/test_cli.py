"""Tests for the CLI."""

import json
from pathlib import Path

import duckdb
from typer.testing import CliRunner

from gest.cli import app

runner = CliRunner()


class TestCLI:
    def test_compute(self, db_path: str, tmp_path: Path) -> None:
        result = runner.invoke(
            app, ["compute", db_path, "test_release", "--output-dir", str(tmp_path)]
        )
        assert result.exit_code == 0

        output_file = tmp_path / "test_release.json"
        assert output_file.exists()

        data = json.loads(output_file.read_text())
        assert data["release"] == "test_release"
        assert len(data["metrics"]) > 0

        domains = {m["domain"] for m in data["metrics"]}
        assert "study" in domains
        assert "colocalisation" in domains
        assert "credibleset" in domains
        assert "variant" in domains
        assert "l2gprediction" in domains


class TestDiff:
    def test_diff_creates_output_with_expected_tables(
        self, db_path: str, db_path_alt: str, tmp_path: Path
    ) -> None:
        result = runner.invoke(
            app,
            [
                "diff",
                db_path,
                db_path_alt,
                "25.12",
                "26.03",
                "--output-dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0

        output_file = tmp_path / "diff_25_12_vs_26_03.duckdb"
        assert output_file.exists()

        conn = duckdb.connect(str(output_file), read_only=True)
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
            ).fetchall()
        }
        conn.close()

        assert "study_only_in_25_12" in tables
        assert "study_only_in_26_03" in tables
        assert "variant_only_in_25_12" in tables
        assert "variant_only_in_26_03" in tables

    def test_diff_correct_row_counts(
        self, db_path: str, db_path_alt: str, tmp_path: Path
    ) -> None:
        runner.invoke(
            app,
            [
                "diff",
                db_path,
                db_path_alt,
                "25.12",
                "26.03",
                "--output-dir",
                str(tmp_path),
            ],
        )
        output_file = tmp_path / "diff_25_12_vs_26_03.duckdb"
        conn = duckdb.connect(str(output_file), read_only=True)

        def _count(table: str) -> int:
            row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
            assert row is not None
            return row[0]

        # study: db_path has s3, s4 not in alt; alt has s5 not in db_path
        assert _count("study_only_in_25_12") == 2
        assert _count("study_only_in_26_03") == 1

        # variant: db_path has v2, v3 not in alt; alt has v4 not in db_path
        assert _count("variant_only_in_25_12") == 2
        assert _count("variant_only_in_26_03") == 1

        # credible_set: db_path has sl2, sl3, sl3 not in alt; alt has sl4
        assert _count("credible_set_only_in_25_12") == 3
        assert _count("credible_set_only_in_26_03") == 1

        # colocalisation: db_path has (sl1,sl3,coloc), (sl2,sl3,coloc); alt has (sl1,sl4,coloc)
        assert _count("colocalisation_only_in_25_12") == 2
        assert _count("colocalisation_only_in_26_03") == 1

        # l2g: db_path has (sl1,g2), (sl2,g1), (sl3,g3); alt has (sl4,g4)
        assert _count("l2g_prediction_only_in_25_12") == 3
        assert _count("l2g_prediction_only_in_26_03") == 1

        conn.close()

    def test_diff_identical_dbs_produce_empty_tables(
        self, db_path: str, tmp_path: Path
    ) -> None:
        result = runner.invoke(
            app,
            ["diff", db_path, db_path, "a", "b", "--output-dir", str(tmp_path)],
        )
        assert result.exit_code == 0

        output_file = tmp_path / "diff_a_vs_b.duckdb"
        conn = duckdb.connect(str(output_file), read_only=True)

        table_counts = {
            row[0]: conn.execute(f"SELECT COUNT(*) FROM {row[0]}").fetchone()[0]
            for row in conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
            ).fetchall()
        }

        assert table_counts["l2gprediction_correlation_stats"] == 1
        assert table_counts["l2gprediction_significant_changes"] == 0
        assert table_counts["l2gprediction_score_sample"] > 0

        for table_name, count in table_counts.items():
            if table_name.startswith("l2gprediction_"):
                continue
            assert count == 0, f"Expected 0 rows in {table_name}, got {count}"

        conn.close()

    def test_diff_skips_missing_tables(
        self, db_path: str, db_path_alt: str, tmp_path: Path
    ) -> None:
        """Tables like 'target' that don't exist in either DB are skipped."""
        result = runner.invoke(
            app,
            [
                "diff",
                db_path,
                db_path_alt,
                "25.12",
                "26.03",
                "--output-dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0

        output_file = tmp_path / "diff_25_12_vs_26_03.duckdb"
        conn = duckdb.connect(str(output_file), read_only=True)
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
            ).fetchall()
        }
        conn.close()

        # target table doesn't exist in test fixtures, so no target tables should be created
        assert "target_only_in_25_12" not in tables
        assert "target_only_in_26_03" not in tables
