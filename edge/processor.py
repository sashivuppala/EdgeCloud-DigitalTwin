"""Edge node processing for low-latency anomaly detection."""

from __future__ import annotations

from collections import deque
from time import perf_counter

import numpy as np

from utils.config import SystemConfig
from utils.models import ProcessedRecord, SensorRecord


class EdgeProcessor:
    """Perform lightweight anomaly detection close to the data source."""

    def __init__(self, config: SystemConfig) -> None:
        self.config = config
        self.recent_temperatures: deque[float] = deque(maxlen=25)
        self.recent_vibrations: deque[float] = deque(maxlen=25)

    def process(self, sensor: SensorRecord, processing_location: str) -> ProcessedRecord:
        """Run fast threshold and trend-based checks."""

        start = perf_counter()
        anomaly_types: list[str] = []
        score = 0.0

        if sensor.temperature >= self.config.temperature_threshold:
            anomaly_types.append("temperature_threshold")
            score += 0.35
        if sensor.vibration >= self.config.vibration_threshold:
            anomaly_types.append("vibration_threshold")
            score += 0.35
        if sensor.pressure >= self.config.pressure_threshold or sensor.pressure < 25.0:
            anomaly_types.append("pressure_abnormal")
            score += 0.15
        if sensor.fuel_flow <= self.config.fuel_flow_low_threshold:
            anomaly_types.append("fuel_flow_low")
            score += 0.15

        if self.recent_temperatures:
            temp_delta = sensor.temperature - self.recent_temperatures[-1]
            vib_delta = sensor.vibration - self.recent_vibrations[-1]
            if temp_delta > 8.0:
                anomaly_types.append("temperature_spike")
                score += 0.20
            if vib_delta > 0.25:
                anomaly_types.append("vibration_spike")
                score += 0.20

        if len(self.recent_temperatures) >= 10:
            recent_temp_mean = float(np.mean(self.recent_temperatures))
            if sensor.temperature > recent_temp_mean + 6.5:
                anomaly_types.append("thermal_drift")
                score += 0.10

        self.recent_temperatures.append(sensor.temperature)
        self.recent_vibrations.append(sensor.vibration)

        anomaly_detected = bool(anomaly_types)
        score = min(score, 1.0)
        edge_latency_ms = (perf_counter() - start) * 1000

        return ProcessedRecord(
            sensor=sensor,
            anomaly_detected=anomaly_detected,
            anomaly_score=round(score, 4),
            anomaly_types=anomaly_types,
            edge_latency_ms=round(edge_latency_ms, 4),
            processing_location=processing_location,
        )
