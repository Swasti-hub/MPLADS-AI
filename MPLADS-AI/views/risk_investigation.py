"""
views/risk_investigation.py
---------------------------
Core investigation workspace for vigilance and audit officers.
Features:
  1. Header & Responsible AI Notice
  2. Prominent Search Project by Work ID field (placeholder WS/MP18227/2024-2025/148775)
  3. Multi-parameter filtering across geography, risk tiers, categories,
     and operational anomaly reasons with fast case dossier lookup.
"""

import streamlit as st
import pandas as pd

from services.data_service import load_master_data, filter_projects, find_project_by_work_id
from components.cards import render_header, render_important_notice
from components.tables import render_project_roster_table
from utils.formatting import format_count, normalize_work_id


def render_risk_investigation():
    """Renders the comprehensive project screening and filter workbench."""
    
    # Header
    render_header(
        title="Risk Investigation Workspace",
        subtitle="Multi-Parameter Screening & Case Triage",
        tagline="Filter, triage, and inspect flagged MPLADS works across operational parameters",
        show_status=True
    )

    # Advisory Notice
    render_important_notice(
        title="Administrative Verification Protocol",
        text="Filtered results are prioritized by AI-computed anomaly scores. All findings must be corroborated with primary sanction orders and payment vouchers."
    )

    df = load_master_data()

    # 1. DEDICATED PROMINENT WORK ID SEARCH SECTION
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-bottom: 0.85rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 0.88rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.4rem;">
            Search Project by Work ID
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("work_id_direct_search_form", clear_on_submit=False):
        col_input, col_btn = st.columns([3.5, 1.2])
        with col_input:
            work_id_query = st.text_input(
                "Search Project by Work ID",
                placeholder="WS/MP18227/2024-2025/148775",
                key="risk_inv_work_id_input",
                label_visibility="collapsed"
            )
        with col_btn:
            search_clicked = st.form_submit_button(
                "Search & Investigate →",
                type="primary",
                use_container_width=True
            )

        if search_clicked:
            clean_query = work_id_query.strip() if work_id_query else ""
            if not clean_query:
                st.warning("Please enter a Work ID to search.")
            else:
                record, count, msg = find_project_by_work_id(df, clean_query)
                if count >= 1:
                    st.session_state["selected_work_id"] = record["Work ID"]
                    st.session_state["current_page"] = "Project Details"
                    st.rerun()
                else:
                    st.error("No project found for this Work ID.")

    st.markdown("</div>", unsafe_allow_html=True)

    # 2. MULTI-PARAMETER FILTERING PANEL
    with st.expander("Audit Filter Controls & Screening Criteria", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)

        with f_col1:
            risk_options = ["High", "Medium", "Low"]
            selected_risks = st.multiselect(
                "Risk Classification",
                options=risk_options,
                default=["High"],
                help="Filter by AI calibrated risk tier"
            )

        with f_col2:
            state_options = sorted(df["State"].dropna().unique().tolist())
            selected_states = st.multiselect(
                "State / UT",
                options=state_options,
                default=[],
                placeholder="All States / UTs"
            )

        with f_col3:
            if selected_states:
                const_options = sorted(df[df["State"].isin(selected_states)]["Constituency"].dropna().unique().tolist())
            else:
                const_options = sorted(df["Constituency"].dropna().unique().tolist())
            selected_const = st.multiselect(
                "Constituency",
                options=const_options,
                default=[],
                placeholder="All Constituencies"
            )

        with f_col4:
            cat_options = sorted(df["Work Category"].dropna().unique().tolist())
            selected_cats = st.multiselect(
                "Work Category",
                options=cat_options,
                default=[],
                placeholder="All Categories"
            )

        # Row 2 Filters: Anomaly Reason & Score Slider
        f_row2_1, f_row2_2, f_row2_3 = st.columns([1.5, 1.5, 1])

        with f_row2_1:
            anomaly_reasons = [
                "All",
                "Potential Over-Disbursement",
                "Unusual Payment Pattern",
                "Timeline Issue",
                "Missing Administrative Information",
                "Multivariate Statistical Anomaly"
            ]
            selected_reason = st.selectbox(
                "Specific Anomaly Finding",
                options=anomaly_reasons,
                index=0,
                help="Filter specifically for projects exhibiting this operational deviation"
            )

        with f_row2_2:
            score_range = st.slider(
                "Anomaly Score Range (0.00 = Normal, 1.00 = Highest Deviation)",
                min_value=0.0,
                max_value=1.0,
                value=(0.0, 1.0),
                step=0.01
            )

        with f_row2_3:
            search_query = st.text_input(
                "Keyword Search",
                placeholder="Description, MP, or Authority...",
                help="Search within filtered results by text"
            )

    # Apply filters
    filtered_df = filter_projects(
        df,
        risk_levels=selected_risks if selected_risks else None,
        states=selected_states if selected_states else None,
        constituencies=selected_const if selected_const else None,
        work_categories=selected_cats if selected_cats else None,
        min_score=score_range[0],
        max_score=score_range[1],
        search_query=search_query,
        anomaly_reason=selected_reason
    )

    # Sort descending by anomaly score
    filtered_df = filtered_df.sort_values(by="anomaly_score", ascending=False)

    # Quick Summary Bar
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.6rem 0.9rem; margin-bottom: 0.85rem;">
    """, unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Matching Projects", format_count(len(filtered_df)))
    with m2:
        high_cnt = int((filtered_df["risk_level"] == "High").sum())
        st.metric("High Risk Matches", format_count(high_cnt))
    with m3:
        med_cnt = int((filtered_df["risk_level"] == "Medium").sum())
        st.metric("Medium Risk Matches", format_count(med_cnt))
    with m4:
        tot_disb = float(filtered_df["Total_Disbursed"].fillna(0).sum())
        from utils.formatting import format_inr
        st.metric("Cumulative Disbursed", format_inr(tot_disb, compact=True))
    st.markdown("</div>", unsafe_allow_html=True)

    # Render interactive project table with direct investigation selector
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem;">
        <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.4rem;">
            Filtered Project Roster
        </div>
    """, unsafe_allow_html=True)
    render_project_roster_table(
        filtered_df,
        key_prefix="investigation_main",
        page_size=20,
        show_investigation_picker=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
