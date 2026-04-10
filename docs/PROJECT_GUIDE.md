# EdgeCloud-DigitalTwin Project Guide

## 1. Purpose of This Document

This guide is the combined `About` and `Help` document for the `EdgeCloud-DigitalTwin` project.

It is written for:

- Product Owners who want to understand what was built and why it matters
- Developers who need to install, run, extend, test, and maintain the codebase
- Stakeholders who want a clear summary of the architecture, modules, data flow, and outputs

This document explains:

- what the product does
- how the system works end to end
- how the code is organized
- how to install and run the project
- how to test it
- how to extend it safely

---

## 2. Product Overview

`EdgeCloud-DigitalTwin` simulates a predictive maintenance platform for aerospace systems using an edge-cloud digital twin architecture.

The project models a realistic operational flow:

1. Sensor telemetry is generated to imitate live aerospace equipment data.
2. An edge processor performs low-latency anomaly detection.
3. An orchestration engine decides whether processing should stay at the edge or be handled in the cloud.
4. A cloud digital twin stores history, updates system state, and performs deeper analysis.
5. The API exposes the current health status and system metrics.
6. SQLite logs telemetry, anomaly events, and orchestration decisions for traceability.

In simple terms, this product demonstrates how an intelligent maintenance system can:

- react quickly to urgent conditions at the edge
- use the cloud for broader analysis and long-term learning
- balance performance, latency, and compute cost
- provide visibility into system behavior

---

## 3. Business-Focused Summary

### What problem this solves

Modern aerospace and industrial systems generate large amounts of sensor data. Some issues require immediate local action, while others need deeper historical analysis. Sending everything to the cloud can introduce latency and cost. Processing everything at the edge can limit analytical depth.

This project demonstrates a hybrid model where:

- time-sensitive checks happen at the edge
- deeper analysis and state management happen in the cloud
- a routing engine dynamically chooses the best processing location

### Why it is useful

This design is useful for predictive maintenance because it helps:

- detect faults earlier
- reduce unplanned downtime
- improve operational safety
- optimize compute cost
- support scalable monitoring architectures

### What was built

We built a complete working simulation that includes:

- synthetic sensor telemetry generation
- anomaly injection
- edge anomaly screening
- cloud digital twin state management
- orchestration logic
- API endpoints
- database logging
- metrics collection
- optional visualization
- test cases
- Docker packaging

---

## 4. System Architecture

## High-Level Components

The project is divided into five major layers:

1. Simulator
2. Edge Processing
3. Cloud Digital Twin
4. Orchestration
5. API and Monitoring

### End-to-End Flow

```text
Simulator -> Orchestrator -> Edge Processor -> Cloud Digital Twin -> SQLite/API/Dashboard
```

### Logical Behavior

- The simulator creates live telemetry records.
- The orchestrator evaluates latency, CPU load, and analysis complexity.
- The edge processor performs lightweight anomaly checks.
- The cloud updates the digital twin and optionally retrains a model.
- The database stores all important events.
- The API exposes status and metrics to external systems.

---

## 5. Project Structure

```text
EdgeCloud-DigitalTwin/
├── api/
│   ├── __init__.py
│   └── app.py
├── cloud/
│   ├── __init__.py
│   └── digital_twin.py
├── database/
│   ├── __init__.py
│   ├── db.py
│   └── repository.py
├── docs/
│   └── PROJECT_GUIDE.md
├── edge/
│   ├── __init__.py
│   └── processor.py
├── orchestrator/
│   ├── __init__.py
│   └── engine.py
├── simulator/
│   ├── __init__.py
│   └── generator.py
├── tests/
│   ├── __init__.py
│   └── test_system.py
├── utils/
│   ├── __init__.py
│   ├── config.py
│   ├── metrics.py
│   ├── models.py
│   └── system.py
├── .gitignore
├── dashboard.py
├── Dockerfile
├── main.py
├── README.md
├── requirements.txt
├── requirements-ml.txt
└── run_simulation.py
```

---

## 6. Module-by-Module Explanation

## `simulator/generator.py`

This module is responsible for generating synthetic aerospace telemetry.

It creates:

- temperature
- vibration
- pressure
- fuel_flow
- timestamp
- simulated latency
- simulated CPU load

It also injects abnormal conditions such as:

- sudden spikes
- gradual degradation
- pressure drops
- fuel flow drops
- threshold breaches
- random noise

