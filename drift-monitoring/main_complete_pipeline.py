'''
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Dev"
__desc__ = "Complete pipeline for bike sharing drift monitoring using hourly data."
'''

import os
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import pickle
import logging
import requests
import zipfile
import time
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset, RegressionPreset
from evidently.test_suite import TestSuite
from evidently.tests import TestColumnDrift
from evidently import ColumnMapping
from evidently.tests import TestShareOfMissingValues
from evidently.ui.workspace import Workspace

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

## Load environment variables
load_dotenv()

## Set file paths and parameters from .env or fallback
DATA_URL = os.getenv("DATA_URL", "https://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip")
RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "data/raw")
PROCESSED_DATA_PATH = os.getenv("PROCESSED_DATA_PATH", "data/processed")
DATA_PATH = os.getenv("DATA_PATH", "hour.csv")
RANDOM_STATE = int(os.getenv("RANDOM_STATE", 42))
USE_WORKSPACE: bool = os.getenv("USE_WORKSPACE", "false").lower() == "true"
TARGET_COL = os.getenv("TARGET_COL", "cnt")
REPORT_DIR = os.getenv("REPORT_DIR", "reports")
MODEL_DIR = os.getenv("MODEL_DIR", "models")
MODEL_PATH = os.getenv("MODEL_PATH", "models/random_forest_model.joblib")
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "evidently_workspace")
ADVANCED_PREPROCESSING = os.getenv("ADVANCED_PREPROCESSING", "True") == "True"

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(WORKSPACE_DIR, exist_ok=True)

## ========== Logging Setup ==========
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(funcName)s]: %(message)s",
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)

logger = setup_logger()

## ========== Timer Decorator ==========
def log_execution_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"Function '{func.__name__}' executed in {end - start:.4f}s")
        return result
    return wrapper
   
## ============================================================
## Step 1 - Collect and extract raw data
## ============================================================
@log_execution_time
def download_and_extract_data(url: str, extract_to: str, expected_file: str) -> str:
    """
        Download and extract dataset from a remote ZIP archive

        Args:
            url (str): URL of the dataset ZIP file
            extract_to (str): Directory to extract files
            expected_file (str): Expected CSV filename inside the archive

        Returns:
            str: Full path to the extracted CSV file
    """
    
    try:
        zip_path = os.path.join(extract_to, "dataset.zip")

        ## Check if already extracted
        if not os.path.exists(os.path.join(extract_to, expected_file)):
            logger.info(f"Downloading dataset from {url} ...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            ## Save ZIP locally
            with open(zip_path, "wb") as f:
                f.write(response.content)
            logger.info("Download completed.")

            ## Extract ZIP contents
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)
            logger.info("Extraction completed.")

        ## Check extracted file exists
        extracted_file_path = os.path.join(extract_to, expected_file)
        if not os.path.exists(extracted_file_path):
            raise FileNotFoundError(f"{expected_file} not found after extraction.")

        return extracted_file_path

    except Exception as e:
        logger.exception(f"Failed during download or extraction: {e}")
        raise
   
## ============================================================
## Step 2 - Load and process data
## ============================================================
@log_execution_time
def load_and_preprocess_data(filepath: str, processed_file: str = "hour_processed.csv") -> pd.DataFrame:
    """
        Load and preprocess the bike sharing dataset

        Args:
            filepath (str): Path to the CSV file to load

        Returns:
            pd.DataFrame: Cleaned and preprocessed DataFrame
    """
    
    try:
        logger.info(f"Loading dataset from {filepath} ...")
        df = pd.read_csv(filepath)

        ## Drop irrelevant columns
        columns_to_drop = ["instant", "casual", "registered"]
        df.drop(columns=columns_to_drop, inplace=True)

        ## Convert original 'dteday' and 'hr' into precise datetime
        df["datetime"] = pd.to_datetime(df["dteday"]) + pd.to_timedelta(df["hr"], unit='h')
        df.set_index("datetime", inplace=True)

        ## Remove old date features
        df.drop(columns=["dteday", "yr", "mnth", "hr"], inplace=True)

        ## Optional: sort by datetime
        df.sort_index(inplace=True)

        ## Logging and save
        logger.info(f"Date range: {df.index.min()} to {df.index.max()}")
        logger.info(f"Data shape after preprocessing: {df.shape}")
        df.to_csv(PROCESSED_DATA_PATH + "/" + processed_file)
        logger.info(f"Preprocessed dataset saved to {PROCESSED_DATA_PATH}/{processed_file}")

        return df

    except Exception as e:
        logger.exception(f"Error during data preprocessing: {e}")
        raise

