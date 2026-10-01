"""
views/command_center.py
-----------------------
Executive Command Center for the MPLADS AI Risk Monitoring Platform.
Structured for high-authority government oversight:
  1. Header: "MPLADS AI" & "AI-Assisted Anomaly & Risk Monitoring System" with Operational Status
  2. Notice: Responsible AI Risk Screening Advisory
  3. KPI Row: 6 left-accented cards (34,450 genuine projects, 1,727 High, 3,442 Med, 29,281 Low, 1,719 Anomalies, Total Disbursed)
  4. Work ID Search Bar (prominent quick lookup)
  5. 3-Column Analytics Row (Equal height):
       LEFT: Risk Level Distribution (Donut)
       CENTER: Anomaly Root Cause Classification (Horizontal Bar)
       RIGHT: State-wise Risk Overview (Top Jurisdictions)
  6. Priority Investigations:
       Heading: Priority Investigations
       Subtitle: Projects requiring additional review based on AI-assisted anomaly screening.
       Compact table with "View / Investigate" action
  7. Analyze New MPLADS Data Section with instant upload and demo batch
"""

import streamlit as st
import pandas as pd

from services.data_service import (
    load_master_data,
    get_dataset_kpis,
    get_anomaly_category_counts,
    get_demo_batch,
    find_project_by_work_id
)
from components.cards import render_header, render_important_notice, render_kpi_card
from components.charts import (
    plot_risk_donut,
    plot_anomaly_categories,
    plot_state_risk_overview_compact
)
from components.tables import render_project_roster_table
from utils.formatting import format_inr, format_count


