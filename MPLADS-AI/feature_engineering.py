"""
feature_engineering.py
----------------------
Constructs operational features for MPLADS anomaly and fraud-risk detection.
Engineers:
  - Timeline duration features with training-set median imputation
  - Financial discrepancy ratios and differences
  - Project lifecycle presence indicators (including Has_Payment_Data)
  - Frequency-encoded categorical features using learned mappings

Preserves all 34,450 genuine project rows and keeps Allocated_Amount for reporting.
Supports two modes:
  1. Fit mode (training): Computes statistics and returns (df, preprocessing_artifacts).
  2. Transform mode (inference): Applies pre-computed artifacts to new data without leakage.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Ensure UTF-8 output encoding for Windows terminal compatibility
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import config


def compute_lifecycle_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates binary indicators (0/1) for whether a project has reached
    a specific lifecycle stage or has recorded payment information.
    """
    df["Has_Recommendation"] = df["Recommended_Date"].notna().astype(int)
    df["Has_Sanction"] = df["Sanction_Date"].notna().astype(int)
    df["Has_Completion"] = df["Completion Date"].notna().astype(int)
    
    # Has_Disbursement: check Total_Disbursed or Amount Disbursed ( ₹ )
    disbursed_val = df["Total_Disbursed"].fillna(df["Amount Disbursed ( ₹ )"]).fillna(0)
    df["Has_Disbursement"] = (disbursed_val > 0).astype(int)
    
    # Has_Payment_Data: indicator so missing payments are not interpreted as zero payments
    df["Has_Payment_Data"] = df["Number_of_Payments"].notna().astype(int)
    
    return df


def compute_duration_features(
    df: pd.DataFrame,
    median_rec_to_sanc: float = None,
    median_sanc_to_comp: float = None
) -> tuple[pd.DataFrame, float, float]:
    """
    Calculates operational timelines in days between milestones:
      - Recommendation_to_Sanction_Days: Duration from MP recommendation to administrative sanction
      - Sanction_to_Completion_Days: Duration from sanction to project completion
    
    Missing Handling:
      Uses training-set median imputation instead of 0 for missing durations,
      while preserving Has_* stage indicator flags so the model distinguishes
      unreached stages from actual short durations.
    """
    rec_to_sanc = (df["Sanction_Date"] - df["Recommended_Date"]).dt.days
    sanc_to_comp = (df["Completion Date"] - df["Sanction_Date"]).dt.days
    
    # Calculate medians if not provided (fit mode)
    if median_rec_to_sanc is None:
        valid_rec = rec_to_sanc.dropna()
        median_rec_to_sanc = float(valid_rec.median()) if len(valid_rec) > 0 else 0.0
        
    if median_sanc_to_comp is None:
        valid_sanc = sanc_to_comp.dropna()
        median_sanc_to_comp = float(valid_sanc.median()) if len(valid_sanc) > 0 else 0.0
        
    # Impute missing with training-set median
    df["Recommendation_to_Sanction_Days"] = rec_to_sanc.fillna(median_rec_to_sanc).astype(float)
    df["Sanction_to_Completion_Days"] = sanc_to_comp.fillna(median_sanc_to_comp).astype(float)
    
    # Flag invalid reverse-chronological dates (e.g., completed before sanction)
    df["Flag_Negative_Sanction_Completion"] = np.where(sanc_to_comp.notna(), (sanc_to_comp < 0).astype(int), 0)
    df["Flag_Negative_Rec_Sanction"] = np.where(rec_to_sanc.notna(), (rec_to_sanc < 0).astype(int), 0)
    
    return df, median_rec_to_sanc, median_sanc_to_comp


