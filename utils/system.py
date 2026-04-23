"""System composition root for the enterprise pipeline digital twin."""

from __future__ import annotations

from database.db import get_connection, initialize_database
from database.repository import TelemetryRepository
from edge.processor import EdgeProcessor
from cloud.digital_twin import CloudDigitalTwin
from orchestrator.engine import OrchestrationEngine
from utils.config import SystemConfig
from utils.metrics import MetricsTracker
from utils.models import DigitalTwinState, OrchestrationDecision, PipelineEvent, ProcessedRecord


class EdgeCloudDigitalTwinSystem:
    """Coordinate simulator input, edge validation, cloud analysis, and logging."""

    def __init__(self, config: SystemConfig | None = None) -> None:
        self.config = config or SystemConfig()
        self.connection = get_connection(self.config.database_path)
        initialize_database(self.connection)
        self.repository = TelemetryRepository(self.connection)
        self.edge = EdgeProcessor(self.config)
        self.cloud = CloudDigitalTwin(self.config)
        self.orchestrator = OrchestrationEngine(self.config)
        self.metrics = MetricsTracker(self.config)

    def ingest_event(self, event: PipelineEvent) -> tuple[ProcessedRecord, OrchestrationDecision]:
        """Process one enterprise event through the full edge-cloud workflow."""

        backlog_severity = event.queue_depth / self.config.severe_backlog_threshold
        requires_complex_analysis = (
            event.scenario in {
                "malformed_xml_burst",
                "transformation_bottleneck",
                "publication_failure_spike",
                "retry_storm",
                "mixed_enterprise_load",
            }
            or event.xml_complexity >= self.config.xml_complexity_threshold
            or event.transform_latency_ms >= self.config.transform_latency_threshold_ms
        )
        decision = self.orchestrator.decide(
            processing_time_ms=event.processing_time_ms,
            queue_depth=event.queue_depth,
            requires_complex_analysis=requires_complex_analysis,
            retry_count=event.retry_count,
            publish_failure_risk=event.publish_status != "SUCCESS",
            backlog_severity=backlog_severity,
            downstream_ack_delay_ms=event.downstream_ack_delay_ms,
        )

        processed = self.edge.process(event=event, processing_location=decision.location)
        processed = self.cloud.process(processed)

        self.repository.log_orchestration(decision)
        self.repository.log_processed_record(processed)
        self.metrics.record(processed)

        return processed, decision

    def ingest_sensor_data(self, sensor: PipelineEvent) -> tuple[ProcessedRecord, OrchestrationDecision]:
        """Backward-compatible wrapper preserved for existing call sites."""

        return self.ingest_event(sensor)

    def get_state(self) -> DigitalTwinState:
        """Return the current cloud digital twin state."""

        return self.cloud.get_state()

    def get_metrics(self):
        """Return the current metrics snapshot."""

        return self.metrics.snapshot()
