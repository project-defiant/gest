"""Data loading utilities for the Streamlit app."""

import os
import tempfile
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from huggingface_hub import snapshot_download
except ImportError:  # pragma: no cover - exercised when optional dep is missing
    snapshot_download = None  # type: ignore[assignment]

from gest import ReleaseReport

DIFF_PREVIEW_ROWS = 10
METRICS_PATH_ENV = "METRICS_PATH"
HF_DATASET_PREFIX = "hf://datasets/"
HF_DATASET_WEB_PREFIX = "https://huggingface.co/datasets/"


def _extract_hf_dataset_id(metrics_path: str) -> str | None:
    """Extract a Hugging Face dataset repo ID from a metrics path string.

    :param metrics_path: Input metrics path candidate.
    :return: Dataset repo ID when the input encodes a HF dataset, otherwise ``None``.
    """
    cleaned = metrics_path.strip().rstrip("/")

    if cleaned.startswith(HF_DATASET_PREFIX):
        repo_id = cleaned.removeprefix(HF_DATASET_PREFIX).strip("/")
        return repo_id or None

    if cleaned.startswith(HF_DATASET_WEB_PREFIX):
        repo_id = cleaned.removeprefix(HF_DATASET_WEB_PREFIX).strip("/")
        return repo_id or None

    if cleaned.startswith(("/", "./", "../", "~")):
        return None

    if cleaned.count("/") == 1 and " " not in cleaned:
        owner, name = cleaned.split("/", maxsplit=1)
        if owner and name:
            return cleaned

    return None


def _resolve_metrics_path(metrics_dir: str = "metrics") -> Path:
    """Resolve where to read metrics from.

    Reads from ``METRICS_PATH`` when set; otherwise falls back to ``metrics_dir``.
    Supports local directories and Hugging Face dataset references.

    :param metrics_dir: Local fallback metrics directory.
    :return: Local path containing metric JSON and diff DuckDB files.
    """
    source = os.getenv(METRICS_PATH_ENV, metrics_dir)
    source_path = Path(source).expanduser()
    if source_path.exists():
        return source_path

    repo_id = _extract_hf_dataset_id(source)
    if repo_id is None:
        return source_path

    if snapshot_download is None:
        msg = (
            "Hugging Face metrics source configured but dependency is missing. "
            "Install `huggingface-hub` to use dataset-backed metrics."
        )
        raise RuntimeError(msg)

    snapshot_path = snapshot_download(
        repo_id=repo_id,
        repo_type="dataset",
        allow_patterns=["*.json", "diff_*.duckdb"],
    )
    return Path(snapshot_path)


def _format_diff_label(table_name: str, domain: str) -> str:
    """Create a readable label from a diff table name.

    :param table_name: Diff table name (for example ``study_only_in_25_12``).
    :param domain: Domain prefix used in the table name.
    :return: Human-readable section label.
    """
    suffix = table_name.replace(f"{domain}_", "", 1)
    if suffix.startswith("only_in_"):
        release_label = suffix.replace("only_in_", "", 1)
        return f"Only in {release_label}"
    return suffix.replace("_", " ").title()


@st.cache_data
def load_all_reports(metrics_dir: str = "metrics") -> list[ReleaseReport]:
    """Load all release report JSON files from the metrics directory.

    :param metrics_dir: Local fallback path containing JSON report files.
        The ``METRICS_PATH`` env var overrides this and may point to a local
        folder or a Hugging Face dataset repo.
    :return: List of ReleaseReport objects.
    """
    metrics_path = _resolve_metrics_path(metrics_dir)
    if not metrics_path.exists():
        return []
    reports = []
    for f in sorted(metrics_path.glob("*.json")):
        reports.append(ReleaseReport.model_validate_json(f.read_text()))
    return reports


