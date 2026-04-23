"""Dynamic orchestration rules for enterprise workflow placement."""

from __future__ import annotations

from utils.config import SystemConfig
from utils.models import OrchestrationDecision


class OrchestrationEngine:
    """Decide whether work should run at the edge or in the cloud."""

    def __init__(self, config: SystemConfig) -> None:
        self.config = config

    def decide(
        self,
        processing_time_ms: float,
        queue_depth: int,
        requires_complex_analysis: bool,
        retry_count: int,
        publish_failure_risk: bool,
        backlog_severity: float,
    ) -> OrchestrationDecision:
        """Apply enterprise workflow orchestration rules."""

        if processing_time_ms <= self.config.processing_time_edge_threshold_ms and queue_depth < self.config.queue_backlog_threshold and not requires_complex_analysis:
            return OrchestrationDecision(
                location="edge",
                reason="low-latency validation handled at edge",
                processing_time_ms=processing_time_ms,
                queue_depth=queue_depth,
                requires_complex_analysis=requires_complex_analysis,
            )
        if backlog_severity >= 1.0 or queue_depth >= self.config.severe_backlog_threshold:
            return OrchestrationDecision(
                location="cloud",
                reason="high backlog triggered cloud offload",
                processing_time_ms=processing_time_ms,
                queue_depth=queue_depth,
                requires_complex_analysis=requires_complex_analysis,
            )
        if retry_count >= self.config.retry_storm_threshold + 1:
            return OrchestrationDecision(
                location="cloud",
                reason="retry storm risk requires centralized analysis",
                processing_time_ms=processing_time_ms,
                queue_depth=queue_depth,
                requires_complex_analysis=True,
            )
        if publish_failure_risk:
            return OrchestrationDecision(
                location="cloud",
                reason="publish failure risk escalated to cloud",
                processing_time_ms=processing_time_ms,
                queue_depth=queue_depth,
                requires_complex_analysis=True,
            )
        if requires_complex_analysis:
            return OrchestrationDecision(
                location="cloud",
                reason="complex transformation escalated to cloud",
                processing_time_ms=processing_time_ms,
                queue_depth=queue_depth,
                requires_complex_analysis=requires_complex_analysis,
            )
        return OrchestrationDecision(
            location="cloud",
            reason="normal workflow synchronization routed to cloud",
            processing_time_ms=processing_time_ms,
            queue_depth=queue_depth,
            requires_complex_analysis=requires_complex_analysis,
        )
