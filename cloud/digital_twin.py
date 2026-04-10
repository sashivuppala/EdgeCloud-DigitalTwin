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
    """Store history, retrain models, and maintain aggregate health state."""

    def __init__(self, config: SystemConfig) -> None:
        self.config = config
        self.state = DigitalTwinState()
        self.history: deque[dict[str, float]] = deque(maxlen=2000)
        self.model: IsolationForest | None = None

    def _state_from_health(self, health_score: float) -> str:
        """Map a numeric health score to a state label."""

        if health_score >= 0.85:
            return "healthy"
        if health_score >= 0.65:
            return "warning"
        return "critical"

    def process(self, record: ProcessedRecord) -> ProcessedRecord:
        """Add cloud insights and refresh the digital twin state."""

        sensor = record.sensor
        self.history.append(
            {
                "temperature": sensor.temperature,
                "vibration": sensor.vibration,
                "pressure": sensor.pressure,
                "fuel_flow": sensor.fuel_flow,
            }
        )
        deep_score = self.deep_analysis(record)
        record.cloud_analysis = {
            "deep_anomaly_score": deep_score,
            "recommended_action": "inspect_engine" if deep_score > 0.55 else "continue_monitoring",
        }
        self.update_state(record, deep_score)

        if len(self.history) >= self.config.retrain_window and len(self.history) % 25 == 0:
            self.retrain_model()
        return record

    def deep_analysis(self, record: ProcessedRecord) -> float:
        """Run richer analysis using historical context and, when available, a retrained model."""

        features = [[
            record.sensor.temperature,
            record.sensor.vibration,
            record.sensor.pressure,
            record.sensor.fuel_flow,
        ]]
        model_score = 0.0
        if self.model is not None:
            raw_score = float(-self.model.score_samples(features)[0])
            model_score = min(max(raw_score, 0.0), 1.0)

        heuristic_score = record.anomaly_score
        if record.sensor.pressure < 25.5:
            heuristic_score += 0.15
        if record.sensor.fuel_flow < 80.0:
            heuristic_score += 0.20
        if record.sensor.temperature > 95.0 and record.sensor.vibration > 1.2:
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
        model.fit(frame[["temperature", "vibration", "pressure", "fuel_flow"]])
        self.model = model

    def update_state(self, record: ProcessedRecord, deep_score: float) -> None:
        """Refresh aggregate twin metrics from recent history."""

        history_frame = pd.DataFrame(list(self.history)[-30:])
        anomaly_count = self.state.anomaly_count + int(record.anomaly_detected)
        total_samples = self.state.total_samples + 1
        health_score = max(0.0, 1.0 - ((anomaly_count / max(total_samples, 1)) * 0.6 + deep_score * 0.4))

        if history_frame.empty:
            averages = {"temperature": 0.0, "vibration": 0.0, "pressure": 0.0, "fuel_flow": 0.0}
        else:
            averages = history_frame.mean(numeric_only=True).to_dict()

        self.state = DigitalTwinState(
            status=self._state_from_health(health_score),
            last_updated=utc_now(),
            anomaly_count=anomaly_count,
            total_samples=total_samples,
            health_score=round(health_score, 4),
            moving_average_temperature=round(float(averages.get("temperature", 0.0)), 3),
            moving_average_vibration=round(float(averages.get("vibration", 0.0)), 4),
            moving_average_pressure=round(float(averages.get("pressure", 0.0)), 3),
            moving_average_fuel_flow=round(float(averages.get("fuel_flow", 0.0)), 3),
            last_anomaly_types=record.anomaly_types,
        )

    def get_state(self) -> DigitalTwinState:
        """Return the current digital twin state."""

        return self.state