def metrics_to_dataframe(
    reports: list[ReleaseReport], metric_name: str
) -> pd.DataFrame:
    """Extract a specific metric from all reports into a single DataFrame.

    :param reports: List of ReleaseReport objects.
    :param metric_name: The name of the metric to extract.
    :return: DataFrame with results from all releases combined.
    """
    rows: list[dict[str, object]] = []
    for report in reports:
        for metric in report.metrics:
            if metric.name == metric_name:
                for row in metric.result:
                    rows.append({**row, "release": report.release})
    return pd.DataFrame(rows)


def _humanize(col: str) -> str:
    return col.replace("_", " ").title()


def _rows_per_release(df: pd.DataFrame) -> int:
    return int(df.groupby("release").size().max())


def render_metric(df: pd.DataFrame, title: str, metric_name: str) -> None:
    """Render a metric as KPI cards + table + CSV download.

    :param df: DataFrame containing the metric data with a ``release`` column.
    :param title: Display title for the metric section.
    :param metric_name: Unique metric identifier (used for widget keys).
    """
    if df.empty:
        return

    st.subheader(title)

    non_release_cols = [c for c in df.columns if c != "release"]
    numeric_cols = [c for c in non_release_cols if pd.api.types.is_numeric_dtype(df[c])]
    string_cols = [
        c for c in non_release_cols if df[c].dtype == object and c not in numeric_cols
    ]

    if not numeric_cols:
        st.dataframe(df, use_container_width=True)
        st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False),
            file_name=f"{metric_name}.csv",
            mime="text/csv",
            key=f"download_{metric_name}",
        )
        return

    def _format_value(value: float | int | None) -> str:
        if value is None or pd.isna(value):
            return "—"
        value_float = float(value)
        if value_float.is_integer():
            return f"{int(value_float):,}"
        return f"{value_float:,.2f}"

    selected_releases = list(df["release"].astype(str).drop_duplicates())
    latest_release = selected_releases[-1]
    previous_release = selected_releases[-2] if len(selected_releases) > 1 else None
    latest_df = df[df["release"] == latest_release]
    previous_df = df[df["release"] == previous_release] if previous_release else None

    if string_cols:
        value_col = numeric_cols[0]
        latest_total = float(latest_df[value_col].sum())
        latest_groups = float(latest_df[string_cols[0]].nunique())
        previous_total = (
            float(previous_df[value_col].sum()) if previous_df is not None else None
        )

        col_total, col_groups = st.columns(2)
        col_total.metric(
            label=f"Total {value_col.replace('_', ' ').title()}",
            value=_format_value(latest_total),
            delta=(
                _format_value(latest_total - previous_total)
                if previous_total is not None
                else None
            ),
            help=f"Release: {latest_release}",
        )
        col_groups.metric(
            label=f"Distinct {string_cols[0].replace('_', ' ').title()}",
            value=_format_value(latest_groups),
            help=f"Release: {latest_release}",
        )
    else:
        metric_cols = st.columns(len(numeric_cols))
        for column, value_col in zip(metric_cols, numeric_cols, strict=False):
            latest_value = float(latest_df[value_col].sum())
            previous_value = (
                float(previous_df[value_col].sum()) if previous_df is not None else None
            )
            column.metric(
                label=value_col.replace("_", " ").title(),
                value=_format_value(latest_value),
                delta=(
                    _format_value(latest_value - previous_value)
                    if previous_value is not None
                    else None
                ),
                help=f"Release: {latest_release}",
            )

    is_distribution = bool(numeric_cols) and _rows_per_release(df) > 1

    if is_distribution and string_cols:
        # Type A: category × count grouped bar (horizontal, sorted)
        value_col = numeric_cols[0]
        category_col = string_cols[0]
        fig = px.bar(
            df,
            x=value_col,
            y=category_col,
            color="release",
            orientation="h",
            barmode="group",
            labels={
                value_col: _humanize(value_col),
                category_col: _humanize(category_col),
                "release": "Release",
            },
            template="plotly_white",
            title=title,
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    elif is_distribution and not string_cols and len(numeric_cols) == 2:
        # Type B: numeric frequency distribution (e.g. gene_count_per_study_locus)
        x_col, y_col = numeric_cols[0], numeric_cols[1]
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            color="release",
            barmode="group",
            labels={
                x_col: _humanize(x_col),
                y_col: _humanize(y_col),
                "release": "Release",
            },
            template="plotly_white",
            title=title,
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Raw data", expanded=False):
        st.caption(f"Rows: {len(df):,}")
        st.dataframe(df, use_container_width=True)
        st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False),
            file_name=f"{metric_name}.csv",
            mime="text/csv",
            key=f"download_{metric_name}",
        )


