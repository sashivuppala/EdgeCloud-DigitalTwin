# EdgeCloud-DigitalTwin

`EdgeCloud-DigitalTwin` is a complete Python project that simulates an aerospace predictive-maintenance pipeline using an edge-cloud digital twin architecture. It generates live telemetry, performs low-latency anomaly screening at the edge, sends richer analysis to the cloud, and dynamically orchestrates where work runs based on system conditions.

## Features

- Synthetic aerospace telemetry with realistic drift, noise, spikes, and threshold breaches
- Edge anomaly detection with low-latency heuristics
- Cloud digital twin state with historical storage, deeper analysis, and retraining
- Dynamic orchestration between edge and cloud
- FastAPI endpoints for data ingestion and monitoring
- SQLite logging for sensor, anomaly, and orchestration records
- Metrics tracking for latency, anomaly rate, processing split, and simulated cost
- Optional Streamlit dashboard for live monitoring
- Docker support and basic unit tests

## Project Structure

```text
edgecloud-digital-twin/
├── api/
├── cloud/
├── database/
├── edge/
├── orchestrator/
├── simulator/
├── tests/
├── utils/
├── dashboard.py
├── main.py
├── run_simulation.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Installation

1. Create and activate a virtual environment.

Recommended Python version: `3.10` to `3.12`. The project code is written for Python `3.10+`, but scientific packages such as `scikit-learn` may lag on very new interpreters like Python `3.14`.

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Optional ML enhancement for cloud retraining:

```bash
pip install -r requirements-ml.txt
```

## Run the API Server

```bash
python main.py
```

The API starts on `http://127.0.0.1:8000`.

## Run the Simulation

The simulation can stream data directly through the system service or post it to the API.

Direct mode:

```bash
python run_simulation.py --scenario normal --iterations 50
```

API mode:

```bash
python run_simulation.py --scenario anomaly_injection --iterations 30 --use-api
```

## Dashboard

Launch the Streamlit dashboard:

```bash
streamlit run dashboard.py
```

The dashboard reads the same SQLite database and shows live telemetry, anomaly alerts, orchestration decisions, and latency trends.

## API Endpoints

### `POST /sensor-data`

Accepts a single telemetry sample plus optional system conditions.

Sample request:

```bash
curl -X POST http://127.0.0.1:8000/sensor-data \
  -H "Content-Type: application/json" \
  -d "{\"temperature\": 81.2, \"vibration\": 0.63, \"pressure\": 31.4, \"fuel_flow\": 102.6, \"timestamp\": \"2026-04-09T12:00:00Z\", \"latency_ms\": 22.0, \"cpu_load\": 0.42}"
```

### `GET /status`

Returns the current digital twin state.

```bash
curl http://127.0.0.1:8000/status
```

### `GET /metrics`

Returns aggregated system metrics.

```bash
curl http://127.0.0.1:8000/metrics
```

## Sample Scenarios

### Normal operation

```bash
python run_simulation.py --scenario normal --iterations 40
```

### High latency

```bash
python run_simulation.py --scenario high_latency --iterations 40
```

### Edge overload

```bash
python run_simulation.py --scenario edge_overload --iterations 40
```

### Forced anomaly injection

```bash
python run_simulation.py --scenario anomaly_injection --iterations 40
```

## Run Tests

```bash
pytest -q
```

## Docker

Build the image:

```bash
docker build -t edgecloud-digitaltwin .
```

Run the container:

```bash
docker run -p 8000:8000 edgecloud-digitaltwin
```

## Notes

- SQLite logs are stored by default at `edgecloud_digital_twin.db`.
- The cloud retraining routine uses `IsolationForest` when `scikit-learn` is installed and enough historical samples are available.
- The orchestration engine can be tuned in `utils/config.py`.
