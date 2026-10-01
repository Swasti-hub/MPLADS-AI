"""
risk_explanation.py
-------------------
Generates human-readable, auditable explanations for all High and Medium risk projects.
Translates statistical anomaly scores into concrete operational signals:
  - Over-disbursement relative to recorded sanction
  - Timeline chronology reversals or prolonged durations
  - Unusual payment installment counts (data-driven 95th percentile)
  - Large recommendation vs sanction divergences
  - Funds disbursed when sanction information is unavailable in current dataset
  - Complex multivariate operational deviations

Rules:
  - High allocation alone NEVER causes a project to become High Risk.
  - Adheres strictly to "Requires Investigation" or "Potential Anomaly" terminology.
  - Never asserts confirmed fraud.
  - Does not claim missing sanction information implies an absent sanction.
  - Generates outputs/master_with_risk.csv and outputs/anomaly_summary.csv.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Ensure UTF-8 output encoding for Windows terminal compatibility
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import config


def generate_project_explanations(
    df: pd.DataFrame,
    payment_p95: float = None,
    duration_p99: float = None
) -> pd.Series:
    """
    Evaluates rule-based signals on every project row and formats a human-readable
    explanation string for why the project requires audit/investigation.
    Uses data-driven percentiles for thresholds and excludes allocation bias.
    """
    reasons_list = []
    
    # Calculate empirical thresholds if not provided
    if duration_p99 is None:
        valid_durations = df.loc[df["Sanction_to_Completion_Days"] > 0, "Sanction_to_Completion_Days"]
        duration_p99 = float(valid_durations.quantile(0.99)) if len(valid_durations) > 0 else 744.0
        
    if payment_p95 is None:
        valid_payments = df["Number_of_Payments"].dropna()
        payment_p95 = float(valid_payments.quantile(0.95)) if len(valid_payments) > 0 else 2.0
        
    for idx, row in df.iterrows():
        signals = []
        risk_level = row.get("risk_level", config.LABEL_LOW_RISK)
        
        # Generate detailed signals for Medium and High risk projects, or flagged anomalies
        if risk_level in [config.LABEL_HIGH_RISK, config.LABEL_MEDIUM_RISK] or row.get("anomaly_flag", 0) == 1:
            
            # Signal 1: Over-disbursement compared to recorded sanction
            disbursed = row.get("Total_Disbursed", 0.0)
            sanction = row.get("Sanction_Amount", np.nan)
            if pd.notna(sanction) and sanction > 0 and (disbursed > sanction + 1000):
                diff = disbursed - sanction
                signals.append(
                    f"Potential Over-Disbursement: Disbursed amount (₹{disbursed:,.0f}) exceeds recorded sanctioned amount (₹{sanction:,.0f}) by ₹{diff:,.0f}"
                )
                
            # Signal 2: Negative/Reversed Chronology
            if row.get("Flag_Negative_Sanction_Completion", 0) == 1:
                signals.append("Timeline Discrepancy: Completion date is recorded prior to the administrative sanction date")
            if row.get("Flag_Negative_Rec_Sanction", 0) == 1:
                signals.append("Timeline Discrepancy: Sanction date is recorded prior to the MP recommendation date")
                
            # Signal 3: Prolonged execution duration
            comp_days = row.get("Sanction_to_Completion_Days", 0.0)
            if comp_days > duration_p99 and row.get("Has_Sanction", 0) == 1:
                signals.append(
                    f"Unusually Long Duration: Project took {int(comp_days):,} days from sanction to completion (exceeds 99th percentile of {int(duration_p99)} days)"
                )
                
            # Signal 4: Unusual Payment Installments (data-driven 95th percentile)
            payments = row.get("Number_of_Payments", np.nan)
            has_payment_data = row.get("Has_Payment_Data", 1)
            if pd.notna(payments) and payments > payment_p95:
                signals.append(
                    f"Unusual Payment Frequency: High number of payment installments ({int(payments)} tranches, exceeds 95th percentile of {int(payment_p95)})"
                )
            elif has_payment_data == 1 and payments == 0 and disbursed > 0:
                signals.append("Process Discrepancy: Total disbursement > 0 recorded with 0 payment installments")
                
            # Signal 5: Large Recommended vs Sanction Variance
            rec_amt = row.get("Recommended_Amount", np.nan)
            if pd.notna(rec_amt) and pd.notna(sanction) and sanction > 0:
                ratio = rec_amt / sanction
                if ratio > 2.0 or ratio < 0.3:
                    signals.append(
                        f"Recommendation Variance: Recommended (₹{rec_amt:,.0f}) diverges significantly from Sanction (₹{sanction:,.0f})"
                    )
                    
            # Signal 6: Disbursement when sanction information is unavailable
            if row.get("Has_Disbursement", 0) == 1 and row.get("Has_Sanction", 0) == 0:
                signals.append(
                    f"Missing Stage Information: Disbursement recorded (₹{disbursed:,.0f}), but sanction information is unavailable in the current dataset"
                )
                
            # Signal 7: Fallback for multi-dimensional tree isolation
            if not signals:
                signals.append("Multivariate Statistical Outlier: Complex deviation across lifecycle, state-frequency, and budget features")
                
            full_explanation = "Requires Investigation: " + "; ".join(signals)
        else:
            full_explanation = "Standard Pattern: Metrics align with typical MPLADS implementation norms"
            
        reasons_list.append(full_explanation)
        
    return pd.Series(reasons_list, index=df.index)


def generate_anomaly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates anomaly counts, risk breakdowns, and financial exposure
    grouped by State and Work Category.
    """
    summary = df.groupby(["State", "Work Category"]).agg(
        Total_Projects=("Work ID", "count"),
        High_Risk_Count=("risk_level", lambda s: (s == config.LABEL_HIGH_RISK).sum()),
        Medium_Risk_Count=("risk_level", lambda s: (s == config.LABEL_MEDIUM_RISK).sum()),
        Low_Risk_Count=("risk_level", lambda s: (s == config.LABEL_LOW_RISK).sum()),
        Anomalies_Flagged=("anomaly_flag", "sum"),
        Mean_Anomaly_Score=("anomaly_score", "mean"),
        Total_Disbursed=("Total_Disbursed", "sum")
    ).reset_index()
    
    summary["High_Risk_%"] = (summary["High_Risk_Count"] / summary["Total_Projects"] * 100).round(2)
    summary["Mean_Anomaly_Score"] = summary["Mean_Anomaly_Score"].round(4)
    summary = summary.sort_values(by="High_Risk_Count", ascending=False)
    return summary


