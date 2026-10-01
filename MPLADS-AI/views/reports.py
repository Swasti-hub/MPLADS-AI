"""
views/reports.py
----------------
Reporting and export center for the MPLADS AI Platform.
Organized into 4 clean enterprise report sections:
  1. High Risk Report (Complete register of High-Risk works)
  2. Anomaly Report (All projects flagged as statistical anomalies)
  3. Filtered Results & State Summary Report
  4. Project Investigation Report (Printable single-case audit memorandum)
"""

import io
import streamlit as st
import pandas as pd

from services.data_service import load_master_data, load_anomaly_summary
from services.investigation_service import get_project_by_id, build_investigation_dossier
from components.cards import render_header, render_important_notice
from utils.formatting import format_inr, format_date_str, format_count


def generate_project_text_memo(dossier: dict) -> str:
    """Generates an official formatted plain-text investigation brief for an individual case."""
    lines = []
    lines.append("================================================================================")
    lines.append("           MPLADS PROJECT AUDIT BRIEF & CASE INVESTIGATION DOSSIER")
    lines.append("           CONFIDENTIAL / FOR OFFICIAL INVESTIGATION ONLY")
    lines.append("================================================================================")
    lines.append(f"GENERATED DATE : {pd.Timestamp.now().strftime('%d-%b-%Y %H:%M:%S')}")
    lines.append(f"WORK ID        : {dossier['work_id']}")
    lines.append(f"STATE / UT     : {dossier['state']}")
    lines.append(f"CONSTITUENCY   : {dossier['constituency']}")
    lines.append(f"HON'BLE MP     : {dossier['mp']}")
    lines.append(f"WORK CATEGORY  : {dossier['category']}")
    lines.append(f"WORK STATUS    : {dossier['work_status']}")
    lines.append(f"IDA            : {dossier['ida']}")
    lines.append("--------------------------------------------------------------------------------")
    lines.append(f"WORK DESCRIPTION:\n{dossier['description']}")
    lines.append("--------------------------------------------------------------------------------")
    lines.append("1. AI RISK ASSESSMENT")
    lines.append(f"   - Risk Classification : {dossier['risk_level']} Risk")
    lines.append(f"   - Anomaly Score       : {dossier['anomaly_score']:.4f} (Calibrated [0.0, 1.0])")
    lines.append(f"   - Audit Priority      : {dossier['priority_label']}")
    lines.append("--------------------------------------------------------------------------------")
    lines.append("2. FINANCIAL BREAKDOWN")
    fin = dossier['financials']
    lines.append(f"   - Recommended Amount  : {format_inr(fin['recommended_amt'])}")
    lines.append(f"   - Sanctioned Amount   : {format_inr(fin['sanction_amt'])}")
    lines.append(f"   - Total Disbursed     : {format_inr(fin['total_disbursed'])}")
    lines.append(f"   - Variance (Disb-Sanc): {format_inr(fin['disb_sanct_diff'])}")
    lines.append(f"   - Disb/Sanc Ratio     : {fin['disb_sanct_ratio']:.2f}x")
    if fin['alerts']:
        for al in fin['alerts']:
            lines.append(f"   [!] ALERT: {al['tag']} - {al['message']}")
    lines.append("--------------------------------------------------------------------------------")
    lines.append("3. PAYMENT & LIFECYCLE TIMELINE")
    pmts = dossier['payments']
    tl = dossier['timeline']
    lines.append(f"   - Payment Tranches    : {pmts['number_of_payments']} installments")
    lines.append(f"   - MP Recommendation   : {format_date_str(tl['rec_date'])}")
    lines.append(f"   - Admin Sanction Date : {format_date_str(tl['sanct_date'])}")
    lines.append(f"   - Completion Date     : {format_date_str(tl['comp_date'])}")
    if tl['alerts']:
        for al in tl['alerts']:
            lines.append(f"   [!] TIMELINE ALERT: {al['tag']} - {al['message']}")
    lines.append("--------------------------------------------------------------------------------")
    lines.append("4. AUDIT SIGNALS & WHY FLAGGED")
    for b in dossier['explanation_bullets']:
        lines.append(f"   * {b}")
    lines.append("--------------------------------------------------------------------------------")
    lines.append("5. RECOMMENDED PROCEDURAL ACTIONS FOR AUDIT OFFICERS")
    for i, act in enumerate(dossier['recommended_actions'], 1):
        lines.append(f"   {i}. {act}")
    lines.append("================================================================================")
    lines.append("DISCLAIMER: AI-assisted preliminary screening. Does not constitute legal evidence")
    lines.append("or confirmed fraud. Verification must be executed through primary physical records.")
    lines.append("================================================================================")
    return "\n".join(lines)