def render_count_group(
    reports: list[ReleaseReport],
    metric_names: list[str],
    section_title: str,
) -> None:
    """Render a group of scalar count metrics as KPI cards, a bar chart and a joined table.

    Collects one scalar value per metric per release, displays them as
    side-by-side ``st.metric`` KPI cards, then renders a grouped bar chart
    (X = metric label, colour = release) followed by a wide raw-data expander.

    :param reports: List of ReleaseReport objects (already filtered by selected releases).
    :param metric_names: Ordered list of metric name identifiers to group together.
    :param section_title: Display title shown as the section subheader.
    """
    # Collect series: metric_name → {release: value}
    series: dict[str, dict[str, float]] = {}
    titles: dict[str, str] = {}

    for metric_name in metric_names:
        for report in reports:
            for metric in report.metrics:
                if metric.name == metric_name and metric.result:
                    if metric_name not in titles:
                        titles[metric_name] = metric.title
                    row = metric.result[0]
                    # The scalar column is the first non-release key
                    scalar_col = next((k for k in row if k != "release"), None)
                    if scalar_col is not None:
                        series.setdefault(metric_name, {})[report.release] = float(
                            row[scalar_col]
                        )

    available = [m for m in metric_names if m in series]
    if not available:
        return

    st.subheader(section_title)

    # Determine releases present
    all_releases = sorted({rel for m in available for rel in series[m]})
    latest_release = all_releases[-1]
    previous_release = all_releases[-2] if len(all_releases) > 1 else None

    def _format_value(value: float | None) -> str:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return "—"
        if value == int(value):
            return f"{int(value):,}"
        return f"{value:,.2f}"

    # KPI cards
    kpi_cols = st.columns(len(available))
    for col, metric_name in zip(kpi_cols, available, strict=False):
        latest_val = series[metric_name].get(latest_release)
        prev_val = (
            series[metric_name].get(previous_release)
            if previous_release is not None
            else None
        )
        delta: str | None = None
        if latest_val is not None and prev_val is not None:
            diff = latest_val - prev_val
            delta = ("+" if diff >= 0 else "") + _format_value(diff)
        col.metric(
            label=titles.get(metric_name, metric_name.replace("_", " ").title()),
            value=_format_value(latest_val),
            delta=delta,
            help=f"Release: {latest_release}",
        )

    # Wide DataFrame for the expander
    wide_rows: list[dict[str, object]] = []
    for rel in all_releases:
        row: dict[str, object] = {"release": rel}
        for metric_name in available:
            row[metric_name] = series[metric_name].get(rel)
        wide_rows.append(row)
    wide_df = pd.DataFrame(wide_rows)

    # Long DataFrame for the bar chart
    records: list[dict[str, object]] = []
    for rel in all_releases:
        for metric_name in available:
            val = series[metric_name].get(rel)
            if val is not None:
                records.append(
                    {
                        "release": rel,
                        "metric": titles.get(
                            metric_name,
                            metric_name.replace("_", " ").title(),
                        ),
                        "value": val,
                    }
                )
    long_df = pd.DataFrame(records)

    if not long_df.empty:
        fig = px.bar(
            long_df,
            x="metric",
            y="value",
            color="release",
            barmode="group",
            labels={"metric": "Metric", "value": "Count", "release": "Release"},
            template="plotly_white",
            title=section_title,
        )
        fig.update_layout(xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Raw data", expanded=False):
        st.caption(f"Releases: {', '.join(all_releases)}")
        st.dataframe(wide_df, use_container_width=True)
        st.download_button(
            label="Download CSV",
            data=wide_df.to_csv(index=False),
            file_name=f"{section_title.lower().replace(' ', '_')}_counts.csv",
            mime="text/csv",
            key=f"download_count_group_{section_title}",
        )


def render_grouped_group(
    reports: list[ReleaseReport],
    metric_names: list[str],
    group_key: str,
    section_title: str,
) -> None:
    """Render a group of per-category metrics as KPI cards, a faceted bar chart and a joined table.

    Joins all metrics on the shared grouping key and release into a wide
    DataFrame, displays aggregated KPI cards, a faceted grouped bar chart
    (one facet per metric, X = category, colour = release), and a raw-data
    expander.

    :param reports: List of ReleaseReport objects (already filtered by selected releases).
    :param metric_names: Ordered list of metric name identifiers sharing the same grouping key.
    :param group_key: The shared categorical column (e.g. ``"studyType"``, ``"projectId"``).
    :param section_title: Display title shown as the section subheader.
    """
    frames: dict[str, pd.DataFrame] = {}
    titles: dict[str, str] = {}

    for metric_name in metric_names:
        df = metrics_to_dataframe(reports, metric_name)
        if df.empty:
            continue
        for report in reports:
            for metric in report.metrics:
                if metric.name == metric_name:
                    titles[metric_name] = metric.title
                    break
            if metric_name in titles:
                break
        count_col = next(
            (
                c
                for c in df.columns
                if c not in ("release", group_key)
                and pd.api.types.is_numeric_dtype(df[c])
            ),
            None,
        )
        if count_col is None:
            continue
        label = titles.get(metric_name, metric_name.replace("_", " ").title())
        frames[metric_name] = df[[group_key, "release", count_col]].rename(
            columns={count_col: label}
        )

    available = [m for m in metric_names if m in frames]
    if not available:
        return

    wide_df = frames[available[0]]
    for metric_name in available[1:]:
        wide_df = pd.merge(
            wide_df, frames[metric_name], on=[group_key, "release"], how="outer"
        )

    all_releases = sorted(wide_df["release"].astype(str).unique().tolist())
    latest_release = all_releases[-1]
    previous_release = all_releases[-2] if len(all_releases) > 1 else None

    latest_wide = wide_df[wide_df["release"] == latest_release]
    previous_wide = (
        wide_df[wide_df["release"] == previous_release]
        if previous_release is not None
        else None
    )
    value_labels = [titles.get(m, m.replace("_", " ").title()) for m in available]

    def _fmt(value: float | None) -> str:
        if value is None or pd.isna(value):
            return "—"
        value_float = float(value)
        if value_float.is_integer():
            return f"{int(value_float):,}"
        return f"{value_float:,.2f}"

    st.subheader(section_title)

    # KPI cards – sum across categories for the latest release
    kpi_cols = st.columns(len(available))
    for col, label in zip(kpi_cols, value_labels, strict=False):
        if label not in latest_wide.columns:
            continue
        latest_val = float(latest_wide[label].sum())
        prev_val = (
            float(previous_wide[label].sum())
            if previous_wide is not None and label in previous_wide.columns
            else None
        )
        delta: str | None = None
        if prev_val is not None:
            diff = latest_val - prev_val
            delta = ("+" if diff >= 0 else "") + _fmt(diff)
        col.metric(
            label=label,
            value=_fmt(latest_val),
            delta=delta,
            help=f"Release: {latest_release}",
        )

    # Faceted grouped bar chart
    long_df = pd.melt(
        wide_df,
        id_vars=[group_key, "release"],
        value_vars=value_labels,
        var_name="metric",
        value_name="value",
    )
    if not long_df.empty:
        n_metrics = len(value_labels)
        fig = px.bar(
            long_df,
            x=group_key,
            y="value",
            color="release",
            facet_col="metric",
            facet_col_wrap=min(2, n_metrics),
            barmode="group",
            labels={
                group_key: _humanize(group_key),
                "value": "Count",
                "release": "Release",
                "metric": "Metric",
            },
            template="plotly_white",
            title=section_title,
        )
        fig.update_layout(xaxis_tickangle=-30)
        # Strip "metric=…" prefix from facet labels
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Raw data", expanded=False):
        st.caption(f"Releases: {', '.join(all_releases)}")
        st.dataframe(
            wide_df.sort_values(["release", group_key]), use_container_width=True
        )
        st.download_button(
            label="Download CSV",
            data=wide_df.to_csv(index=False),
            file_name=f"{section_title.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            key=f"download_grouped_group_{section_title}",
        )


def load_diff_db(metrics_dir: str = "metrics") -> str | None:
    """Find a diff DuckDB file in the metrics directory.

    :param metrics_dir: Local fallback path containing diff files.
        The ``METRICS_PATH`` env var overrides this and may point to a local
        folder or a Hugging Face dataset repo.
    :return: Path to the first diff DuckDB file found, or ``None``.
    """
    metrics_path = _resolve_metrics_path(metrics_dir)
    if not metrics_path.exists():
        return None
    matches = sorted(metrics_path.glob("diff_*.duckdb"))
    return str(matches[0]) if matches else None


@st.cache_data
def load_diff_tables(db_path: str, domain: str) -> dict[str, tuple[pd.DataFrame, int]]:
    """Load anti-join tables for a domain from a diff DuckDB file.

    :param db_path: Path to the diff DuckDB file.
    :param domain: Domain name (e.g. ``"study"``).
    :return: Dict mapping table name to a tuple of (preview DataFrame, total row count).
    """
    con = duckdb.connect(db_path, read_only=True)
    try:
        tables = con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_name LIKE ?",
            [f"{domain}_only_in_%"],
        ).fetchall()
        result: dict[str, tuple[pd.DataFrame, int]] = {}
        for (table_name,) in tables:
            count: int = con.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[
                0
            ]  # type: ignore[index]
            preview = con.execute(
                f'SELECT * FROM "{table_name}" LIMIT {DIFF_PREVIEW_ROWS}'
            ).df()
            result[table_name] = (preview, count)
        return result
    finally:
        con.close()


