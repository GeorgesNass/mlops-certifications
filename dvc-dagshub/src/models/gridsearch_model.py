'''
        __author__ = "Georges Nassopoulos"
        __copyright__ = None
        __version__ = "1.0.0"
        __email__ = "georges.nassopoulos@gmail.com"
        __status__ = "Dev"
        __desc__ = "Performs GridSearchCV on Ridge model with logging, result saving and plotting."
'''

import os
import sys
import json
import yaml
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV

## "src" folder is added to PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "..", "..", "src"))
sys.path.insert(0, src_path)

from utils.logger import get_logger, log_step

## Initialize logger
logger = get_logger(name="gridsearch_model", log_file="logs/gridsearch_model.log")

@log_step(logger)
def run_grid_search():
    """
    Perform hyperparameter tuning using GridSearchCV with Ridge regression

    This script does the following :
        - Loads preprocessed and normalized training features (`X_train_scaled`) and target (`y_train`),
        - Sets up a grid of hyperparameters for Ridge regression (e.g., alpha values),
        - Performs a grid search using 5-fold cross-validation to find the best hyperparameters,
        - Logs the best parameters and training performance, and
        - Saves:
                - The best hyperparameters to `models/data/best_params.pkl`
                - Full GridSearchCV results to `models/data/gridsearch_results.csv`
                - Summary statistics (best score, best params, etc.) to `models/data/gridsearch_summary.json`
                - A plot of mean cross-validation scores to `models/data/gridsearch_plot.png`

    """

    ## Load training data
    X_train = joblib.load("data/processed/X_train_scaled.pkl")
    y_train = joblib.load("data/processed/y_train.pkl")
    logger.info("Loaded X_train_scaled with shape %s and y_train with shape %s", X_train.shape, y_train.shape)

    ## Define model and parameter grid
    model = Ridge()
    with open("params.yaml") as f:
        params = yaml.safe_load(f)

    alpha_values = params["gridsearch"]["alpha_values"]
    param_grid = {"alpha": alpha_values}
    logger.info("Starting GridSearchCV with Ridge and params: %s", param_grid)

    ## GridSearchCV
    grid = GridSearchCV(
        model,
        param_grid,
        scoring="neg_mean_squared_error",
        cv=5,
        verbose=0,
        n_jobs=-1,
        return_train_score=True
    )

    grid.fit(X_train, y_train)
    logger.info("GridSearchCV completed.")

    ## Ensure model output folder
    os.makedirs("models/data", exist_ok=True)

    ## Save best parameters
    joblib.dump(grid.best_params_, "models/data/best_params.pkl")
    logger.info("Best parameters saved to models/data/best_params.pkl: %s", grid.best_params_)

    ## Save full grid results to CSV
    results_df = pd.DataFrame(grid.cv_results_)
    results_df.to_csv("models/data/gridsearch_results.csv", index=False)
    logger.info("Full GridSearch results saved to gridsearch_results.csv")

    ## Save JSON summary
    summary = {
        "best_params": grid.best_params_,
        "best_score_neg_mse": grid.best_score_,
        "scoring": grid.scoring,
        "n_splits": grid.cv
    }

    with open("models/data/gridsearch_summary.json", "w") as f:
        json.dump(summary, f, indent=4)
    logger.info("GridSearch summary saved to gridsearch_summary.json")

    ## OPTIONAL : Plot MSE vs alpha
    if "param_alpha" in results_df.columns:
        alphas = results_df["param_alpha"].astype(float)
        errors = -results_df["mean_test_score"]

        plt.figure(figsize=(8, 4))
        plt.plot(alphas, errors, marker="o")
        plt.xlabel("Alpha")
        plt.ylabel("Mean Squared Error")
        plt.title("GridSearchCV - Ridge Regression")
        plt.grid(True)
        plt.tight_layout()
        plot_path = "models/data/gridsearch_plot.png"
        plt.savefig(plot_path)
        logger.info("GridSearch plot saved to %s", plot_path)

if __name__ == "__main__":
    run_grid_search()