def render_reports():
    """Renders the comprehensive reports and download center."""
    
    # Header
    render_header(
        title="Reports & Audit Export Center",
        subtitle="Official Verification Dockets & Investigation Briefs",
        tagline="Generate and export structured verification dockets, anomaly registers, and case briefs",
        show_status=True
    )

    # Advisory Notice
    render_important_notice(
        title="Audit Dossier Protocol",
        text="Official reports generated by this platform are structured for administrative field audits. All figures reflect verified portal records."
    )

    df = load_master_data()
    summary_df = load_anomaly_summary()

    # Section 1: System-Wide Audit Registers (High Risk, Anomaly, Filtered/Summary)
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.2rem;">
            Official Audit Registers & Summary Reports
        </div>
        <div style="font-size: 0.78rem; color: #64748B; margin-bottom: 0.75rem;">
            Download structured datasets formatted for spreadsheets and audit reporting:
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**1. High Risk Report**")
        st.caption("Complete register of all 1,727 High-Risk works sorted by risk score.")
        high_risk_df = df[df["risk_level"] == "High"].sort_values(by="anomaly_score", ascending=False)
        csv_high = high_risk_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download High Risk Report (CSV)",
            data=csv_high,
            file_name="mplads_high_risk_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    with c2:
        st.markdown("**2. Anomaly Report**")
        st.caption("All 1,719 works flagged as statistical anomalies by Isolation Forest.")
        anom_df = df[df["anomaly_flag"] == 1].sort_values(by="anomaly_score", ascending=False)
        csv_anom = anom_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Anomaly Report (CSV)",
            data=csv_anom,
            file_name="mplads_anomaly_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    with c3:
        st.markdown("**3. Filtered Results & State Summary**")
        st.caption("Aggregated risk counts, exposure, and mean scores across states.")
        csv_sum = summary_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Summary Report (CSV)",
            data=csv_sum,
            file_name="mplads_state_summary_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Section 2: Case Investigation Report (Single Project Export)
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.2rem;">
            4. Project Investigation Report (Single Case Brief)
        </div>
        <div style="font-size: 0.78rem; color: #64748B; margin-bottom: 0.75rem;">
            Generate an official, printable investigation memorandum for physical field audits:
        </div>
    """, unsafe_allow_html=True)

    work_ids = df[df["risk_level"] == "High"]["Work ID"].dropna().unique().tolist()
    
    col_sel, col_btn = st.columns([3, 1.2])
    with col_sel:
        selected_id = st.selectbox(
            "Select Project for Formal Audit Memo:",
            options=work_ids,
            index=0,
            help="Choose a High Risk Work ID to generate a printable case brief",
            label_visibility="collapsed"
        )

    project_row = get_project_by_id(df, selected_id)
    dossier = build_investigation_dossier(project_row)
    memo_text = generate_project_text_memo(dossier)

    with col_btn:
        st.download_button(
            "Download Audit Memo (.TXT)",
            data=memo_text.encode("utf-8"),
            file_name=f"MPLADS_Investigation_Memo_{selected_id.replace('/', '_')}.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True
        )

    with st.expander("Preview Official Investigation Memo", expanded=True):
        st.text(memo_text)
        
    st.markdown("</div>", unsafe_allow_html=True)
