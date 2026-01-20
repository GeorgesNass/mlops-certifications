
# 🚲 Bike Drift Monitoring

This project implements a full monitoring pipeline to detect **data drift**, **target drift**, and **performance degradation** for a regression model predicting bike rental counts. It uses `scikit-learn` for modeling and `Evidently` for monitoring, with a CLI orchestrator.

---

## 📁 Project Structure

```
.
├── .env                      		# Environment config (DATA_URL, MODEL_TYPE, etc.)
├── main_complete_pipeline.py       # complete code  menu to run each pipeline step
├── requirements.txt          		# Project dependencies            
│
├── logs/                     		# Logs per module
│
├── data/                  			# Raw and processed data
│
├── models/                  		# Trained models
│
├── reports/                  		# Generated monitoring reports
│
└─ deliverable/
   └─ exam_NASSOPOULOS.tar
```

---

## 📊  Exam Questions (Evaluation Summary Table)

| **Question** | **Values That Justify Conclusion** | **Conclusion** |
|-------------|-------------------------------------|----------------|
| **1. What changed during weeks 1, 2, and 3?** | - R² score dropped: week1 = 0.36 --> week2 = -0.33 --> week3 = -0.91 (`regression_report_week*.json`)  <br> - RMSE increased: 41.6 --> 72.7 --> 90.9 <br> - cnt drift score: 0.659 (week1), 0.651 (week2), 0.602 (week3) (`target_drift_report_week*.json`) <br> - Pearson correlation temp-cnt: 0.403 (ref) --> 0.360 --> 0.346 --> 0.085 (`target_drift_report_week*.json`) | Model performance deteriorated each week due to increasing prediction error and weakening correlation between features and the target. |
| **2. What seems to be the root cause of the drift (using only data)?** | - Drift scores for `temp`, `atemp`, `hum` all > 0.7 (`data_drift_report_week*.json`) <br> - `hum` drift = 1.125 (week3) <br> - Prediction drift scores: 0.78 (week1), 0.65 (week2), 0.49 (week3) <br> - Correlations between features and target (`cnt`) decrease sharply | Key input features experienced major distribution shifts, breaking model assumptions. Feature-target correlations weakened, and predictions drifted as a result. |
| **3. What strategy would you apply?** | - Constant performance decay across metrics <br> - 80–90% of columns drifted across weeks (`data_drift_report_week*.json`) <br> - Model trained only on January reference set | Set up regular retraining (weekly or biweekly) using recent data, and automate drift detection. Investigate feature normalization or adaptation to seasonal effects (maybe because it was jan/feb). |

---

## 📊 Dataset

- **Source**: [UCI Bike Sharing Dataset](https://archive.ics.uci.edu/ml/datasets/Bike+Sharing+Dataset)
- **Target column**: `cnt` (total bike rentals)
- Automatically downloaded via `DATA_URL` and loaded from `TARGET_CSV` defined in `.env`.

---
## Environment Setup

Create and activate a virtual environment:

### Linux / macOS
```bash
python3 -m venv .venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
python -m venv .venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---


## ⚙️ .env Configuration Example

```env
DATA_URL=https://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip
RAW_DATA_DIR=data/raw
PROCESSED_DATA_PATH=data/processed
RANDOM_STATE=42
USE_WORKSPACE=true
DATA_PATH=hour.csv
TARGET_COL=cnt
REPORT_DIR=reports
MODEL_DIR=models
MODEL_PATH=models/random_forest_model.joblib
WORKSPACE_DIR=evidently_workspace
ADVANCED_PREPROCESSING=True
```



---

## 🚀 Running the CLI

```bash
python main_complete_pipeline.py
```

---

## 📈 Monitoring Reports (Evidently)

| Preset               | Purpose                                   |
|----------------------|-------------------------------------------|
| `RegressionPreset`   | Evaluate model performance (MAE, R², etc.)|
| `TargetDriftPreset`  | Track changes in target variable `cnt`    |
| `DataDriftPreset`    | Detect drift in input features            |

- Reports are saved in `reports/`:
  - `regression_report.html`
  - `target_drift_report.html`
  - `data_drift_report.html`

---

## 🌐 Visualizing Reports (Evidently UI)

To launch a local web interface to browse reports:

```bash
evidently ui --workspace ./evidently_workspace/
```

Then open in your browser:

```
http://localhost:8000
```

You can drag and drop your `.html` reports into the interface.

---

## 📦 Artifacts

| File / Folder        | Content                          |
|----------------------|----------------------------------|
| `models/model.pkl`   | Trained model if saved           |
| `logs/*.log`         | Log files per module             |
| `reports/*.html`     | Monitoring reports               |

---

## 👨‍💻 Author

- **Georges Nassopoulos**
- 📧 georges.nassopoulos@gmail.com
- 🛠️ Status: Dev | MLOps Monitoring Project

---

## 📜 License

This project is for educational and evaluation purposes only. No license specified.
