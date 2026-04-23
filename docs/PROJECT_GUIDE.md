# EdgeCloud-DigitalTwin Project Guide

## 1. Purpose

This guide is the primary help and about document for `EdgeCloud-DigitalTwin`.

It is written for:

- engineering teams onboarding to the codebase
- product and delivery teams who want a clear understanding of what the system does
- stakeholders who need a concise explanation of architecture, simulation scope, and operational value

The project has been refactored in place into an enterprise software-oriented digital twin for distributed processing pipelines.

## 2. Product Overview

`EdgeCloud-DigitalTwin` models an enterprise document and workflow processing platform using an edge-cloud digital twin architecture.

The platform simulates:

- document ingestion
- lightweight validation
- transformation stages
- publish outcomes
- acknowledgement delays
- queue buildup
- retry storms
- workflow health degradation

The goal is to show how a distributed enterprise pipeline can be monitored and orchestrated in real time using:

- edge validation for fast screening
- cloud analysis for deeper trend intelligence
- a digital twin for workflow health state
- orchestration logic for routing decisions

## 3. Refactoring Summary

The system architecture was intentionally preserved while the domain model was refocused.

### Preserved architectural elements

- API layer
- orchestration engine
- cloud digital twin pattern
- dashboard
- SQLite logging
- simulation runner
- Docker support
- automated tests

### Updated domain concepts

Old sensor-style telemetry concepts were replaced with enterprise workflow concepts such as:

- `document_size_kb`
- `xml_complexity`
- `validation_error_count`
- `processing_time_ms`
- `queue_depth`
- `retry_count`
- `transform_latency_ms`
- `publish_status`
- `downstream_ack_delay_ms`

## 4. Enterprise Pipeline Interpretation

### Edge layer

The edge layer represents:

- low-latency validation
- lightweight parsing checks
- quick anomaly detection
- early rejection or escalation of malformed work

### Cloud layer

The cloud layer represents:

- deeper analysis
- historical trend evaluation
- health scoring
- anomaly model retraining
- centralized intelligence for retries, backlogs, and publish instability

### Digital twin

The digital twin represents the live health of the workflow platform, not a physical asset.

It tracks:

- total events processed
- failed events
- validation issue trends
- retry storm risk
- backlog severity
- publish health
- overall health score
- overall status

## 5. Architecture

```text
Input/Event Simulator
        |
        v
Orchestration Engine
        |
        +--> Edge Validation Layer
        |
        +--> Cloud Analysis Layer
                 |
                 v
        Pipeline Digital Twin State
                 |
                 v
      SQLite Logging + API + Dashboard
```

### Conceptual inspiration

This design aligns conceptually to large-scale enterprise processing environments where workflows include validation, transformation, publishing, retries, acknowledgements, and monitoring of queue-driven throughput.

## 6. Main Components

### `simulator/generator.py`

Generates enterprise workflow events and scenario-specific anomalies.

Scenarios include:

- `normal_processing`
- `high_queue_backlog`
- `malformed_xml_burst`
- `transformation_bottleneck`
- `publication_failure_spike`
- `retry_storm`
- `downstream_ack_delay`
- `mixed_enterprise_load`

### `edge/processor.py`

Implements the edge validation layer.

It performs:

- threshold checks for validation errors
- XML complexity checks
- queue depth spike checks
- retry pressure checks
- publish failure and acknowledgement delay screening

### `cloud/digital_twin.py`

Maintains historical workflow state and computes aggregate pipeline health.

It calculates:

- deep anomaly scores
- publish health
- backlog severity
- retry storm risk
- validation issue trend
- final digital twin status

### `orchestrator/engine.py`

Determines whether an event should remain at the edge or be analyzed in the cloud.

Routing factors:

- processing time
- queue depth
- event complexity
- retry count
- publish failure risk
- backlog severity

### `database/db.py` and `database/repository.py`

Persist:

- pipeline events
- anomaly logs
- orchestration logs

### `api/app.py`

Exposes:

- `POST /pipeline-event`
- `POST /sensor-data` as a compatibility alias
- `GET /status`
- `GET /metrics`

### `dashboard.py`

Provides a monitoring view for:

- pipeline status
- health score
- event volume
- processing time
- queue backlog trend
- retry trend
- publish distribution
- routing distribution
- recent anomalies

## 7. Event Schema

Each simulated event contains:

- `document_id`
- `document_type`
- `document_size_kb`
- `xml_complexity`
- `validation_error_count`
- `processing_time_ms`
- `queue_depth`
- `retry_count`
- `transform_latency_ms`
- `publish_status`
- `downstream_ack_delay_ms`
- `timestamp`
- `scenario`

