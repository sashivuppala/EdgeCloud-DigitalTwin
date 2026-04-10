"""Configuration values used across the project."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SystemConfig:
    """Central configuration for simulation and orchestration."""

    database_path: Path = Path("edgecloud_digital_twin.db")
    latency_threshold_ms: float = 75.0
    edge_overload_threshold: float = 0.80
    temperature_threshold: float = 92.0
    vibration_threshold: float = 1.15
    pressure_threshold: float = 36.5
    fuel_flow_low_threshold: float = 82.0
    retrain_window: int = 120
    cloud_cost_per_event: float = 0.025
    edge_cost_per_event: float = 0.008
