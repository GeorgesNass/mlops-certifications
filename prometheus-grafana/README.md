# 📄 Monitoring a Machine Learning Model  
FastAPI · Prometheus · Grafana

## Project Overview

This project demonstrates how to expose a machine learning model through a **FastAPI API**
and monitor it using **Prometheus** and **Grafana**.

The API serves a trained **RandomForest** model and exposes:
- HTTP metrics (requests, latency, status codes)
- Inference metrics (count and duration)

Grafana is used to visualize these metrics through a custom dashboard.


## Project Structure

```
project-root/
├── main.py                      ## Application entrypoint (ASGI)
├── docker-compose.yml           ## Service orchestration
├── Dockerfile               	 ## dockerfile to deploie service
├── requirements.txt             ## python requirements
├── prometheus.yml               ## Prometheus scrape configuration
├── load_test.sh                 ## Load testing script
├── grafana/
│   └── dashboards/
│       └── grafana_dashboard_fastapi_prometheus.json
├── models/
│   └── trained_model.joblib     ## Trained ML model
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py               ## FastAPI application factory
│   │   └── routes.py            ## API routes (/predict, /)
│   ├── core/
│   │   ├── __init__.py
│   │   └── model.py             ## Model loading and feature building
│   ├── monitoring/
│   │   ├── __init__.py
│   │   └── metrics.py           ## Prometheus metrics
│   └── schemas/
│       ├── __init__.py
│       └── accident.py          ## Pydantic request schema
└── README.md
```

## Requirements

- Docker
- Docker Compose
- (Optional) Python 3.9+


## Windows & WSL2 Prerequisites

### PowerShell (Windows)

```powershell
## Check WSL installation and default version
wsl --status

## Install WSL if not already installed (admin PowerShell)
wsl --install

## List available Linux distributions
wsl --list --online

## Install Ubuntu distribution
wsl --install -d Ubuntu

## Start Ubuntu (WSL)
wsl -d Ubuntu

## Check Docker installation
docker --version
docker compose version
```

---

### Ubuntu (WSL)

```bash
## Update package list
sudo apt update

## Install Git
sudo apt install -y git

## Verify Git installation
git --version
```

---

### Python setup (Ubuntu / WSL)

```bash
## Check Python installation
python3 --version

## Install pip and venv if missing
sudo apt install -y python3-pip python3-venv
```


### Prerequest : Data science / ML commandes

```bash
## Clone the repository (from prometheus-grafana directory)
git clone https://github.com/DataScientest-Studio/Template_MLOps_accidents.git

## Move into the project directory
cd Template_MLOps_accidents

## Checkout the correct branch
git checkout notebook_8_prometheus_mlops

## Create a Python virtual environment (correct way)
python3 -m venv .my_env

## Activate the virtual environment (you should see (.my_env) in the prompt)
source .my_env/bin/activate

## Install Python dependencies
pip install -r requirements.txt

## Import raw data (INTERACTIVE SCRIPT)
## When prompted:
## - If asked to create the raw directory -> type: y
python3 ./src/data/import_raw_data.py

## Run preprocessing (INTERACTIVE SCRIPT)
## When prompted:
## - Enter the file path for the input data  -> type: data/raw
## - Enter the file path for the output data -> type: data/preprocessed
## - If asked to create the directory        -> type: y
python3 ./src/data/make_dataset.py

## Train the Random Forest model (NON INTERACTIVE)
python3 ./src/models/train_model.py

## Verify that the trained model exists
## Expected file: trained_model.joblib
ls -lh models/

```

## Run the Project — Linux

```bash
## Move to the project root directory
cd /path/to/project-root

## Get the models in this root directory
cp -r Template_MLOps_accidents/models/ .

## Build and start all services (FastAPI, Prometheus, Grafana)
docker compose up --build

## (Optional) Run services in detached mode
docker compose up -d --build

## (Optional) Make the load test script executable
chmod +x load_test.sh

## (Optional) Run the load test script for a more interactive view
./load_test.sh
```

## Run the Project — Windows PowerShell (via Linux)

```powershell
## Start a Linux shell using WSL
wsl
```

```bash
## Move to the project root directory inside Linux
cd /path/to/project-root

## Build and start all services (FastAPI, Prometheus, Grafana)
docker compose up --build

## (Optional) Run services in detached mode
docker compose up -d --build

## (Optional) Make the load test script executable
chmod +x load_test.sh

## (Optional) Run the load test script for a more interactive execution
./load_test.sh
```

## Access the Services

- FastAPI (Swagger UI):  
  http://localhost:8000/docs

- Prometheus:  
  http://localhost:9090

- Grafana:  
  http://localhost:3000  
  Default credentials: `admin / admin`


## New Features

### API Instrumentation

- Prometheus metrics added to the FastAPI application:
  - `http_requests_total` → HTTP request count by endpoint and status.
  - `inference_time_seconds` → inference duration metrics.
- `/metrics` endpoint is exposed automatically.
- Metrics are available at runtime without Docker Compose changes.

### Grafana Dashboard


Location:
```
grafana/dashboards/grafana_dashboard_fastapi_prometheus.json
```

- Custom Grafana dashboard provided as a JSON file.
- Visualizes prediction count, inference latency, and HTTP traffic.
- Can be imported manually into Grafana using the Prometheus data source.

### Panels Overview  

| Panel Name                | Description                              | Mandatory? | Formula (PromQL)                                                                 | Type     | Unit        |
|----------------------------|------------------------------------------|------------|-----------------------------------------------------------------------------------|----------|-------------|
| **Total Predictions**      | Count of predictions (success + errors) | ✅ Yes     | `api_predict_total`                                                               | Stat     | count       |
| **Avg Inference Time**     | Average latency over 5–30 min windows   | ✅ Yes     | `rate(inference_time_seconds_sum[30m]) / rate(inference_time_seconds_count[30m])`   | TimeSeries | ms          |
| **Requests/sec by Status** | Breakdown of requests by HTTP code      | ❌ Bonus   | `sum by (status) (rate(http_requests_total[1m]))`                                 | Pie/Bar  | rps         |
| **p95 Latency (5m)**       | 95th percentile latency                 | ❌ Bonus   | `histogram_quantile(0.95, rate(inference_time_seconds_bucket[5m]))`               | TimeSeries | ms          |
| **Error Rate (%)**         | Percentage of failed requests           | ❌ Bonus   | `(sum(rate(http_requests_total{status=~"4..|5.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100` | Stat | %           |

## Author

Georges Nassopoulos  
Email: georges.nassopoulos@gmail.com  
Status: Educational / Exam project
---
