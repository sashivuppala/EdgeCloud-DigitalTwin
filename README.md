# EdgeCloud-DigitalTwin: Digital Twin for Enterprise Processing Pipelines

`EdgeCloud-DigitalTwin` is a digital twin and orchestration system for enterprise processing pipelines. It models distributed document and workflow processing, routes work between edge and cloud layers, maintains a live pipeline health model, and exposes APIs, metrics, logs, and dashboards for operational visibility.

For a detailed product and engineering guide, see [docs/PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md).

## Project Purpose

This project demonstrates how a distributed enterprise processing platform can be represented as an edge-cloud digital twin:

- the input event generator produces workflow records such as XML-heavy documents, validation results, transformation timings, and publish outcomes
- the edge validation layer performs low-latency validation and quick anomaly screening
- the cloud analysis layer performs deeper trend analysis, workflow-state evaluation, and health scoring
- the orchestration engine decides where work should be processed based on latency, backlog, retry pressure, and complexity
- the API, database, and dashboard make the workflow state visible to operators and developers

This design is aligned to enterprise workflow platforms where validation, transformation, publishing, acknowledgement, retries, and queue behavior must be monitored continuously.

## Domain Refactoring Note

The core edge-cloud architecture remains the same, but the domain has been refocused from generic telemetry-style processing to enterprise workflow and document processing. The event generator, digital twin, orchestration logic, dashboard, and documentation now model distributed pipeline operations consistently.

## Features

- Enterprise pipeline event generation for document ingestion and workflow execution
- Scenarios for queue backlog, malformed XML bursts, retry storms, transformation bottlenecks, and publish failures
- Edge validation for lightweight parsing checks and quick anomaly detection
- Cloud analysis for historical trend analysis, digital twin state updates, and optional retraining
- Orchestration logic that routes work between edge and cloud based on queue depth, latency, retry pressure, and complexity
- FastAPI endpoints for pipeline event ingestion, status, metrics, and health
- SQLite logging for events, anomalies, and orchestration decisions
- Streamlit dashboard for pipeline health, routing visibility, and recent event activity
- Docker support and automated tests

## Architecture

```text
Input/Event Generator
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

## Enterprise Event Model

Each pipeline event includes:

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

## Simulation Scenarios

The event generator supports these enterprise pipeline scenarios:

- `normal_processing`
- `high_queue_backlog`
- `malformed_xml_burst`
- `transformation_bottleneck`
- `publication_failure_spike`
- `retry_storm`
- `downstream_ack_delay`

## Edge vs Cloud Processing

### Edge Validation Layer

The edge layer is optimized for low-latency checks such as:

- validation error threshold breaches
- malformed XML indicators
- queue spikes
- retry storm early warnings
- publish and acknowledgement issues that need immediate screening

### Cloud Analysis Layer

The cloud layer is responsible for:

- historical trend analysis
- digital twin state updates
- aggregate workflow health scoring
- backlog severity tracking
- retry storm risk analysis
- optional anomaly model retraining

### Orchestration Engine

The orchestration engine routes work based on:

- processing time
- queue depth
- event complexity
- retry count
- publish failure risk
- backlog severity
- downstream acknowledgment delay

Example routing reasons include:

- `low-latency validation handled at edge`
- `complex transformation escalated to cloud`
- `high backlog triggered cloud offload`
- `retry storm risk requires centralized analysis`
- `publish failure pattern requires cloud-level investigation`

## Pipeline Digital Twin Health Model

The digital twin maintains a workflow-level state including:

- total events processed
- failed events
- pending events
- anomaly count
- validation issue trend
- retry storm risk
- backlog severity
- publish health
- average processing time
- overall pipeline health score
- overall status: `HEALTHY`, `DEGRADED`, or `CRITICAL`

## Project Structure

```text
edgecloud-digital-twin/
|-- api/
|-- cloud/
|-- database/
|-- docs/
|-- edge/
|-- orchestrator/
|-- simulator/
|-- tests/
|-- utils/
|-- dashboard.py
|-- Dockerfile
|-- main.py
|-- requirements.txt
|-- requirements-ml.txt
|-- run_simulation.py
`-- README.md
```

## Installation

Recommended Python version: `3.10` to `3.12`.

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

Optional model support:

```bash
pip install -r requirements-ml.txt
```

## Run the API

```bash
python main.py
```

API base URL:

```text
http://127.0.0.1:8000
```

## Run the Event Generator

Direct mode:

```bash
python run_simulation.py --scenario normal_processing --iterations 50
```

API mode:

```bash
python run_simulation.py --scenario retry_storm --iterations 30 --use-api
```

## API Usage

### `POST /pipeline-event`

Process an enterprise workflow event through the edge-cloud twin.

Example:

```bash
curl -X POST http://127.0.0.1:8000/pipeline-event \
  -H "Content-Type: application/json" \
  -d "{\"document_id\":\"DOC-001\",\"document_type\":\"INVOICE\",\"document_size_kb\":188.4,\"xml_complexity\":0.41,\"validation_error_count\":0,\"processing_time_ms\":135.0,\"queue_depth\":28,\"retry_count\":0,\"transform_latency_ms\":122.0,\"publish_status\":\"SUCCESS\",\"downstream_ack_delay_ms\":88.0,\"timestamp\":\"2026-04-22T12:00:00Z\",\"scenario\":\"normal_processing\"}"
```

### `GET /status`

Returns the current pipeline digital twin state.

### `GET /metrics`

Returns aggregate pipeline metrics.

### `GET /health`

Returns a compact workflow health view for readiness and operational checks.

## Dashboard Usage

Launch the dashboard:

```bash
streamlit run dashboard.py
```

The dashboard shows:

- total pipeline events
- pipeline health score
- healthy, degraded, and critical state visibility
- queue backlog trend
- retry count trend
- publish failure count and publish status distribution
- processing and acknowledgement trend
- routing distribution
- top anomaly reasons
- recent event log

## Running Tests

```bash
python -m pytest -q tests/test_system.py
```

## Test Results

The test suite covers:

- normal enterprise processing
- edge routing for low-latency validation
- cloud offload during high backlog
- malformed XML burst detection
- retry storm escalation
- publication failure effects on metrics and state
- API endpoint behavior

Recorded validation result for this refactor:

```text
7 passed in 1.47s
```

If a local environment is missing dependencies, install the packages from `requirements.txt` before running the suite.

## Docker

Build:

```bash
docker build -t edgecloud-digitaltwin .
```

Run:

```bash
docker run -p 8000:8000 edgecloud-digitaltwin
```

## Notes

- SQLite logs are stored by default at `edgecloud_digital_twin.db`
- Cloud retraining uses `IsolationForest` when `scikit-learn` is installed
- Orchestration thresholds can be tuned in [utils/config.py](utils/config.py)