### Why this matters

This makes the project realistic enough to test predictive maintenance and orchestration logic without depending on a real aircraft or a physical sensor network.

## `edge/processor.py`

This module represents the edge node.

It performs fast anomaly checks using:

- threshold detection
- spike detection
- short-term trend comparison

It produces:

- anomaly flag
- anomaly score
- anomaly type list
- local processing latency

### Why this matters

Edge processing is useful when:

- the response must be fast
- network latency is high
- simple rules are enough to identify risk quickly

## `cloud/digital_twin.py`

This module simulates the cloud system and maintains the digital twin state.

Responsibilities include:

- storing recent historical data in memory
- performing deeper analysis
- updating the system health score
- maintaining moving averages
- tracking anomaly counts
- optionally retraining an anomaly model using `IsolationForest`

### Why this matters

The cloud provides richer context and long-term state management. This is where the system builds a broader operational view instead of reacting only to the latest event.

## `orchestrator/engine.py`

This module decides where the workload should be processed.

Rules implemented:

- if latency is above threshold, keep processing at the edge
- if edge CPU load is too high, offload to the cloud
- if complex analysis is required, process in the cloud
- otherwise, use the cloud for normal synchronization and full-state updates

### Why this matters

This is the core intelligence that demonstrates edge-cloud workload balancing.

## `database/db.py`

Creates the SQLite connection and database schema.

Tables:

- `sensor_data`
- `anomaly_logs`
- `orchestration_logs`

## `database/repository.py`

This is the persistence layer.

Responsibilities include:

- writing processed telemetry to SQLite
- logging anomaly events
- logging orchestration decisions
- reading recent history for dashboard and analysis use

## `utils/config.py`

Contains centralized system configuration values such as:

- latency threshold
- overload threshold
- sensor thresholds
- retraining window
- simulated compute cost values

## `utils/models.py`

Defines Pydantic models and shared data structures used across the system.

Key models:

- `SensorRecord`
- `ProcessedRecord`
- `OrchestrationDecision`
- `DigitalTwinState`
- `MetricsSnapshot`

## `utils/metrics.py`

Tracks and calculates:

- total events
- average latency
- anomaly count
- anomaly detection rate
- edge processing percentage
- cloud processing percentage
- simulated cost

## `utils/system.py`

This is the composition root of the project.

It wires together:

- database
- edge processor
- cloud digital twin
- orchestration engine
- metrics tracker

This is the main module used by the API and simulation runner.

## `api/app.py`

This module exposes the system through FastAPI.

Endpoints:

- `POST /sensor-data`
- `GET /status`
- `GET /metrics`
- `GET /`

## `run_simulation.py`

This is the main simulation runner for scenario execution.

It supports:

- normal operation
- high latency
- edge overload
- anomaly injection

It can run in:

- direct ingestion mode
- API mode

## `dashboard.py`

This is the optional Streamlit dashboard.

It displays:

- twin status
- health score
- anomaly counts
- average latency
- live sensor charts
- routing distribution
- recent anomalies

## `tests/test_system.py`

Contains basic validation for:

- normal operation
- high-latency routing
- edge overload routing
- anomaly injection detection
- API endpoint behavior

---

## 7. Code Logic Explained in Plain English

### Step 1: Data is generated

The simulator creates sensor readings every second or at a configurable interval. The values are not constant. They vary naturally and sometimes include faults.

### Step 2: The orchestrator decides where to process

The system checks runtime conditions such as latency and CPU usage. Based on those values, it chooses edge or cloud routing.

### Step 3: The edge processor reacts quickly

The edge module performs simple checks to determine whether the incoming telemetry appears abnormal.

### Step 4: The cloud updates the twin

The cloud module stores the latest readings in history, computes health-related metrics, and updates the current digital twin state.

### Step 5: Logs and metrics are stored

The system records the event to SQLite and updates global metrics such as average latency and anomaly rates.

### Step 6: External consumers can query the API

Other services or users can query the API to get the latest twin state and performance metrics.

---

## 8. APIs and Their Purpose

## `POST /sensor-data`

### Purpose

Accept a telemetry sample and run it through the full edge-cloud system.

### Input

JSON payload with fields such as:

- `temperature`
- `vibration`
- `pressure`
- `fuel_flow`
- `timestamp`
- `latency_ms`
- `cpu_load`
- `scenario`

### Output

Returns:

