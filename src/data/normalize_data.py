'''
        __author__ = "Georges Nassopoulos"
        __copyright__ = None
        __version__ = "1.0.0"
        __email__ = "georges.nassopoulos@gmail.com"
        __status__ = "Dev"
        __desc__ = "Normalizes numeric features using StandardScaler and logs all metadata and excluded columns."
'''

import os
import sys
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler

## "src" folder is added to PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "..", "..", "src"))
sys.path.insert(0, src_path)

from utils.logger import get_logger, log_step

## Initialize logger
logger = get_logger(name="normalize_data", log_file="logs/normalize_data.log")

@log_step(logger)
def normalize_and_save():
    """
	Normalize training and test feature sets using StandardScaler

	This function :
		- Loads raw feature training and test data,
		- Applies normalization only on numeric columns,
		- Saves scaled versions of X_train and X_test, and
		- Persists the scaler object and metadata (mean, std, column names)
    """

    ## Load input datasets
    X_train = joblib.load("data/processed/X_train.pkl")
    X_test = joblib.load("data/processed/X_test.pkl")
    logger.info("Loaded X_train with shape %s and X_test with shape %s", X_train.shape, X_test.shape)

    ## Identify numeric columns only
    all_cols = list(X_train.columns)
    numeric_cols = X_train.select_dtypes(include=["number"]).columns.tolist()
    non_numeric_cols = list(set(all_cols) - set(numeric_cols))

    if non_numeric_cols:
        logger.warning("Excluded non-numeric columns: %s", non_numeric_cols)
    logger.info("Kept numeric columns: %s", numeric_cols)

    ## Save column names used in normalization
    os.makedirs("models/data", exist_ok=True)
    with open("models/data/scaled_columns.json", "w") as f:
        json.dump(numeric_cols, f, indent=4)
    logger.info("Scaled column names saved to models/data/scaled_columns.json")

    ## Subset numeric columns for normalization
    X_train = X_train[numeric_cols]
    X_test = X_test[numeric_cols]

    ## Normalize using StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    logger.info("StandardScaler applied successfully.")

    ## Save scaled datasets
    joblib.dump(X_train_scaled, "data/processed/X_train_scaled.pkl")
    joblib.dump(X_test_scaled, "data/processed/X_test_scaled.pkl")
    logger.info("Scaled datasets saved to data/processed/")

    ## Save scaler object
    joblib.dump(scaler, "models/data/scaler.pkl")
    logger.info("Scaler object saved to models/data/scaler.pkl")

    ## Save scaler stats
    scaler_stats = {
        "mean_": scaler.mean_.tolist(),
        "scale_": scaler.scale_.tolist(),
        "var_": scaler.var_.tolist(),
        "features": numeric_cols
    }

    with open("models/data/scaler_stats.json", "w") as f:
        json.dump(scaler_stats, f, indent=4)
    logger.info("Scaler stats saved to models/data/scaler_stats.json")

    ## Save metadata about output shapes
    normalize_info = {
        "X_train_scaled_shape": X_train_scaled.shape,
        "X_test_scaled_shape": X_test_scaled.shape,
        "excluded_columns": non_numeric_cols
    }

    with open("data/processed/normalize_info.json", "w") as f:
        json.dump(normalize_info, f, indent=4)
    logger.info("Normalization metadata saved to data/processed/normalize_info.json")

    ## Log a few stats
    logger.info("Sample means (first 3 features): %s", np.mean(X_train_scaled, axis=0)[:3])
    logger.info("Sample stds  (first 3 features): %s", np.std(X_train_scaled, axis=0)[:3])

if __name__ == "__main__":
    normalize_and_save()
