"""
anomaly_model.py
----------------
Trains an unsupervised Isolation Forest model from scikit-learn on the
operational MPLADS features.
Calculates:
  - anomaly_score: MinMax normalized score between 0.0 (normal) and 1.0 (most anomalous)
  - anomaly_flag: Binary indicator (1 = anomalous outlier, 0 = typical inlier)
  - risk_level: Stratified into 'Low', 'Medium', and 'High' risk tiers

Threshold calculation:
  Isolation Forest outputs score_samples where lower (more negative) values indicate anomalies.
  We compute raw_anomaly_score = -score_samples(X).
  - High Risk:   Score >= 95th percentile (Top 5% most anomalous records)
  - Medium Risk: 85th percentile <= Score < 95th percentile
  - Low Risk:    Score < 85th percentile (Typical, standard project execution)

Work ID and macro Allocated_Amount are strictly excluded from the ML feature matrix.
Saves the trained model, feature scaler, threshold metadata, and all preprocessing mappings using joblib.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler
import joblib

# Ensure UTF-8 output encoding for Windows terminal compatibility
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import config

# List of 20 purely operational features used strictly for training Isolation Forest
ML_FEATURE_COLS = [
    # Operational Financial fields
    "Total_Disbursed",
    "Number_of_Payments",
    
    # Financial Ratios & Differences
    "Disbursement_vs_Sanction_Ratio",
    "Disbursement_Sanction_Difference",
    "Recommended_vs_Sanction_Difference",
    "Recommended_vs_Sanction_Ratio",
    "Flag_Disbursement_Exceeds_Sanction",
    
    # Operational Timeline Durations
    "Recommendation_to_Sanction_Days",
    "Sanction_to_Completion_Days",
    "Flag_Negative_Sanction_Completion",
    "Flag_Negative_Rec_Sanction",
    
    # Lifecycle Milestone Indicators
    "Has_Recommendation",
    "Has_Sanction",
    "Has_Completion",
    "Has_Disbursement",
    "Has_Payment_Data",
    
    # Contextual Institutional Density
    "Work Category_Freq",
    "State_Freq",
    "IDA_Freq",
    "Constituency_Freq"
]


def select_features(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Validates and extracts the ML feature matrix.
    Guarantees Work ID and Allocated_Amount are strictly excluded.
    """
    assert config.IDENTIFIER_COL not in ML_FEATURE_COLS, "CRITICAL ERROR: Work ID must NOT be in ML features!"
    assert "Allocated_Amount" not in ML_FEATURE_COLS, "CRITICAL ERROR: Allocated_Amount must NOT be in ML features!"
    assert "Allocated_vs_Category_Mean_Ratio" not in ML_FEATURE_COLS, "CRITICAL ERROR: Macro allocation ratio must NOT be in ML features!"
    
    available_features = [col for col in ML_FEATURE_COLS if col in df.columns]
    missing_features = [col for col in ML_FEATURE_COLS if col not in df.columns]
    
    if missing_features:
        print(f"[WARNING] Some ML features not found in DataFrame: {missing_features}")
        
    print(f"[INFO] Selected {len(available_features)} operational features for Isolation Forest training.")
    X = df[available_features].copy()
    
    # Final check: replace any residual inf or NaN with safe defaults
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return X, available_features


def train_isolation_forest(X: pd.DataFrame, feature_names: list[str]) -> tuple[IsolationForest, RobustScaler, dict]:
    """
    Scales features with RobustScaler (resistant to extreme financial outliers)
    and fits the Isolation Forest model.
    """
    print("[INFO] Scaling operational feature matrix using RobustScaler...")
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)
    
    print(f"[INFO] Initializing Isolation Forest with parameters: {config.ISOLATION_FOREST_PARAMS}")
    model = IsolationForest(**config.ISOLATION_FOREST_PARAMS)
    
    print(f"[INFO] Fitting Isolation Forest on {len(X):,} samples...")
    model.fit(X_scaled)
    print("[SUCCESS] Model fitting completed.")
    
    # Compute raw anomaly scores: negative decision function (higher = more anomalous)
    raw_scores = -model.score_samples(X_scaled)
    
    min_score = float(raw_scores.min())
    max_score = float(raw_scores.max())
    
    # Calculate empirical risk score percentiles
    high_threshold = float(np.percentile(raw_scores, config.RISK_PERCENTILE_HIGH))
    med_threshold = float(np.percentile(raw_scores, config.RISK_PERCENTILE_MEDIUM))
    
    metadata = {
        "feature_names": feature_names,
        "min_score": min_score,
        "max_score": max_score,
        "high_threshold": high_threshold,
        "med_threshold": med_threshold,
        "contamination": config.ISOLATION_FOREST_PARAMS["contamination"]
    }
    
    return model, scaler, metadata


