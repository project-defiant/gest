"""CLI for computing release metrics."""

import sys
from datetime import datetime, timezone
from pathlib import Path

import typer
from loguru import logger

from duckdb import connect

from gest import (
    DOMAIN_TABLES,
    MetricResult,
    QueryResolver,
    ReleaseReport,
    anti_join_sql,
    l2g_score_comparison_sqls,
)

app = typer.Typer(help="Gest: OpenTargets release metrics tool.")


@app.command()
def compute(
    db_path: str = typer.Argument(help="Path to the DuckDB database file."),
    release: str = typer.Argument(help="Release identifier (e.g. '24.12')."),
    output_dir: Path = typer.Option(
        Path("metrics"), help="Directory to write output JSON."
    ),
) -> None:
    """Compute all metrics for a release and write results to JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)

    all_queries = QueryResolver.all_queries()
    logger.info(f"Running {len(all_queries)} metrics for release {release}")

    results: list[MetricResult] = []
    for domain, query_file in all_queries:
        metric = query_file.to_metric(release)
        logger.info(f"  {domain}/{metric.view}")
        df = metric.resolve_query(db_path)
        results.append(
            MetricResult(
                domain=domain,
                name=metric.view,
                title=metric.metadata.title,
                description=metric.metadata.description,
                result=df.to_dicts(),
            )
        )

    report = ReleaseReport(
        release=release,
        computed_at=datetime.now(timezone.utc),
        metrics=results,
    )

    output_file = output_dir / f"{release}.json"
    output_file.write_text(report.model_dump_json(indent=2))
    logger.info(f"Wrote {output_file}")


def _sanitize_label(label: str) -> str:
    """Replace dots and dashes with underscores for valid DuckDB identifiers."""
    return label.replace(".", "_").replace("-", "_")


@app.command()
def diff(
    db_path_x: str = typer.Argument(help="Path to the first DuckDB database file."),
    db_path_y: str = typer.Argument(help="Path to the second DuckDB database file."),
    release_x: str = typer.Argument(help="Release label for the first database."),
    release_y: str = typer.Argument(help="Release label for the second database."),
    output_dir: Path = typer.Option(
        Path("metrics"), help="Directory to write output DuckDB file."
    ),
) -> None:
    """Compare two release databases and output rows unique to each."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = (
        output_dir
        / f"diff_{_sanitize_label(release_x)}_vs_{_sanitize_label(release_y)}.duckdb"
    )

    with connect(str(output_file)) as conn:
        conn.execute(f"ATTACH '{db_path_x}' AS release_x (READ_ONLY)")
        conn.execute(f"ATTACH '{db_path_y}' AS release_y (READ_ONLY)")

        label_x = _sanitize_label(release_x)
        label_y = _sanitize_label(release_y)

        tables_x = [
            row[0]
            for row in conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_catalog = 'release_x'"
            ).fetchall()
        ]
        tables_y = [
            row[0]
            for row in conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_catalog = 'release_y'"
            ).fetchall()
        ]

        for table in DOMAIN_TABLES:
            if table.name not in tables_x or table.name not in tables_y:
                logger.warning(f"Skipping {table.name}: not found in both databases")
                continue

            only_in_x = f"{table.name}_only_in_{label_x}"
            only_in_y = f"{table.name}_only_in_{label_y}"

            conn.execute(anti_join_sql("release_x", "release_y", table, only_in_x))
            conn.execute(anti_join_sql("release_y", "release_x", table, only_in_y))

            count_x = conn.execute(f"SELECT COUNT(*) FROM {only_in_x}").fetchone()[0]  # type: ignore[index]
            count_y = conn.execute(f"SELECT COUNT(*) FROM {only_in_y}").fetchone()[0]  # type: ignore[index]
            logger.info(
                f"{table.name}: {count_x} only in {release_x}, {count_y} only in {release_y}"
            )

        if "l2g_prediction" in tables_x and "l2g_prediction" in tables_y:
            for table_name, sql in l2g_score_comparison_sqls(
                "release_x", "release_y", release_x, release_y
            ):
                conn.execute(sql)
                count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]  # type: ignore[index]
                logger.info(f"{table_name}: {count:,} rows")

    logger.info(f"Wrote {output_file}")


@app.command()
def dashboard() -> None:
    """Launch the Streamlit dashboard."""
    from streamlit.web.cli import main as st_main

    app_path = str(Path(__file__).resolve().parent.parent.parent / "app" / "main.py")
    sys.argv = ["streamlit", "run", app_path]
    st_main()