## ============================================================
## Step 3 Train and predict
## ============================================================
@log_execution_time
def train_and_predict(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
        Train a RandomForestRegressor model and generate predictions

        Parameters:
            df (pd.DataFrame): Preprocessed DataFrame with target and features

        Returns:
            Tuple of DataFrames: df_train_with_predictions, df_test, df_test_with_predictions
    """
    
    target_col = TARGET_COL
    if target_col not in df.columns:
        logger.error(f"Target column '{target_col}' not found.")
        raise ValueError(f"Target column '{target_col}' missing from data")

    ## Split into features and target
    X = df.drop(columns=[target_col])
    y = df[target_col]

    ## Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    ## Define model
    model = RandomForestRegressor(n_estimators=100, random_state=RANDOM_STATE)

    ## Cross-validation
    logger.info("Performing 5-fold cross-validation ...")
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring="r2")
    logger.info(f"Cross-validation R² mean: {scores.mean():.4f} ± {scores.std():.4f}")

    ## Train model
    model.fit(X_train, y_train)
    logger.info("Model training complete.")

    ## Save model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    logger.info(f"Model saved to {MODEL_PATH}")

    ## Generate predictions for test
    y_test_pred = model.predict(X_test)
    df_test = X_test.copy()
    df_test[target_col] = y_test
    df_test["prediction"] = y_test_pred

    ## Generate predictions for train
    y_train_pred = model.predict(X_train)
    df_train = X_train.copy()
    df_train[target_col] = y_train
    df_train["prediction"] = y_train_pred

    logger.info(f"Predictions added. Preview:\n{df_test[['prediction']].head(3)}")
    return df_train, df_test, df_test

## ============================================================
## Step 4 - Generate Evidently monitoring reports
## ============================================================
@log_execution_time
def generate_evidently_reports(reference_df: pd.DataFrame, current_df: pd.DataFrame, target_col: str) -> tuple[list, list, list]:
    """
        Generate monitoring reports using Evidently for Week 1, 2, 3 of February

        Args:
            reference_df (pd.DataFrame): Training set used as reference
            current_df (pd.DataFrame): Entire test set (includes all weeks)
            target_col (str): Name of the target column

        Returns:
            tuple: lists of regression, target_drift, and data_drift reports (one per week)
    """
    
    try:
    
        ## Define column mapping for Evidently to correctly interpret the dataset
        column_mapping = ColumnMapping()
        column_mapping.target = target_col
        column_mapping.prediction = "prediction"
        column_mapping.numerical_features = ["temp", "atemp", "hum", "windspeed", "mnth", "hr", "weekday"]
        column_mapping.categorical_features = ["season", "holiday", "workingday"]

        ## Define monitoring periods: 3 consecutive weeks in February
        week_periods = {
            "week1": ("2011-01-29", "2011-02-07"),
            "week2": ("2011-02-08", "2011-02-14"),
            "week3": ("2011-02-15", "2011-02-21")
        }

        ## Initialize lists to store all generated reports
        regression_reports = []
        target_drift_reports = []
        data_drift_reports = []

        ## Iterate over each week to generate separate reports
        for week_name, (start_str, end_str) in week_periods.items():
            start = pd.Timestamp(start_str + " 00:00:00")
            end = pd.Timestamp(end_str + " 23:00:00")

            logger.info(f"Generating reports for {week_name} ({start} to {end})")

            ## Filter current week’s data from the full dataset
            current_week_df = current_df.sort_index().loc[start:end]

            ## Count all rows before dropping missing values
            total_rows = len(current_week_df)
            logger.info(f"{week_name} - total rows before dropping NaNs: {total_rows}")

            ## Identify and display rows containing NaNs in target or prediction
            rows_with_nans = current_week_df[current_week_df[[target_col, "prediction"]].isna().any(axis=1)]
            if not rows_with_nans.empty:
                logger.info(f"{week_name} - rows with NaNs in 'target' or 'prediction': {len(rows_with_nans)}")
                print(f"\n[DEBUG] {week_name} - Preview of dropped rows due to NaNs:\n{rows_with_nans.head()}\n")
            else:
                logger.info(f"{week_name} - No NaNs detected in 'target' or 'prediction' columns.")

            ## Remove rows with missing values in target or prediction
            current_week_df = current_week_df.dropna(subset=[target_col, "prediction"])
            logger.info(f"{week_name} - rows after dropping NaNs: {len(current_week_df)}")

            ## Skip week if no valid data remains
            if current_week_df.empty:
                logger.warning(f"No valid data for {week_name} after dropping NaNs. Skipping...")
                continue

            # --- Regression Report ---
            ## Generate and save regression performance report
            reg_report = Report(metrics=[RegressionPreset()])
            reg_report.run(reference_data=reference_df, current_data=current_week_df, column_mapping=column_mapping)
            reg_html_path = os.path.join(REPORT_DIR, f"regression_report_{week_name}.html")
            reg_json_path = os.path.join(REPORT_DIR, f"regression_report_{week_name}.json")
            reg_report.save_html(reg_html_path)
            reg_report.save_json(reg_json_path)
            regression_reports.append(reg_report)
            logger.info(f"Saved regression report to {reg_html_path} and {reg_json_path}")

            # --- Target Drift Report ---
            ## Generate and save target drift analysis
            tgt_report = Report(metrics=[TargetDriftPreset()])
            tgt_report.run(reference_data=reference_df, current_data=current_week_df, column_mapping=column_mapping)
            tgt_html_path = os.path.join(REPORT_DIR, f"target_drift_report_{week_name}.html")
            tgt_json_path = os.path.join(REPORT_DIR, f"target_drift_report_{week_name}.json")
            tgt_report.save_html(tgt_html_path)
            tgt_report.save_json(tgt_json_path)
            target_drift_reports.append(tgt_report)
            logger.info(f"Saved target drift report to {tgt_html_path} and {tgt_json_path}")

            # --- Data Drift Report ---
            ## Generate and save data drift analysis
            drift_report = Report(metrics=[DataDriftPreset()])
            drift_report.run(reference_data=reference_df, current_data=current_week_df, column_mapping=column_mapping)
            drift_html_path = os.path.join(REPORT_DIR, f"data_drift_report_{week_name}.html")
            drift_json_path = os.path.join(REPORT_DIR, f"data_drift_report_{week_name}.json")
            drift_report.save_html(drift_html_path)
            drift_report.save_json(drift_json_path)
            data_drift_reports.append(drift_report)
            logger.info(f"Saved data drift report to {drift_html_path} and {drift_json_path}")

        ## Return all reports in lists grouped by type
        return regression_reports, target_drift_reports, data_drift_reports

    except Exception as e:
        ## Log and raise any unexpected error during the reporting process
        logger.error(f"[ERROR] Failed to generate reports: {e}")
        raise e

## ============================================================
## Step 4b - Generate Test Suite report
## ============================================================
@log_execution_time
def generate_test_suite(reference_df: pd.DataFrame, current_df: pd.DataFrame, target_col: str) -> TestSuite:
    """
        Generate a Test Suite report using Evidently to check missing values and target drift

        Args:
            reference_df (pd.DataFrame): Historical reference dataset
            current_df (pd.DataFrame): Current dataset to evaluate
            target_col (str): Target column to test for drift and missing values

        Returns:
            TestSuite: The generated test suite object for further analysis
    """
    
    try:
    
        ## Initialize test suite with missing values and column drift tests
        suite = TestSuite(tests=[
            TestShareOfMissingValues(missing_values=[target_col]),
            TestColumnDrift(column_name=target_col)
        ])

        ## Run the test suite on the reference and current datasets
        suite.run(reference_data=reference_df, current_data=current_df)

        ## Save the test suite report as an HTML file
        suite_path = os.path.join(REPORT_DIR, "test_suite_report.html")
        suite.save_html(suite_path)
        logger.info(f"Test suite report successfully saved to {suite_path}")

        return suite  ## Return suite for further use (e.g., drift analysis)

    except Exception as e:
        logger.exception(f"Failed to generate test suite report: {e}")
        return None

## ============================================================
## Step 5b - Add Reports to Evidently Workspace UI (BONUS)
## ============================================================
@log_execution_time
def add_reports_to_workspace_ui(
    workspace_dir: Path,
    regression_report: Report,
    test_suite_report: TestSuite,
    target_drift_report: Report,
    data_drift_report: Report,
    project_name: str = "final_hour_model_monitoring"
) -> None:
    """
        Add all generated Evidently reports to the Workspace UI

        Args:
            workspace_dir (Path): Path to the Evidently workspace directory
            regression_report (Report): Regression performance report
            test_suite_report (TestSuite): Test suite report
            target_drift_report (Report): Target drift report
            data_drift_report (Report): Data drift report
            project_name (str): Name of the monitoring project
    """
    
    try:
        if not USE_WORKSPACE:
            logger.info("Workspace export is disabled. Skipping.")
            return

        logger.info("Initializing Evidently Workspace at: %s", workspace_dir)
        workspace = Workspace(workspace_dir)

        project = workspace.create_project(project_name)
        project.description = "Weekly monitoring reports for bike sharing model."

        all_reports = [
            regression_report,
            test_suite_report,
            target_drift_report,
            data_drift_report
        ]

        ## Save each report, directly as an item or for each item (per week) of a list
        for item in all_reports:
            if isinstance(item, list):
                # logger.warning(f"Expected Report/TestSuite, got list: {item}")
                for sub_item in item:
                    workspace.add_report(project.id, sub_item)
                    logger.info(f"Added report to workspace: {type(sub_item).__name__}")
            else:
                workspace.add_report(project.id, item)
                logger.info(f"Added report to workspace: {type(item).__name__}")

        logger.info("All reports successfully added to Evidently Workspace.")

    except Exception as e:
        logger.exception(f"Error while adding reports to workspace: {e}")

## ============================================================
## Step 6 - Analyze Drift Results and Suggest Strategy
## ============================================================
@log_execution_time
def analyze_drift_and_suggest_strategy(test_suite: TestSuite, target_column: str) -> None:
    """
        Analyze drift test results and suggest actions based on model behavior

        Args:
            test_suite (TestSuite): The suite of Evidently test results
            target_column (str): Name of the column to analyze drift for
    """
    
    try:
        logger.info("Step 6 - Analyzing test suite results...")

        ## Extract test results
        test_results = test_suite.as_dict()
        tests = test_results.get("tests", [])

        drift_found = False
        missing_values_found = False

        for test in tests:
            if test["name"] == f"TestColumnDrift[{target_column}]":
                if test["status"] == "FAIL":
                    drift_found = True
                    logger.warning("Significant drift detected on target column.")
            if test["name"] == f"TestShareOfMissingValues[{target_column}]":
                if test["status"] == "FAIL":
                    missing_values_found = True
                    logger.warning("Missing values detected in target column.")

        ## Suggestion logic
        if drift_found and not missing_values_found:
            logger.info("Strategy: Re-train the model with new weekly data to adapt to the new distribution.")
        elif drift_found and missing_values_found:
            logger.info("Strategy: Investigate data pipeline issues. Fix missing values before re-training.")
        elif not drift_found and missing_values_found:
            logger.info("Strategy: Perform data cleaning. Model is still valid but needs complete inputs.")
        else:
            logger.info("Strategy: No drift detected. Model can be used without re-training.")

    except Exception as e:
        logger.exception("Error during drift analysis: %s", e)

## ============================================================
## Main Execution Block
## ============================================================
if __name__ == "__main__":
    """
        Main entry point for executing the full pipeline from data loading
        to monitoring report generation and drift strategy suggestion
    """
    
    try:
    
        ## Step 1 - Collect and extract raw data
        extracted_csv_path = download_and_extract_data(DATA_URL, RAW_DATA_DIR, "hour.csv")

        ## Step 2 - Load and preprocess data
        df_processed = load_and_preprocess_data(extracted_csv_path)

        ## Step 3 - Train model and predict
        df_train, df_test, df_test_with_preds = train_and_predict(df_processed)

        ## Step 4 - Generate Evidently reports
        reg_report, tgt_drift, data_drift = generate_evidently_reports(
            reference_df=df_train,
            current_df=df_test_with_preds,
            target_col=TARGET_COL
        )

        ## Step 4b (BONUS) - Generate Evidently test suite
        test_suite = generate_test_suite(
            reference_df=df_train,
            current_df=df_test_with_preds,
            target_col=TARGET_COL
        )

        ## ============================================================
        ## Step 5 - Already Covered in Reports Generated in Step 4
        ## ============================================================
        logger.info("Step 5 - Drift already computed via dashboard & test suite.")
        logger.info("Please refer to the dashboard report or README for detailed drift analysis.")

        ## Step 5b (BONUS) - Add all reports to Evidently Workspace UI
        add_reports_to_workspace_ui(
            workspace_dir=WORKSPACE_DIR,
            regression_report=reg_report,
            test_suite_report=test_suite,
            target_drift_report=tgt_drift,
            data_drift_report=data_drift
        )

        ## Step 6 - Analyze drift results and suggest strategy
        analyze_drift_and_suggest_strategy(
            test_suite=test_suite,
            target_column=TARGET_COL
        )

        logger.info("Pipeline completed successfully.")

    except Exception as main_e:
        logger.exception("Pipeline failed: %s", main_e)