def compute_financial_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates financial consistency features:
      - Disbursement_vs_Sanction_Ratio: Total_Disbursed / Sanction_Amount
      - Disbursement_Sanction_Difference: Total_Disbursed - Sanction_Amount
      - Recommended_vs_Sanction_Difference: Recommended_Amount - Sanction_Amount
      - Recommended_vs_Sanction_Ratio: Recommended_Amount / Sanction_Amount
    
    Missing Handling:
      If Sanction or Recommended amounts are missing (stage information unavailable),
      differences are imputed as 0.0 and ratios default to 1.0 (neutral baseline),
      ensuring unreached stages are NEVER automatically labeled as anomalous.
    """
    total_disbursed = df["Total_Disbursed"].fillna(df["Amount Disbursed ( ₹ )"]).fillna(0.0)
    sanction_amt = df["Sanction_Amount"]
    recommended_amt = df["Recommended_Amount"]
    
    # 1. Disbursement vs Sanction Difference
    df["Disbursement_Sanction_Difference"] = np.where(
        sanction_amt.notna(),
        total_disbursed - sanction_amt,
        0.0
    )
    
    # 2. Disbursement vs Sanction Ratio
    df["Disbursement_vs_Sanction_Ratio"] = np.where(
        (sanction_amt.notna()) & (sanction_amt > 0),
        np.clip(total_disbursed / sanction_amt, 0.0, 100.0),
        1.0  # Neutral baseline when sanction information is unavailable
    )
    
    # 3. Recommended vs Sanction Difference
    df["Recommended_vs_Sanction_Difference"] = np.where(
        (recommended_amt.notna()) & (sanction_amt.notna()),
        recommended_amt - sanction_amt,
        0.0
    )
    
    # 4. Recommended vs Sanction Ratio
    df["Recommended_vs_Sanction_Ratio"] = np.where(
        (recommended_amt.notna()) & (sanction_amt.notna()) & (sanction_amt > 0),
        np.clip(recommended_amt / sanction_amt, 0.0, 100.0),
        1.0  # Neutral baseline
    )
    
    # 5. Over-disbursement Flag: Disbursed strictly exceeds sanction by > ₹1000
    df["Flag_Disbursement_Exceeds_Sanction"] = np.where(
        (sanction_amt.notna()) & (total_disbursed > sanction_amt + 1000),
        1,
        0
    )
    
    return df


def encode_categorical_context(
    df: pd.DataFrame,
    freq_maps: dict = None
) -> tuple[pd.DataFrame, dict]:
    """
    Encodes high-cardinality categorical variables using learned frequency maps.
    Ensures no distribution leakage during prediction.
    """
    if freq_maps is None:
        freq_maps = {}
        compute_freqs = True
    else:
        compute_freqs = False
        
    for col in config.CATEGORICAL_COLS:
        if col in df.columns:
            if compute_freqs:
                f_map = df[col].value_counts(normalize=True).to_dict()
                freq_maps[col] = f_map
            else:
                f_map = freq_maps.get(col, {})
            # Map categories; unknown new categories default to 0.0
            df[f"{col}_Freq"] = df[col].map(f_map).fillna(0.0)
            
    return df, freq_maps


def run_feature_engineering(
    input_df: pd.DataFrame = None,
    preprocessing_artifacts: dict = None,
    save_output: bool = True
) -> tuple[pd.DataFrame, dict]:
    """
    Orchestrates feature engineering on the cleaned dataset.
    Preserves all 34,450 genuine rows and all original columns while appending ML features.
    
    If preprocessing_artifacts is None:
      Computes medians and frequency maps, returning them for joblib serialization.
    If preprocessing_artifacts is provided:
      Reuses learned mappings and imputation values to prevent leakage during inference.
    """
    if input_df is None:
        if not config.CLEANED_DATA_PATH.exists():
            raise FileNotFoundError(f"Cleaned dataset not found at {config.CLEANED_DATA_PATH}. Run data_analysis.py first.")
        print(f"[INFO] Loading cleaned data from: {config.CLEANED_DATA_PATH}")
        df = pd.read_csv(config.CLEANED_DATA_PATH, low_memory=False)
        for col in config.DATE_COLS:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
    else:
        df = input_df.copy()
        
    initial_rows = len(df)
    is_fit_mode = (preprocessing_artifacts is None)
    print(f"[INFO] Beginning feature engineering on {initial_rows:,} records (Mode: {'Fit' if is_fit_mode else 'Transform'})...")
    
    # 1. Lifecycle presence indicators (includes Has_Payment_Data)
    df = compute_lifecycle_indicators(df)
    
    # 2. Operational timelines with median imputation
    rec_median = None
    sanc_median = None
    if not is_fit_mode:
        rec_median = preprocessing_artifacts["imputation_values"].get("Recommendation_to_Sanction_Days")
        sanc_median = preprocessing_artifacts["imputation_values"].get("Sanction_to_Completion_Days")
        
    df, rec_median, sanc_median = compute_duration_features(df, rec_median, sanc_median)
    
    # 3. Financial discrepancy ratios & differences
    df = compute_financial_features(df)
    
    # 4. Contextual categorical frequency encoding
    freq_maps = None
    if not is_fit_mode:
        freq_maps = preprocessing_artifacts.get("categorical_freq_maps")
        
    df, freq_maps = encode_categorical_context(df, freq_maps)
    
    # 5. Numerical imputations
    if is_fit_mode:
        median_payments = float(df["Number_of_Payments"].dropna().median()) if "Number_of_Payments" in df else 1.0
        median_allocated = float(df["Allocated_Amount"].dropna().median()) if "Allocated_Amount" in df else 147000000.0
        median_disbursed = float(df["Total_Disbursed"].dropna().median()) if "Total_Disbursed" in df else 0.0
        median_amt_disbursed = float(df["Amount Disbursed ( ₹ )"].dropna().median()) if "Amount Disbursed ( ₹ )" in df else 0.0
        
        # Calculate data-driven thresholds for risk explanations
        payment_p95 = float(df["Number_of_Payments"].dropna().quantile(0.95)) if "Number_of_Payments" in df else 2.0
        valid_durations = (df["Completion Date"] - df["Sanction_Date"]).dt.days.dropna()
        duration_p99 = float(valid_durations[valid_durations > 0].quantile(0.99)) if len(valid_durations[valid_durations > 0]) > 0 else 744.0
        
        imputation_values = {
            "Recommendation_to_Sanction_Days": rec_median,
            "Sanction_to_Completion_Days": sanc_median,
            "Number_of_Payments": median_payments,
            "Allocated_Amount": median_allocated,
            "Total_Disbursed": median_disbursed,
            "Amount Disbursed ( ₹ )": median_amt_disbursed
        }
        
        preprocessing_artifacts = {
            "imputation_values": imputation_values,
            "categorical_freq_maps": freq_maps,
            "payment_p95": payment_p95,
            "duration_p99": duration_p99
        }
    else:
        imputation_values = preprocessing_artifacts["imputation_values"]
        
    for col, default_val in imputation_values.items():
        if col in df.columns:
            df[col] = df[col].fillna(default_val)
            
    assert len(df) == initial_rows, f"Row count changed! Expected {initial_rows}, got {len(df)}"
    print(f"[SUCCESS] Feature engineering complete. Total rows: {len(df):,}, Total columns: {len(df.columns)}")
    
    if save_output:
        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(config.FEATURE_ENGINEERED_PATH, index=False, encoding="utf-8")
        print(f"[SUCCESS] Feature-engineered dataset saved to: {config.FEATURE_ENGINEERED_PATH}")
        
    return df, preprocessing_artifacts


if __name__ == "__main__":
    run_feature_engineering()
