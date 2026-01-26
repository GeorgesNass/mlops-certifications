'''
        __author__ = "Georges Nassopoulos"
        __copyright__ = None
        __version__ = "1.0.0"
        __email__ = "georges.nassopoulos@gmail.com"
        __status__ = "Dev"
        __desc__ = "Evaluate the trained Ridge regression model on test data and log performance metrics."
'''

import os
import sys
import json
import hashlib
import joblib
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

## "src" folder is added to PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "..", "..", "src"))
sys.path.insert(0, src_path)

from utils.logger import get_logger, log_step

## Initialize logger
logger = get_logger(name="evaluate_model", log_file="logs/evaluate_model.log")

@log_step(logger)
def evaluate_model():
    """
        Evaluate the trained Ridge regression model on the test set

        This function:
                - Loads the trained Ridge model and the preprocessed test data (features and targets),
                - Performs predictions on the test set,
                - Computes evaluation metrics (Mean Squared Error and R² score),
                - Saves a JSON report with metrics, model identity and test shapes, and
                - Logs all steps and results for full traceability
    """

    ## Load model
    model_path = "models/models/final_model.pkl"
    if not os.path.exists(model_path):
        logger.error("Model not found at %s. Please run train_model.py first.", model_path)
        return
    model = joblib.load(model_path)
    logger.info("Model loaded from %s", model_path)

    ## Load test data
    X_test_path = "data/processed/X_test_scaled.pkl"
    y_test_path = "data/processed/y_test.pkl"
    if not os.path.exists(X_test_path) or not os.path.exists(y_test_path):
        logger.error("Missing test data. Please run normalize_data.py and split_data.py.")
        return

    X_test = joblib.load(X_test_path)
    y_test = joblib.load(y_test_path)
    logger.info("Loaded test data: X_test %s | y_test %s", X_test.shape, y_test.shape)

    ## Predict
    y_pred = model.predict(X_test)
    logger.info("Prediction on test set completed.")

    ## Compute metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    logger.info("Test MSE: %.4f | RMSE: %.4f | MAE: %.4f | R²: %.4f", mse, rmse, mae, r2)

    ## Save predictions
    predictions_df = pd.DataFrame({"y_true": y_test, "y_pred": y_pred})
    pred_path = "models/models/test_predictions.csv"
    predictions_df.to_csv(pred_path, index=False)
    logger.info("Test predictions saved to %s", pred_path)

    ## OPTIONAL : Save residual plot
    residuals = y_test - y_pred
    plt.figure(figsize=(8, 4))
    plt.hist(residuals, bins=30)
    plt.title("Residuals Distribution")
    plt.xlabel("Residual")
    plt.ylabel("Frequency")
    hist_path = "models/models/residuals_hist.png"
    plt.tight_layout()
    plt.savefig(hist_path)
    plt.close()
    logger.info("Residuals histogram saved to %s", hist_path)

    ## Compute model hash
    with open(model_path, "rb") as f:
        model_hash = hashlib.md5(f.read()).hexdigest()

    ## Save evaluation metadata
    metadata = {
        "model_type": "Ridge",
        "model_path": model_path,
        "model_md5": model_hash,
        "evaluated_at": datetime.datetime.now().isoformat(),
        "test_samples": len(y_test),
        "test_metrics": {
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        }
    }

    metadata_path = "models/models/eval_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)
    logger.info("Evaluation metadata saved to %s", metadata_path)

    ## Save metrics to metrics.json for DVC tracking
    metrics = {
        "mse": mean_squared_error(y_test, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
        "mae": mean_absolute_error(y_test, y_pred),
        "r2": r2_score(y_test, y_pred)
    }

    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)

    logger.info("Evaluation completed successfully.")

if __name__ == "__main__":
    evaluate_model()
