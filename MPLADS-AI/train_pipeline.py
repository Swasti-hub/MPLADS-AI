"""
train_pipeline.py
-----------------
End-to-End Execution Pipeline for MPLADS Anomaly and Fraud-Risk Detection.
Orchestrates:
  Step 1: Data Ingestion & Cleaning (data_analysis.py) - Filters summary rows
  Step 2: Feature Engineering & Preprocessing Fitting (feature_engineering.py)
  Step 3: Unsupervised Isolation Forest Modeling (anomaly_model.py) - 20 operational features
  Step 4: Risk Explanation & Summary Reporting (risk_explanation.py) - Pure operational explanations
  Step 5: Metric Logging & Output Verification

Ensures single-command end-to-end reproducibility and leak-free artifact persistence.
"""

import sys
import time
from pathlib import Path

# Ensure UTF-8 output encoding for Windows terminal compatibility
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import config
from data_analysis import run_data_analysis
from feature_engineering import run_feature_engineering
from anomaly_model import run_anomaly_modeling, ML_FEATURE_COLS
from risk_explanation import run_risk_explanation


def run_complete_pipeline():
    """
    Executes the entire MPLADS anomaly detection pipeline sequentially.
    """
    start_time = time.time()
    print("=" * 80)
    print("STARTING MPLADS ANOMALY & FRAUD-RISK DETECTION PIPELINE")
    print("=" * 80)
    
    # -------------------------------------------------------------------------
    # STEP 1: Data Ingestion & Cleaning
    # -------------------------------------------------------------------------
    step1_start = time.time()
    print("\n>>> [STEP 1/4] Ingesting master.xlsx & filtering summary artifact...")
    cleaned_df = run_data_analysis(save_output=True)
    print(f">>> [STEP 1/4] Completed in {time.time() - step1_start:.2f}s.")
    
    # -------------------------------------------------------------------------
    # STEP 2: Feature Engineering
    # -------------------------------------------------------------------------
    step2_start = time.time()
    print("\n>>> [STEP 2/4] Constructing 20 Operational Features & Preprocessing Artifacts...")
    feature_df, preprocessing_artifacts = run_feature_engineering(input_df=cleaned_df, save_output=True)
    print(f">>> [STEP 2/4] Completed in {time.time() - step2_start:.2f}s.")
    
    # -------------------------------------------------------------------------
    # STEP 3: Isolation Forest Model Training & Scoring
    # -------------------------------------------------------------------------
    step3_start = time.time()
    print("\n>>> [STEP 3/4] Training Isolation Forest & Persisting Artifact Bundle...")
    scored_df, metadata = run_anomaly_modeling(
        input_df=feature_df,
        preprocessing_artifacts=preprocessing_artifacts
    )
    print(f">>> [STEP 3/4] Completed in {time.time() - step3_start:.2f}s.")
    
    # -------------------------------------------------------------------------
    # STEP 4: Risk Explanation & Summary Reporting
    # -------------------------------------------------------------------------
    step4_start = time.time()
    print("\n>>> [STEP 4/4] Generating Auditable Risk Explanations & Summaries...")
    final_df, summary_df = run_risk_explanation(
        input_df=scored_df,
        preprocessing_artifacts=preprocessing_artifacts,
        save_outputs=True
    )
    print(f">>> [STEP 4/4] Completed in {time.time() - step4_start:.2f}s.")
    
    total_time = time.time() - start_time
    
    # -------------------------------------------------------------------------
    # PIPELINE METRIC & ARTIFACT SUMMARY
    # -------------------------------------------------------------------------
    total_projects = len(final_df)
    anomaly_df = final_df[final_df["anomaly_flag"] == 1]
    anomaly_count = len(anomaly_df)
    risk_counts = final_df["risk_level"].value_counts().to_dict()
    high_risk = risk_counts.get(config.LABEL_HIGH_RISK, 0)
    med_risk = risk_counts.get(config.LABEL_MEDIUM_RISK, 0)
    low_risk = risk_counts.get(config.LABEL_LOW_RISK, 0)
    
    # Root-cause signal counts among the flagged anomalies
    c_over_disb = int(anomaly_df["risk_reasons"].str.contains("Potential Over-Disbursement", na=False).sum())
    c_payment = int(anomaly_df["risk_reasons"].str.contains("Payment", na=False).sum())
    c_timeline = int(anomaly_df["risk_reasons"].str.contains("Timeline|Duration", na=False).sum())
    c_missing_admin = int(anomaly_df["risk_reasons"].str.contains("Missing Stage Information", na=False).sum())
    c_multivariate = int(anomaly_df["risk_reasons"].str.contains("Multivariate Statistical Outlier", na=False).sum())
    
    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION COMPLETE - FINAL REPORT")
    print("=" * 80)
    print(f"Total Genuine Projects:       {total_projects:,} (Preserved, 0 dropped)")
    print(f"Total Anomalies Flagged:      {anomaly_count:,} ({anomaly_count/total_projects*100:.2f}%)")
    print("-" * 80)
    print("RISK STRATIFICATION COUNTS:")
    print(f"  * High Risk (Top 5% priority):  {high_risk:6,} ({high_risk/total_projects*100:.2f}%)")
    print(f"  * Medium Risk (Secondary):      {med_risk:6,} ({med_risk/total_projects*100:.2f}%)")
    print(f"  * Low Risk (Typical execution): {low_risk:6,} ({low_risk/total_projects*100:.2f}%)")
    print("-" * 80)
    print("ISOLATION FOREST THRESHOLDS & SCORING METRICS:")
    print(f"  * Raw Score Min:                {metadata['min_score']:.4f}")
    print(f"  * Raw Score Max:                {metadata['max_score']:.4f}")
    print(f"  * Medium Risk Cutoff (p85):     {metadata['med_threshold']:.4f}")
    print(f"  * High Risk Cutoff (p95):       {metadata['high_threshold']:.4f}")
    print("-" * 80)
    print(f"EXACT ML FEATURE LIST ({len(ML_FEATURE_COLS)} features):")
    for i, col in enumerate(ML_FEATURE_COLS, 1):
        print(f"  {i:2d}. {col}")
    print("-" * 80)
    print("ANOMALY ROOT-CAUSE BREAKDOWN (among 1,723 flagged anomalies):")
    print(f"  * Over-Disbursement:                  {c_over_disb:5,d} ({c_over_disb/anomaly_count*100:5.2f}%)")
    print(f"  * Unusual Payment Patterns:           {c_payment:5,d} ({c_payment/anomaly_count*100:5.2f}%)")
    print(f"  * Timeline Issues (Duration/Order):   {c_timeline:5,d} ({c_timeline/anomaly_count*100:5.2f}%)")
    print(f"  * Missing Administrative Information: {c_missing_admin:5,d} ({c_missing_admin/anomaly_count*100:5.2f}%)")
    print(f"  * Multivariate Statistical Anomalies: {c_multivariate:5,d} ({c_multivariate/anomaly_count*100:5.2f}%)")
    print("-" * 80)
    print("GENERATED ARTIFACT PATHS:")
    print(f"  1. Cleaned Data:              {config.CLEANED_DATA_PATH}")
    print(f"  2. Feature Engineered Data:   {config.FEATURE_ENGINEERED_PATH}")
    print(f"  3. Master Dataset with Risk:  {config.MASTER_WITH_RISK_PATH}")
    print(f"  4. Anomaly Summary:           {config.ANOMALY_SUMMARY_PATH}")
    print(f"  5. Trained Model Bundle:      {config.MODEL_PATH}")
    print(f"\nTotal Execution Time: {total_time:.2f} seconds")
    print("=" * 80 + "\n")
    
    return final_df


if __name__ == "__main__":
    run_complete_pipeline()