def compute_scores_and_risk(
    df: pd.DataFrame,
    model: IsolationForest,
    scaler: RobustScaler,
    metadata: dict
) -> pd.DataFrame:
    """
    Scores the dataset, computes normalized anomaly_score, assigns anomaly_flag,
    and classifies projects into Low, Medium, and High risk tiers.
    """
    X, _ = select_features(df)
    X_scaled = scaler.transform(X)
    
    # 1. Predictions (-1 is outlier, 1 is inlier) -> convert to 1 (anomaly), 0 (normal)
    preds = model.predict(X_scaled)
    df["anomaly_flag"] = (preds == -1).astype(int)
    
    # 2. Raw scores (higher = more anomalous)
    raw_scores = -model.score_samples(X_scaled)
    
    # 3. Min-Max normalize anomaly_score to [0.0, 1.0] range
    min_s = metadata["min_score"]
    max_s = metadata["max_score"]
    score_range = max_s - min_s if max_s > min_s else 1.0
    df["anomaly_score"] = np.clip((raw_scores - min_s) / score_range, 0.0, 1.0).round(4)
    
    # 4. Assign Risk Level based on calibrated threshold percentiles
    high_th = metadata["high_threshold"]
    med_th = metadata["med_threshold"]
    
    conditions = [
        raw_scores >= high_th,
        (raw_scores >= med_th) & (raw_scores < high_th)
    ]
    choices = [config.LABEL_HIGH_RISK, config.LABEL_MEDIUM_RISK]
    df["risk_level"] = np.select(conditions, choices, default=config.LABEL_LOW_RISK)
    
    # Risk summary printout
    risk_counts = df["risk_level"].value_counts()
    print("\n" + "=" * 60)
    print("ANOMALY MODEL SCORING & RISK STRATIFICATION RESULTS")
    print("=" * 60)
    print(f"Total Projects Processed: {len(df):,}")
    print(f"Anomalies Flagged (Flag=1): {df['anomaly_flag'].sum():,} ({df['anomaly_flag'].mean()*100:.2f}%)")
    print("\nRisk Level Distribution:")
    for level in [config.LABEL_HIGH_RISK, config.LABEL_MEDIUM_RISK, config.LABEL_LOW_RISK]:
        count = risk_counts.get(level, 0)
        pct = (count / len(df)) * 100
        print(f"  - {level:8s}: {count:6,} projects ({pct:5.2f}%)")
    print("=" * 60 + "\n")
    
    return df


def save_model_artifact(
    model: IsolationForest,
    scaler: RobustScaler,
    metadata: dict,
    preprocessing_artifacts: dict = None,
    output_path: Path = config.MODEL_PATH
) -> None:
    """
    Saves model, scaler, threshold metadata, and all learned preprocessing mappings
    into a single reusable joblib bundle.
    """
    bundle = {
        "model": model,
        "scaler": scaler,
        "metadata": metadata,
        "preprocessing": preprocessing_artifacts or {}
    }
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, output_path)
    print(f"[SUCCESS] Trained model bundle saved to: {output_path}")


def run_anomaly_modeling(
    input_df: pd.DataFrame = None,
    preprocessing_artifacts: dict = None
) -> tuple[pd.DataFrame, dict]:
    """
    Orchestrates anomaly model training and scoring.
    """
    if input_df is None:
        if not config.FEATURE_ENGINEERED_PATH.exists():
            raise FileNotFoundError(f"Feature dataset not found at {config.FEATURE_ENGINEERED_PATH}. Run feature_engineering.py first.")
        print(f"[INFO] Loading feature dataset from: {config.FEATURE_ENGINEERED_PATH}")
        df = pd.read_csv(config.FEATURE_ENGINEERED_PATH, low_memory=False)
    else:
        df = input_df.copy()
        
    X, feature_names = select_features(df)
    model, scaler, metadata = train_isolation_forest(X, feature_names)
    df_scored = compute_scores_and_risk(df, model, scaler, metadata)
    save_model_artifact(model, scaler, metadata, preprocessing_artifacts)
    
    return df_scored, metadata


if __name__ == "__main__":
    run_anomaly_modeling()
