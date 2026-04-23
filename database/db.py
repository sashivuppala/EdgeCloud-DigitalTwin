"""SQLite database bootstrap utilities."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def get_connection(db_path: Path) -> sqlite3.Connection:
    """Create a SQLite connection with row access by name."""

    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    """Create all tables required by the application."""

    cursor = connection.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS pipeline_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            document_id TEXT NOT NULL,
            document_type TEXT NOT NULL,
            document_size_kb REAL NOT NULL,
            xml_complexity REAL NOT NULL,
            validation_error_count INTEGER NOT NULL,
            processing_time_ms REAL NOT NULL,
            queue_depth INTEGER NOT NULL,
            retry_count INTEGER NOT NULL,
            transform_latency_ms REAL NOT NULL,
            publish_status TEXT NOT NULL,
            downstream_ack_delay_ms REAL NOT NULL,
            scenario TEXT NOT NULL,
            processing_location TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS anomaly_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            anomaly_detected INTEGER NOT NULL,
            anomaly_score REAL NOT NULL,
            anomaly_types TEXT NOT NULL,
            processing_location TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS orchestration_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            location TEXT NOT NULL,
            reason TEXT NOT NULL,
            processing_time_ms REAL NOT NULL,
            queue_depth INTEGER NOT NULL,
            requires_complex_analysis INTEGER NOT NULL
        );
        """
    )
    connection.commit()
