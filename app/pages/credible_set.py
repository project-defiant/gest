"""Credible set domain metrics page."""

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
    "total_count_of_credible_sets",
    "number_of_credible_sets",
]

_STUDY_TYPE_GROUP: list[str] = [
    "number_of_credible_sets_per_study_type",
    "unique_lead_variants_per_study_type",
]

_PROJECT_GROUP: list[str] = [
    "number_of_credible_sets_per_project",
    "unique_lead_variants_per_project",
]

st.header("Credible Set Metrics")

reports = load_all_reports()
if not reports:
    st.warning("No reports found.")
    st.stop()

releases = [r.release for r in reports]
selected = st.sidebar.multiselect(
    "Releases", releases, default=releases, key="cs_releases"
)
filtered = [r for r in reports if r.release in selected]

if not filtered:
    st.info("Select at least one release to view credible set metrics.")
    st.stop()

st.caption(f"Selected releases: {', '.join(r.release for r in filtered)}")

cs_metrics = sorted(
    {m.name for r in filtered for m in r.metrics if m.domain == "credibleset"}
)
if not cs_metrics:
    st.info("No credible set metrics available for the selected releases.")
    st.stop()

render_count_group(filtered, _COUNT_GROUP, "Credible Set Counts")
render_grouped_group(
    filtered, _STUDY_TYPE_GROUP, "studyType", "Credible Sets per Study Type"
)
render_grouped_group(filtered, _PROJECT_GROUP, "projectId", "Credible Sets per Project")

_ALL_GROUPED = set(_COUNT_GROUP) | set(_STUDY_TYPE_GROUP) | set(_PROJECT_GROUP)

for metric_name in cs_metrics:
    if metric_name in _ALL_GROUPED:
        continue
    sample = next(m for r in filtered for m in r.metrics if m.name == metric_name)
    df = metrics_to_dataframe(filtered, metric_name)
    render_metric(df, sample.title, metric_name)

diff_db = load_diff_db()
if diff_db:
    render_diff_section(diff_db, "credible_set", "cs")
