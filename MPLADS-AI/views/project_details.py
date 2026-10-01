"""
views/project_details.py
------------------------
Detailed case dossier screen for investigating officers.
Structured with high-authority visual hierarchy:
  1. Top: PROJECT INVESTIGATION, Work ID, Risk Level badge, Risk Score
  2. Search Project by Work ID field with placeholder WS/MP18227/2024-2025/148775
  3. WHY WAS THIS FLAGGED? (Prominent audit signals)
  4. RECOMMENDED INVESTIGATION (Numbered operational action steps)
  5. RISK ASSESSMENT & WORK METADATA
  6. FINANCIAL ANALYSIS
  7. PAYMENT ANALYSIS
  8. TIMELINE ANALYSIS
  9. ADMINISTRATIVE DATA
"""

import streamlit as st
import pandas as pd
import numpy as np

from services.data_service import load_master_data, find_project_by_work_id
from services.investigation_service import get_project_by_id, build_investigation_dossier
from components.cards import (
    render_project_summary_header,
    render_audit_alert,
    render_stage_indicator
)
from utils.formatting import format_inr, format_date_str, format_count, normalize_work_id


def render_project_details():
    """Renders the comprehensive project-level investigation file."""
    
    df = load_master_data()

    # Determine which project to view
    current_work_id = st.session_state.get("selected_work_id", None)
    if not current_work_id or not str(current_work_id).strip():
        # Default to the highest risk project in the dataset
        high_risk_subset = df[df["risk_level"] == "High"]
        if not high_risk_subset.empty:
            current_work_id = high_risk_subset.sort_values(by="anomaly_score", ascending=False).iloc[0]["Work ID"]
        else:
            current_work_id = df.iloc[0]["Work ID"]
        st.session_state["selected_work_id"] = current_work_id

    # 1. DIRECT WORK ID SEARCH
    st.markdown("<div class='details-search-section'>", unsafe_allow_html=True)
    with st.container():
        with st.form("project_details_search_form", clear_on_submit=False):
            col_lbl, col_search, col_s_btn, col_back_btn = st.columns([1.2, 2.8, 1, 1])
            with col_lbl:
                st.markdown(
                    "<div style='padding-top:6px; font-weight:700; font-size:0.86rem; color:#0F2B48;'>Search Project by Work ID</div>",
                    unsafe_allow_html=True
                )
            with col_search:
                search_input = st.text_input(
                    "Search Project by Work ID",
                    placeholder="WS/MP18227/2024-2025/148775",
                    key="details_search_input",
                    label_visibility="collapsed"
                )
            with col_s_btn:
                search_submitted = st.form_submit_button(
                    "Search Work ID",
                    type="primary",
                    use_container_width=True
                )
            with col_back_btn:
                back_clicked = st.form_submit_button(
                    "← Back to Roster",
                    type="secondary",
                    use_container_width=True
                )

            if back_clicked:
                st.session_state["current_page"] = "Risk Investigation"
                st.rerun()

            if search_submitted:
                clean_q = search_input.strip() if search_input else ""
                if not clean_q:
                    st.warning("Please enter a Work ID to search.")
                else:
                    record, count, msg = find_project_by_work_id(df, clean_q)
                    if count >= 1:
                        st.session_state["selected_work_id"] = record["Work ID"]
                        st.rerun()
                    else:
                        st.error("No project found for this Work ID.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. FETCH PROJECT RECORD
    project_row = get_project_by_id(df, current_work_id)
    if not project_row:
        st.error(f"No project found for this Work ID: '{current_work_id}'.")
        return

    dossier = build_investigation_dossier(project_row)

    # 3. TOP: PROJECT INVESTIGATION HEADER (Work ID, Risk Level badge, Risk Score)
    render_project_summary_header(
        work_id=dossier["work_id"],
        state=dossier["state"],
        constituency=dossier["constituency"],
        mp=dossier["mp"],
        category=dossier["category"],
        risk_level=dossier["risk_level"],
        anomaly_score=dossier["anomaly_score"],
        priority_label=dossier["priority_label"]
    )

    # 4. WHY WAS THIS FLAGGED? (PROMINENT SECTION)
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #DC2626; border-radius: 4px; padding: 0.9rem 1.1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 0.88rem; font-weight: 700; color: #991B1B; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.4rem;">
            ⚠ Why Was This Flagged? &bull; Primary Operational Deviations
        </div>
    """, unsafe_allow_html=True)

    if dossier["explanation_bullets"]:
        for bullet in dossier["explanation_bullets"]:
            if "Standard Pattern" in bullet:
                render_audit_alert("Standard Pattern", bullet, level="info")
            elif "Potential Over-Disbursement" in bullet or "Timeline Discrepancy" in bullet or "Chronology Reversal" in bullet:
                render_audit_alert("Critical Risk Indicator", bullet, level="danger")
            else:
                render_audit_alert("Operational Variance", bullet, level="warning")
    else:
        render_audit_alert("Information", "No adverse operational signals detected.", level="info")

    st.markdown("</div>", unsafe_allow_html=True)

    # 5. RECOMMENDED INVESTIGATION (ACTIONABLE AUDIT PROTOCOL)
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #2563EB; border-radius: 4px; padding: 0.9rem 1.1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 0.88rem; font-weight: 700; color: #1E3A8A; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.35rem;">
            Recommended Investigation Action Plan
        </div>
        <div style="font-size: 0.8rem; color: #475569; margin-bottom: 0.6rem;">
            Procedural checklist for conducting an administrative field audit and reconciliation:
        </div>
    """, unsafe_allow_html=True)

    # Core required recommendation items
    rec_steps = [
        "Verify sanction order against approved schedule of rates and administrative approval file.",
        "Verify payment records and treasury release vouchers for each disbursed installment.",
        "Check whether revised sanction exists or if offline approval was granted by district authorities."
    ]
    # Add any dossier-specific steps
    for act in dossier["recommended_actions"]:
        if act not in rec_steps:
            rec_steps.append(act)

    for i, step in enumerate(rec_steps[:4], 1):
        st.markdown(f"<div style='font-size: 0.85rem; color: #1E293B; margin-bottom: 5px;'><strong>{i}.</strong> {step}</div>", unsafe_allow_html=True)

    st.caption("Responsible AI Note: Anomaly screening flags operational variance requiring investigation; it does not constitute confirmed fraud.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 6. RISK ASSESSMENT & ADMINISTRATIVE METADATA
    with st.container():
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.9rem 1.1rem; margin-bottom: 1rem;">
            <div style="font-size: 0.88rem; font-weight: 700; color: #0F2B48; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.5rem; border-bottom: 1px solid #F1F5F9; padding-bottom: 0.3rem;">
                Risk Assessment & Administrative Metadata
            </div>
        """, unsafe_allow_html=True)
        m_c1, m_c2, m_c3 = st.columns(3)
        with m_c1:
            st.markdown(f"**Work ID:** `{dossier['work_id']}`")
            st.markdown(f"**Work Category:** {dossier['category']}")
            st.markdown(f"**Work Status:** {dossier['work_status']}")
        with m_c2:
            st.markdown(f"**State / UT:** {dossier['state']}")
            st.markdown(f"**Constituency:** {dossier['constituency']}")
            st.markdown(f"**Hon'ble MP:** {dossier['mp']}")
        with m_c3:
            st.markdown(f"**Implementing District Authority (IDA):**<br><span style='font-size:0.86rem; color:#334155;'>{dossier['ida']}</span>", unsafe_allow_html=True)
            
        st.markdown(f"**Work Description:**<br><span style='color:#475569; font-size:0.86rem;'>{dossier['description']}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 7. FINANCIAL ANALYSIS & PAYMENT ANALYSIS (TWO COLUMNS)
    f_col, p_col = st.columns(2)

    with f_col:
        st.markdown("""
        <div class="gov-panel">
            <div class="gov-panel-header">
                <span class="gov-panel-title">Financial Analysis</span>
                <span class="gov-panel-subtitle">Expenditure Compliance</span>
            </div>
        """, unsafe_allow_html=True)
        fin = dossier["financials"]

        for alert in fin["alerts"]:
            render_audit_alert(alert["tag"], alert["message"], level=alert["type"])

        rec_str = format_inr(fin["recommended_amt"])
        sanc_str = format_inr(fin["sanction_amt"])
        disb_str = format_inr(fin["total_disbursed"])
        diff_str = format_inr(fin["disb_sanct_diff"])
        
        st.markdown(f"""
        | Financial Parameter | Recorded Value | Compliance Note |
        | :--- | :--- | :--- |
        | **Recommended Amount** | {rec_str} | Proposed by MP |
        | **Sanctioned Amount** | {sanc_str} | Approved by Authority |
        | **Total Disbursed** | {disb_str} | Cumulative releases |
        | **Disbursement Variance** | {diff_str} | {'Excess expenditure' if fin['disb_sanct_diff'] > 1000 else 'Within approved sanction'} |
        | **Disbursement / Sanction Ratio** | {fin['disb_sanct_ratio']:.2f}x | Ratio of releases to approval |
        """)

        if pd.notna(fin["allocated_macro"]):
            st.caption(
                f"**Macro Constituency Allocation:** {format_inr(fin['allocated_macro'])} "
                "(Macro entitlement; strictly excluded from ML risk scoring)."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with p_col:
        st.markdown("""
        <div class="gov-panel">
            <div class="gov-panel-header">
                <span class="gov-panel-title">Payment Analysis</span>
                <span class="gov-panel-subtitle">Installment Tranches</span>
            </div>
        """, unsafe_allow_html=True)
        pmts = dossier["payments"]

        for alert in pmts["alerts"]:
            render_audit_alert(alert["tag"], alert["message"], level=alert["type"])

        st.markdown(f"""
        | Parameter | Recorded Status | Audit Baseline |
        | :--- | :--- | :--- |
        | **Installment Count** | **{format_count(pmts['number_of_payments'])}** payment tranches | 95% of works have &le; 2 tranches |
        | **Payment Data Availability** | {'Recorded' if pmts['has_payment_data'] else 'Not Recorded'} | Required for tranche audit |
        """)

        if pmts["number_of_payments"] > 2:
            st.warning(
                f"High installment frequency: This project utilized {pmts['number_of_payments']} separate payment releases. "
                "Auditors should confirm whether works were legitimately phased or split to bypass administrative limits."
            )
        else:
            st.success("Payment installment frequency is consistent with standard single-work implementation.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 8. TIMELINE ANALYSIS & ADMINISTRATIVE DATA (TWO COLUMNS)
    t_col, a_col = st.columns(2)

    with t_col:
        st.markdown("""
        <div class="gov-panel">
            <div class="gov-panel-header">
                <span class="gov-panel-title">Timeline Analysis</span>
                <span class="gov-panel-subtitle">Lifecycle Chronology</span>
            </div>
        """, unsafe_allow_html=True)
        tl = dossier["timeline"]

        for alert in tl["alerts"]:
            render_audit_alert(alert["tag"], alert["message"], level=alert["type"])

        rec_d = format_date_str(tl["rec_date"])
        sanc_d = format_date_str(tl["sanct_date"])
        comp_d = format_date_str(tl["comp_date"])

        rec_sanc_days = f"{int(tl['rec_sanct_days']):,} days" if pd.notna(tl['rec_sanct_days']) and tl['rec_sanct_days'] > 0 else "N/A"
        sanc_comp_days = f"{int(tl['sanct_comp_days']):,} days" if pd.notna(tl['sanct_comp_days']) and tl['sanct_comp_days'] > 0 else "N/A"

        st.markdown(f"""
        | Milestone | Recorded Date | Benchmark Duration |
        | :--- | :--- | :--- |
        | **MP Recommendation** | {rec_d} | Initial work proposal |
        | **Administrative Sanction** | {sanc_d} | {rec_sanc_days} from proposal |
        | **Work Completion** | {comp_d} | {sanc_comp_days} from sanction |
        """)
        st.markdown("</div>", unsafe_allow_html=True)

    with a_col:
        st.markdown("""
        <div class="gov-panel">
            <div class="gov-panel-header">
                <span class="gov-panel-title">Administrative Data</span>
                <span class="gov-panel-subtitle">Milestone Verification</span>
            </div>
        """, unsafe_allow_html=True)
        st_c1, st_c2 = st.columns(2)
        stages = dossier["admin_stages"]
        
        with st_c1:
            render_stage_indicator("MP Recommendation", stages["Has Recommendation"], "Proposal stage")
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            render_stage_indicator("Administrative Sanction", stages["Has Administrative Sanction"], "Approval order")
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            render_stage_indicator("Completion Record", stages["Has Completion Record"], "Certificate")
            
        with st_c2:
            render_stage_indicator("Disbursement Record", stages["Has Disbursement Record"], "Treasury release")
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            render_stage_indicator("Payment Data Ledger", stages["Has Payment Installment Data"], "Tranche ledger")
        st.markdown("</div>", unsafe_allow_html=True)
