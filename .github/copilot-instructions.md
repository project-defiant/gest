# Project Guidelines

## Code Style

- Target Python 3.13+ and keep code type-safe under strict `ty` checks.
- Follow existing style in `src/gest/*.py` and `app/*.py`: small typed functions, Pydantic models for schema, and concise Sphinx-style docstrings.
- Keep metric/domain names aligned with current code and SQL file stems (for example `number_of_studies`, `total_count_of_variants`).

## Architecture

- Core metric abstractions live in `src/gest/__init__.py` (`QueryFile`, `Metric`, `ReleaseReport`, `DomainTable`, `anti_join_sql`).
- CLI entry points are in `src/gest/cli.py` (`gest compute`, `gest diff`, `gest dashboard`).
- SQL metrics are organized by domain enums in `src/gest/sql/*/__init__.py`, each pointing to `.sql` files in the same directory.
- Streamlit UI entry is `app/main.py`; shared loading/rendering helpers are in `app/data.py`; domain pages are in `app/pages/*.py`.

## Build and Test

- Setup: `uv sync`
- Compute metrics: `uv run gest compute /path/to/release.db 26.03`
- Diff releases: `uv run gest diff /path/to/release_x.db /path/to/release_y.db 25.12 26.03`
- Run dashboard: `uv run streamlit run app/main.py` (or `uv run gest dashboard`)
- Lint/format/type-check: `uv run ruff check .`, `uv run ruff format .`, `uv run ty check`
- Tests: `uv run pytest tests/ -v`

## Project Conventions

- Every metric SQL query must project the release token (for example `'{release}' AS release`) because `Metric.resolve_query()` formats SQL via `.format(release=...)`.
- Add new metrics by adding a `.sql` file plus a `QueryFile` enum member in the matching domain module (for example `src/gest/sql/study/__init__.py`).
- `QueryResolver.all_queries()` derives `MetricResult.domain` from enum class names: `StudyQuery -> study`, `CredibleSetQuery -> credibleset`, `L2GPredictionQuery -> l2gprediction`, `ColocalisationQuery -> colocalisation`, `VariantQuery -> variant`.
- Be careful when touching Streamlit page filters in `app/main.py` and `app/pages/*.py`: sidebar multiselect keys are page-specific (`study_releases`, `cs_releases`, `coloc_releases`, `variant_releases`, `l2g_releases`).

## Integration Points

- Diff output is a DuckDB file under `metrics/` named like `diff_25_12_vs_26_03.duckdb`; pages read this via `load_diff_db()` and `load_diff_tables()` in `app/data.py`.
- `gest diff` uses DuckDB `ATTACH ... (READ_ONLY)` for both release databases and writes anti-join tables per domain.
- Release labels are sanitized in `src/gest/cli.py` using `_sanitize_label()` (dots/dashes become underscores) before output file/table naming.

## Security

- Treat input DuckDB paths as untrusted external data sources; keep `ATTACH` mode read-only as implemented in `src/gest/cli.py`.
- Do not weaken release-label sanitization or emit unsanitized identifiers into DuckDB object names.
- Avoid adding new SQL interpolation beyond the existing `{release}` placeholder pattern in checked-in SQL files under `src/gest/sql/`.
