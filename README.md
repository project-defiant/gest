---
title: Gest
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
pinned: false
short_description: Genetics data tests
license: mit
---

# Welcome to Streamlit!

Edit `/src/streamlit_app.py` to customize this app to your heart's desire. :heart:

If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).
# Gest

Genomics metrics tool for comparing OpenTargets Genetics releases. Computes metrics over GWAS/QTL studies, colocalisation, credible sets, L2G predictions, and variants stored in DuckDB, then visualises them in a Streamlit dashboard.

## Setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

The input DuckDB release databases used by `gest compute` and `gest diff` should be generated with the `seqqurat` package from OpenTargets.

### 1. Compute metrics

Run the `gest compute` command against a DuckDB database for each release you want to compare:

```bash
gest compute /path/to/release_24_12.db 24.12
gest compute /path/to/release_25_03.db 25.03
```

This writes a JSON report per release into the `metrics/` directory (default). Use `--output-dir` to change the location:

```bash
gest compute /path/to/db 24.12 --output-dir my_metrics
```

### 2. Diff two releases

Compare two release databases row-by-row to find which rows are unique to each release:

```bash
gest diff /path/to/release_25_12.db /path/to/release_26_03.db 25.12 26.03
```

This creates a DuckDB file at `metrics/diff_25_12_vs_26_03.duckdb` containing tables named `{domain}_only_in_{release}` for each direction (e.g. `study_only_in_25_12`, `study_only_in_26_03`). Use `--output-dir` to change the output location.

Tables that don't exist in both databases are skipped with a warning.

### 3. Start the dashboard

```bash
streamlit run app/main.py
```

The app reads all JSON reports from `metrics/` and displays every metric with a chart, data table, and CSV download button. Use the sidebar to select which releases to compare.

To override the metrics source, set `METRICS_PATH`:

```bash
# Local directory
METRICS_PATH=/path/to/metrics streamlit run app/main.py

# Hugging Face dataset repo
METRICS_PATH=owner/dataset-name streamlit run app/main.py
```

Domain-specific pages (Study, Credible Set, Colocalisation, Variant, L2G Prediction) are available in the sidebar navigation.

## Development

```bash
uv run ruff check .           # lint
uv run ruff format .          # format
uv run ty check               # type check (strict)
uv run pytest tests/ -v       # run tests
```

## Project structure

```
src/gest/
  __init__.py          # Core abstractions: Metric, QueryFile, ReleaseReport, QueryResolver, DomainTable
  cli.py               # CLI (typer): gest compute, gest diff
  sql/                 # SQL queries organised by domain
    study/
    colocalisation/
    credible_set/
    variant/
    l2g_prediction/

app/
  main.py              # Streamlit overview page
  data.py              # Data loading + render_metric() helper
  pages/               # Domain-specific Streamlit pages

metrics/               # Generated JSON reports (one per release)
```
