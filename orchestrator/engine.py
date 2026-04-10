"""Dynamic orchestration rules for edge/cloud placement."""

from __future__ import annotations

from utils.config import SystemConfig
from utils.models import OrchestrationDecision


class OrchestrationEngine:
    """Decide whether work should run at the edge or in the cloud."""

    def __init__(self, config: SystemConfig) -> None:
        self.config = config

    def decide(self, latency_ms: float, cpu_load: float, requires_complex_analysis: bool) -> OrchestrationDecision:
        """Apply the orchestration rules provided by the project requirements."""

        if latency_ms > self.config.latency_threshold_ms:
            return OrchestrationDecision(
                location="edge",
                reason="latency-sensitive traffic kept at the edge",
                latency_ms=latency_ms,
                cpu_load=cpu_load,
                requires_complex_analysis=requires_complex_analysis,
            )
        if cpu_load > self.config.edge_overload_threshold:
            return OrchestrationDecision(
                location="cloud",
                reason="edge overloaded, workload offloaded to cloud",
                latency_ms=latency_ms,
                cpu_load=cpu_load,
                requires_complex_analysis=requires_complex_analysis,
            )
        if requires_complex_analysis:
            return OrchestrationDecision(
                location="cloud",
                reason="complex analysis requires cloud resources",
                latency_ms=latency_ms,
                cpu_load=cpu_load,
                requires_complex_analysis=requires_complex_analysis,
            )
        return OrchestrationDecision(
            location="cloud",
            reason="normal routing to cloud for full twin synchronization",
            latency_ms=latency_ms,
            cpu_load=cpu_load,
            requires_complex_analysis=requires_complex_analysis,
        )
