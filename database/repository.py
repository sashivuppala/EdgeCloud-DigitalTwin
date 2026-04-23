"""Repository helpers for persisting and loading pipeline event data."""

from __future__ import annotations

import json
import sqlite3

import pandas as pd

from utils.models import OrchestrationDecision, ProcessedRecord


class TelemetryRepository:
    """SQLite-backed repository for pipeline events, anomalies, and orchestration logs."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def log_processed_record(self, record: ProcessedRecord) -> None:
        """Persist pipeline event and anomaly data."""

        event = record.event
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO pipeline_events (
                timestamp, document_id, document_type, document_size_kb, xml_complexity,
                validation_error_count, processing_time_ms, queue_depth, retry_count,
                transform_latency_ms, publish_status, downstream_ack_delay_ms, scenario, processing_location
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.timestamp.isoformat(),
                event.document_id,
                event.document_type,
                event.document_size_kb,
                event.xml_complexity,
                event.validation_error_count,
                event.processing_time_ms,
                event.queue_depth,
                event.retry_count,
                event.transform_latency_ms,
                event.publish_status,
                event.downstream_ack_delay_ms,
                event.scenario,
                record.processing_location,
            ),
        )
        cursor.execute(
            """
            INSERT INTO anomaly_logs (
                timestamp, anomaly_detected, anomaly_score, anomaly_types, processing_location
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                event.timestamp.isoformat(),
                int(record.anomaly_detected),
                record.anomaly_score,
                json.dumps(record.anomaly_types),
                record.processing_location,
            ),
        )
        self.connection.commit()

    def log_orchestration(self, decision: OrchestrationDecision) -> None:
        """Persist orchestration decisions."""

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO orchestration_logs (
                timestamp, location, reason, processing_time_ms, queue_depth, requires_complex_analysis
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                decision.decided_at.isoformat(),
                decision.location,
                decision.reason,
                decision.processing_time_ms,
                decision.queue_depth,
                int(decision.requires_complex_analysis),
            ),
        )
        self.connection.commit()

    def fetch_recent_sensor_data(self, limit: int = 100) -> pd.DataFrame:
        """Return recent pipeline event history as a pandas DataFrame."""

        query = """
        SELECT timestamp, document_id, document_type, document_size_kb, xml_complexity,
               validation_error_count, processing_time_ms, queue_depth, retry_count,
               transform_latency_ms, publish_status, downstream_ack_delay_ms,
               scenario, processing_location
        FROM pipeline_events
        ORDER BY id DESC
        LIMIT ?
        """
        frame = pd.read_sql_query(query, self.connection, params=(limit,))
        if not frame.empty:
            frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
            frame = frame.sort_values("timestamp")
        return frame

    def fetch_recent_anomalies(self, limit: int = 20) -> pd.DataFrame:
        """Return recent anomaly records."""

        query = """
        SELECT timestamp, anomaly_detected, anomaly_score, anomaly_types, processing_location
        FROM anomaly_logs
        WHERE anomaly_detected = 1
        ORDER BY id DESC
        LIMIT ?
        """
        frame = pd.read_sql_query(query, self.connection, params=(limit,))
        if not frame.empty:
            frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        return frame

    def fetch_recent_orchestration(self, limit: int = 50) -> pd.DataFrame:
        """Return recent orchestration decisions."""

        query = """
        SELECT timestamp, location, reason, processing_time_ms, queue_depth, requires_complex_analysis
        FROM orchestration_logs
        ORDER BY id DESC
        LIMIT ?
        """
        frame = pd.read_sql_query(query, self.connection, params=(limit,))
        if not frame.empty:
            frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        return frame
