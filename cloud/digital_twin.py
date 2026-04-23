"""Cloud-side historical analysis and digital twin state management."""

from __future__ import annotations

from collections import deque

import pandas as pd

try:
    from sklearn.ensemble import IsolationForest
except ImportError:  # pragma: no cover - exercised only in limited environments
    IsolationForest = None

from utils.config import SystemConfig
from utils.models import DigitalTwinState, ProcessedRecord, utc_now


class CloudDigitalTwin:
    """Store history, retrain models, and maintain aggregate pipeline state."""

    def __init__(self, config: SystemConfig) -> None:
        self.config = config
        self.state = DigitalTwinState()
        self.history: deque[dict[str, float]] = deque(maxlen=2000)
        self.model: IsolationForest | None = None

    def _state_from_health(self, health_score: float) -> str:
        """Map a numeric health score to a state label."""

        if health_score >= 0.85:
            return "HEALTHY"
        if health_score >= 0.65:
            return "DEGRADED"
        return "CRITICAL"

    def process(self, record: ProcessedRecord) -> ProcessedRecord:
        """Add cloud insights and refresh the digital twin state."""

        event = record.event
        self.history.append(
            {
                "document_size_kb": event.document_size_kb,
                "xml_complexity": event.xml_complexity,
                "validation_error_count": event.validation_error_count,
                "processing_time_ms": event.processing_time_ms,
                "queue_depth": event.queue_depth,
                "retry_count": event.retry_count,
                "transform_latency_ms": event.transform_latency_ms,
                "publish_failed": 1 if event.publish_status == "FAILED" else 0,
                "pending_publish": 1 if event.publish_status == "PENDING" else 0,
                "downstream_ack_delay_ms": event.downstream_ack_delay_ms,
            }
        )
        deep_score = self.deep_analysis(record)
        record.cloud_analysis = {
            "deep_anomaly_score": deep_score,
            "recommended_action": "stabilize_pipeline" if deep_score > 0.55 else "continue_processing",
        }
        self.update_state(record, deep_score)

        if len(self.history) >= self.config.retrain_window and len(self.history) % 25 == 0:
            self.retrain_model()
        return record

    def deep_analysis(self, record: ProcessedRecord) -> float:
        """Run richer analysis using historical context and, when available, a retrained model."""

        features = [[
            record.event.document_size_kb,
            record.event.xml_complexity,
            record.event.validation_error_count,
            record.event.processing_time_ms,
            record.event.queue_depth,
            record.event.retry_count,
            record.event.transform_latency_ms,
            record.event.downstream_ack_delay_ms,
        ]]
        model_score = 0.0
        if self.model is not None:
            raw_score = float(-self.model.score_samples(features)[0])
            model_score = min(max(raw_score, 0.0), 1.0)

        heuristic_score = record.anomaly_score
        if record.event.queue_depth >= self.config.severe_backlog_threshold:
            heuristic_score += 0.15
        if record.event.publish_status == "FAILED":
            heuristic_score += 0.20
        if record.event.retry_count >= self.config.retry_storm_threshold + 1:
            heuristic_score += 0.20
        if (
            record.event.xml_complexity >= self.config.xml_complexity_threshold
            and record.event.validation_error_count >= self.config.validation_error_threshold
        ):
            heuristic_score += 0.20

        return round(min(max((heuristic_score + model_score) / 2 if model_score else heuristic_score, 0.0), 1.0), 4)

    def retrain_model(self) -> None:
        """Retrain an unsupervised anomaly model on recent history."""

        if IsolationForest is None:
            return

        frame = pd.DataFrame(list(self.history)[-self.config.retrain_window :])
        if len(frame) < 40:
            return

        model = IsolationForest(contamination=0.08, random_state=42)
        model.fit(
            frame[
                [
                    "document_size_kb",
                    "xml_complexity",
                    "validation_error_count",
                    "processing_time_ms",
                    "queue_depth",
                    "retry_count",
                    "transform_latency_ms",
                    "downstream_ack_delay_ms",
                ]
            ]
        )
        self.model = model

    def update_state(self, record: ProcessedRecord, deep_score: float) -> None:
        """Refresh aggregate twin metrics from recent history."""

        history_frame = pd.DataFrame(list(self.history)[-30:])
        anomaly_count = self.state.anomaly_count + int(record.anomaly_detected)
        total_events_processed = self.state.total_events_processed + 1
        failed_events = self.state.failed_events + int(record.event.publish_status != "SUCCESS")

        if history_frame.empty:
            averages = {
                "processing_time_ms": 0.0,
                "queue_depth": 0.0,
                "retry_count": 0.0,
                "downstream_ack_delay_ms": 0.0,
                "validation_error_count": 0.0,
                "publish_failed": 0.0,
            }
        else:
            averages = history_frame.mean(numeric_only=True).to_dict()

        backlog_severity = min(float(averages.get("queue_depth", 0.0)) / self.config.severe_backlog_threshold, 1.5)
        retry_storm_risk = min(float(averages.get("retry_count", 0.0)) / (self.config.retry_storm_threshold + 1), 1.5)
        publish_health = max(0.0, 1.0 - float(averages.get("publish_failed", 0.0)))
        validation_issue_trend = float(averages.get("validation_error_count", 0.0))

        health_penalty = (
            (anomaly_count / max(total_events_processed, 1)) * 0.35
            + min(validation_issue_trend / 8.0, 1.0) * 0.15
            + min(retry_storm_risk, 1.0) * 0.15
            + min(backlog_severity, 1.0) * 0.15
            + (1.0 - publish_health) * 0.10
            + deep_score * 0.10
        )
        health_score = max(0.0, 1.0 - health_penalty)

        self.state = DigitalTwinState(
            status=self._state_from_health(health_score),
            last_updated=utc_now(),
            total_events_processed=total_events_processed,
            failed_events=failed_events,
            anomaly_count=anomaly_count,
            validation_issue_trend=round(validation_issue_trend, 3),
            retry_storm_risk=round(retry_storm_risk, 3),
            backlog_severity=round(backlog_severity, 3),
            publish_health=round(publish_health, 3),
            health_score=round(health_score, 4),
            average_processing_time_ms=round(float(averages.get("processing_time_ms", 0.0)), 3),
            average_queue_depth=round(float(averages.get("queue_depth", 0.0)), 3),
            average_retry_count=round(float(averages.get("retry_count", 0.0)), 3),
            average_ack_delay_ms=round(float(averages.get("downstream_ack_delay_ms", 0.0)), 3),
            last_anomaly_types=record.anomaly_types,
        )

    def get_state(self) -> DigitalTwinState:
        """Return the current digital twin state."""

        return self.state
