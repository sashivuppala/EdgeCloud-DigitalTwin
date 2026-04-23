"""Optional Streamlit dashboard for live pipeline monitoring."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.system import EdgeCloudDigitalTwinSystem

st.set_page_config(page_title="EdgeCloud Pipeline Twin Dashboard", layout="wide")

st.title("EdgeCloud Pipeline Digital Twin Dashboard")
st.caption("Live operational view of enterprise workflow events, anomalies, routing decisions, and pipeline health.")

system = EdgeCloudDigitalTwinSystem()
repository = system.repository
state = system.get_state()
metrics = system.get_metrics()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Pipeline Status", state.status)
col2.metric("Health Score", f"{state.health_score:.2f}")
col3.metric("Total Pipeline Events", metrics.total_events)
col4.metric("Avg Processing Time (ms)", f"{metrics.average_processing_time_ms:.2f}")

sensor_frame = repository.fetch_recent_sensor_data(limit=200)
anomaly_frame = repository.fetch_recent_anomalies(limit=20)
orchestration_frame = repository.fetch_recent_orchestration(limit=200)

if sensor_frame.empty:
    st.info("No data yet. Run `python run_simulation.py` or post a pipeline event to the API.")
else:
    st.subheader("Queue Backlog and Retry Trend")
    chart_frame = sensor_frame.set_index("timestamp")[["queue_depth", "retry_count"]]
    st.line_chart(chart_frame)

    st.subheader("Processing and Acknowledgement Trend")
    st.line_chart(sensor_frame.set_index("timestamp")[["processing_time_ms", "transform_latency_ms", "downstream_ack_delay_ms"]])

    st.subheader("Pipeline Health Score Trend")
    st.line_chart(sensor_frame.set_index("timestamp")[["twin_health_score"]])

    st.subheader("Publish Status Distribution")
    publish_counts = sensor_frame["publish_status"].value_counts().rename_axis("publish_status").reset_index(name="count")
    st.bar_chart(publish_counts.set_index("publish_status"))

    st.subheader("Routing Distribution")
    if not orchestration_frame.empty:
        counts = orchestration_frame["location"].value_counts().rename_axis("location").reset_index(name="count")
        st.bar_chart(counts.set_index("location"))

    st.subheader("Top Anomaly Reasons")
    if not anomaly_frame.empty:
        expanded = (
            anomaly_frame.assign(anomaly_types=anomaly_frame["anomaly_types"].fillna("[]"))
            .assign(anomaly_types=lambda frame: frame["anomaly_types"].str.strip("[]").str.replace('"', "", regex=False))
        )
        reason_counts = (
            expanded["anomaly_types"]
            .str.split(",")
            .explode()
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .value_counts()
            .head(8)
            .rename_axis("anomaly_reason")
            .reset_index(name="count")
        )
        if not reason_counts.empty:
            st.bar_chart(reason_counts.set_index("anomaly_reason"))

if not anomaly_frame.empty:
    st.subheader("Recent Pipeline Anomalies")
    display_frame = anomaly_frame.copy()
    display_frame["timestamp"] = pd.to_datetime(display_frame["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(display_frame, use_container_width=True)

event_log_frame = repository.fetch_recent_event_log(limit=20)
if not event_log_frame.empty:
    st.subheader("Recent Event Log")
    event_log_frame["timestamp"] = pd.to_datetime(event_log_frame["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(event_log_frame, use_container_width=True)
