"""Pydantic models shared by the enterprise pipeline twin."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class PipelineEvent(BaseModel):
    """Single pipeline event emitted by the simulator or API."""

    document_id: str
    document_type: str
    document_size_kb: float
    xml_complexity: float
    validation_error_count: int
    processing_time_ms: float
    queue_depth: int
    retry_count: int
    transform_latency_ms: float
    publish_status: str
    downstream_ack_delay_ms: float
    timestamp: datetime = Field(default_factory=utc_now)
    scenario: str = "normal_processing"


class ProcessedRecord(BaseModel):
    """Edge-processed pipeline event plus anomaly classification."""

    event: PipelineEvent
    anomaly_detected: bool
    anomaly_score: float
    anomaly_types: list[str]
    edge_latency_ms: float
    processing_location: str
    cloud_analysis: dict[str, Any] = Field(default_factory=dict)


class OrchestrationDecision(BaseModel):
    """Decision returned by the orchestrator."""

    location: str
    reason: str
    processing_time_ms: float
    queue_depth: int
    requires_complex_analysis: bool
    decided_at: datetime = Field(default_factory=utc_now)


class DigitalTwinState(BaseModel):
    """Aggregated enterprise pipeline state maintained in the cloud."""

    status: str = "HEALTHY"
    last_updated: datetime = Field(default_factory=utc_now)
    total_events_processed: int = 0
    failed_events: int = 0
    anomaly_count: int = 0
    validation_issue_trend: float = 0.0
    retry_storm_risk: float = 0.0
    backlog_severity: float = 0.0
    publish_health: float = 1.0
    health_score: float = 1.0
    average_processing_time_ms: float = 0.0
    average_queue_depth: float = 0.0
    average_retry_count: float = 0.0
    average_ack_delay_ms: float = 0.0
    last_anomaly_types: list[str] = Field(default_factory=list)


class MetricsSnapshot(BaseModel):
    """System metrics exposed by the API."""

    total_events: int
    average_processing_time_ms: float
    anomaly_count: int
    anomaly_detection_rate: float
    failed_events: int
    publish_failure_count: int
    edge_processed: int
    cloud_processed: int
    edge_processing_pct: float
    cloud_processing_pct: float
    simulated_cost: float
