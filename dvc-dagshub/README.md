
# Flotation Regression Project (DVC Pipeline)

This project implements a complete end-to-end machine learning pipeline using **DVC** and **scikit-learn** to model the silica concentration in a flotation process. The pipeline includes preprocessing, normalization, hyperparameter tuning, model training, and evaluation.

## 🔧 Project Structure

```
├── data/
│   ├── raw/                    # Raw dataset (CSV)
│   └── processed/              # Processed data (pkl/csv)
├── models/
│   └── data/                   # Trained models, parameters, scaler, plots
│   └── models/                 # Final model and evaluation outputs
├── src/
│   ├── data/                   # split_data.py, normalize_data.py
│   └── models/                 # train_model.py, evaluate_model.py, gridsearch_model.py
│   └── utils/                  # logger.py, helpers.py
├── dvc.yaml                    # DVC pipeline definition
├── params.yaml                # Hyperparameters (e.g. alpha)
├── dag.png                    # PNG of pipeline graph
├── metrics.json               # Model evaluation metrics
└── README.md                  # This file
```

## ⚙️ Pipeline Stages

The workflow is tracked by **DVC** and consists of the following stages:

1. **Data Split**: Load `raw.csv`, split into train/test, save as Pickle files.
2. **Normalization**: StandardScaler on numeric features, save scaled data.
3. **Grid Search**: GridSearchCV with Ridge model using `params.yaml` for alpha values.
4. **Model Training**: Train final Ridge model using best alpha.
5. **Model Evaluation**: Predict on test data, compute metrics and residuals.

## 🧪 Example Metrics Output

The following metrics are tracked in `metrics.json`:

```json
{
  "mse": 12.34,
  "rmse": 3.51,
  "mae": 2.78,
  "r2": 0.91
}
```

## 📊 Pipeline Visualization

This project includes a visual DAG (generated via `dvc dag --dot | dot -Tpng -o dag.png`):

![DVC DAG](dag.png)

## 📁 params.yaml (example)

```yaml
split_data:
  test_size: 0.2
  random_state: 42

gridsearch_model:
  alpha_values: [0.01, 0.1, 1.0, 10.0, 100.0]
```

## 📌 Reproducibility

Use the following to reproduce the pipeline:

```bash
dvc repro
```

To push tracked files to DagsHub remote storage:

```bash
dvc push
git push origin main
```

---

## ✍️ Author

**Georges Nassopoulos**  
📧 georges.nassopoulos@gmail.com  
📅 Version: 1.0.0  
📍 Status: Dev