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
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temperature REAL NOT NULL,
            vibration REAL NOT NULL,
            pressure REAL NOT NULL,
            fuel_flow REAL NOT NULL,
            latency_ms REAL NOT NULL,
            cpu_load REAL NOT NULL,
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
            latency_ms REAL NOT NULL,
            cpu_load REAL NOT NULL,
            requires_complex_analysis INTEGER NOT NULL
        );
        """
    )
    connection.commit()
