"""
services/prediction_service.py
------------------------------
Prediction and validation service for scoring new or unlabelled MPLADS project data.
Applies strictly pre-learned preprocessing mappings and imputations from the trained model
bundle without recalculating on new datasets, ensuring ZERO data leakage and NO retraining.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import joblib
from typing import Tuple, Dict, Any

import config
from data_analysis import clean_data_types
from feature_engineering import run_feature_engineering
from anomaly_model import compute_scores_and_risk
from risk_explanation import generate_project_explanations


EXPECTED_MINIMAL_COLUMNS = [
    "Work ID", "Work Category", "State", "IDA", "Constituency",
    "Total_Disbursed", "Number_of_Payments", "Sanction_Amount",
    "Recommended_Amount", "Recommended_Date", "Sanction_Date", "Completion Date"
]

RECOMMENDED_COLUMNS = [
    "Work ID", "Work Category", "Work Description", "State", "IDA",
    "Hon'ble Members of Parliament", "Constituency", "Allocated_Amount",
    "Recommended_Date", "Completion Date", "Amount Disbursed ( ₹ )",
    "Total_Disbursed", "Number_of_Payments", "Recommended_Amount",
    "Sanction_Date", "Sanction_Amount", "Work_Status"
]


@st.cache_resource(show_spinner="Loading trained ML model bundle...")
def get_trained_model_bundle(model_path: Path = config.MODEL_PATH) -> dict:
    """
    Loads saved model, scaler, threshold metadata, and learned preprocessing mappings.
    Cached across user sessions for fast inference.
    """
    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained model artifact not found at: {model_path}. "
            "Please ensure outputs/trained_model.joblib is present."
        )
    return joblib.load(model_path)


def validate_uploaded_data(df: pd.DataFrame) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates uploaded raw DataFrame schema.
    Returns (is_valid, message, details).
    """
    if df is None or len(df) == 0:
        return False, "The uploaded file is empty.", {}

    # Standardize column casing/spacing for inspection
    raw_cols = [str(c).strip() for c in df.columns]
    
    # Must have an identifier
    id_col = None
    for cand in ["Work ID", "Work_ID", "WorkId", "work_id"]:
        if cand in raw_cols:
            id_col = cand
            break
            
    if not id_col:
        return False, (
            "Required column 'Work ID' is missing. The platform requires a unique "
            "project identifier to perform audit tracking."
        ), {"found_columns": raw_cols}

    # Check for presence of key operational columns
    found_cols = set(raw_cols)
    missing_key_cols = [c for c in EXPECTED_MINIMAL_COLUMNS if c not in found_cols]

    # Flexible matching for alternate column names
    col_mapping = {}
    if id_col != "Work ID":
        col_mapping[id_col] = "Work ID"
        
    for alt, standard in [
        ("Total Disbursed", "Total_Disbursed"),
        ("Amount Disbursed", "Amount Disbursed ( ₹ )"),
        ("Payments", "Number_of_Payments"),
        ("Sanction Amount", "Sanction_Amount"),
        ("Recommended Amount", "Recommended_Amount"),
        ("Work_Category", "Work Category"),
        ("Work Status", "Work_Status"),
    ]:
        if alt in found_cols and standard not in found_cols:
            col_mapping[alt] = standard

    details = {
        "total_records": len(df),
        "found_columns": list(found_cols),
        "missing_key_cols": missing_key_cols,
        "col_mapping": col_mapping
    }

    # If more than half of expected columns are missing, flag warning
    if len(missing_key_cols) > 6:
        missing_str = ", ".join(missing_key_cols[:5]) + ("..." if len(missing_key_cols) > 5 else "")
        return False, (
            f"Uploaded file lacks essential MPLADS operational columns ({missing_str}). "
            "Please check the required schema."
        ), details

    return True, "File schema validated successfully.", details


def score_new_dataset(
    df_raw: pd.DataFrame,
    col_mapping: dict = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes the full inference pipeline on a new dataset using the deployed model.
    Steps:
      1. Schema renaming if necessary
      2. Data type cleaning & portal artifact filtering
      3. Feature engineering with pre-learned preprocessing artifacts (NO RETRAINING)
      4. Scoring with Isolation Forest & calibrated percentiles
      5. Rule-based auditable explanation generation
    """
    df = df_raw.copy()
    if col_mapping:
        df = df.rename(columns=col_mapping)

    # Ensure all required columns exist (fill missing optional fields with NaN)
    for col in RECOMMENDED_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan

    # 1. Cleaning
    df_cleaned = clean_data_types(df)

    # 2. Load model bundle
    bundle = get_trained_model_bundle()
    model = bundle["model"]
    scaler = bundle["scaler"]
    metadata = bundle["metadata"]
    preprocessing_artifacts = bundle.get("preprocessing", {})

    # 3. Feature Engineering in Transform Mode (is_fit_mode=False)
    df_features, _ = run_feature_engineering(
        input_df=df_cleaned,
        preprocessing_artifacts=preprocessing_artifacts,
        save_output=False
    )

    # 4. Compute anomaly scores and risk tiers
    df_scored = compute_scores_and_risk(df_features, model, scaler, metadata)

    # 5. Attach audit explanations using learned empirical thresholds
    df_scored["risk_reasons"] = generate_project_explanations(
        df_scored,
        payment_p95=preprocessing_artifacts.get("payment_p95"),
        duration_p99=preprocessing_artifacts.get("duration_p99")
    )

    # 6. Summary metrics
    n_total = len(df_scored)
    n_high = int((df_scored["risk_level"] == config.LABEL_HIGH_RISK).sum())
    n_med = int((df_scored["risk_level"] == config.LABEL_MEDIUM_RISK).sum())
    n_low = int((df_scored["risk_level"] == config.LABEL_LOW_RISK).sum())
    n_anomalies = int((df_scored["anomaly_flag"] == 1).sum()) if "anomaly_flag" in df_scored.columns else 0

    summary = {
        "processed_count": n_total,
        "high_risk_count": n_high,
        "high_risk_pct": (n_high / n_total * 100) if n_total else 0.0,
        "medium_risk_count": n_med,
        "medium_risk_pct": (n_med / n_total * 100) if n_total else 0.0,
        "low_risk_count": n_low,
        "low_risk_pct": (n_low / n_total * 100) if n_total else 0.0,
        "anomalies_flagged": n_anomalies,
        "anomalies_pct": (n_anomalies / n_total * 100) if n_total else 0.0
    }

    return df_scored, summary
