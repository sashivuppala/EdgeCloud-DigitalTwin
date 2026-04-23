"""Edge validation layer for low-latency event screening."""

from __future__ import annotations

from collections import deque
from time import perf_counter

import numpy as np

from utils.config import SystemConfig
from utils.models import PipelineEvent, ProcessedRecord


class EdgeProcessor:
    """Perform lightweight validation and quick anomaly screening."""

    def __init__(self, config: SystemConfig) -> None:
        self.config = config
        self.recent_processing_times: deque[float] = deque(maxlen=25)
        self.recent_queue_depths: deque[int] = deque(maxlen=25)

    def process(self, event: PipelineEvent, processing_location: str) -> ProcessedRecord:
        """Run fast validation and operational checks."""

        # TODO(stage-2-ai): Replace or augment threshold rules with a compact edge anomaly model.

        start = perf_counter()
        anomaly_types: list[str] = []
        score = 0.0

        if event.validation_error_count >= self.config.validation_error_threshold:
            anomaly_types.append("validation_error_threshold")
            score += 0.30
        if event.xml_complexity >= self.config.xml_complexity_threshold:
            anomaly_types.append("xml_complexity_high")
            score += 0.20
        if event.queue_depth >= self.config.queue_backlog_threshold:
            anomaly_types.append("queue_backlog")
            score += 0.18
        if event.retry_count >= self.config.retry_storm_threshold:
            anomaly_types.append("retry_storm_risk")
            score += 0.22
        if event.publish_status == "FAILED":
            anomaly_types.append("publish_failed")
            score += 0.22
        if event.downstream_ack_delay_ms >= self.config.downstream_ack_delay_threshold_ms:
            anomaly_types.append("downstream_ack_delay")
            score += 0.12

        if self.recent_processing_times:
            processing_delta = event.processing_time_ms - self.recent_processing_times[-1]
            queue_delta = event.queue_depth - self.recent_queue_depths[-1]
            if processing_delta > 120.0:
                anomaly_types.append("processing_time_spike")
                score += 0.20
            if queue_delta > 80:
                anomaly_types.append("queue_depth_spike")
                score += 0.20

        if len(self.recent_processing_times) >= 10:
            recent_mean = float(np.mean(self.recent_processing_times))
            if event.processing_time_ms > recent_mean + 95.0:
                anomaly_types.append("sustained_processing_drift")
                score += 0.10

        self.recent_processing_times.append(event.processing_time_ms)
        self.recent_queue_depths.append(event.queue_depth)

        anomaly_detected = bool(anomaly_types)
        score = min(score, 1.0)
        edge_latency_ms = (perf_counter() - start) * 1000

        return ProcessedRecord(
            event=event,
            anomaly_detected=anomaly_detected,
            anomaly_score=round(score, 4),
            anomaly_types=sorted(set(anomaly_types)),
            edge_latency_ms=round(edge_latency_ms, 4),
            processing_location=processing_location,
        )
