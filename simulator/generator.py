"""Synthetic enterprise pipeline event generation and live streaming."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import timedelta
from typing import Iterator

import numpy as np

from utils.models import PipelineEvent, utc_now


@dataclass(slots=True)
class ScenarioProfile:
    """Scenario-specific controls for enterprise workflow simulation."""

    name: str
    queue_depth_range: tuple[int, int]
    processing_time_range: tuple[float, float]
    transform_latency_range: tuple[float, float]
    ack_delay_range: tuple[float, float]
    retry_range: tuple[int, int]
    anomaly_probability: float


SCENARIOS: dict[str, ScenarioProfile] = {
    "normal_processing": ScenarioProfile("normal_processing", (10, 65), (60.0, 180.0), (50.0, 160.0), (20.0, 110.0), (0, 1), 0.04),
    "high_queue_backlog": ScenarioProfile("high_queue_backlog", (180, 360), (110.0, 260.0), (140.0, 320.0), (70.0, 160.0), (1, 3), 0.10),
    "malformed_xml_burst": ScenarioProfile("malformed_xml_burst", (30, 120), (90.0, 220.0), (70.0, 220.0), (40.0, 150.0), (1, 3), 0.35),
    "transformation_bottleneck": ScenarioProfile("transformation_bottleneck", (90, 220), (160.0, 380.0), (380.0, 760.0), (80.0, 220.0), (1, 4), 0.22),
    "publication_failure_spike": ScenarioProfile("publication_failure_spike", (45, 140), (80.0, 210.0), (110.0, 260.0), (120.0, 420.0), (1, 5), 0.30),
    "retry_storm": ScenarioProfile("retry_storm", (120, 260), (140.0, 330.0), (200.0, 420.0), (120.0, 260.0), (3, 8), 0.28),
    "downstream_ack_delay": ScenarioProfile("downstream_ack_delay", (40, 130), (90.0, 230.0), (90.0, 240.0), (450.0, 1100.0), (1, 3), 0.18),
}


class PipelineEventSimulator:
    """Generate enterprise workflow events with realistic anomalies."""

    def __init__(self, seed: int = 7) -> None:
        self.random = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)
        self.step = 0
        self.degradation_factor = 0.0
        self.current_time = utc_now()
        self.document_types = [
            "INVOICE",
            "CLAIM",
            "POLICY_UPDATE",
            "PURCHASE_ORDER",
            "CUSTOMER_PROFILE",
            "SETTLEMENT_NOTICE",
        ]

    def _base_values(self) -> dict[str, float]:
        """Return nominal processing characteristics with small oscillations."""

        phase = self.step / 8.0
        return {
            "document_size_kb": 240.0 + 70.0 * np.sin(phase),
            "xml_complexity": 0.34 + 0.09 * np.cos(phase),
            "validation_error_count": 0.6 + 0.4 * np.sin(phase / 2),
            "processing_time_ms": 110.0 + 35.0 * np.cos(phase / 2.5),
            "queue_depth": 42.0 + 15.0 * np.sin(phase / 3),
            "retry_count": 0.3 + 0.2 * np.cos(phase / 4),
            "transform_latency_ms": 105.0 + 30.0 * np.sin(phase / 2.7),
            "downstream_ack_delay_ms": 75.0 + 22.0 * np.cos(phase / 2.2),
        }

    def _apply_noise(self, values: dict[str, float]) -> dict[str, float]:
        """Apply realistic random noise to each metric."""

        values["document_size_kb"] += float(self.np_rng.normal(0, 18.0))
        values["xml_complexity"] += float(self.np_rng.normal(0, 0.03))
        values["validation_error_count"] += float(self.np_rng.normal(0, 0.4))
        values["processing_time_ms"] += float(self.np_rng.normal(0, 18.0))
        values["queue_depth"] += float(self.np_rng.normal(0, 9.0))
        values["retry_count"] += float(self.np_rng.normal(0, 0.35))
        values["transform_latency_ms"] += float(self.np_rng.normal(0, 22.0))
        values["downstream_ack_delay_ms"] += float(self.np_rng.normal(0, 30.0))
        return values

    def _apply_degradation(self, values: dict[str, float]) -> dict[str, float]:
        """Inject gradual pipeline strain over time."""

        self.degradation_factor += 0.003
        values["processing_time_ms"] += self.degradation_factor * 95.0
        values["queue_depth"] += self.degradation_factor * 80.0
        values["transform_latency_ms"] += self.degradation_factor * 105.0
        values["downstream_ack_delay_ms"] += self.degradation_factor * 90.0
        return values

    def _apply_anomalies(self, values: dict[str, float], scenario: str) -> tuple[dict[str, float], list[str]]:
        """Inject enterprise pipeline anomalies."""

        anomaly_types: list[str] = []
        profile = SCENARIOS.get(scenario, SCENARIOS["normal_processing"])
        should_inject = self.random.random() < profile.anomaly_probability

        publish_status = "SUCCESS"
        if should_inject:
            choice = self.random.choice(
                ["xml_failure", "publish_failure", "retry_spike", "backlog_spike", "transform_bottleneck"]
            )
            if choice == "xml_failure":
                values["xml_complexity"] += self.random.uniform(0.25, 0.4)
                values["validation_error_count"] += self.random.uniform(5.0, 11.0)
                anomaly_types.append("malformed_xml_pattern")
            elif choice == "publish_failure":
                publish_status = "FAILED"
                values["downstream_ack_delay_ms"] += self.random.uniform(240.0, 520.0)
                anomaly_types.append("publish_failure")
            elif choice == "retry_spike":
                values["retry_count"] += self.random.uniform(4.0, 8.0)
                anomaly_types.append("retry_storm_risk")
            elif choice == "backlog_spike":
                values["queue_depth"] += self.random.uniform(140.0, 260.0)
                values["processing_time_ms"] += self.random.uniform(70.0, 140.0)
                anomaly_types.append("queue_backlog_spike")
            else:
                values["transform_latency_ms"] += self.random.uniform(260.0, 480.0)
                anomaly_types.append("transform_bottleneck")

        if self.step and self.step % 45 == 0:
            values["queue_depth"] += 35.0
            values["retry_count"] += 1.0
            anomaly_types.append("gradual_pipeline_degradation")

        if scenario == "malformed_xml_burst":
            values["xml_complexity"] += self.random.uniform(0.18, 0.32)
            values["validation_error_count"] += self.random.uniform(3.0, 8.0)
            anomaly_types.append("schema_breakage_burst")
        elif scenario == "transformation_bottleneck":
            values["transform_latency_ms"] += self.random.uniform(180.0, 360.0)
            anomaly_types.append("mapping_delay")
        elif scenario == "publication_failure_spike":
            publish_status = "FAILED" if self.random.random() < 0.45 else publish_status
            anomaly_types.append("publication_gateway_instability")
        elif scenario == "retry_storm":
            values["retry_count"] += self.random.uniform(2.0, 5.0)
            anomaly_types.append("retry_surge")
        elif scenario == "downstream_ack_delay":
            values["downstream_ack_delay_ms"] += self.random.uniform(220.0, 520.0)
            publish_status = "PENDING"
            anomaly_types.append("ack_wait")

        return values, sorted(set(anomaly_types)), publish_status

    def generate_record(self, scenario: str = "normal_processing") -> PipelineEvent:
        """Generate a single enterprise workflow event."""

        self.step += 1
        self.current_time += timedelta(seconds=1)

        values = self._base_values()
        values = self._apply_noise(values)
        values = self._apply_degradation(values)
        values, _, publish_status = self._apply_anomalies(values, scenario)

        profile = SCENARIOS.get(scenario, SCENARIOS["normal_processing"])
        values["queue_depth"] = max(values["queue_depth"], self.random.uniform(*profile.queue_depth_range))
        values["processing_time_ms"] = max(values["processing_time_ms"], self.random.uniform(*profile.processing_time_range))
        values["transform_latency_ms"] = max(values["transform_latency_ms"], self.random.uniform(*profile.transform_latency_range))
        values["downstream_ack_delay_ms"] = max(values["downstream_ack_delay_ms"], self.random.uniform(*profile.ack_delay_range))
        values["retry_count"] = max(values["retry_count"], self.random.uniform(*profile.retry_range))

        return PipelineEvent(
            document_id=f"DOC-{self.step:06d}",
            document_type=self.random.choice(self.document_types),
            document_size_kb=round(max(values["document_size_kb"], 24.0), 3),
            xml_complexity=round(min(max(values["xml_complexity"], 0.02), 1.0), 4),
            validation_error_count=int(max(round(values["validation_error_count"]), 0)),
            processing_time_ms=round(max(values["processing_time_ms"], profile.processing_time_range[0]), 3),
            queue_depth=int(max(round(max(values["queue_depth"], profile.queue_depth_range[0])), 0)),
            retry_count=int(max(round(max(values["retry_count"], profile.retry_range[0])), 0)),
            transform_latency_ms=round(max(values["transform_latency_ms"], profile.transform_latency_range[0]), 3),
            publish_status=publish_status,
            downstream_ack_delay_ms=round(max(values["downstream_ack_delay_ms"], profile.ack_delay_range[0]), 3),
            timestamp=self.current_time,
            scenario=scenario,
        )

    def stream(self, iterations: int, interval_seconds: float, scenario: str = "normal_processing") -> Iterator[PipelineEvent]:
        """Yield a simulated live pipeline event stream."""

        for _ in range(iterations):
            yield self.generate_record(scenario=scenario)
            if interval_seconds > 0:
                time.sleep(interval_seconds)
