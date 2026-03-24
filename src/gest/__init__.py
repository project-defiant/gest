"""Core abstractions for the gest metrics library."""

from datetime import datetime
from pathlib import Path
from typing import Any

from duckdb import connect
from polars import DataFrame
from pydantic import BaseModel


class Metadata(BaseModel):
    """Class representing the metadata for a metric."""

    description: str
    title: str


class Metric(BaseModel):
    """Class representing a metric with its query."""

    query: str
    metadata: Metadata
    release: str
    view: str

    def resolve_query(self, db_path: str) -> DataFrame:
        """Execute the query against a DuckDB database and return results.

        :param db_path: Path to the DuckDB database file.
        :return: A Polars DataFrame with query results.
        """
        query = self.query.format(release=self.release).rstrip().rstrip(";")
        with connect(db_path) as conn:
            conn.execute(f"CREATE OR REPLACE TEMPORARY VIEW {self.view} AS ({query})")
            result = conn.execute(f"SELECT * FROM {self.view}").pl()
        return result


class QueryFile(BaseModel):
    """Class representing a query file containing multiple metrics."""

    file: str
    metadata: Metadata

    def to_metric(self, release: str) -> Metric:
        """Convert the query file into a Metric instance.

        :param release: The release identifier to substitute in the query.
        :return: A Metric instance.
        """
        view_name = Path(self.file).stem
        with open(self.file) as f:
            query = f.read()
        return Metric(
            query=query, metadata=self.metadata, view=view_name, release=release
        )


class MetricResult(BaseModel):
    """Result of executing a single metric query."""

    domain: str
    name: str
    title: str
    description: str
    result: list[dict[str, Any]]


class ReleaseReport(BaseModel):
    """Collection of metric results for a single release."""

    release: str
    computed_at: datetime
    metrics: list[MetricResult]


class DomainTable(BaseModel):
    """A domain table with its uniqueness keys for anti-join comparisons."""

    name: str
    keys: list[str]


DOMAIN_TABLES: list[DomainTable] = [
    DomainTable(name="study", keys=["studyId"]),
    DomainTable(name="variant", keys=["variantId"]),
    DomainTable(name="credible_set", keys=["studyLocusId"]),
    DomainTable(
        name="colocalisation",
        keys=["leftStudyLocusId", "rightStudyLocusId", "colocalisationMethod"],
    ),
    DomainTable(name="l2g_prediction", keys=["studyLocusId", "geneId"]),
    DomainTable(name="target", keys=["id"]),
]


def anti_join_sql(
    left_db: str,
    right_db: str,
    table: DomainTable,
    output_table: str,
) -> str:
    """Generate SQL for an anti-join between two attached databases.

    :param left_db: Alias of the left (source) database.
    :param right_db: Alias of the right (comparison) database.
    :param table: The domain table definition with keys.
    :param output_table: Name for the output table.
    :return: A CREATE TABLE AS SELECT anti-join SQL string.
    """
    on_clause = " AND ".join(f"l.{k} = r.{k}" for k in table.keys)
    where_clause = f"r.{table.keys[0]} IS NULL"
    return (
        f"CREATE TABLE {output_table} AS "
        f"SELECT l.* FROM {left_db}.{table.name} l "
        f"LEFT JOIN {right_db}.{table.name} r ON {on_clause} "
        f"WHERE {where_clause}"
    )


def l2g_score_comparison_sqls(
    left_db: str, right_db: str, release_x: str, release_y: str
) -> list[tuple[str, str]]:
    """Return (table_name, sql) pairs for l2g score comparison tables.

    :param left_db: Alias of the left (old) database.
    :param right_db: Alias of the right (new) database.
    :param release_x: Release label for the left database.
    :param release_y: Release label for the right database.
    :return: List of (table_name, CREATE TABLE AS sql) tuples.
    """
    correlation_sql = (
        f"CREATE TABLE l2gprediction_correlation_stats AS "
        f"SELECT "
        f"    corr(x.score, y.score) AS pearson_r, "
        f"    COUNT(*) AS n_common_pairs, "
        f"    '{release_x}' AS release_old, "
        f"    '{release_y}' AS release_new "
        f"FROM {left_db}.l2g_prediction x "
        f"JOIN {right_db}.l2g_prediction y "
        f"    ON x.studyLocusId = y.studyLocusId AND x.geneId = y.geneId"
    )

    changes_sql = (
        f"CREATE TABLE l2gprediction_significant_changes AS "
        f"SELECT "
        f"    x.studyLocusId, "
        f"    x.geneId, "
        f"    x.score AS score_old, "
        f"    y.score AS score_new, "
        f"    y.score - x.score AS delta, "
        f"    ABS(y.score - x.score) > 0.5 AS delta_above_50pct, "
        f"    (x.score < 0.05 AND y.score >= 0.05) AS score_crossed_threshold "
        f"FROM {left_db}.l2g_prediction x "
        f"JOIN {right_db}.l2g_prediction y "
        f"    ON x.studyLocusId = y.studyLocusId AND x.geneId = y.geneId "
        f"WHERE ABS(y.score - x.score) > 0.5 OR (x.score < 0.05 AND y.score >= 0.05) "
        f"ORDER BY ABS(y.score - x.score) DESC"
    )

    sample_sql = (
        f"CREATE TABLE l2gprediction_score_sample AS "
        f"SELECT * FROM ("
        f"    SELECT "
        f"        x.studyLocusId, x.geneId, "
        f"        x.score AS score_old, y.score AS score_new, "
        f"        y.score - x.score AS delta, "
        f"        ABS(y.score - x.score) > 0.5 AS delta_above_50pct, "
        f"        (x.score < 0.05 AND y.score >= 0.05) AS score_crossed_threshold "
        f"    FROM {left_db}.l2g_prediction x "
        f"    JOIN {right_db}.l2g_prediction y "
        f"        ON x.studyLocusId = y.studyLocusId AND x.geneId = y.geneId"
        f") USING SAMPLE reservoir(50000 ROWS)"
    )

    return [
        ("l2gprediction_correlation_stats", correlation_sql),
        ("l2gprediction_significant_changes", changes_sql),
        ("l2gprediction_score_sample", sample_sql),
    ]


class QueryResolver:
    """Discovers all query files across all domains."""

    @staticmethod
    def all_queries() -> list[tuple[str, "QueryFile"]]:
        """Collect all (domain, QueryFile) pairs from all domain enums.

        :return: List of (domain_name, QueryFile) tuples.
        """
        from gest.sql.colocalisation import ColocalisationQuery
        from gest.sql.credible_set import CredibleSetQuery
        from gest.sql.l2g_prediction import L2GPredictionQuery
        from gest.sql.study import StudyQuery
        from gest.sql.variant import VariantQuery

        queries: list[tuple[str, QueryFile]] = []
        for domain_enum in [
            StudyQuery,
            ColocalisationQuery,
            CredibleSetQuery,
            VariantQuery,
            L2GPredictionQuery,
        ]:
            domain_name = domain_enum.__name__.replace("Query", "").lower()
            for member in domain_enum:
                queries.append((domain_name, member.value))
        return queries
