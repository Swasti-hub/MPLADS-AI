"""
components/tables.py
--------------------
Enterprise project tables with formatted financial columns,
risk indicators, and integrated "View / Investigate" actions.
Compact, clean styling suitable for government audit review.
"""

import streamlit as st
import pandas as pd
from utils.formatting import format_inr


def prepare_display_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selects, orders, and formats presentation columns for the project roster.
    Columns:
      Work ID | State | Constituency | Work Category | Sanctioned Amount |
      Disbursed Amount | Payments | Risk Score | Risk Level | Primary Reason | Action
    """
    table_df = pd.DataFrame()
    
    table_df["Work ID"] = df["Work ID"] if "Work ID" in df.columns else ""
    table_df["State"] = df["State"] if "State" in df.columns else ""
    table_df["Constituency"] = df["Constituency"] if "Constituency" in df.columns else ""
    table_df["Work Category"] = df["Work Category"] if "Work Category" in df.columns else ""
    table_df["Sanctioned Amount"] = df["Sanction_Amount"] if "Sanction_Amount" in df.columns else 0.0
    table_df["Disbursed Amount"] = df["Total_Disbursed"] if "Total_Disbursed" in df.columns else 0.0
    table_df["Payments"] = df["Number_of_Payments"] if "Number_of_Payments" in df.columns else 0
    table_df["Risk Score"] = df["anomaly_score"] if "anomaly_score" in df.columns else 0.0
    table_df["Risk Level"] = df["risk_level"] if "risk_level" in df.columns else "Low"
    table_df["Primary Reason"] = df["risk_reasons"] if "risk_reasons" in df.columns else "Standard Pattern"
    table_df["Action"] = "🔍 View / Investigate"

    return table_df


def render_project_roster_table(
    df: pd.DataFrame,
    key_prefix: str = "roster",
    page_size: int = 15,
    show_investigation_picker: bool = True
):
    """
    Renders an enterprise project table with a prominent View / Investigate case dossier action.
    """
    if df.empty:
        st.info("No projects match the specified filter criteria.")
        return

    st.caption(f"Showing **{len(df):,}** projects (ranked by Risk Score descending)")

    # Clean display dataframe
    display_df = prepare_display_dataframe(df)

    # Render table with enterprise styling
    st.dataframe(
        display_df,
        column_config={
            "Work ID": st.column_config.TextColumn("Work ID", width="medium"),
            "State": st.column_config.TextColumn("State", width="small"),
            "Constituency": st.column_config.TextColumn("Constituency", width="small"),
            "Work Category": st.column_config.TextColumn("Work Category", width="small"),
            "Sanctioned Amount": st.column_config.NumberColumn("Sanctioned Amount", format="₹%d"),
            "Disbursed Amount": st.column_config.NumberColumn("Disbursed Amount", format="₹%d"),
            "Payments": st.column_config.NumberColumn("Payments", format="%d"),
            "Risk Score": st.column_config.NumberColumn("Risk Score", format="%.4f"),
            "Risk Level": st.column_config.TextColumn("Risk Level", width="small"),
            "Primary Reason": st.column_config.TextColumn("Primary Reason", width="large"),
            "Action": st.column_config.TextColumn("Action", width="small")
        },
        use_container_width=True,
        hide_index=True,
        height=min(430, 42 + 35 * min(len(display_df), page_size))
    )

    if show_investigation_picker:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        col_pick, col_btn = st.columns([3.2, 1.2])
        with col_pick:
            work_ids = df["Work ID"].dropna().unique().tolist()
            selected_id = st.selectbox(
                "Select Work ID to open case dossier:",
                options=work_ids,
                key=f"{key_prefix}_picker",
                label_visibility="collapsed"
            )
        with col_btn:
            if st.button("View / Investigate Case →", key=f"{key_prefix}_btn", type="primary", use_container_width=True):
                st.session_state["selected_work_id"] = selected_id
                st.session_state["current_page"] = "Project Details"
                st.rerun()
