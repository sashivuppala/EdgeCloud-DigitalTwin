"""Repository helpers for persisting and loading telemetry data."""

from __future__ import annotations

import json
import sqlite3

import pandas as pd

from utils.models import OrchestrationDecision, ProcessedRecord


class TelemetryRepository:
    """SQLite-backed repository for telemetry, anomalies, and orchestration logs."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def log_processed_record(self, record: ProcessedRecord) -> None:
        """Persist sensor and anomaly data."""

        sensor = record.sensor
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO sensor_data (
                timestamp, temperature, vibration, pressure, fuel_flow,
                latency_ms, cpu_load, scenario, processing_location
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sensor.timestamp.isoformat(),
                sensor.temperature,
                sensor.vibration,
                sensor.pressure,
                sensor.fuel_flow,
                sensor.latency_ms,
                sensor.cpu_load,
                sensor.scenario,
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
                sensor.timestamp.isoformat(),
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
                timestamp, location, reason, latency_ms, cpu_load, requires_complex_analysis
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                decision.decided_at.isoformat(),
                decision.location,
                decision.reason,
                decision.latency_ms,
                decision.cpu_load,
                int(decision.requires_complex_analysis),
            ),
        )
        self.connection.commit()

    def fetch_recent_sensor_data(self, limit: int = 100) -> pd.DataFrame:
        """Return recent sensor history as a pandas DataFrame."""

        query = """
        SELECT timestamp, temperature, vibration, pressure, fuel_flow, latency_ms, cpu_load,
               scenario, processing_location
        FROM sensor_data
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
        SELECT timestamp, location, reason, latency_ms, cpu_load, requires_complex_analysis
        FROM orchestration_logs
        ORDER BY id DESC
        LIMIT ?
        """
        frame = pd.read_sql_query(query, self.connection, params=(limit,))
        if not frame.empty:
            frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        return frame