_L2G_COMPARISON_TABLES = (
    "l2gprediction_correlation_stats",
    "l2gprediction_significant_changes",
    "l2gprediction_score_sample",
)


@st.cache_data
def load_l2g_comparison(
    db_path: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame] | None:
    """Load l2g score comparison tables. Returns None if tables are absent.

    :param db_path: Path to the diff DuckDB file.
    :return: Tuple of (correlation_stats, significant_changes, score_sample) DataFrames,
        or ``None`` if any required table is missing.
    """
    con = duckdb.connect(db_path, read_only=True)
    try:
        existing = {
            row[0]
            for row in con.execute(
                "SELECT table_name FROM information_schema.tables"
            ).fetchall()
        }
        if not all(t in existing for t in _L2G_COMPARISON_TABLES):
            return None
        correlation = con.execute("SELECT * FROM l2gprediction_correlation_stats").df()
        changes = con.execute("SELECT * FROM l2gprediction_significant_changes").df()
        sample = con.execute("SELECT * FROM l2gprediction_score_sample").df()
    finally:
        con.close()
    return correlation, changes, sample


def render_l2g_comparison(db_path: str) -> None:
    """Render the L2G Score Comparison section.

    :param db_path: Path to the diff DuckDB file.
    """
    data = load_l2g_comparison(db_path)
    if data is None:
        return

    correlation, changes, sample = data
    row = correlation.iloc[0]
    pearson_r: float = float(row["pearson_r"])
    n_common: int = int(row["n_common_pairs"])
    release_old: str = str(row["release_old"])
    release_new: str = str(row["release_new"])

    st.header("L2G Score Comparison")

    kpi_left, kpi_right = st.columns(2)
    kpi_left.metric("Pearson r", f"{pearson_r:.4f}")
    kpi_right.metric("Common pairs", f"{n_common:,}")

    # Build scatter plot
    # Assign highlight category for the significant-changes overlay
    def _category(row: pd.Series) -> str:
        if row["delta_above_50pct"] and row["score_crossed_threshold"]:
            return "Both"
        if row["delta_above_50pct"]:
            return "|delta| > 0.5"
        return "Crossed threshold"

    if not changes.empty:
        changes = changes.copy()
        changes["category"] = changes.apply(_category, axis=1)

    # Background layer (gray sample)
    fig = px.scatter(
        sample,
        x="score_old",
        y="score_new",
        opacity=0.2,
        color_discrete_sequence=["#aaaaaa"],
        labels={"score_old": release_old, "score_new": release_new},
        title=f"L2G Score Comparison (R = {pearson_r:.4f})",
        template="plotly_white",
    )
    fig.update_traces(marker_size=3, name="background", showlegend=True)

    # Highlight layer (significant changes)
    if not changes.empty:
        highlight_fig = px.scatter(
            changes,
            x="score_old",
            y="score_new",
            color="category",
            labels={
                "score_old": release_old,
                "score_new": release_new,
                "category": "Change type",
            },
        )
        for trace in highlight_fig.data:
            trace.update(marker_size=6)
            fig.add_trace(trace)

    # Diagonal reference line
    fig.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=1,
        y1=1,
        xref="x",
        yref="y",
        line=dict(color="black", dash="dash", width=1),
    )
    fig.update_layout(xaxis_title=release_old, yaxis_title=release_new)
    st.plotly_chart(fig, use_container_width=True)

    # Significant changes table
    with st.expander(f"Significant changes ({len(changes):,} pairs)", expanded=False):
        st.dataframe(changes, use_container_width=True)

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as file:
            parquet_path = Path(file.name)
        try:
            with duckdb.connect(db_path, read_only=True) as con:
                con.execute(
                    f"COPY (SELECT * FROM l2gprediction_significant_changes) TO '{parquet_path}' (FORMAT PARQUET)"
                )
            parquet_bytes = parquet_path.read_bytes()
        finally:
            parquet_path.unlink(missing_ok=True)

        st.download_button(
            label="Download full table (Parquet)",
            data=parquet_bytes,
            file_name="l2gprediction_significant_changes.parquet",
            mime="application/octet-stream",
            key="download_l2g_significant_changes",
        )


