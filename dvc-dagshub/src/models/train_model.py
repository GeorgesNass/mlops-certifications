'''
        __author__ = "Georges Nassopoulos"
        __copyright__ = None
        __version__ = "1.0.0"
        __email__ = "georges.nassopoulos@gmail.com"
        __status__ = "Dev"
        __desc__ = "Train Ridge regression model using best parameters, compute train metrics, and log metadata including model hash and random seed."
'''

import os
import sys
import joblib
import json
import hashlib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score

## "src" folder is added to PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "..", "..", "src"))
sys.path.insert(0, src_path)

from utils.logger import get_logger, log_step

## Initialize logger
logger = get_logger(name="train_model", log_file="logs/train_model.log")

@log_step(logger)
def train_final_model():
    """
	Train a Ridge regression model using the best hyperparameters obtained via GridSearchCV.

	This function :
			- loads the preprocessed training data (scaled features and targets),
			- initializes a Ridge regression model with the best parameters, and
			- fits it to the data
    """

    ## Set seed for reproducibility
    random_seed = 42
    np.random.seed(random_seed)

    ## Load preprocessed training data
    X_train = joblib.load("data/processed/X_train_scaled.pkl")
    y_train = joblib.load("data/processed/y_train.pkl")
    logger.info("Loaded X_train_scaled with shape %s and y_train with shape %s", X_train.shape, y_train.shape)

    ## Load best hyperparameters determined by grid search
    best_params_path = "models/data/best_params.pkl"
    if not os.path.exists(best_params_path):
        logger.error("Missing best_params.pkl from GridSearch. Please run gridsearch_model.py first.")
        return

    best_params = joblib.load(best_params_path)
    logger.info("Loaded best parameters: %s", best_params)

    ## Initialize and train the Ridge regression model
    model = Ridge(**best_params)
    model.fit(X_train, y_train)
    logger.info("Model trained successfully.")

    ## Evaluate performance on training data
    y_pred_train = model.predict(X_train)
    mse = mean_squared_error(y_train, y_pred_train)
    r2 = r2_score(y_train, y_pred_train)
    logger.info("Train MSE: %.4f | Train R²: %.4f", mse, r2)

    ## Prepare directory to store model
    model_dir = "models/models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "final_model.pkl")

    ## Warn if the file will be overwritten
    if os.path.exists(model_path):
        logger.warning("Overwriting existing model at %s", model_path)

    ## Save the trained model to disk
    joblib.dump(model, model_path)
    logger.info("Final model saved to %s", model_path)

    ## Compute the hash (checksum) of the model file for traceability
    with open(model_path, "rb") as f:
        model_hash = hashlib.md5(f.read()).hexdigest()

    ## Load feature names from normalization step
    scaled_cols_path = "models/data/scaled_columns.json"
    if os.path.exists(scaled_cols_path):
        with open(scaled_cols_path, "r") as f:
            feature_names = json.load(f)
    else:
        logger.warning("scaled_columns.json not found. Feature names will not be saved.")
        feature_names = []

    ## Save metadata related to training and model identity
    metadata = {
        "model_type": "Ridge",
        "best_params": best_params,
        "random_seed": random_seed,
        "training_samples": len(X_train),
		"features": feature_names,
        "model_md5": model_hash,
        "train_metrics": {
            "mse": mse,
            "r2": r2
        }
    }

    ## Save metadata as JSON
    metadata_path = os.path.join(model_dir, "train_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)
    logger.info("Training metadata saved to %s", metadata_path)

    ## Final summary in logs
    logger.info("Model training complete.")
    logger.info("Parameters: %s", best_params)
    logger.info("Train MSE: %.4f | Train R²: %.4f", mse, r2)
    logger.info("Model hash (md5): %s", model_hash)

if __name__ == "__main__":
    train_final_model()