- whether the data was processed successfully
- whether an anomaly was detected
- which processing location was used
- why the routing decision was made
- current digital twin status

## `GET /status`

### Purpose

Return the latest digital twin state.

### Output includes

- status
- health score
- anomaly count
- total samples
- moving averages
- latest anomaly types

## `GET /metrics`

### Purpose

Return operational metrics.

### Output includes

- total events
- average latency
- anomaly detection rate
- edge vs cloud counts
- edge vs cloud percentages
- simulated cost

---

## 9. Developer Installation Guide

## Required Software

Before working on this project, install the following:

### Mandatory

- Python `3.10`, `3.11`, or `3.12`
- `pip`
- Git

### Recommended

- Visual Studio Code or PyCharm
- Postman or curl for API testing
- Docker Desktop if container execution is required

### Optional

- Streamlit for dashboard viewing
- scikit-learn for optional cloud-side model retraining

## Why Python 3.10 to 3.12 is recommended

The code is written for Python `3.10+`, but some scientific dependencies can lag behind the newest Python version. For the smoothest experience, use Python `3.10` to `3.12`.

---

## 10. Environment Setup

## Step 1: Clone the repository

```bash
git clone https://github.com/sashivuppala/EdgeCloud-DigitalTwin.git
cd EdgeCloud-DigitalTwin
```

## Step 2: Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

## Step 3: Install base dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Install optional ML dependencies

Only needed if the developer wants `IsolationForest` retraining support:

```bash
pip install -r requirements-ml.txt
```

## Step 5: Verify installation

```bash
python -m compileall .
```

Optional:

```bash
pytest -q
```

---

## 11. Packages Used

## Core packages

- `fastapi`
- `uvicorn`
- `numpy`
- `pandas`
- `requests`
- `pytest`
- `streamlit`

## Optional machine learning package

- `scikit-learn`

## Standard library modules used

- `sqlite3`
- `argparse`
- `dataclasses`
- `datetime`
- `json`
- `pathlib`
- `time`
- `collections`

---

## 12. How to Run the Project

## Run the API

```bash
python main.py
```

The API will start on:

```text
http://127.0.0.1:8000
```

## Run a simulation directly

```bash
python run_simulation.py --scenario normal --iterations 50
```

## Run a high-latency scenario

```bash
python run_simulation.py --scenario high_latency --iterations 50
```

## Run an edge overload scenario

```bash
python run_simulation.py --scenario edge_overload --iterations 50
```

## Run anomaly injection

```bash
python run_simulation.py --scenario anomaly_injection --iterations 50
```

## Run the simulation through the API

Make sure the API is already running, then:

```bash
python run_simulation.py --scenario anomaly_injection --iterations 30 --use-api
```

## Run the dashboard

```bash
streamlit run dashboard.py
```

---

## 13. Example API Calls

## Post sensor data

```bash
curl -X POST http://127.0.0.1:8000/sensor-data \
  -H "Content-Type: application/json" \
  -d "{\"temperature\": 81.2, \"vibration\": 0.63, \"pressure\": 31.4, \"fuel_flow\": 102.6, \"timestamp\": \"2026-04-09T12:00:00Z\", \"latency_ms\": 22.0, \"cpu_load\": 0.42, \"scenario\": \"normal\"}"
```

## Get digital twin status

```bash
curl http://127.0.0.1:8000/status
```

## Get metrics

```bash
curl http://127.0.0.1:8000/metrics
```

---

## 14. Database Details

The project uses SQLite for persistent logging.

Default database file:

```text
edgecloud_digital_twin.db
```

### Table descriptions

## `sensor_data`

Stores:

- sensor values
- timestamp
- latency
- CPU load
- scenario
- processing location

## `anomaly_logs`

Stores:

- anomaly flag
- anomaly score
- anomaly types
- processing location
- timestamp

## `orchestration_logs`

Stores:

- routing location
- decision reason
- latency
- CPU load
- complexity requirement flag
- timestamp

---

## 15. Sample Scenarios and Expected Outcomes

## Normal operation

Expected behavior:

- most data is healthy
- limited anomalies
- cloud processing dominates unless latency becomes elevated

## High latency

Expected behavior:

- more workload remains at the edge
- routing reason should indicate latency sensitivity

## Edge overload

Expected behavior:

- workload shifts to cloud
- routing reason should indicate edge overload

## Anomaly injection

Expected behavior:

- anomaly counts increase
- digital twin status may degrade from healthy to warning or critical

