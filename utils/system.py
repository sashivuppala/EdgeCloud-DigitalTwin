"""System composition root for the edge-cloud digital twin."""

from __future__ import annotations

from database.db import get_connection, initialize_database
from database.repository import TelemetryRepository
from edge.processor import EdgeProcessor
from cloud.digital_twin import CloudDigitalTwin
from orchestrator.engine import OrchestrationEngine
from utils.config import SystemConfig
from utils.metrics import MetricsTracker
from utils.models import DigitalTwinState, OrchestrationDecision, ProcessedRecord, SensorRecord


class EdgeCloudDigitalTwinSystem:
    """Coordinate simulator input, edge processing, cloud analysis, and logging."""

    def __init__(self, config: SystemConfig | None = None) -> None:
        self.config = config or SystemConfig()
        self.connection = get_connection(self.config.database_path)
        initialize_database(self.connection)
        self.repository = TelemetryRepository(self.connection)
        self.edge = EdgeProcessor(self.config)
        self.cloud = CloudDigitalTwin(self.config)
        self.orchestrator = OrchestrationEngine(self.config)
        self.metrics = MetricsTracker(self.config)

    def ingest_sensor_data(self, sensor: SensorRecord) -> tuple[ProcessedRecord, OrchestrationDecision]:
        """Process one telemetry event through the full edge-cloud workflow."""

        requires_complex_analysis = sensor.scenario in {"anomaly_injection", "edge_overload"} or sensor.vibration > 0.95
        decision = self.orchestrator.decide(
            latency_ms=sensor.latency_ms,
            cpu_load=sensor.cpu_load,
            requires_complex_analysis=requires_complex_analysis,
        )

        processed = self.edge.process(sensor=sensor, processing_location=decision.location)
        processed = self.cloud.process(processed)

        self.repository.log_orchestration(decision)
        self.repository.log_processed_record(processed)
        self.metrics.record(processed)

        return processed, decision

    def get_state(self) -> DigitalTwinState:
        """Return the current cloud digital twin state."""

        return self.cloud.get_state()

    def get_metrics(self):
        """Return the current metrics snapshot."""

        return self.metrics.snapshot()
