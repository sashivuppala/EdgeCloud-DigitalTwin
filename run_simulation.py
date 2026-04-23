"""Run live enterprise pipeline scenarios against the digital twin system."""

from __future__ import annotations

import argparse
from pprint import pprint

from simulator.generator import PipelineEventSimulator, SCENARIOS
from utils.system import PipelineTwinPlatform


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Run enterprise pipeline twin simulations.")
    parser.add_argument("--scenario", choices=sorted(SCENARIOS.keys()), default="normal_processing")
    parser.add_argument("--iterations", type=int, default=25)
    parser.add_argument("--interval", type=float, default=0.0)
    parser.add_argument("--use-api", action="store_true", help="Send records to the FastAPI server instead of direct ingestion.")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000/pipeline-event")
    return parser.parse_args()


def run_direct(scenario: str, iterations: int, interval: float) -> None:
    """Run a local simulation directly against the system class."""

    simulator = PipelineEventSimulator()
    system = PipelineTwinPlatform()

    for record in simulator.stream(iterations=iterations, interval_seconds=interval, scenario=scenario):
        processed, decision = system.ingest_event(record)
        pprint(
            {
                "timestamp": record.timestamp.isoformat(),
                "document_id": record.document_id,
                "document_type": record.document_type,
                "scenario": scenario,
                "route": decision.location,
                "reason": decision.reason,
                "anomaly": processed.anomaly_detected,
                "anomaly_types": processed.anomaly_types,
                "queue_depth": record.queue_depth,
                "processing_time_ms": record.processing_time_ms,
                "publish_status": record.publish_status,
            }
        )

    print("\nDigital Twin State")
    pprint(system.get_state().model_dump())
    print("\nMetrics")
    pprint(system.get_metrics().model_dump())


def run_via_api(scenario: str, iterations: int, interval: float, api_url: str) -> None:
    """Run a simulation by posting records to the API layer."""

    import requests

    simulator = PipelineEventSimulator()
    for record in simulator.stream(iterations=iterations, interval_seconds=interval, scenario=scenario):
        response = requests.post(api_url, json=record.model_dump(mode="json"), timeout=15)
        response.raise_for_status()
        pprint(response.json())


if __name__ == "__main__":
    args = parse_args()
    if args.use_api:
        run_via_api(args.scenario, args.iterations, args.interval, args.api_url)
    else:
        run_direct(args.scenario, args.iterations, args.interval)
