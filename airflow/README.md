# Weather Data Pipeline

## 📦 Description

This project builds a weather data pipeline using Apache Airflow to:
- Fetch real-time weather data from the OpenWeatherMap API
- Save each data retrieval as a timestamped JSON file
- Convert JSON files into CSV format
- Validate data integrity
- Train and evaluate ML models (Linear Regression, Decision Tree, Random Forest)
- Save and log the best performing model
- Generate a temperature plot
- Clean up old files

## 🗂️ Project Structure

```text
.
├─ docker-compose.yaml        # Docker Compose file to run Airflow locally
├─ README.md
├─ exam_NASSOPOULOS.zip       # Original exam deliverable (required format)
│
├─ dags/
│  └─ weather_pipeline_dag.py # Main Airflow DAG
│
├─ raw_files/                 # Raw input data
├─ clean_data/                # Processed / cleaned data
│
├─ configs/                   # Configuration files (.env.example, Airflow notes)
├─ scripts/                   # Utility or helper scripts
└─ artifacts/                 # Generated artifacts (models, plots, reports)

```

## 🐍 Creating a Virtual Environment

### 🛠️ Clean installation guide (Ubuntu)

#### Step 1 – Install build tools

Make sure required system packages are installed to avoid compilation errors during `pip install`:

```bash
sudo apt update
sudo apt install -y build-essential python3-dev python3-pip python3.8-venv python3-wheel
```

#### Step 2 – Create a clean virtual environment

```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
```

#### Step 3 – Minimal and stable `requirements.txt`

Create or edit your `requirements.txt` as follows (only what’s used in the DAG):

```txt
apache-airflow==2.7.3 --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.7.3/constraints-3.8.txt
scikit-learn
matplotlib
pandas
joblib
```

#### Step 4 – Clean installation

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

###  🛠️ Clean installation guide (Windows)

To isolate dependencies:

```bash
python3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

To deactivate:
```bash
deactivate
```

---

## Configuration (.env)

This project uses a `.env` file (at the repository root, next to `docker-compose.yaml`) to inject runtime configuration into Docker Compose and Airflow.

- **AIRFLOW_UID / AIRFLOW_GID**: prevent file permission issues on mounted volumes.
- **WEATHER_API_KEY**: required by the DAG to call the OpenWeatherMap API.
- **CITIES**: list of cities fetched by the pipeline.
- **AIRFLOW_IMAGE_NAME**: allows using a custom Airflow image built once.
- **_PIP_ADDITIONAL_REQUIREMENTS**: must stay empty to avoid pip spam in logs.

Create a file named `.env` with the following content:

```env
AIRFLOW_UID=1000
AIRFLOW_GID=0
WEATHER_API_KEY=__PUT_YOUR_OPENWEATHERMAP_KEY_HERE__
CITIES=["paris","london","washington"]
AIRFLOW_IMAGE_NAME=airflow-custom:2.8.1
_PIP_ADDITIONAL_REQUIREMENTS=
```

⚠️ Do NOT commit your real API key. Add `.env` to `.gitignore`.

---

## Custom Airflow image (recommended)

Avoid runtime pip installs that cause long startups and log spam.

### Dockerfile.airflow
Place this file at project root:

```Dockerfile
FROM apache/airflow:2.8.1
USER root
RUN pip install --no-cache-dir scikit-learn
USER airflow
```

---

## Disable runtime pip installs

In `.env`:

```env
_PIP_ADDITIONAL_REQUIREMENTS=
```

---

## Reduce log noise (optional)

In `docker-compose.yaml` → `environment:`

```yaml
PYTHONWARNINGS: "ignore::DeprecationWarning,ignore::FutureWarning"
AIRFLOW__LOGGING__LOGGING_LEVEL: "WARNING"
```

---

## 🔧 Configure `fs_default` Connection for Airflow FileSensor

To allow your `FileSensor` to detect files in the `/app/raw_files` directory (mounted in your Docker container), you must add a new connection in Airflow.


### Option 1 — Docker Compose (recommended)

Define the connection directly in `docker-compose.yaml`:

```yaml
environment:
  AIRFLOW_CONN_FS_DEFAULT: "fs://?extra__fs__path=%2Fapp%2Fraw_files"
```

No action is required in the Airflow UI.

---

### Option 2 — Airflow UI (manual)

If not defined in Docker Compose:

1. Open http://localhost:8080
2. Go to **Admin → Connections**
3. Click **+**

| Field     | Value           |
|----------|-----------------|
| Conn Id  | fs_default      |
| Conn Type| File (path)     |
| Host     | /app/raw_files  |
| Extra   | *(empty)*       |

Save.

---

## 🚀 Run the Pipeline (WITHOUT AIRFLOW)

You can test the entire workflow locally without launching Airflow:

```bash
python dags/weather_tasks/weather_pipeline_dag_enriched.py
```

The script will:
1. Ensure required folders exist or prompt for custom paths.
2. Fetch weather data for multiple cities.
3. Convert recent and all JSONs into CSV files.
4. Validate both `data.csv` and `fulldata.csv`.
5. Train three models (LR, DT, RF), select and save the best.
6. Optionally generate a temperature plot.
7. Optionally clean up old files.

## 📁 Folder Structure and Handling

- In Docker/Airflow: default base directory is `/app`.
- Locally: base directory is where the script resides.
- If `raw_files/` or `clean_data/` are missing:
    - You will be prompted to specify a path.
    - Folders will be created automatically.

## 🐘 Using Airflow with Docker

1. Shut down and remove any old containers:
```bash
docker-compose down
rm docker-compose.yaml
```

2. Download the provided Docker Compose config:
```bash
wget https://dst-de.s3.eu-west-3.amazonaws.com/airflow_fr/eval/docker-compose.yaml
```

3. Create required folders:
```bash
mkdir dags logs plugins clean_data raw_files
sudo chmod -R 777 dags logs plugins
WEATHER_API_KEY=<YOUR_WEATHER_API_HERE>
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0\nWEATHER_API_KEY=${WEATHER_API_KEY}\nCITIES=[\"paris\", \"london\", \"washington\"]" > .env
```

4. Initialize and start services:
```bash
docker-compose up airflow-init
docker-compose up -d
```

5. Download initial data for manual triggering:
```bash
wget https://dst-de.s3.eu-west-3.amazonaws.com/airflow_avance_fr/eval/data.csv -O clean_data/data.csv
echo '[]' >> raw_files/null_file.json
```

## ✅ DAG Tasks Overview

| Task Name                | Description                                           |
|--------------------------|-------------------------------------------------------|
| fetch_weather_data       | Downloads weather data and saves as timestamped JSON |
| transform_recent_json    | Converts recent JSONs to `data.csv`                  |
| transform_all_json       | Converts all JSONs to `fulldata.csv`                 |
| validate_csv_file        | Validates temperature values and NaNs                |
| training_models          | Trains LR, DT, RF and logs scores                    |
| select_and_save_best_model | Saves best model and logs performance             |
| plot_temperature         | Generates plot for temperature evolution             |
| cleanup_old_files        | Deletes old `.csv` and `.json` files                 |

## ✨ Notes

- Make sure your API key is valid (use `.env` or export `API_KEY` manually).
- Ensure your call rate respects OpenWeatherMap limits to avoid throttling.
- Recommended to let the DAG run for 15+ minutes for enough observations.
- Plot and cleanup are optional when running manually.