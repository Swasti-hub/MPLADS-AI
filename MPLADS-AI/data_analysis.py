"""
data_analysis.py
----------------
Loads master.xlsx, filters out embedded portal summary/grand-total artifact rows,
cleans column whitespace and types, prints a data quality report,
and saves the cleaned dataset preserving all 34,450 genuine projects.
"""

import os
import sys
import pandas as pd
import openpyxl
from pathlib import Path

# Ensure UTF-8 output encoding for Windows terminal compatibility
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import config


def load_raw_dataset(file_path: Path = config.RAW_DATA_PATH, sheet_name: str = config.DATA_SHEET_NAME) -> pd.DataFrame:
    """
    Loads raw Excel dataset and checks sheet availability.
    Ensures master.xlsx is opened in read-only mode and not modified.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found at: {file_path}")
    
    print(f"[INFO] Inspecting workbook: {file_path}")
    wb = openpyxl.load_workbook(str(file_path), read_only=True, data_only=True)
    available_sheets = wb.sheetnames
    wb.close()
    
    print(f"[INFO] Available sheets in workbook: {available_sheets}")
    if sheet_name not in available_sheets:
        raise ValueError(f"Sheet '{sheet_name}' not found in {file_path}. Available: {available_sheets}")
    
    print(f"[INFO] Loading '{sheet_name}' from {file_path.name}...")
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(f"[SUCCESS] Loaded {len(df):,} raw rows from Excel.")
    return df


def clean_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters out portal grand-total/summary artifacts (blank/whitespace Work ID),
    standardizes whitespace in column names, and casts date and numeric columns cleanly.
    Preserves all 34,450 genuine project rows.
    """
    cleaned_df = df.copy()
    
    # Strip whitespace from column names
    cleaned_df.columns = [str(c).strip() for c in cleaned_df.columns]
    
    # Identify and filter out embedded portal grand-total/summary artifact rows
    # A summary row has an empty, null, or whitespace-only Work ID
    is_summary_row = (
        cleaned_df[config.IDENTIFIER_COL].isna() |
        cleaned_df[config.IDENTIFIER_COL].astype(str).str.strip().isin(["", "nan", "None", "\xa0"])
    )
    num_summary = int(is_summary_row.sum())
    if num_summary > 0:
        print(f"[INFO] Identified and excluded {num_summary} portal grand-total/summary artifact row(s).")
        cleaned_df = cleaned_df[~is_summary_row].copy()
    
    # Clean date columns
    for col in config.DATE_COLS:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors="coerce")
            
    # Clean numeric/financial columns
    for col in config.FINANCIAL_COLS:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce")
            
    # Clean categorical string columns (strip trailing whitespace)
    for col in config.CATEGORICAL_COLS + [config.IDENTIFIER_COL, config.STATUS_COL]:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
            # Restore genuine NaNs that became string 'nan'
            cleaned_df[col] = cleaned_df[col].replace({"nan": None, "None": None, "": None, "\xa0": None})
            
    return cleaned_df


def generate_data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates a structured data-quality summary table detailing column names,
    data types, non-null counts, and missing value percentages.
    """
    total_rows = len(df)
    report_rows = []
    
    for col in df.columns:
        missing_count = int(df[col].isna().sum())
        missing_pct = (missing_count / total_rows * 100) if total_rows > 0 else 0.0
        report_rows.append({
            "Column Name": col,
            "Data Type": str(df[col].dtype),
            "Non-Null Count": total_rows - missing_count,
            "Missing Count": missing_count,
            "Missing (%)": f"{missing_pct:.2f}%"
        })
        
    report_df = pd.DataFrame(report_rows)
    return report_df


def print_data_summary(df: pd.DataFrame, report_df: pd.DataFrame) -> None:
    """
    Prints a formatted summary of the dataset and quality audit.
    """
    print("\n" + "=" * 80)
    print("MPLADS DATA QUALITY & INSPECTION REPORT")
    print("=" * 80)
    print(f"Total Genuine Projects:    {len(df):,}")
    print(f"Total Columns:             {len(df.columns)}")
    print("-" * 80)
    print(report_df.to_string(index=False))
    print("-" * 80)
    
    print("\n[KEY DATA CHARACTERISTICS]")
    print(f"1. Unique States:           {df['State'].nunique() if 'State' in df else 'N/A'}")
    print(f"2. Unique Constituencies:   {df['Constituency'].nunique() if 'Constituency' in df else 'N/A'}")
    print(f"3. Unique Work Categories:  {df['Work Category'].nunique() if 'Work Category' in df else 'N/A'}")
    if "Allocated_Amount" in df:
        print(f"4. Total Allocated Budget:  ₹{df['Allocated_Amount'].sum():,.2f}")
    if "Total_Disbursed" in df:
        print(f"5. Total Disbursed Amount:  ₹{df['Total_Disbursed'].sum():,.2f}")
    print("=" * 80 + "\n")


def run_data_analysis(save_output: bool = True) -> pd.DataFrame:
    """
    Main function to execute ingestion, cleaning, reporting, and caching.
    """
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    df_raw = load_raw_dataset()
    df_cleaned = clean_data_types(df_raw)
    report_df = generate_data_quality_report(df_cleaned)
    print_data_summary(df_cleaned, report_df)
    
    if save_output:
        df_cleaned.to_csv(config.CLEANED_DATA_PATH, index=False, encoding="utf-8")
        print(f"[SUCCESS] Cleaned dataset saved to: {config.CLEANED_DATA_PATH} ({len(df_cleaned):,} genuine projects)")
        
    return df_cleaned


if __name__ == "__main__":
    run_data_analysis()
