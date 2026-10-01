"""
config.py
---------
Central configuration module for the MPLADS Anomaly and Fraud-Risk Detection System.
Stores all file paths, column names, model hyperparameters, and risk thresholds
in one place to ensure consistency across the entire pipeline.
"""

from pathlib import Path

# -----------------------------------------------------------------------------
# Directory and File Paths
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR
OUTPUT_DIR = BASE_DIR / "outputs"

# Input Raw Data
RAW_DATA_PATH = DATA_DIR / "master.xlsx"
DATA_SHEET_NAME = "Sheet1"

# Output Pipeline Artifacts
CLEANED_DATA_PATH = OUTPUT_DIR / "cleaned_data.csv"
FEATURE_ENGINEERED_PATH = OUTPUT_DIR / "feature_engineered_data.csv"
MASTER_WITH_RISK_PATH = OUTPUT_DIR / "master_with_risk.csv"
ANOMALY_SUMMARY_PATH = OUTPUT_DIR / "anomaly_summary.csv"
MODEL_PATH = OUTPUT_DIR / "trained_model.joblib"

# -----------------------------------------------------------------------------
# Column Definitions
# -----------------------------------------------------------------------------
# Identifier column (strictly excluded from ML features)
IDENTIFIER_COL = "Work ID"

# Text / Description columns (not used directly in numeric anomaly detection)
TEXT_COLS = [
    "Work Description",
    "Hon'ble Members of Parliament"
]

# Date columns present in the raw dataset
DATE_COLS = [
    "Recommended_Date",
    "Sanction_Date",
    "Completion Date"
]

# Financial & Numerical columns present in the raw dataset
FINANCIAL_COLS = [
    "Allocated_Amount",
    "Amount Disbursed ( ₹ )",
    "Total_Disbursed",
    "Number_of_Payments",
    "Recommended_Amount",
    "Sanction_Amount"
]

# Categorical columns to encode
CATEGORICAL_COLS = [
    "Work Category",
    "State",
    "IDA",
    "Constituency"
]

# Work status column
STATUS_COL = "Work_Status"

# -----------------------------------------------------------------------------
# Isolation Forest Model Hyperparameters
# -----------------------------------------------------------------------------
ISOLATION_FOREST_PARAMS = {
    "n_estimators": 150,
    "max_samples": "auto",
    "contamination": 0.05,     # Expected proportion of significant outliers (5%)
    "random_state": 42,        # Ensures full reproducibility
    "n_jobs": -1
}

# -----------------------------------------------------------------------------
# Risk Level Thresholds
# -----------------------------------------------------------------------------
# Stratification based on anomaly score percentiles:
# - High Risk: Top 5% anomaly score (percentile >= 95.0)
# - Medium Risk: 85th to 95th percentile (85.0 <= percentile < 95.0)
# - Low Risk: Remaining 85% of projects (percentile < 85.0)
RISK_PERCENTILE_HIGH = 95.0
RISK_PERCENTILE_MEDIUM = 85.0

# Text labels for risk levels
LABEL_HIGH_RISK = "High"
LABEL_MEDIUM_RISK = "Medium"
LABEL_LOW_RISK = "Low"
