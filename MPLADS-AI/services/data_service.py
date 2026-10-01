"""
services/data_service.py
-------------------------
Data loading, caching, filtering, and aggregation service for the MPLADS AI Platform.
Loads outputs/master_with_risk.csv and outputs/anomaly_summary.csv efficiently.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st

import config


@st.cache_data(show_spinner="Loading verified MPLADS master dataset...")
def load_master_data() -> pd.DataFrame:
    """
    Loads outputs/master_with_risk.csv using st.cache_data.
    Ensures 34,450 genuine projects are loaded with proper data types.
    """
    path = config.MASTER_WITH_RISK_PATH
    if not path.exists():
        # Fallback to feature_engineered_data.csv or raise clear error
        raise FileNotFoundError(
            f"Master scored dataset not found at: {path}. "
            "Please ensure outputs/master_with_risk.csv exists."
        )
        
    df = pd.read_csv(path, low_memory=False)
    
    # Ensure proper typing for numeric fields
    numeric_cols = [
        "Allocated_Amount", "Amount Disbursed ( ₹ )", "Total_Disbursed",
        "Number_of_Payments", "Recommended_Amount", "Sanction_Amount",
        "Recommendation_to_Sanction_Days", "Sanction_to_Completion_Days",
        "Disbursement_Sanction_Difference", "Disbursement_vs_Sanction_Ratio",
        "Recommended_vs_Sanction_Difference", "Recommended_vs_Sanction_Ratio",
        "anomaly_score", "anomaly_flag"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
    # Clean text columns
    text_cols = ["Work ID", "Work Category", "State", "IDA", "Hon'ble Members of Parliament", "Constituency", "Work_Status", "risk_level", "risk_reasons"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
            
    # Precompute normalized Work ID for fast, exact, robust O(1) matching
    from utils.formatting import normalize_work_id
    df["_normalized_work_id"] = df["Work ID"].apply(normalize_work_id)
            
    return df


@st.cache_data(show_spinner=False)
def load_anomaly_summary() -> pd.DataFrame:
    """
    Loads outputs/anomaly_summary.csv.
    """
    path = config.ANOMALY_SUMMARY_PATH
    if path.exists():
        return pd.read_csv(path)
    # Generate on the fly if needed
    df = load_master_data()
    from risk_explanation import generate_anomaly_summary
    return generate_anomaly_summary(df)


def get_dataset_kpis(df: pd.DataFrame) -> dict:
    """
    Computes top-level Command Center KPI metrics.
    """
    total_projects = len(df)
    high_risk_count = int((df["risk_level"] == config.LABEL_HIGH_RISK).sum())
    med_risk_count = int((df["risk_level"] == config.LABEL_MEDIUM_RISK).sum())
    low_risk_count = int((df["risk_level"] == config.LABEL_LOW_RISK).sum())
    anomalies_count = int((df["anomaly_flag"] == 1).sum()) if "anomaly_flag" in df.columns else 0
    total_disbursed = float(df["Total_Disbursed"].fillna(0).sum())
    
    return {
        "total_projects": total_projects,
        "high_risk_count": high_risk_count,
        "high_risk_pct": (high_risk_count / total_projects * 100) if total_projects else 0.0,
        "med_risk_count": med_risk_count,
        "med_risk_pct": (med_risk_count / total_projects * 100) if total_projects else 0.0,
        "low_risk_count": low_risk_count,
        "low_risk_pct": (low_risk_count / total_projects * 100) if total_projects else 0.0,
        "anomalies_count": anomalies_count,
        "anomalies_pct": (anomalies_count / total_projects * 100) if total_projects else 0.0,
        "total_disbursed": total_disbursed
    }


def get_anomaly_category_counts(df: pd.DataFrame) -> dict:
    """
    Categorizes anomalies among flagged/high-risk projects into primary audit categories.
    """
    flagged = df[(df["risk_level"] == config.LABEL_HIGH_RISK) | (df["anomaly_flag"] == 1)]
    
    categories = {
        "Potential Over-Disbursement": 0,
        "Unusual Payment Pattern": 0,
        "Timeline Issue": 0,
        "Missing Administrative Information": 0,
        "Multivariate Statistical Anomaly": 0
    }
    
    for _, row in flagged.iterrows():
        reasons = str(row.get("risk_reasons", ""))
        
        # Primary reason classification
        if "Over-Disbursement" in reasons:
            categories["Potential Over-Disbursement"] += 1
        elif "Missing Stage Information" in reasons or "sanction information is unavailable" in reasons:
            categories["Missing Administrative Information"] += 1
        elif "Unusual Payment" in reasons or "payment installments" in reasons:
            categories["Unusual Payment Pattern"] += 1
        elif "Timeline" in reasons or "Duration" in reasons or "Chronology" in reasons:
            categories["Timeline Issue"] += 1
        else:
            categories["Multivariate Statistical Anomaly"] += 1
            
    return categories


def filter_projects(
    df: pd.DataFrame,
    risk_levels: list = None,
    states: list = None,
    constituencies: list = None,
    mps: list = None,
    work_categories: list = None,
    min_score: float = 0.0,
    max_score: float = 1.0,
    search_query: str = "",
    anomaly_reason: str = None
) -> pd.DataFrame:
    """
    Filters the master project dataset using user-selected criteria.
    """
    filtered = df.copy()
    
    if risk_levels:
        filtered = filtered[filtered["risk_level"].isin(risk_levels)]
        
    if states:
        filtered = filtered[filtered["State"].isin(states)]
        
    if constituencies:
        filtered = filtered[filtered["Constituency"].isin(constituencies)]
        
    if mps:
        filtered = filtered[filtered["Hon'ble Members of Parliament"].isin(mps)]
        
    if work_categories:
        filtered = filtered[filtered["Work Category"].isin(work_categories)]
        
    if min_score > 0.0 or max_score < 1.0:
        filtered = filtered[(filtered["anomaly_score"] >= min_score) & (filtered["anomaly_score"] <= max_score)]
        
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        mask = (
            filtered["Work ID"].str.lower().str.contains(q) |
            filtered["Work Description"].str.lower().str.contains(q) |
            filtered["Constituency"].str.lower().str.contains(q) |
            filtered["Hon'ble Members of Parliament"].str.lower().str.contains(q)
        )
        filtered = filtered[mask]
        
    if anomaly_reason and anomaly_reason != "All":
        if anomaly_reason == "Potential Over-Disbursement":
            filtered = filtered[filtered["risk_reasons"].str.contains("Over-Disbursement", case=False, na=False)]
        elif anomaly_reason == "Unusual Payment Pattern":
            filtered = filtered[filtered["risk_reasons"].str.contains("Payment", case=False, na=False)]
        elif anomaly_reason == "Timeline Issue":
            filtered = filtered[filtered["risk_reasons"].str.contains("Timeline|Duration", case=False, na=False)]
        elif anomaly_reason == "Missing Administrative Information":
            filtered = filtered[filtered["risk_reasons"].str.contains("Missing Stage|sanction information is unavailable", case=False, na=False)]
        elif anomaly_reason == "Multivariate Statistical Anomaly":
            filtered = filtered[filtered["risk_reasons"].str.contains("Multivariate", case=False, na=False)]
            
    return filtered


def get_demo_batch(df: pd.DataFrame, n_samples: int = 50) -> pd.DataFrame:
    """
    Generates a realistic demo batch of raw project records (stripping risk columns)
    to allow judges/users to test the upload & inference pipeline instantly.
    """
    # Sample a mix of High, Medium, and Low risk projects
    high_sample = df[df["risk_level"] == config.LABEL_HIGH_RISK].head(15)
    med_sample = df[df["risk_level"] == config.LABEL_MEDIUM_RISK].head(15)
    low_sample = df[df["risk_level"] == config.LABEL_LOW_RISK].head(20)
    
    demo_df = pd.concat([high_sample, med_sample, low_sample]).sample(frac=1.0, random_state=42).reset_index(drop=True)
    
    # Keep only the original input columns present in raw master.xlsx
    input_cols = [
        "Work ID", "Work Category", "Work Description", "State", "IDA",
        "Hon'ble Members of Parliament", "Constituency", "Allocated_Amount",
        "Recommended_Date", "Completion Date", "Amount Disbursed ( ₹ )",
        "Total_Disbursed", "Number_of_Payments", "Recommended_Amount",
        "Sanction_Date", "Sanction_Amount", "Work_Status"
    ]
    avail_cols = [c for c in input_cols if c in demo_df.columns]
    return demo_df[avail_cols]


def find_project_by_work_id(df: pd.DataFrame, work_id: str) -> tuple[dict | None, int, str]:
    """
    Exact normalized search for a Work ID across the entire master dataset.
    Returns:
        (record_dict, match_count, status_message)
    """
    from utils.formatting import normalize_work_id
    norm_id = normalize_work_id(work_id)
    if not norm_id:
        return None, 0, "Please enter a valid Work ID."
        
    if "_normalized_work_id" not in df.columns:
        df["_normalized_work_id"] = df["Work ID"].apply(normalize_work_id)
        
    matches = df[df["_normalized_work_id"] == norm_id]
    count = len(matches)
    
    if count == 1:
        return matches.iloc[0].to_dict(), 1, "Project found."
    elif count == 0:
        return None, 0, "No project found for this Work ID."
    else:
        return matches.iloc[0].to_dict(), count, f"Warning: Found {count} project records sharing this Work ID."