def render_diff_section(db_path: str, domain: str, widget_key: str) -> None:
    """Render anti-join diff tables for a domain.

    :param db_path: Path to the diff DuckDB file.
    :param domain: Domain name (e.g. ``"study"``).
    :param widget_key: Prefix for Streamlit widget keys.
    """
    tables = load_diff_tables(db_path, domain)
    if not tables:
        return

    st.header("Release Comparison")
    for table_name in sorted(tables):
        df, total_rows = tables[table_name]
        label = _format_diff_label(table_name, domain)
        st.subheader(f"{label} ({total_rows:,} rows)")
        st.caption(f"Showing first {min(total_rows, DIFF_PREVIEW_ROWS)} rows")
        st.dataframe(df, use_container_width=True)

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as file:
            parquet_path = Path(file.name)

        try:
            with duckdb.connect(db_path, read_only=True) as con:
                con.execute(
                    f"COPY (SELECT * FROM \"{table_name}\") TO '{parquet_path}' (FORMAT PARQUET)"
                )
            parquet_bytes = parquet_path.read_bytes()
        finally:
            parquet_path.unlink(missing_ok=True)

        st.download_button(
            label="Download full table (Parquet)",
            data=parquet_bytes,
            file_name=f"{table_name}.parquet",
            mime="application/octet-stream",
            key=f"download_diff_{widget_key}_{table_name}",
        )
