"""Colocalisation domain metrics page."""

import streamlit as st

from app.data import (
    load_all_reports,
    load_diff_db,
    metrics_to_dataframe,
    render_count_group,
    render_diff_section,
    render_grouped_group,
    render_metric,
)

_COUNT_GROUP: list[str] = [
    "total_count_of_colocalisations",
    "number_of_significant_clpp",
    "number_of_significant_h4",
    "number_of_unique_pairs_significant_clpp",
    "number_of_unique_pairs_significant_h4",
]

_STUDY_TYPE_GROUP: list[str] = [
    "number_of_significant_clpp_per_study_type",
    "number_of_significant_h4_per_study_type",
    "number_of_unique_pairs_significant_clpp_per_study_type",
    "number_of_unique_pairs_significant_h4_per_study_type",
]

st.header("Colocalisation Metrics")

reports = load_all_reports()
if not reports:
    st.warning("No reports found.")
    st.stop()

releases = [r.release for r in reports]
selected = st.sidebar.multiselect(
    "Releases", releases, default=releases, key="coloc_releases"
)
filtered = [r for r in reports if r.release in selected]

if not filtered:
    st.info("Select at least one release to view colocalisation metrics.")
    st.stop()

st.caption(f"Selected releases: {', '.join(r.release for r in filtered)}")

coloc_metrics = sorted(
    {m.name for r in filtered for m in r.metrics if m.domain == "colocalisation"}
)
if not coloc_metrics:
    st.info("No colocalisation metrics available for the selected releases.")
    st.stop()

render_count_group(filtered, _COUNT_GROUP, "Colocalisation Counts")
render_grouped_group(
    filtered,
    _STUDY_TYPE_GROUP,
    "rightStudyType",
    "Colocalisations per Study Type",
)

_ALL_GROUPED = set(_COUNT_GROUP) | set(_STUDY_TYPE_GROUP)

for metric_name in coloc_metrics:
    if metric_name in _ALL_GROUPED:
        continue
    sample = next(m for r in filtered for m in r.metrics if m.name == metric_name)
    df = metrics_to_dataframe(filtered, metric_name)
    render_metric(df, sample.title, metric_name)

diff_db = load_diff_db()
if diff_db:
    render_diff_section(diff_db, "colocalisation", "coloc")
