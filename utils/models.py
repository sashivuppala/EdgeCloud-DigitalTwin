"""Pydantic models shared by the system."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class SensorRecord(BaseModel):
    """Single telemetry sample emitted by the simulator or API."""

    temperature: float
    vibration: float
    pressure: float
    fuel_flow: float
    timestamp: datetime = Field(default_factory=utc_now)
    latency_ms: float = 20.0
    cpu_load: float = 0.35
    scenario: str = "normal"


class ProcessedRecord(BaseModel):
    """Edge-processed telemetry plus anomaly classification."""

    sensor: SensorRecord
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
    latency_ms: float
    cpu_load: float
    requires_complex_analysis: bool
    decided_at: datetime = Field(default_factory=utc_now)


class DigitalTwinState(BaseModel):
    """Aggregated aircraft/system state maintained in the cloud."""

    status: str = "healthy"
    last_updated: datetime = Field(default_factory=utc_now)
    anomaly_count: int = 0
    total_samples: int = 0
    health_score: float = 1.0
    moving_average_temperature: float = 0.0
    moving_average_vibration: float = 0.0
    moving_average_pressure: float = 0.0
    moving_average_fuel_flow: float = 0.0
    last_anomaly_types: list[str] = Field(default_factory=list)


class MetricsSnapshot(BaseModel):
    """System metrics exposed by the API."""

    total_events: int
    average_latency_ms: float
    anomaly_count: int
    anomaly_detection_rate: float
    edge_processed: int
    cloud_processed: int
    edge_processing_pct: float
    cloud_processing_pct: float
    simulated_cost: float
