# EdgeCloud-DigitalTwin

`EdgeCloud-DigitalTwin` is a digital twin and orchestration system for enterprise processing pipelines. It simulates distributed document and workflow processing, routes work between edge and cloud layers, maintains a live pipeline health model, and exposes metrics, logs, and dashboards for operational monitoring.

For a complete combined product overview, developer onboarding guide, setup manual, architecture explanation, and stakeholder-friendly summary, see [docs/PROJECT_GUIDE.md](C:\Users\kiran\Details of Your Vehicle\EdgeCloud-DigitalTwin\docs\PROJECT_GUIDE.md).

## Project Purpose

This project demonstrates how an enterprise document and event-processing platform can be modeled as an edge-cloud digital twin:

- the input simulator generates workflow events such as XML-heavy documents and publish operations
- the edge validation layer performs low-latency validation and quick anomaly screening
- the cloud analysis layer handles deeper trend analysis and digital twin state management
- the orchestration engine decides where work should be processed based on backlog, latency, retry pressure, and complexity
- the API, database, and dashboard provide visibility into pipeline health

This architecture is conceptually inspired by large-scale document and workflow processing platforms where validation, transformation, publishing, acknowledgement, and retry behavior must be monitored continuously.

## Domain Refactoring Note

The architecture of the project remains the same as the earlier edge-cloud digital twin implementation, but the domain has been refocused from generic telemetry processing to enterprise workflow and document processing. The simulator, digital twin, orchestration logic, dashboard, and documentation now model distributed pipeline operations instead of device-style telemetry.

## Features

- Enterprise pipeline event simulation for document ingestion and workflow execution
- Scenarios for queue backlog, malformed XML bursts, retry storms, transformation bottlenecks, and publish failures
- Edge validation for lightweight parsing checks and quick anomaly detection
- Cloud analysis for historical trend analysis, digital twin state updates, and optional retraining
- Orchestration logic that routes work between edge and cloud based on queue depth, latency, retry pressure, and complexity
- FastAPI endpoints for event ingestion, status, and metrics
- SQLite logging for events, anomalies, and orchestration decisions
- Streamlit dashboard for pipeline health and routing visibility
- Docker support and automated tests

## Architecture

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

## Enterprise Event Model

Each simulated pipeline event includes:

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

The simulator supports these enterprise pipeline scenarios:

- `normal_processing`
- `high_queue_backlog`
- `malformed_xml_burst`
- `transformation_bottleneck`
- `publication_failure_spike`
- `retry_storm`
- `downstream_ack_delay`
- `mixed_enterprise_load`

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

Example routing reasons include:

- `low-latency validation handled at edge`
- `complex transformation escalated to cloud`
- `high backlog triggered cloud offload`
- `retry storm risk requires centralized analysis`

## Pipeline Digital Twin Health Model

The digital twin maintains a live workflow-level state including:

- total events processed
- failed events
- anomaly count
- validation issue trend
- retry storm risk
- backlog severity
- publish health
- health score
- overall status: `HEALTHY`, `DEGRADED`, or `CRITICAL`

## Project Structure

```text
edgecloud-digital-twin/
├── api/
├── cloud/
├── database/
├── docs/
├── edge/
├── orchestrator/
├── simulator/
├── tests/
├── utils/
├── dashboard.py
├── Dockerfile
├── main.py
├── requirements.txt
├── requirements-ml.txt
├── run_simulation.py
└── README.md
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

## Run the Simulator

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

## Dashboard Usage

Launch the dashboard:

```bash
streamlit run dashboard.py
```

The dashboard shows:

- total pipeline events
- pipeline health score
- queue backlog trend
- retry count trend
- publish status distribution
- processing and acknowledgement trend
- routing distribution
- top anomaly reasons

## Running Tests

```bash
python -m pytest -q tests/test_system.py
```

## Test Results

The refactored test suite covers:

- normal enterprise processing
- edge routing for low-latency validation
- cloud offload during high backlog
- malformed XML burst detection
- retry storm escalation
- publication failure effects on metrics and state
- API endpoint behavior

Expected validation output:

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
- Orchestration thresholds can be tuned in [utils/config.py](C:\Users\kiran\Details of Your Vehicle\EdgeCloud-DigitalTwin\utils\config.py)
