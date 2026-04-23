"""FastAPI application for the enterprise pipeline digital twin."""

from __future__ import annotations

from fastapi import FastAPI

from utils.models import PipelineEvent
from utils.system import EdgeCloudDigitalTwinSystem

app = FastAPI(title="EdgeCloud-DigitalTwin", version="1.0.0")
system = EdgeCloudDigitalTwinSystem()


@app.get("/")
def root() -> dict[str, str]:
    """Basic health endpoint."""

    return {"message": "EdgeCloud-DigitalTwin pipeline API is running"}


@app.post("/pipeline-event")
def ingest_pipeline_event(record: PipelineEvent) -> dict:
    """Accept a processing event and process it through the system."""

    processed, decision = system.ingest_event(record)
    return {
        "message": "pipeline event processed",
        "processing_location": decision.location,
        "routing_reason": decision.reason,
        "anomaly_detected": processed.anomaly_detected,
        "anomaly_types": processed.anomaly_types,
        "pipeline_status": system.get_state().status,
        "document_id": record.document_id,
    }


@app.post("/sensor-data")
def ingest_sensor_data(record: PipelineEvent) -> dict:
    """Backward-compatible alias for the existing endpoint style."""

    processed, decision = system.ingest_event(record)
    return {
        "message": "pipeline event processed",
        "processing_location": decision.location,
        "routing_reason": decision.reason,
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
