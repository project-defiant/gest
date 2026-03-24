"""Streamlit app for comparing OpenTargets release metrics."""

import pandas as pd
import plotly.express as px
import streamlit as st

from app.data import load_all_reports

st.set_page_config(page_title="Gest - Genetics Test - release metrics", layout="wide")
st.title("Gest - Genetics Test - release Metrics")
st.subheader("Overall table counts by release")

reports = load_all_reports()

if not reports:
    st.warning("No metric reports found. Run `gest compute` to generate them.")
    st.stop()

releases = [r.release for r in reports]
st.sidebar.header("Releases")
selected = st.sidebar.multiselect(
    "Select releases to compare", releases, default=releases
)

filtered = [r for r in reports if r.release in selected]

if not filtered:
    st.info("Select at least one release to view metrics.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.markdown("Navigate to domain pages for detailed metrics.")
st.caption(f"Selected releases: {', '.join(r.release for r in filtered)}")
st.caption("Missing values indicate a metric was not present in that release report.")

METRIC_COLUMNS: list[tuple[str, str]] = [
    ("total_count_of_studies", "Studies"),
    ("total_count_of_credible_sets", "Credible Sets"),
    ("total_count_of_variants", "Variants"),
    ("total_count_of_predictions", "Predictions"),
    ("total_count_of_colocalisations", "Colocalisations"),
]


def _extract_metric_value(report: object, metric_name: str) -> float | None:
    metrics = getattr(report, "metrics", [])
    for metric in metrics:
        if metric.name != metric_name or not metric.result:
            continue
        first_row = metric.result[0]
        if metric_name in first_row and isinstance(first_row[metric_name], int | float):
            return float(first_row[metric_name])
        numeric_values = [
            value
            for key, value in first_row.items()
            if key != "release" and isinstance(value, int | float)
        ]
        if numeric_values:
            return float(numeric_values[0])
    return None


def _format_value(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{value:,.2f}"


summary_rows: list[dict[str, float | str | None]] = []
for report in filtered:
    row: dict[str, float | str | None] = {"Release": report.release}
    for metric_name, label in METRIC_COLUMNS:
        row[label] = _extract_metric_value(report, metric_name)
    summary_rows.append(row)

summary_df = pd.DataFrame(summary_rows)

st.subheader("Current Release Snapshot")
latest_report = filtered[-1]
previous_report = filtered[-2] if len(filtered) > 1 else None

metric_columns = st.columns(len(METRIC_COLUMNS))
for column, (metric_name, label) in zip(metric_columns, METRIC_COLUMNS, strict=False):
    current_value = _extract_metric_value(latest_report, metric_name)
    delta_text: str | None = None
    if previous_report is not None:
        previous_value = _extract_metric_value(previous_report, metric_name)
        if current_value is not None and previous_value is not None:
            delta = current_value - previous_value
            delta_text = _format_value(delta)
    column.metric(
        label=label,
        value=_format_value(current_value),
        delta=delta_text,
        help=f"Release: {latest_report.release}",
    )

display_df = summary_df.copy()
for _, label in METRIC_COLUMNS:
    display_df[label] = display_df[label].map(_format_value)

st.subheader("Release Summary")
st.dataframe(display_df, use_container_width=True, hide_index=True)

chart_df = summary_df.melt(
    id_vars=["Release"],
    value_vars=[label for _, label in METRIC_COLUMNS],
    var_name="Table",
    value_name="Count",
).dropna(subset=["Count"])

if chart_df.empty:
    st.info("No overview counts available for the selected releases.")
else:
    chart = px.bar(
        chart_df,
        x="Release",
        y="Count",
        color="Table",
        barmode="group",
        title="Table counts by release",
    )
    st.plotly_chart(chart, use_container_width=True)
