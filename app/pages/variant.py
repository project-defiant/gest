"""Variant domain metrics page."""

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

for metric_name in variant_metrics:
    if metric_name in _COUNT_GROUP:
        continue
    sample = next(m for r in filtered for m in r.metrics if m.name == metric_name)
    df = metrics_to_dataframe(filtered, metric_name)
    render_metric(df, sample.title, metric_name)

diff_db = load_diff_db()
if diff_db:
    render_diff_section(diff_db, "variant", "variant")
