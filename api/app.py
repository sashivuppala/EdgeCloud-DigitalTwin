"""FastAPI application for the edge-cloud digital twin."""

from __future__ import annotations

from fastapi import FastAPI

from utils.models import SensorRecord
from utils.system import EdgeCloudDigitalTwinSystem

app = FastAPI(title="EdgeCloud-DigitalTwin", version="1.0.0")
system = EdgeCloudDigitalTwinSystem()


@app.get("/")
def root() -> dict[str, str]:
    """Basic health endpoint."""

    return {"message": "EdgeCloud-DigitalTwin API is running"}


@app.post("/sensor-data")
def ingest_sensor_data(record: SensorRecord) -> dict:
    """Accept a telemetry sample and process it through the system."""

    processed, decision = system.ingest_sensor_data(record)
    return {
        "message": "sensor data processed",
        "processing_location": decision.location,
        "reason": decision.reason,
        "anomaly_detected": processed.anomaly_detected,
        "anomaly_types": processed.anomaly_types,
        "digital_twin_status": system.get_state().status,
    }


@app.get("/status")
def get_status() -> dict:
    """Return the current digital twin state."""

    return system.get_state().model_dump(mode="json")


@app.get("/metrics")
def get_metrics() -> dict:
    """Return aggregate metrics."""

    return system.get_metrics().model_dump(mode="json")