def run_risk_explanation(
    input_df: pd.DataFrame = None,
    preprocessing_artifacts: dict = None,
    save_outputs: bool = True
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Attaches risk explanations to scored dataframe and exports final master_with_risk.csv
    and anomaly_summary.csv.
    """
    if input_df is None:
        raise ValueError("input_df must be provided to run_risk_explanation")
    
    df = input_df.copy()
    print("[INFO] Generating human-readable risk explanations for flagged projects...")
    
    payment_p95 = preprocessing_artifacts.get("payment_p95") if preprocessing_artifacts else None
    duration_p99 = preprocessing_artifacts.get("duration_p99") if preprocessing_artifacts else None
    
    df["risk_reasons"] = generate_project_explanations(
        df,
        payment_p95=payment_p95,
        duration_p99=duration_p99
    )
    
    assert len(df) == len(input_df), "Row count altered during explanation generation!"
    summary_df = generate_anomaly_summary(df)
    
    if save_outputs:
        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(config.MASTER_WITH_RISK_PATH, index=False, encoding="utf-8")
        summary_df.to_csv(config.ANOMALY_SUMMARY_PATH, index=False, encoding="utf-8")
        print(f"[SUCCESS] Final scored dataset saved to: {config.MASTER_WITH_RISK_PATH}")
        print(f"[SUCCESS] Anomaly summary report saved to: {config.ANOMALY_SUMMARY_PATH}")
        
    return df, summary_df


if __name__ == "__main__":
    pass
