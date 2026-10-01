"""
predict.py
----------
Inference module for scoring new or unlabelled MPLADS project datasets.
Loads the trained Isolation Forest bundle from joblib, applies learned
preprocessing mappings and imputation statistics (without leakage or recalculation),
and outputs predictions with anomaly scores, risk levels, and human-auditable explanations.

Usage:
  python predict.py --input <path_to_new_dataset.xlsx_or_csv> [--output <output_path.csv>]
"""

import sys
import argparse
import pandas as pd
from pathlib import Path
import joblib

# Ensure UTF-8 output encoding for Windows terminal compatibility
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import config
from data_analysis import clean_data_types
from feature_engineering import run_feature_engineering
from anomaly_model import compute_scores_and_risk
from risk_explanation import generate_project_explanations


def load_model_bundle(model_path: Path = config.MODEL_PATH) -> dict:
    """
    Loads saved model, scaler, threshold metadata, and learned preprocessing mappings from joblib.
    """
    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained model not found at '{model_path}'. Please run 'train_pipeline.py' first."
        )
    bundle = joblib.load(model_path)
    return bundle


def predict_dataset(
    input_path: str | Path,
    output_path: str | Path = None,
    model_bundle: dict = None
) -> pd.DataFrame:
    """
    End-to-end inference function for new MPLADS project data.
    Uses strictly the learned preprocessing mappings from training.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found at: {input_path}")
        
    print(f"[INFO] Loading input file for scoring: {input_path}")
    if input_path.suffix.lower() in [".xlsx", ".xls"]:
        df_raw = pd.read_excel(input_path)
    else:
        df_raw = pd.read_csv(input_path, low_memory=False)
        
    print(f"[INFO] Ingested {len(df_raw):,} raw records. Applying cleaning and feature engineering...")
    df_cleaned = clean_data_types(df_raw)
    
    if model_bundle is None:
        model_bundle = load_model_bundle()
        
    model = model_bundle["model"]
    scaler = model_bundle["scaler"]
    metadata = model_bundle["metadata"]
    preprocessing_artifacts = model_bundle.get("preprocessing", {})
    
    # Apply learned mappings and imputations without recalculating on new dataset
    df_features, _ = run_feature_engineering(
        input_df=df_cleaned,
        preprocessing_artifacts=preprocessing_artifacts,
        save_output=False
    )
    
    print("[INFO] Computing anomaly scores and risk levels...")
    df_scored = compute_scores_and_risk(df_features, model, scaler, metadata)
    
    print("[INFO] Generating audit risk explanations using learned empirical thresholds...")
    df_scored["risk_reasons"] = generate_project_explanations(
        df_scored,
        payment_p95=preprocessing_artifacts.get("payment_p95"),
        duration_p99=preprocessing_artifacts.get("duration_p99")
    )
    
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_scored.to_csv(output_path, index=False, encoding="utf-8")
        print(f"[SUCCESS] Scored predictions saved to: {output_path}")
        
    return df_scored


def main():
    parser = argparse.ArgumentParser(description="Score new MPLADS projects for anomaly and fraud-risk.")
    parser.add_argument("--input", type=str, default=str(config.CLEANED_DATA_PATH), help="Path to input Excel or CSV file")
    parser.add_argument("--output", type=str, default=str(config.OUTPUT_DIR / "sample_predictions.csv"), help="Path to save scored results")
    args = parser.parse_args()
    
    predict_dataset(input_path=args.input, output_path=args.output)


if __name__ == "__main__":
    main()
