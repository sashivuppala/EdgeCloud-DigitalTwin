"""Metrics tracking for orchestration and anomaly detection."""

from __future__ import annotations

from dataclasses import dataclass

from utils.config import SystemConfig
from utils.models import MetricsSnapshot, ProcessedRecord


@dataclass
class MetricsTracker:
    """Track pipeline timing, failure rate, route distribution, and cost."""

    config: SystemConfig
    total_events: int = 0
    total_processing_time_ms: float = 0.0
    anomaly_count: int = 0
    failed_events: int = 0
    publish_failure_count: int = 0
    edge_processed: int = 0
    cloud_processed: int = 0
    simulated_cost: float = 0.0

    def record(self, processed: ProcessedRecord) -> None:
        """Update aggregate counters."""

        self.total_events += 1
        end_to_end_processing_time = processed.event.processing_time_ms + processed.edge_latency_ms
        if processed.processing_location == "cloud":
            end_to_end_processing_time += 12.0
            self.cloud_processed += 1
            self.simulated_cost += self.config.cloud_cost_per_event
        else:
            self.edge_processed += 1
            self.simulated_cost += self.config.edge_cost_per_event

        self.total_processing_time_ms += end_to_end_processing_time
        self.anomaly_count += int(processed.anomaly_detected)
        if processed.event.publish_status != "SUCCESS":
            self.failed_events += 1
        if processed.event.publish_status == "FAILED":
            self.publish_failure_count += 1

    def snapshot(self) -> MetricsSnapshot:
        """Return a metrics snapshot for API exposure."""

        total = max(self.total_events, 1)
        return MetricsSnapshot(
            total_events=self.total_events,
            average_processing_time_ms=round(self.total_processing_time_ms / total, 4),
            anomaly_count=self.anomaly_count,
            anomaly_detection_rate=round(self.anomaly_count / total, 4),
            failed_events=self.failed_events,
            publish_failure_count=self.publish_failure_count,
            edge_processed=self.edge_processed,
            cloud_processed=self.cloud_processed,
            edge_processing_pct=round((self.edge_processed / total) * 100, 2),
            cloud_processing_pct=round((self.cloud_processed / total) * 100, 2),
            simulated_cost=round(self.simulated_cost, 4),
        )
