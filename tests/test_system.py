"""Unit tests covering the main simulation scenarios."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.app import app
from simulator.generator import SensorDataSimulator
from utils.config import SystemConfig
from utils.system import EdgeCloudDigitalTwinSystem


def build_system(tmp_path: Path) -> EdgeCloudDigitalTwinSystem:
    """Create an isolated system for tests."""

    return EdgeCloudDigitalTwinSystem(
        SystemConfig(database_path=tmp_path / "test.db")
    )


def test_normal_operation_updates_metrics(tmp_path: Path) -> None:
    """Normal simulation should produce events and metrics."""

    simulator = SensorDataSimulator(seed=1)
    system = build_system(tmp_path)

    for _ in range(10):
        system.ingest_sensor_data(simulator.generate_record("normal"))

    metrics = system.get_metrics()
    assert metrics.total_events == 10
    assert metrics.average_latency_ms > 0


def test_high_latency_routes_to_edge(tmp_path: Path) -> None:
    """High latency should trigger edge routing."""

    simulator = SensorDataSimulator(seed=2)
    system = build_system(tmp_path)
    record = simulator.generate_record("high_latency")

    _, decision = system.ingest_sensor_data(record)
    assert decision.location == "edge"


def test_edge_overload_offloads_to_cloud(tmp_path: Path) -> None:
    """Edge overload should force cloud offload."""

    simulator = SensorDataSimulator(seed=3)
    system = build_system(tmp_path)
    record = simulator.generate_record("edge_overload")

    _, decision = system.ingest_sensor_data(record)
    assert decision.location == "cloud"


def test_anomaly_injection_increases_anomaly_count(tmp_path: Path) -> None:
    """Injected anomalies should be detected at least once in a short run."""

    simulator = SensorDataSimulator(seed=4)
    system = build_system(tmp_path)

    for _ in range(20):
        system.ingest_sensor_data(simulator.generate_record("anomaly_injection"))

    assert system.get_state().anomaly_count >= 1


def test_api_endpoints() -> None:
    """FastAPI endpoints should accept data and expose state."""

    client = TestClient(app)
    payload = {
        "temperature": 78.1,
        "vibration": 0.51,
        "pressure": 31.2,
        "fuel_flow": 100.4,
        "timestamp": "2026-04-09T12:00:00Z",
        "latency_ms": 22.0,
        "cpu_load": 0.41,
        "scenario": "normal",
    }
    post_response = client.post("/sensor-data", json=payload)
    assert post_response.status_code == 200

    status_response = client.get("/status")
    metrics_response = client.get("/metrics")
    assert status_response.status_code == 200
    assert metrics_response.status_code == 200