---

## 16. Testing Guide

## Unit tests included

The project includes tests for:

- normal processing
- edge routing under high latency
- cloud offload under edge overload
- anomaly detection under injection scenario
- FastAPI endpoint correctness

## Run tests

```bash
pytest -q
```

## Good validation sequence for a developer

1. Install dependencies
2. Run `python -m compileall .`
3. Run `pytest -q`
4. Start the API with `python main.py`
5. Run one direct simulation
6. Run one API-driven simulation
7. Open the dashboard if required

---

## 17. Docker Guide

## Build the image

```bash
docker build -t edgecloud-digitaltwin .
```

## Run the container

```bash
docker run -p 8000:8000 edgecloud-digitaltwin
```

### When Docker is useful

Docker is useful when:

- the team wants consistent runtime behavior
- a developer wants isolated dependencies
- the app needs to be demonstrated quickly without manual local setup

---

## 18. Troubleshooting Guide

## Problem: `pytest` not found

Solution:

```bash
python -m pytest -q
```

## Problem: `ModuleNotFoundError`

Solution:

- confirm the virtual environment is activated
- reinstall dependencies using `pip install -r requirements.txt`

## Problem: scikit-learn install issues on new Python versions

Solution:

- use Python `3.10` to `3.12`
- or skip optional ML installation and run the heuristic cloud analysis path

## Problem: dashboard shows no data

Solution:

- run the simulation first
- confirm the SQLite database file is being created

## Problem: API works but metrics are empty

Solution:

- send data through `POST /sensor-data`
- or run `run_simulation.py --use-api`

---

## 19. How a Developer Should Extend This Project

If a developer joins this project, the recommended order of understanding is:

1. Read `README.md`
2. Read this guide
3. Start with `utils/system.py`
4. Review `utils/models.py`
5. Review `simulator/generator.py`
6. Review `edge/processor.py`
7. Review `cloud/digital_twin.py`
8. Review `orchestrator/engine.py`
9. Review `api/app.py`
10. Run the sample scenarios

### Safe extension examples

- add new sensor fields
- add richer orchestration policies
- replace rule-based edge logic with a tiny ML model
- upgrade the cloud twin to use a stronger model
- replace SQLite with PostgreSQL
- add authentication to the API
- add alerting and notifications

### Important implementation notes

- keep the simulator, edge, cloud, and API layers separate
- avoid placing database logic directly inside API endpoints
- keep shared data contracts in `utils/models.py`
- add tests for each behavioral change

---

## 20. Product Owner and Stakeholder Talking Points

If a Product Owner needs to explain this project to others, the following summary works well:

`EdgeCloud-DigitalTwin` is a predictive maintenance simulation platform that demonstrates how real-time aerospace telemetry can be processed using both edge and cloud resources. The system intelligently decides where to process workloads based on latency, resource pressure, and complexity. It detects anomalies, maintains a digital twin of the monitored system, tracks performance and cost metrics, and exposes everything through APIs and dashboards.

### Key outcomes delivered

- real-time telemetry simulation
- edge-cloud workload orchestration
- anomaly detection pipeline
- digital twin state tracking
- operational metrics and logging
- API-based observability
- testable, modular Python codebase

### Value to the business

- demonstrates predictive maintenance architecture
- provides a foundation for future productionization
- helps communicate system design to engineering and non-engineering teams
- supports demos, prototypes, and further research

---

## 21. Limitations and Future Improvements

Current limitations:

- sensor values are simulated rather than connected to live devices
- security and authentication are not yet implemented
- the ML retraining path is intentionally simple
- SQLite is suitable for demo and local use, not large-scale production

Recommended next steps:

- add authentication and role-based access
- add message queue or streaming middleware
- support multiple aircraft or asset IDs
- persist digital twin snapshots explicitly
- add alert rules and notifications
- expand the dashboard
- integrate with cloud services or container orchestration

---

## 22. Final Summary

This project is a complete, modular, end-to-end demonstration of an edge-cloud digital twin system for predictive maintenance.

It includes:

- a realistic simulator
- an edge analytics path
- a cloud digital twin
- orchestration logic
- APIs
- metrics
- logs
- tests
- deployment support
- developer onboarding guidance

For technical onboarding, this guide should be treated as the first reference after the README.

For business and product communication, this guide can also serve as the main explanation of what was built, why it matters, and how it can evolve.
