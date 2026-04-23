"""Unit tests covering the enterprise pipeline simulation scenarios."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from api.app import app
from simulator.generator import SensorDataSimulator
from utils.config import SystemConfig
from utils.system import EdgeCloudDigitalTwinSystem


def build_system() -> EdgeCloudDigitalTwinSystem:
    """Create an isolated system for tests."""

    runtime_dir = Path("test_runtime")
    runtime_dir.mkdir(exist_ok=True)
    return EdgeCloudDigitalTwinSystem(
        SystemConfig(database_path=runtime_dir / f"{uuid4().hex}.db")
    )


def test_normal_operation_updates_metrics() -> None:
    """Normal enterprise processing should produce events and metrics."""

    simulator = SensorDataSimulator(seed=1)
    system = build_system()

    for _ in range(10):
        system.ingest_event(simulator.generate_record("normal_processing"))

    metrics = system.get_metrics()
    assert metrics.total_events == 10
    assert metrics.average_processing_time_ms > 0


def test_normal_processing_routes_to_edge() -> None:
    """Low-latency validation should remain at the edge."""

    simulator = SensorDataSimulator(seed=2)
    system = build_system()
    record = simulator.generate_record("normal_processing")
    record = record.model_copy(update={"processing_time_ms": 140.0, "queue_depth": 40, "xml_complexity": 0.32})

    _, decision = system.ingest_event(record)
    assert decision.location == "edge"
    assert "edge" in decision.reason


def test_high_backlog_offloads_to_cloud() -> None:
    """High backlog should force cloud offload."""

    simulator = SensorDataSimulator(seed=3)
    system = build_system()
    record = simulator.generate_record("high_queue_backlog")
    record = record.model_copy(update={"queue_depth": 320, "processing_time_ms": 290.0})

    _, decision = system.ingest_event(record)
    assert decision.location == "cloud"
    assert "backlog" in decision.reason


def test_malformed_xml_burst_increases_anomaly_count() -> None:
    """Malformed XML bursts should be detected at least once in a short run."""

    simulator = SensorDataSimulator(seed=4)
    system = build_system()

    for _ in range(20):
        system.ingest_event(simulator.generate_record("malformed_xml_burst"))

    assert system.get_state().anomaly_count >= 1
    assert system.get_state().validation_issue_trend >= 1.0


def test_retry_storm_routes_to_cloud() -> None:
    """Retry storms should trigger centralized analysis."""

    simulator = SensorDataSimulator(seed=5)
    system = build_system()
    record = simulator.generate_record("retry_storm")
    record = record.model_copy(update={"retry_count": 7, "queue_depth": 150})

    _, decision = system.ingest_event(record)
    assert decision.location == "cloud"
    assert "retry storm" in decision.reason


def test_publication_failure_impacts_metrics() -> None:
    """Failed publications should surface in metrics and twin state."""

    simulator = SensorDataSimulator(seed=6)
    system = build_system()
    record = simulator.generate_record("publication_failure_spike")
    record = record.model_copy(update={"publish_status": "FAILED", "retry_count": 5})

    processed, _ = system.ingest_event(record)
    metrics = system.get_metrics()
    assert processed.anomaly_detected
    assert metrics.publish_failure_count == 1
    assert system.get_state().failed_events == 1


def test_api_endpoints() -> None:
    """FastAPI endpoints should accept pipeline events and expose state."""

    client = TestClient(app)
    payload = {
        "document_id": "DOC-API-001",
        "document_type": "INVOICE",
        "document_size_kb": 188.4,
        "xml_complexity": 0.41,
        "validation_error_count": 0,
        "processing_time_ms": 135.0,
        "queue_depth": 28,
        "retry_count": 0,
        "transform_latency_ms": 122.0,
        "publish_status": "SUCCESS",
        "downstream_ack_delay_ms": 88.0,
        "timestamp": "2026-04-22T12:00:00Z",
        "scenario": "normal_processing",
    }
    post_response = client.post("/pipeline-event", json=payload)
    assert post_response.status_code == 200
    assert post_response.json()["document_id"] == "DOC-API-001"
    assert "digital_twin_state" in post_response.json()

    status_response = client.get("/status")
    metrics_response = client.get("/metrics")
    health_response = client.get("/health")
    assert status_response.status_code == 200
    assert metrics_response.status_code == 200
    assert health_response.status_code == 200
