"""
views/analyze_new_data.py
-------------------------
Operational inference hub for scoring newly received or unlabelled MPLADS project batches.
Applies the deployed Isolation Forest model and learned operational pre-processing
artifacts (medians, frequency encoders, empirical percentiles) without retraining.
Features the 4-step workflow indicator: 01 Upload → 02 Validate → 03 Analyze → 04 Risk Assessment.
"""

import io
import streamlit as st
import pandas as pd

from services.data_service import load_master_data, get_demo_batch
from services.prediction_service import validate_uploaded_data, score_new_dataset
from components.cards import render_header, render_important_notice, render_kpi_card, render_audit_alert
from components.charts import plot_risk_donut
from components.tables import render_project_roster_table
from utils.formatting import format_count


def render_analyze_new_data():
    """Renders the end-to-end inference page for scoring new project submissions."""
    
    # 1. Header
    render_header(
        title="Analyze New MPLADS Data",
        subtitle="Operational Inference Pipeline & Risk Screening",
        tagline="Upload new or updated project records to screen them against the trained risk baseline.",
        show_status=True
    )

    # 2. Responsible AI Notice
    render_important_notice(
        title="Operational Baseline Screening",
        text="New submissions are evaluated against the verified historical baseline of 34,450 genuine projects. The model scores records without automatic retraining."
    )

    # 3. Flow Indicator Banner: 01 Upload → 02 Validate → 03 Analyze → 04 Risk Assessment
    st.markdown("""
    <div class="workflow-bar">
        <div class="workflow-step">
            <span class="workflow-step-num" style="background:#0F2B48; color:#FFFFFF; padding:2px 6px; border-radius:3px;">01</span>
            <span style="color:#0F2B48; font-weight:700;">Upload Data</span>
        </div>
        <div class="workflow-arrow">&rarr;</div>
        <div class="workflow-step">
            <span class="workflow-step-num" style="background:#0F2B48; color:#FFFFFF; padding:2px 6px; border-radius:3px;">02</span>
            <span style="color:#0F2B48; font-weight:700;">Validate Schema</span>
        </div>
        <div class="workflow-arrow">&rarr;</div>
        <div class="workflow-step">
            <span class="workflow-step-num" style="background:#0F2B48; color:#FFFFFF; padding:2px 6px; border-radius:3px;">03</span>
            <span style="color:#0F2B48; font-weight:700;">Analyze Features</span>
        </div>
        <div class="workflow-arrow">&rarr;</div>
        <div class="workflow-step">
            <span class="workflow-step-num" style="background:#0F2B48; color:#FFFFFF; padding:2px 6px; border-radius:3px;">04</span>
            <span style="color:#0F2B48; font-weight:700;">Risk Assessment</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_master = load_master_data()

    # 4. Large Professional Upload Area
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 1rem 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.25rem;">
            Step 1: Upload Project Records
        </div>
        <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 0.75rem;">
            Select a CSV or Excel file containing newly sanctioned or updated project records.
        </div>
    """, unsafe_allow_html=True)

    col_up, col_demo = st.columns([2.8, 1.2])

    uploaded_df = None
    source_label = ""

    with col_up:
        uploaded_file = st.file_uploader(
            "Upload Project Records (.CSV or .XLSX)",
            type=["csv", "xlsx", "xls"],
            help="Upload raw MPLADS project records matching portal export schema",
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            source_label = f"Uploaded File: {uploaded_file.name}"
            try:
                if uploaded_file.name.lower().endswith((".xlsx", ".xls")):
                    uploaded_df = pd.read_excel(uploaded_file)
                else:
                    uploaded_df = pd.read_csv(uploaded_file, low_memory=False)
            except Exception as e:
                st.error(f"Error reading uploaded file: {str(e)}")
                st.markdown("</div>", unsafe_allow_html=True)
                return

    with col_demo:
        st.markdown("<div style='font-size:0.8rem; font-weight:600; color:#334155; margin-bottom:4px;'>Quick Demonstration:</div>", unsafe_allow_html=True)
        if st.button("Load Demo Batch (50 Records)", type="secondary", use_container_width=True):
            demo_data = get_demo_batch(df_master, n_samples=50)
            st.session_state["demo_batch_df"] = demo_data
            st.session_state["scored_results_df"] = None
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Check if demo batch was activated
    if uploaded_df is None and "demo_batch_df" in st.session_state and st.session_state["demo_batch_df"] is not None:
        uploaded_df = st.session_state["demo_batch_df"]
        source_label = "Demo Batch (50 Unscored Sample Project Records)"

    if uploaded_df is None:
        st.info("Upload a CSV/Excel file above or click 'Load Demo Batch' to evaluate projects.")
        
        # Download Sample Template Helper
        sample_template = get_demo_batch(df_master, n_samples=5)
        csv_template = sample_template.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Blank / Sample CSV Schema Template",
            data=csv_template,
            file_name="mplads_input_template.csv",
            mime="text/csv"
        )
        return

    st.success(f"✓ Records received: **{len(uploaded_df):,} rows** ({source_label})")

    # Step 2: Schema Validation
    is_valid, val_msg, val_details = validate_uploaded_data(uploaded_df)
    if not is_valid:
        st.error(f"Schema Validation Failed: {val_msg}")
        if val_details.get("missing_key_cols"):
            st.warning(f"Missing Essential Columns: {', '.join(val_details['missing_key_cols'])}")
        return

    # Trigger Scoring Button
    col_run, col_note = st.columns([1.5, 2.5])
    with col_run:
        run_screening = st.button("Execute Risk Screening with Deployed Model →", type="primary", use_container_width=True)
    with col_note:
        st.caption("Applies 20 operational features, learned training imputation medians, and Isolation Forest scoring.")

    if run_screening:
        with st.spinner("Executing feature transformation and Isolation Forest scoring..."):
            try:
                scored_df, summary = score_new_dataset(uploaded_df, col_mapping=val_details.get("col_mapping"))
                st.session_state["scored_results_df"] = scored_df
                st.session_state["scored_summary"] = summary
                st.success("✓ Risk screening successfully completed!")
            except Exception as ex:
                st.error(f"Inference error: {str(ex)}")
                return

    # Display Scored Results
    if "scored_results_df" in st.session_state and st.session_state["scored_results_df"] is not None:
        scored_df = st.session_state["scored_results_df"]
        summary = st.session_state["scored_summary"]

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # 5 Required KPI Cards: Projects Processed, High Risk, Medium Risk, Low Risk, Anomalies
        r1, r2, r3, r4, r5 = st.columns(5)
        with r1:
            render_kpi_card(
                "Projects Processed",
                format_count(summary["processed_count"]),
                "Batch size",
                card_type="neutral"
            )
        with r2:
            render_kpi_card(
                "High Risk",
                format_count(summary["high_risk_count"]),
                f"{summary['high_risk_pct']:.1f}% of batch",
                card_type="high-risk"
            )
        with r3:
            render_kpi_card(
                "Medium Risk",
                format_count(summary["medium_risk_count"]),
                f"{summary['medium_risk_pct']:.1f}% of batch",
                card_type="medium-risk"
            )
        with r4:
            render_kpi_card(
                "Low Risk",
                format_count(summary["low_risk_count"]),
                f"{summary['low_risk_pct']:.1f}% of batch",
                card_type="low-risk"
            )
        with r5:
            render_kpi_card(
                "Anomalies",
                format_count(summary["anomalies_flagged"]),
                f"{summary['anomalies_pct']:.1f}% outliers",
                card_type="high-risk"
            )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Visual Donut + Export
        col_chart, col_dl = st.columns([1.2, 1.8])
        with col_chart:
            st.markdown("""
            <div class="gov-panel">
                <div class="gov-panel-header">
                    <span class="gov-panel-title">Batch Risk Distribution</span>
                </div>
            """, unsafe_allow_html=True)
            fig_donut = plot_risk_donut(
                high=summary["high_risk_count"],
                medium=summary["medium_risk_count"],
                low=summary["low_risk_count"]
            )
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with col_dl:
            st.markdown("""
            <div class="gov-panel">
                <div class="gov-panel-header">
                    <span class="gov-panel-title">Export Screened Results</span>
                </div>
                <div style="font-size:0.82rem; color:#475569; margin-bottom:0.75rem;">
                    Download the screened batch with newly computed anomaly scores, risk levels, and audit findings:
                </div>
            """, unsafe_allow_html=True)
            csv_export = scored_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Scored Results (CSV)",
                data=csv_export,
                file_name="mplads_scored_batch.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )
            
            st.markdown("""
            <div style="font-size:0.76rem; color:#64748B; margin-top:0.75rem; line-height:1.4; border-top:1px solid #F1F5F9; padding-top:0.5rem;">
                <strong>Audit Protocol Note:</strong> Evaluated records can be flagged for field verification. Verified outcomes may be logged for scheduled, periodic baseline re-calibration.
            </div>
            </div>
            """, unsafe_allow_html=True)

        # Scored Projects Roster
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-top: 1rem;">
            <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.4rem;">
                Screened Projects Roster
            </div>
        """, unsafe_allow_html=True)
        
        risk_filter = st.radio(
            "Filter Batch Display:",
            ["All Records", "High Risk Only", "Flagged Anomalies"],
            horizontal=True
        )
        if risk_filter == "High Risk Only":
            display_scored = scored_df[scored_df["risk_level"] == "High"]
        elif risk_filter == "Flagged Anomalies":
            display_scored = scored_df[scored_df["anomaly_flag"] == 1]
        else:
            display_scored = scored_df

        display_scored = display_scored.sort_values(by="anomaly_score", ascending=False)
        render_project_roster_table(
            display_scored,
            key_prefix="new_data_table",
            page_size=15,
            show_investigation_picker=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
