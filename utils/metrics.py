"""Metrics tracking for orchestration and anomaly detection."""

from __future__ import annotations

from dataclasses import dataclass

from utils.config import SystemConfig
from utils.models import MetricsSnapshot, ProcessedRecord


@dataclass
class MetricsTracker:
    """Track latency, anomaly rate, route distribution, and cost."""

    config: SystemConfig
    total_events: int = 0
    total_latency_ms: float = 0.0
    anomaly_count: int = 0
    edge_processed: int = 0
    cloud_processed: int = 0
    simulated_cost: float = 0.0

    def record(self, processed: ProcessedRecord) -> None:
        """Update aggregate counters."""

        self.total_events += 1
        end_to_end_latency = processed.sensor.latency_ms + processed.edge_latency_ms
        if processed.processing_location == "cloud":
            end_to_end_latency += 12.0
            self.cloud_processed += 1
            self.simulated_cost += self.config.cloud_cost_per_event
        else:
            self.edge_processed += 1
            self.simulated_cost += self.config.edge_cost_per_event

        self.total_latency_ms += end_to_end_latency
        self.anomaly_count += int(processed.anomaly_detected)

    def snapshot(self) -> MetricsSnapshot:
        """Return a metrics snapshot for API exposure."""

        total = max(self.total_events, 1)
        return MetricsSnapshot(
            total_events=self.total_events,
            average_latency_ms=round(self.total_latency_ms / total, 4),
            anomaly_count=self.anomaly_count,
            anomaly_detection_rate=round(self.anomaly_count / total, 4),
            edge_processed=self.edge_processed,
            cloud_processed=self.cloud_processed,
            edge_processing_pct=round((self.edge_processed / total) * 100, 2),
            cloud_processing_pct=round((self.cloud_processed / total) * 100, 2),
            simulated_cost=round(self.simulated_cost, 4),
        )
