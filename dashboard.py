"""Optional Streamlit dashboard for live monitoring."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.system import EdgeCloudDigitalTwinSystem

st.set_page_config(page_title="EdgeCloud Digital Twin Dashboard", layout="wide")

st.title("EdgeCloud Digital Twin Dashboard")
st.caption("Live operational view of telemetry, anomalies, routing decisions, and latency.")

system = EdgeCloudDigitalTwinSystem()
repository = system.repository
state = system.get_state()
metrics = system.get_metrics()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Twin Status", state.status)
col2.metric("Health Score", f"{state.health_score:.2f}")
col3.metric("Anomalies", metrics.anomaly_count)
col4.metric("Avg Latency (ms)", f"{metrics.average_latency_ms:.2f}")

sensor_frame = repository.fetch_recent_sensor_data(limit=200)
anomaly_frame = repository.fetch_recent_anomalies(limit=20)
orchestration_frame = repository.fetch_recent_orchestration(limit=200)

if sensor_frame.empty:
    st.info("No data yet. Run `python run_simulation.py` or post telemetry to the API.")
else:
    st.subheader("Live Sensor Data")
    chart_frame = sensor_frame.set_index("timestamp")[["temperature", "vibration", "pressure", "fuel_flow"]]
    st.line_chart(chart_frame)

    st.subheader("Latency Trend")
    st.line_chart(sensor_frame.set_index("timestamp")[["latency_ms"]])

    st.subheader("Processing Distribution")
    if not orchestration_frame.empty:
        counts = orchestration_frame["location"].value_counts().rename_axis("location").reset_index(name="count")
        st.bar_chart(counts.set_index("location"))

if not anomaly_frame.empty:
    st.subheader("Recent Anomalies")
    display_frame = anomaly_frame.copy()
    display_frame["timestamp"] = pd.to_datetime(display_frame["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(display_frame, use_container_width=True)
