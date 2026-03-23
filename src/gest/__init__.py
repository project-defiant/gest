from pathlib import Path

from duckdb import connect
from polars import LazyFrame
from pydantic import BaseModel


class Metadata(BaseModel):
    """Class representing the metadata for a metric."""

    description: str
    title: str


class Metric(BaseModel):
    """Class representing a metric with its query"""

    query: str
    metadata: Metadata
    release: str
    view: str

    def resolve_query(self, db_path: str) -> LazyFrame:
        """Method to resolve the query based on the metadata and tables."""
        query = self.query.format(release=self.release)
        with connect(db_path) as conn:
            # CREATE temporary view if not exist
            conn.execute(
                f"CREATE IF NOT EXISTS TEMPORARY VIEW {self.view} AS ({query})"
            )
            # Get the result as a LazyFrame
            result = conn.execute(f"SELECT * FROM {self.view}").pl(lazy=True)
        return result


class QueryFile(BaseModel):
    """Class representing a query file containing multiple metrics."""

    file: str
    metadata: Metadata

    def to_metric(self, release: str) -> Metric:
        """Method to convert the query file into a Metric instance."""
        view_name = Path(self.file).stem.replace(".sql", "")
        with open(self.file, "r") as f:
            query = f.read()
        return Metric(
            query=query, metadata=self.metadata, view=view_name, release=release
        )


class QueryResolver(BaseModel):
    """Class to find queries based on the provided metadata."""
