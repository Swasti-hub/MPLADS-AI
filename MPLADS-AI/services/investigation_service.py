"""
services/investigation_service.py
---------------------------------
Provides deep-dive case file extraction, evidence synthesis, and rule-based audit
recommendations for investigating officers inspecting flagged MPLADS projects.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

import config
from utils.formatting import format_inr, format_date_str, format_count, normalize_work_id


def get_project_by_id(df: pd.DataFrame, work_id: str) -> Dict[str, Any]:
    """
    Finds a single project record by normalized Work ID exact match and returns it as a dictionary.
    """
    if work_id is None or not str(work_id).strip():
        return {}
        
    norm_id = normalize_work_id(work_id)
    if "_normalized_work_id" in df.columns:
        match = df[df["_normalized_work_id"] == norm_id]
    else:
        match = df[df["Work ID"].apply(normalize_work_id) == norm_id]
        
    if match.empty:
        return {}
    return match.iloc[0].to_dict()


def build_investigation_dossier(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constructs a comprehensive audit dossier from a single project record.
    Synthesizes financial, timeline, payment, and administrative evidence.
    """
    if not row:
        return {}

    # Basic Identification
    work_id = str(row.get("Work ID", "Unknown")).strip()
    state = str(row.get("State", "N/A")).strip()
    mp = str(row.get("Hon'ble Members of Parliament", "N/A")).strip()
    constituency = str(row.get("Constituency", "N/A")).strip()
    ida = str(row.get("IDA", "N/A")).strip()
    category = str(row.get("Work Category", "N/A")).strip()
    description = str(row.get("Work Description", "No description provided.")).strip()
    work_status = str(row.get("Work_Status", "N/A")).strip()

    # Risk Metrics
    risk_level = str(row.get("risk_level", config.LABEL_LOW_RISK)).strip()
    anomaly_score = float(row.get("anomaly_score", 0.0))
    anomaly_flag = int(row.get("anomaly_flag", 0))

    if risk_level == config.LABEL_HIGH_RISK:
        priority_label = "Priority 1 — Immediate Audit Verification Required"
        priority_badge = "High"
    elif risk_level == config.LABEL_MEDIUM_RISK:
        priority_label = "Priority 2 — Targeted Document Review Recommended"
        priority_badge = "Medium"
    else:
        priority_label = "Routine Monitoring — Standard Program Guidelines"
        priority_badge = "Low"

    # Financial Evidence
    recommended_amt = row.get("Recommended_Amount", np.nan)
    sanction_amt = row.get("Sanction_Amount", np.nan)
    total_disbursed = float(row.get("Total_Disbursed", 0.0) or 0.0)
    amt_disbursed_raw = float(row.get("Amount Disbursed ( ₹ )", 0.0) or 0.0)
    allocated_macro = row.get("Allocated_Amount", np.nan)

    disb_sanct_diff = float(row.get("Disbursement_Sanction_Difference", 0.0) or 0.0)
    disb_sanct_ratio = float(row.get("Disbursement_vs_Sanction_Ratio", 1.0) or 1.0)

    # Financial Check Classification
    financial_alerts = []
    has_sanction = row.get("Has_Sanction", 1) == 1
    has_disbursement = row.get("Has_Disbursement", 1) == 1

    if pd.notna(sanction_amt) and sanction_amt > 0:
        if total_disbursed > sanction_amt + 1000:
            over_val = total_disbursed - sanction_amt
            financial_alerts.append({
                "type": "danger",
                "tag": "Potential Over-Disbursement",
                "message": (
                    f"Recorded disbursements ({format_inr(total_disbursed)}) exceed sanctioned amount "
                    f"({format_inr(sanction_amt)}) by {format_inr(over_val)} ({((total_disbursed/sanction_amt)-1)*100:.1f}% overrun)."
                )
            })
    elif has_disbursement and not has_sanction:
        financial_alerts.append({
            "type": "warning",
            "tag": "Missing Administrative Sanction Record",
            "message": (
                f"Disbursement of {format_inr(total_disbursed)} recorded, but formal Sanction Amount "
                "is not documented in the current portal dataset."
            )
        })

    # Payment Analysis
    num_payments = row.get("Number_of_Payments", np.nan)
    has_payment_data = row.get("Has_Payment_Data", 1) == 1
    payment_alerts = []

    if pd.notna(num_payments):
        payments_val = int(num_payments)
        if payments_val > 2:
            payment_alerts.append({
                "type": "warning",
                "tag": "Unusual Payment Pattern",
                "message": (
                    f"Project recorded {payments_val} separate payment installments/tranches. "
                    "This exceeds typical multi-stage disbursement patterns for single community works."
                )
            })
        elif payments_val == 0 and total_disbursed > 0 and has_payment_data:
            payment_alerts.append({
                "type": "danger",
                "tag": "Payment Process Discrepancy",
                "message": f"Positive disbursement ({format_inr(total_disbursed)}) recorded with 0 payment tranches."
            })
    else:
        payments_val = 0

    # Timeline Analysis
    rec_date = row.get("Recommended_Date", None)
    sanct_date = row.get("Sanction_Date", None)
    comp_date = row.get("Completion Date", None)

    rec_sanct_days = row.get("Recommendation_to_Sanction_Days", np.nan)
    sanct_comp_days = row.get("Sanction_to_Completion_Days", np.nan)
    neg_sanct_comp = row.get("Flag_Negative_Sanction_Completion", 0) == 1
    neg_rec_sanct = row.get("Flag_Negative_Rec_Sanction", 0) == 1

    timeline_alerts = []
    if neg_sanct_comp:
        timeline_alerts.append({
            "type": "danger",
            "tag": "Chronology Discrepancy",
            "message": (
                f"Completion Date ({format_date_str(comp_date)}) is recorded prior to Sanction Date ({format_date_str(sanct_date)}). "
                "Requires administrative verification of actual commencement and completion memos."
            )
        })
    if neg_rec_sanct:
        timeline_alerts.append({
            "type": "danger",
            "tag": "Chronology Discrepancy",
            "message": (
                f"Sanction Date ({format_date_str(sanct_date)}) is recorded prior to MP Recommendation Date ({format_date_str(rec_date)})."
            )
        })
    if pd.notna(sanct_comp_days) and sanct_comp_days > 744:
        timeline_alerts.append({
            "type": "warning",
            "tag": "Unusually Long Duration",
            "message": (
                f"Execution duration from sanction to completion was {int(sanct_comp_days):,} days "
                "(exceeds 99th percentile benchmark of 744 days for MPLADS works)."
            )
        })

    # Administrative Completeness Indicators
    admin_stages = {
        "Has Recommendation": bool(row.get("Has_Recommendation", 0)),
        "Has Administrative Sanction": bool(row.get("Has_Sanction", 0)),
        "Has Completion Record": bool(row.get("Has_Completion", 0)),
        "Has Disbursement Record": bool(row.get("Has_Disbursement", 0)),
        "Has Payment Installment Data": bool(row.get("Has_Payment_Data", 0))
    }

    # Reasons & Rule-based Recommendations
    raw_reasons = str(row.get("risk_reasons", "Standard Pattern"))
    explanation_bullets = []
    if "Requires Investigation:" in raw_reasons:
        cleaned_reasons = raw_reasons.replace("Requires Investigation:", "").strip()
        explanation_bullets = [s.strip() for s in cleaned_reasons.split(";") if s.strip()]
    elif "Standard Pattern" in raw_reasons:
        explanation_bullets = ["All monitored operational metrics align with typical MPLADS implementation standards."]
    else:
        explanation_bullets = [raw_reasons]

    # Generate Actionable Audit Steps
    recommended_actions: List[str] = []
    if financial_alerts:
        recommended_actions.append("Verify formal Administrative Sanction Order (ASO) and examine if a Revised Sanction was issued by the Competent Authority.")
        recommended_actions.append("Reconcile bank account/treasury disbursement statements against contractor payment vouchers and measurement books.")
    if payment_alerts:
        recommended_actions.append("Review milestone-linked installment sanction memos to verify justification for multiple tranche releases.")
        recommended_actions.append("Inspect vendor/contractor payment acknowledgment receipts and verify whether works were split.")
    if timeline_alerts:
        recommended_actions.append("Retrieve physical Work Commencement and Completion Certificates from the Implementing District Authority (IDA).")
        recommended_actions.append("Cross-reference date stamps on physical files with e-portal data entry logs to identify potential clerical entry errors.")
    if not has_sanction and has_disbursement:
        recommended_actions.append("Request the nodal district authority to furnish the physical sanction memo and update the official e-portal registry.")
    if not recommended_actions:
        if risk_level == config.LABEL_HIGH_RISK:
            recommended_actions.append("Conduct a comprehensive multi-parameter file review covering financial, contractor, and milestone documents.")
            recommended_actions.append("Request clarification from the Nodal Implementing District Authority regarding statistical deviation.")
        else:
            recommended_actions.append("Maintain routine programmatic oversight in accordance with standard MPLADS operational guidelines.")

    return {
        "work_id": work_id,
        "state": state,
        "mp": mp,
        "constituency": constituency,
        "ida": ida,
        "category": category,
        "description": description,
        "work_status": work_status,
        "risk_level": risk_level,
        "anomaly_score": anomaly_score,
        "anomaly_flag": anomaly_flag,
        "priority_label": priority_label,
        "priority_badge": priority_badge,
        "financials": {
            "recommended_amt": recommended_amt,
            "sanction_amt": sanction_amt,
            "total_disbursed": total_disbursed,
            "amt_disbursed_raw": amt_disbursed_raw,
            "allocated_macro": allocated_macro,
            "disb_sanct_diff": disb_sanct_diff,
            "disb_sanct_ratio": disb_sanct_ratio,
            "alerts": financial_alerts
        },
        "payments": {
            "number_of_payments": payments_val,
            "has_payment_data": has_payment_data,
            "alerts": payment_alerts
        },
        "timeline": {
            "rec_date": rec_date,
            "sanct_date": sanct_date,
            "comp_date": comp_date,
            "rec_sanct_days": rec_sanct_days,
            "sanct_comp_days": sanct_comp_days,
            "alerts": timeline_alerts
        },
        "admin_stages": admin_stages,
        "explanation_bullets": explanation_bullets,
        "recommended_actions": recommended_actions
    }