## 8. Pipeline Health Model

The digital twin health score combines multiple operational factors:

- anomaly frequency
- validation issue trend
- retry storm risk
- backlog severity
- publish failure behavior
- deep anomaly analysis

Status values:

- `HEALTHY`
- `DEGRADED`
- `CRITICAL`

## 9. Developer Setup

### Required software

- Python `3.10` to `3.12`
- `pip`
- Git

### Recommended tools

- Visual Studio Code or PyCharm
- Postman or curl
- Docker Desktop

### Optional tools

- Streamlit
- scikit-learn for model retraining

## 10. Installation

### Clone

```bash
git clone https://github.com/sashivuppala/EdgeCloud-DigitalTwin.git
cd EdgeCloud-DigitalTwin
```

### Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

Optional:

```bash
pip install -r requirements-ml.txt
```

## 11. Run Instructions

### Start the API

```bash
python main.py
```

### Run a direct simulation

```bash
python run_simulation.py --scenario normal_processing --iterations 40
```

### Run a backlog-heavy scenario

```bash
python run_simulation.py --scenario high_queue_backlog --iterations 40
```

### Run malformed XML burst simulation

```bash
python run_simulation.py --scenario malformed_xml_burst --iterations 40
```

### Run retry storm simulation

```bash
python run_simulation.py --scenario retry_storm --iterations 40
```

### Run through the API

```bash
python run_simulation.py --scenario mixed_enterprise_load --iterations 30 --use-api
```

### Launch the dashboard

```bash
streamlit run dashboard.py
```

## 12. API Usage

### `POST /pipeline-event`

Processes a single enterprise workflow event.

Sample payload:

```json
{
  "document_id": "DOC-001",
  "document_type": "INVOICE",
  "document_size_kb": 188.4,
  "xml_complexity": 0.41,
  "validation_error_count": 0,
  "processing_time_ms": 135.0,
  "queue_depth": 28,
  "retry_count": 0,
  "transform_latency_ms": 122.0,
  "publish_status": "SUCCESS",
  "downstream_ack_delay_ms": 88.0,
  "timestamp": "2026-04-22T12:00:00Z",
  "scenario": "normal_processing"
}
```

### `GET /status`

Returns the current pipeline digital twin state.

### `GET /metrics`

Returns operational metrics for the workflow platform.

## 13. Database Design

Default database file:

```text
edgecloud_digital_twin.db
```

Tables:

- `pipeline_events`
- `anomaly_logs`
- `orchestration_logs`

### `pipeline_events`

Stores:

- event identity
- document metadata
- processing and queue metrics
- publish status
- scenario
- processing location

### `anomaly_logs`

Stores:

- anomaly flag
- anomaly score
- anomaly types
- processing location
- timestamp

### `orchestration_logs`

Stores:

- route
- reason
- processing time
- queue depth
- complexity flag
- timestamp

## 14. Testing

### Included tests

The suite validates:

- normal enterprise processing
- edge routing for low-latency validation
- cloud routing under high backlog
- malformed XML burst handling
- retry storm escalation
- publication failure metric tracking
- API endpoint correctness

### Run tests

```bash
python -m pytest -q tests/test_system.py
```

### Expected result

```text
7 passed in 1.47s
```

### Test result note for documentation

The current recorded outcome for this refactor run was a clean pass across all seven tests after installing the required packages.

## 15. Developer Walkthrough

Recommended reading order:

1. `README.md`
2. `utils/system.py`
3. `utils/models.py`
4. `simulator/generator.py`
5. `edge/processor.py`
6. `orchestrator/engine.py`
7. `cloud/digital_twin.py`
8. `api/app.py`
9. `dashboard.py`
10. `tests/test_system.py`

## 16. Extension Ideas

Safe next steps:

- add multiple pipeline identifiers or tenant IDs
- add stage-level digital twin views
- add queue partition simulations
- add alerting and notifications
- replace SQLite with PostgreSQL
- add authentication and role-based access
- split edge and cloud into separate services
- enrich dashboard filtering and drill-downs

## 17. Summary for Product and Delivery Teams

`EdgeCloud-DigitalTwin` is now an enterprise pipeline digital twin that simulates how large-scale document and workflow systems behave under normal load and failure conditions. It captures validation issues, transformation bottlenecks, retries, backlog buildup, publication instability, and acknowledgement delays. The platform routes work intelligently across edge and cloud layers, maintains a live health model, and provides operational visibility through APIs, logs, and dashboards.
