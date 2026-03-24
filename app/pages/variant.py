"""Variant domain metrics page."""

import plotly.express as px
import streamlit as st

from app.data import (
    load_all_reports,
    load_diff_db,
    metrics_to_dataframe,
    render_count_group,
    render_diff_section,
    render_metric,
)

_COUNT_GROUP: list[str] = [
    "total_count_of_variants",
    "number_of_variants",
]

_VARIANT_ASSESSMENT_METRIC = "variants_per_max_effect_assessment"

st.header("Variant Metrics")

reports = load_all_reports()
if not reports:
    st.warning("No reports found.")
    st.stop()

releases = [r.release for r in reports]
selected = st.sidebar.multiselect(
    "Releases", releases, default=releases, key="variant_releases"
)
filtered = [r for r in reports if r.release in selected]

if not filtered:
    st.info("Select at least one release to view variant metrics.")
    st.stop()

st.caption(f"Selected releases: {', '.join(r.release for r in filtered)}")

variant_metrics = sorted(
    {m.name for r in filtered for m in r.metrics if m.domain == "variant"}
)
if not variant_metrics:
    st.info("No variant metrics available for the selected releases.")
    st.stop()

render_count_group(filtered, _COUNT_GROUP, "Variant Counts")

if _VARIANT_ASSESSMENT_METRIC in variant_metrics:
    assessment_df = metrics_to_dataframe(filtered, _VARIANT_ASSESSMENT_METRIC)
    required_cols = {"max_assessment", "number_of_variants", "release"}
    if not assessment_df.empty and required_cols.issubset(assessment_df.columns):
        st.subheader("Variants by Maximum Effect Assessment")
        assessment_chart = px.bar(
            assessment_df,
            x="max_assessment",
            y="number_of_variants",
            color="release",
            barmode="group",
            labels={
                "max_assessment": "Assessment",
                "number_of_variants": "Number of Variants",
                "release": "Release",
            },
            title="Variants per max effect assessment",
            template="plotly_white",
        )
        st.plotly_chart(assessment_chart, use_container_width=True)

for metric_name in variant_metrics:
    if metric_name in _COUNT_GROUP:
        continue
    sample = next(m for r in filtered for m in r.metrics if m.name == metric_name)
    df = metrics_to_dataframe(filtered, metric_name)
    render_metric(df, sample.title, metric_name)

diff_db = load_diff_db()
if diff_db:
    render_diff_section(diff_db, "variant", "variant")
