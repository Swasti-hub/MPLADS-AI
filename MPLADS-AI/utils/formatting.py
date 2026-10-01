"""
formatting.py
-------------
Formatters for currency (INR), dates, numbers, percentages,
and HTML badges for the MPLADS AI platform.
"""

import re
import pandas as pd
import numpy as np


def normalize_work_id(work_id) -> str:
    """
    Normalizes a Work ID for robust exact matching:
      - Converts to string
      - Replaces non-breaking spaces (\xa0) and zero-width spaces
      - Strips leading and trailing whitespace
      - Normalizes internal multiple whitespaces to single space
      - Preserves '/' and '-' exactly
      - Uppercases for consistent matching
    """
    if work_id is None or pd.isna(work_id):
        return ""
    s = str(work_id)
    # Remove non-breaking spaces and zero-width characters
    s = s.replace("\xa0", " ").replace("\u200b", "").replace("\ufeff", "")
    # Strip leading and trailing whitespace
    s = s.strip()
    # Normalize internal whitespace
    s = re.sub(r"\s+", " ", s)
    return s.upper()


def format_inr(value, compact: bool = False) -> str:
    """
    Formats a numeric value into Indian Rupee representation.
    If compact is True:
      - >= 1 Crore (10,000,000) -> ₹X.XX Cr
      - >= 1 Lakh (100,000) -> ₹X.XX L
      - Otherwise -> ₹X,XX,XXX
    """
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        val = float(value)
    except (ValueError, TypeError):
        return str(value)
        
    if compact:
        abs_val = abs(val)
        if abs_val >= 10_000_000:
            return f"₹{val / 10_000_000:,.2f} Cr"
        elif abs_val >= 100_000:
            return f"₹{val / 100_000:,.2f} L"
        else:
            return f"₹{val:,.0f}"
            
    # Full standard representation
    return f"₹{val:,.2f}"


def format_count(value) -> str:
    """Formats an integer with comma separators."""
    if value is None or pd.isna(value):
        return "0"
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)


def format_percent(value, decimals: int = 2) -> str:
    """Formats float as percentage string."""
    if value is None or pd.isna(value):
        return "0.0%"
    try:
        return f"{float(value):.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)


def format_date_str(value) -> str:
    """Formats datetime safely as YYYY-MM-DD or returns 'Not Recorded'."""
    if value is None or pd.isna(value) or str(value).strip().lower() in ["nat", "none", "nan", ""]:
        return "Not Recorded"
    try:
        dt = pd.to_datetime(value)
        return dt.strftime("%d %b %Y")
    except Exception:
        return str(value)


def get_risk_badge_html(risk_level: str) -> str:
    """Returns government/enterprise styled HTML risk badge."""
    level = str(risk_level).strip().title()
    if level == "High":
        bg = "#FEE2E2"
        text = "#991B1B"
        border = "#F87171"
        dot = "#DC2626"
    elif level == "Medium":
        bg = "#FEF3C7"
        text = "#92400E"
        border = "#FBBF24"
        dot = "#D97706"
    else:  # Low
        bg = "#D1FAE5"
        text = "#065F46"
        border = "#34D399"
        dot = "#059669"
        
    return f"""<span style="
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background-color: {bg};
        color: {text};
        border: 1px solid {border};
        padding: 2px 10px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.02em;
    "><span style="width: 7px; height: 7px; border-radius: 50%; background-color: {dot}; display: inline-block;"></span>{level} Risk</span>"""
