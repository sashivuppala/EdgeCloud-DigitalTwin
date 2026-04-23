"""Configuration values used across the enterprise pipeline twin."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SystemConfig:
    """Central configuration for simulation and orchestration."""

    database_path: Path = Path("edgecloud_digital_twin.db")
    processing_time_edge_threshold_ms: float = 240.0
    queue_backlog_threshold: int = 140
    severe_backlog_threshold: int = 260
    xml_complexity_threshold: float = 0.78
    validation_error_threshold: int = 5
    retry_storm_threshold: int = 4
    transform_latency_threshold_ms: float = 420.0
    downstream_ack_delay_threshold_ms: float = 650.0
    retrain_window: int = 120
    cloud_cost_per_event: float = 0.025
    edge_cost_per_event: float = 0.008