def render_command_center():
    """Renders the executive government risk monitoring dashboard."""
    
    # 1. Executive Government Header
    render_header(
        title="MPLADS AI",
        subtitle="AI-Assisted Anomaly & Risk Monitoring System",
        tagline="Monitor implementation • Detect anomalies • Enable investigation",
        show_status=True,
        bg_image=True
    )

    # 2. Responsible AI Important Notice
    render_important_notice(
        title="AI-Assisted Risk Screening",
        text="Anomaly flags indicate potential operational deviations requiring verification. Final administrative verification remains with authorized officials."
    )

    # Load master verified dataset
    df = load_master_data()
    kpis = get_dataset_kpis(df)

    # 3. Compact Operational KPIs Row (6 left-accented cards)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_kpi_card(
            "Total Projects",
            format_count(kpis["total_projects"]),
            "Validated records",
            card_type="neutral"
        )
    with c2:
        render_kpi_card(
            "High Risk",
            format_count(kpis["high_risk_count"]),
            f"{kpis['high_risk_pct']:.2f}% of universe",
            card_type="high-risk"
        )
    with c3:
        render_kpi_card(
            "Medium Risk",
            format_count(kpis["med_risk_count"]),
            f"{kpis['med_risk_pct']:.2f}% of universe",
            card_type="medium-risk"
        )
    with c4:
        render_kpi_card(
            "Low Risk",
            format_count(kpis["low_risk_count"]),
            f"{kpis['low_risk_pct']:.2f}% of universe",
            card_type="low-risk"
        )
    with c5:
        render_kpi_card(
            "Flagged Anomalies",
            format_count(kpis["anomalies_count"]),
            f"{kpis['anomalies_pct']:.2f}% outliers",
            card_type="high-risk"
        )
    with c6:
        render_kpi_card(
            "Total Disbursed",
            format_inr(kpis["total_disbursed"], compact=True),
            "Recorded releases",
            card_type="general"
        )

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # 4. Prominent Work ID Quick Search Bar
    with st.container():
        with st.form("cc_work_id_search_form", clear_on_submit=False):
            col_lbl, col_input, col_btn = st.columns([1.2, 3.2, 1.2])
            with col_lbl:
                st.markdown(
                    "<div style='padding-top:6px; font-weight:700; font-size:0.86rem; color:#0F2B48;'>Search Project by Work ID</div>",
                    unsafe_allow_html=True
                )
            with col_input:
                work_id_query = st.text_input(
                    "Search Project by Work ID",
                    placeholder="WS/MP18227/2024-2025/148775",
                    key="cc_work_id_input",
                    label_visibility="collapsed"
                )
            with col_btn:
                search_clicked = st.form_submit_button(
                    "Search Project →",
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

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # 5. Three-Column Balanced Analytics Row (Equal-Height Containers)
    # LEFT: Risk Level Distribution | CENTER: Anomaly Root Cause | RIGHT: State-wise Risk Overview
    col_donut, col_cat, col_state = st.columns([1, 1.15, 1.15])

    with col_donut:
        st.markdown("""
        <div class="gov-panel">
            <div class="gov-panel-header">
                <span class="gov-panel-title">Risk Level Distribution</span>
                <span class="gov-panel-subtitle">Calibrated</span>
            </div>
        """, unsafe_allow_html=True)
        fig_donut = plot_risk_donut(
            high=kpis["high_risk_count"],
            medium=kpis["med_risk_count"],
            low=kpis["low_risk_count"]
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_cat:
        st.markdown("""
        <div class="gov-panel">
            <div class="gov-panel-header">
                <span class="gov-panel-title">Anomaly Root Cause</span>
                <span class="gov-panel-subtitle">Root signals</span>
            </div>
        """, unsafe_allow_html=True)
        cat_counts = get_anomaly_category_counts(df)
        fig_cat = plot_anomaly_categories(cat_counts)
        st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_state:
        st.markdown("""
        <div class="gov-panel">
            <div class="gov-panel-header">
                <span class="gov-panel-title">State-wise Risk Overview</span>
                <span class="gov-panel-subtitle">Top jurisdictions</span>
            </div>
        """, unsafe_allow_html=True)
        fig_state_compact = plot_state_risk_overview_compact(df, top_n=7)
        st.plotly_chart(fig_state_compact, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # 6. Priority Investigations Section
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid #F1F5F9; padding-bottom: 0.4rem; margin-bottom: 0.5rem;">
            <div>
                <span style="color: #0F2B48; font-size: 1.05rem; font-weight: 700;">Priority Investigations</span>
                <div style="color: #64748B; font-size: 0.78rem; margin-top: 1px;">Projects requiring additional review based on AI-assisted anomaly screening.</div>
            </div>
            <span style="font-size: 0.76rem; color: #DC2626; font-weight: 700; background: #FEF2F2; padding: 2px 8px; border-radius: 3px; border: 1px solid #FECACA;">High-Risk Priority</span>
        </div>
    """, unsafe_allow_html=True)

    top_high_risk = df[df["risk_level"] == "High"].sort_values(by="anomaly_score", ascending=False).head(20)
    render_project_roster_table(
        top_high_risk,
        key_prefix="cc_top_priority",
        page_size=10,
        show_investigation_picker=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # 7. Analyze New MPLADS Data Section with Upload & Demo Batch
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid #F1F5F9; padding-bottom: 0.4rem; margin-bottom: 0.5rem;">
            <div>
                <span style="color: #0F2B48; font-size: 1.05rem; font-weight: 700;">Analyze New MPLADS Data</span>
                <div style="color: #64748B; font-size: 0.78rem; margin-top: 1px;">Upload new or updated project records to screen them against the trained risk baseline.</div>
            </div>
            <span style="font-size: 0.76rem; color: #2563EB; font-weight: 700; background: #EFF6FF; padding: 2px 8px; border-radius: 3px; border: 1px solid #BFDBFE;">Inference Pipeline</span>
        </div>
    """, unsafe_allow_html=True)

    col_up_box, col_demo_btn = st.columns([3, 1.2])

    with col_up_box:
        cc_uploaded_file = st.file_uploader(
            "Upload Project Records for Instant Screening",
            type=["csv", "xlsx", "xls"],
            key="cc_uploader",
            label_visibility="collapsed"
        )

    with col_demo_btn:
        st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)
        if st.button("Load Demo Batch (50 Works) →", key="cc_quick_demo_btn", type="secondary", use_container_width=True):
            st.session_state["demo_batch_df"] = get_demo_batch(df, n_samples=50)
            st.session_state["current_page"] = "Analyze New Data"
            st.rerun()

    if cc_uploaded_file is not None:
        try:
            if cc_uploaded_file.name.lower().endswith((".xlsx", ".xls")):
                new_df = pd.read_excel(cc_uploaded_file)
            else:
                new_df = pd.read_csv(cc_uploaded_file, low_memory=False)
                
            st.session_state["demo_batch_df"] = new_df
            st.session_state["current_page"] = "Analyze New Data"
            st.success(f"✓ Received {len(new_df):,} records from {cc_uploaded_file.name}. Opening Analysis Workspace...")
            st.rerun()
        except Exception as e:
            st.error(f"Error parsing uploaded file: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)
