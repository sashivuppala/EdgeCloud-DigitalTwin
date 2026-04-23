"""FastAPI application for the enterprise pipeline digital twin."""

from __future__ import annotations

from fastapi import FastAPI

from utils.models import PipelineEvent
from utils.system import PipelineTwinPlatform

app = FastAPI(title="EdgeCloud-DigitalTwin", version="1.0.0")
system = PipelineTwinPlatform()


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
        "pipeline_health": system.get_state().overall_pipeline_health_score,
        "digital_twin_state": system.get_state().model_dump(mode="json"),
        "document_id": record.document_id,
    }


@app.get("/status")
def get_status() -> dict:
    """Return the current digital twin state."""

    return system.get_state().model_dump(mode="json")


@app.get("/metrics")
def get_metrics() -> dict:
    """Return aggregate metrics."""

    return system.get_metrics().model_dump(mode="json")


@app.get("/health")
def get_health() -> dict:
    """Return a compact health view for operational checks."""

    state = system.get_state()
    return {
        "status": state.status,
        "overall_pipeline_health_score": state.overall_pipeline_health_score,
        "processing_readiness": "READY" if state.status != "CRITICAL" else "ATTENTION_REQUIRED",
        "failed_events": state.failed_events,
        "pending_events": state.pending_events,
    }
