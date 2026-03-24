# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup
uv sync                            # Install dependencies

# Run
python main.py                     # Entry point

# Lint & format
uv run ruff check .                # Lint
uv run ruff format .               # Format

# Type check
uv run ty check                    # Type checking (strict mode)

# Tests (pytest not yet in dependencies — add it to dev group first)
uv run pytest . --doctest-modules --cov=src/
```

## Architecture

**Domain**: Genomics data analytics — metrics over GWAS/QTL studies, colocalisation, credible sets, and L2G predictions, stored in DuckDB.

**Core abstractions** (`src/gest/__init__.py`):
- `Metadata` — title + description for a query
- `QueryFile` — path to a `.sql` file + metadata; converts to `Metric` via `to_metric(release)`
- `Metric` — holds a SQL string, substitutes `{release}` placeholder, creates a DuckDB temporary view, and returns results as a Polars `LazyFrame`
- `QueryResolver` — stub for discovering queries by metadata
- `DomainTable` — table name + uniqueness keys for anti-join comparisons
- `DOMAIN_TABLES` — registry of all domain tables (`study`, `variant`, `credible_set`, `colocalisation`, `l2g_prediction`, `target`)
- `anti_join_sql()` — generates LEFT JOIN anti-join SQL between two attached databases

**Query organisation** (`src/gest/sql/`): Each domain has a subdirectory with an `__init__.py` defining an enum of `QueryFile` instances and the actual `.sql` files. Domains: `study/`, `colocalisation/`, `credible_set/`, `variant/`, `l2g_prediction/`, `association/`.

**Adding a new metric**: write the SQL file in the appropriate domain folder, add a `QueryFile` entry to that domain's enum, call `.to_metric(release).resolve_query(db_path)` to execute it.

## Tooling notes

- Package manager: `uv` (Python 3.13+)
- Linter/formatter: `ruff` (format on save configured in VS Code)
- Type checker: `ty` in strict mode — all code must pass strict type checking
- Docstrings: Sphinx style
