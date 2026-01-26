'''
	__author__ = "Georges Nassopoulos"
	__copyright__ = None
	__version__ = "1.0.0"
	__email__ = "georges.nassopoulos@gmail.com"
	__status__ = "Dev"
	__desc__ = "Splits raw dataset into train/test sets and stores outputs with logging and metadata"
'''

import pandas as pd
from sklearn.model_selection import train_test_split
import os
import joblib
import json
import sys

## "src" folder is added to PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "..", "..", "src"))
sys.path.insert(0, src_path)

from utils.logger import get_logger, log_step

## Initialize logger
logger = get_logger(name="split_data", log_file="logs/split_data.log")

@log_step(logger)
def split_and_save():
    """
	Split the raw dataset into training and testing sets.

	This function performs the following steps:
		- Loads the raw dataset from `data/raw/raw_data.csv`,
		- Splits the data into features (X) and target (y), where the target is 'silica_concentrate',
		- Further splits the dataset into training and testing sets (80/20 split),
		- Saves the resulting datasets (`X_train`, `X_test`, `y_train`, `y_test`)
		     in both `.csv` and `.pkl` formats under `data/processed/`, and
		- Logs basic information including dataset shapes and data integrity metadata
    """

    ## Load raw data
    df = pd.read_csv("data/raw/raw.csv")
    logger.info("Raw dataset loaded successfully.")

    ## Separate features (X) and target (y)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    logger.info("Features shape: %s | Target shape: %s", X.shape, y.shape)

    ## Split into training and test sets (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    ## Ensure output directory exists
    os.makedirs("data/processed", exist_ok=True)

    ## Save splits in .pkl format
    joblib.dump(X_train, "data/processed/X_train.pkl")
    joblib.dump(X_test, "data/processed/X_test.pkl")
    joblib.dump(y_train, "data/processed/y_train.pkl")
    joblib.dump(y_test, "data/processed/y_test.pkl")
    logger.info("Pickle files saved to data/processed/")

    ## Also save y_train and y_test as CSV for quick inspection in DagsHub
    y_train.to_csv("data/processed/y_train.csv", index=False)
    y_test.to_csv("data/processed/y_test.csv", index=False)
    logger.info("Target CSVs saved.")

    ## Save split metadata (shapes) in JSON format
    split_info = {
        "X_train_shape": X_train.shape,
        "X_test_shape": X_test.shape,
        "y_train_shape": y_train.shape,
        "y_test_shape": y_test.shape
    }

    with open("data/processed/split_info.json", "w") as f:
        json.dump(split_info, f, indent=4)
    logger.info("Metadata saved to split_info.json.")

if __name__ == "__main__":
    split_and_save()

