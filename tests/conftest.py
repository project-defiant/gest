"""Shared test fixtures."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import duckdb
import pytest


@pytest.fixture
def db_path() -> Generator[str]:
    """Create a temporary DuckDB database with representative test data."""
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        path = f.name

    # Remove the empty file so DuckDB can create a fresh database
    Path(path).unlink()

    conn = duckdb.connect(path)

    # study table
    conn.execute("""
        CREATE TABLE study (
            studyId VARCHAR,
            studyType VARCHAR,
            projectId VARCHAR
        )
    """)
    conn.execute("""
        INSERT INTO study VALUES
            ('s1', 'gwas', 'GCST'),
            ('s2', 'gwas', 'GCST'),
            ('s3', 'eqtl', 'eQTL_Catalogue'),
            ('s4', 'pqtl', 'UKB_PPP')
    """)

    # credible_set table
    conn.execute("""
        CREATE TABLE credible_set (
            studyLocusId VARCHAR,
            studyId VARCHAR,
            studyType VARCHAR,
            variantId VARCHAR,
            locus INTEGER[]
        )
    """)
    conn.execute("""
        INSERT INTO credible_set VALUES
            ('sl1', 's1', 'gwas', 'v1', [1, 2, 3]),
            ('sl2', 's1', 'gwas', 'v2', [1, 2]),
            ('sl3', 's3', 'eqtl', 'v1', [1]),
            ('sl3', 's3', 'eqtl', 'v1', [1])
    """)

    # colocalisation table
    conn.execute("""
        CREATE TABLE colocalisation (
            leftStudyLocusId VARCHAR,
            rightStudyLocusId VARCHAR,
            colocalisationMethod VARCHAR,
            rightStudyType VARCHAR,
            h4 DOUBLE,
            clpp DOUBLE
        )
    """)
    conn.execute("""
        INSERT INTO colocalisation VALUES
            ('sl1', 'sl2', 'coloc', 'gwas', 0.9, 0.02),
            ('sl1', 'sl3', 'coloc', 'eqtl', 0.5, 0.005),
            ('sl2', 'sl3', 'coloc', 'eqtl', 0.85, 0.05)
    """)

    # variant table
    conn.execute("""
        CREATE TABLE variant (
            variantId VARCHAR,
            variantEffect STRUCT(assessment VARCHAR, score DOUBLE)[]
        )
    """)
    conn.execute("""
        INSERT INTO variant VALUES
            ('v1', [{'assessment': 'benign', 'score': 0.1}, {'assessment': 'pathogenic', 'score': 0.9}]),
            ('v2', [{'assessment': 'benign', 'score': 0.8}]),
            ('v3', [{'assessment': 'pathogenic', 'score': 0.7}])
    """)

    # l2g_prediction table
    conn.execute("""
        CREATE TABLE l2g_prediction (
            studyLocusId VARCHAR,
            geneId VARCHAR,
            score DOUBLE
        )
    """)
    conn.execute("""
        INSERT INTO l2g_prediction VALUES
            ('sl1', 'g1', 0.1),
            ('sl1', 'g2', 0.03),
            ('sl2', 'g1', 0.06),
            ('sl3', 'g3', 0.01)
    """)

    conn.close()

    yield path

    Path(path).unlink(missing_ok=True)


@pytest.fixture
def db_path_alt() -> Generator[str]:
    """Create an alternate DuckDB database with overlapping but different data."""
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        path = f.name

    Path(path).unlink()

    conn = duckdb.connect(path)

    # study table — s1, s2 overlap; s5 is new; s3, s4 removed
    conn.execute("""
        CREATE TABLE study (
            studyId VARCHAR,
            studyType VARCHAR,
            projectId VARCHAR
        )
    """)
    conn.execute("""
        INSERT INTO study VALUES
            ('s1', 'gwas', 'GCST'),
            ('s2', 'gwas', 'GCST'),
            ('s5', 'sqtl', 'eQTL_Catalogue')
    """)

    # credible_set table — sl1 overlaps; sl4 is new; sl2, sl3 removed
    conn.execute("""
        CREATE TABLE credible_set (
            studyLocusId VARCHAR,
            studyId VARCHAR,
            studyType VARCHAR,
            variantId VARCHAR,
            locus INTEGER[]
        )
    """)
    conn.execute("""
        INSERT INTO credible_set VALUES
            ('sl1', 's1', 'gwas', 'v1', [1, 2, 3]),
            ('sl4', 's5', 'sqtl', 'v3', [1, 2])
    """)

    # colocalisation table — first row overlaps; third removed; new row added
    conn.execute("""
        CREATE TABLE colocalisation (
            leftStudyLocusId VARCHAR,
            rightStudyLocusId VARCHAR,
            colocalisationMethod VARCHAR,
            rightStudyType VARCHAR,
            h4 DOUBLE,
            clpp DOUBLE
        )
    """)
    conn.execute("""
        INSERT INTO colocalisation VALUES
            ('sl1', 'sl2', 'coloc', 'gwas', 0.9, 0.02),
            ('sl1', 'sl4', 'coloc', 'sqtl', 0.7, 0.03)
    """)

    # variant table — v1 overlaps; v4 is new; v2, v3 removed
    conn.execute("""
        CREATE TABLE variant (
            variantId VARCHAR,
            variantEffect STRUCT(assessment VARCHAR, score DOUBLE)[]
        )
    """)
    conn.execute("""
        INSERT INTO variant VALUES
            ('v1', [{'assessment': 'benign', 'score': 0.1}]),
            ('v4', [{'assessment': 'pathogenic', 'score': 0.95}])
    """)

    # l2g_prediction table — (sl1, g1) overlaps; (sl4, g4) is new
    conn.execute("""
        CREATE TABLE l2g_prediction (
            studyLocusId VARCHAR,
            geneId VARCHAR,
            score DOUBLE
        )
    """)
    conn.execute("""
        INSERT INTO l2g_prediction VALUES
            ('sl1', 'g1', 0.1),
            ('sl4', 'g4', 0.5)
    """)

    conn.close()

    yield path

    Path(path).unlink(missing_ok=True)
