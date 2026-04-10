"""Synthetic telemetry generation and live streaming."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import timedelta
from typing import Iterator

import numpy as np

from utils.models import SensorRecord, utc_now


@dataclass(slots=True)
class ScenarioProfile:
    """Scenario-specific controls for system condition simulation."""

    name: str
    latency_range: tuple[float, float]
    cpu_range: tuple[float, float]
    anomaly_probability: float


SCENARIOS: dict[str, ScenarioProfile] = {
    "normal": ScenarioProfile("normal", (15.0, 35.0), (0.25, 0.55), 0.05),
    "high_latency": ScenarioProfile("high_latency", (90.0, 150.0), (0.30, 0.60), 0.08),
    "edge_overload": ScenarioProfile("edge_overload", (25.0, 55.0), (0.82, 0.95), 0.07),
    "anomaly_injection": ScenarioProfile("anomaly_injection", (20.0, 45.0), (0.35, 0.70), 0.35),
}


class SensorDataSimulator:
    """Generate aerospace telemetry with noise, spikes, and degradation."""

    def __init__(self, seed: int = 7) -> None:
        self.random = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)
        self.step = 0
        self.degradation_factor = 0.0
        self.current_time = utc_now()

    def _base_values(self) -> dict[str, float]:
        """Return nominal operating ranges with small oscillations."""

        phase = self.step / 8.0
        return {
            "temperature": 74.0 + 4.5 * np.sin(phase),
            "vibration": 0.42 + 0.06 * np.cos(phase),
            "pressure": 30.5 + 1.2 * np.sin(phase / 2),
            "fuel_flow": 101.0 + 2.5 * np.cos(phase / 2.5),
        }

    def _apply_noise(self, values: dict[str, float]) -> dict[str, float]:
        """Apply realistic random noise to each channel."""

        values["temperature"] += float(self.np_rng.normal(0, 1.2))
        values["vibration"] += float(self.np_rng.normal(0, 0.03))
        values["pressure"] += float(self.np_rng.normal(0, 0.35))
        values["fuel_flow"] += float(self.np_rng.normal(0, 0.8))
        return values

    def _apply_degradation(self, values: dict[str, float]) -> dict[str, float]:
        """Inject a gradual degradation pattern over time."""

        self.degradation_factor += 0.003
        values["temperature"] += self.degradation_factor * 4.0
        values["vibration"] += self.degradation_factor * 0.14
        values["pressure"] += self.degradation_factor * 1.8
        values["fuel_flow"] -= self.degradation_factor * 3.5
        return values

    def _apply_anomalies(self, values: dict[str, float], scenario: str) -> tuple[dict[str, float], list[str]]:
        """Inject spikes, threshold breaches, and other abnormal conditions."""

        anomaly_types: list[str] = []
        profile = SCENARIOS.get(scenario, SCENARIOS["normal"])
        should_inject = self.random.random() < profile.anomaly_probability

        if should_inject:
            choice = self.random.choice(
                ["spike", "threshold_breach", "pressure_drop", "fuel_flow_drop"]
            )
            if choice == "spike":
                values["temperature"] += self.random.uniform(12.0, 22.0)
                values["vibration"] += self.random.uniform(0.45, 0.9)
                anomaly_types.append("sudden_spike")
            elif choice == "threshold_breach":
                values["temperature"] = max(values["temperature"], self.random.uniform(93.0, 101.0))
                values["vibration"] = max(values["vibration"], self.random.uniform(1.18, 1.45))
                anomaly_types.append("threshold_breach")
            elif choice == "pressure_drop":
                values["pressure"] -= self.random.uniform(4.5, 7.5)
                anomaly_types.append("pressure_drop")
            else:
                values["fuel_flow"] -= self.random.uniform(18.0, 26.0)
                anomaly_types.append("fuel_flow_drop")

        if self.step and self.step % 45 == 0:
            values["temperature"] += 6.0
            values["vibration"] += 0.12
            anomaly_types.append("gradual_degradation")

        return values, anomaly_types

    def generate_record(self, scenario: str = "normal") -> SensorRecord:
        """Generate a single telemetry sample."""

        self.step += 1
        self.current_time += timedelta(seconds=1)

        values = self._base_values()
        values = self._apply_noise(values)
        values = self._apply_degradation(values)
        values, _ = self._apply_anomalies(values, scenario)

        profile = SCENARIOS.get(scenario, SCENARIOS["normal"])
        return SensorRecord(
            temperature=round(values["temperature"], 3),
            vibration=round(max(values["vibration"], 0.01), 4),
            pressure=round(max(values["pressure"], 0.01), 3),
            fuel_flow=round(max(values["fuel_flow"], 0.01), 3),
            timestamp=self.current_time,
            latency_ms=round(self.random.uniform(*profile.latency_range), 3),
            cpu_load=round(self.random.uniform(*profile.cpu_range), 3),
            scenario=scenario,
        )

    def stream(self, iterations: int, interval_seconds: float, scenario: str = "normal") -> Iterator[SensorRecord]:
        """Yield a simulated live sensor feed."""

        for _ in range(iterations):
            yield self.generate_record(scenario=scenario)
            if interval_seconds > 0:
                time.sleep(interval_seconds)
