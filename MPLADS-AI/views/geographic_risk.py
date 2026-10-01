"""
views/geographic_risk.py
------------------------
Geographic risk oversight module.
Analyzes the distribution of MPLADS anomalies, high-risk projects, and financial exposure
across States, Union Territories, and Parliamentary Constituencies using actual dataset values.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from services.data_service import load_master_data
from components.cards import render_header, render_important_notice
from components.charts import plot_state_risk_distribution
from components.tables import render_project_roster_table
from utils.formatting import format_inr, format_count


def render_geographic_risk():
    """Renders state-level and constituency-level geographic risk dashboards."""
    
    # Header
    render_header(
        title="Geographic Risk Distribution",
        subtitle="Jurisdictional Risk Concentrations & Exposure Analysis",
        tagline="Evaluate operational risk patterns across States, Union Territories, and Parliamentary Constituencies",
        show_status=True
    )

    # Advisory Notice
    render_important_notice(
        title="Jurisdictional Screening Note",
        text="State and constituency aggregations reflect recorded implementation patterns in the dataset. Variations may arise from regional project volume differences."
    )

    df = load_master_data()

    # Aggregate State-level statistics
    state_agg = df.groupby("State").agg(
        Total_Projects=("Work ID", "count"),
        High_Risk=("risk_level", lambda s: (s == "High").sum()),
        Medium_Risk=("risk_level", lambda s: (s == "Medium").sum()),
        Low_Risk=("risk_level", lambda s: (s == "Low").sum()),
        Anomalies_Flagged=("anomaly_flag", "sum"),
        Total_Disbursed=("Total_Disbursed", "sum")
    ).reset_index()

    state_agg["High_Risk_%"] = (state_agg["High_Risk"] / state_agg["Total_Projects"] * 100).round(2)
    state_agg["Anomaly_%"] = (state_agg["Anomalies_Flagged"] / state_agg["Total_Projects"] * 100).round(2)
    state_agg = state_agg.sort_values(by="High_Risk", ascending=False)

    # 1. State Overview Horizontal Bar Chart
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.2rem;">
            State-Level Risk Stratification (Top Jurisdictions)
        </div>
        <div style="font-size: 0.78rem; color: #64748B; margin-bottom: 0.6rem;">
            Distribution of High, Medium, and Low risk projects across the top states ranked by High-Risk volume:
        </div>
    """, unsafe_allow_html=True)

    fig_state = plot_state_risk_distribution(df, top_n=12)
    st.plotly_chart(fig_state, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. State Risk Metrics Table
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.2rem;">
            State / UT Comprehensive Risk Table
        </div>
        <div style="font-size: 0.78rem; color: #64748B; margin-bottom: 0.6rem;">
            Complete jurisdiction ledger with project counts, risk proportions, and cumulative disbursements:
        </div>
    """, unsafe_allow_html=True)
    
    display_state_df = state_agg.copy()
    display_state_df = display_state_df.rename(columns={
        "Total_Projects": "Total Projects",
        "High_Risk": "High Risk",
        "Medium_Risk": "Medium Risk",
        "Low_Risk": "Low Risk",
        "Anomalies_Flagged": "Anomalies",
        "Total_Disbursed": "Total Disbursed",
        "High_Risk_%": "High Risk %",
        "Anomaly_%": "Anomaly Rate %"
    })

    st.dataframe(
        display_state_df,
        column_config={
            "Total Disbursed": st.column_config.NumberColumn(format="₹%d"),
            "Total Projects": st.column_config.NumberColumn(format="%d"),
            "High Risk": st.column_config.NumberColumn(format="%d"),
            "Medium Risk": st.column_config.NumberColumn(format="%d"),
            "Low Risk": st.column_config.NumberColumn(format="%d"),
            "Anomalies": st.column_config.NumberColumn(format="%d"),
            "High Risk %": st.column_config.NumberColumn(format="%.2f%%"),
            "Anomaly Rate %": st.column_config.NumberColumn(format="%.2f%%")
        },
        use_container_width=True,
        hide_index=True,
        height=310
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Deep-Dive Drill-Down by Specific State
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.4rem;">
            Jurisdictional Drill-Down: Parliamentary Constituencies
        </div>
    """, unsafe_allow_html=True)

    all_states = sorted(df["State"].dropna().unique().tolist())
    selected_state = st.selectbox(
        "Select State to inspect Constituencies & Implementing Authorities:",
        options=all_states,
        index=all_states.index("Uttar Pradesh") if "Uttar Pradesh" in all_states else 0
    )

    state_subset = df[df["State"] == selected_state]

    # Constituency aggregation within selected state
    const_agg = state_subset.groupby("Constituency").agg(
        Total_Projects=("Work ID", "count"),
        High_Risk=("risk_level", lambda s: (s == "High").sum()),
        Medium_Risk=("risk_level", lambda s: (s == "Medium").sum()),
        Low_Risk=("risk_level", lambda s: (s == "Low").sum()),
        Total_Disbursed=("Total_Disbursed", "sum")
    ).reset_index().sort_values(by="High_Risk", ascending=False)

    const_agg["High_Risk_%"] = (const_agg["High_Risk"] / const_agg["Total_Projects"] * 100).round(1)

    c_chart_col, c_tbl_col = st.columns([1, 1])
    with c_chart_col:
        st.markdown(f"**Top Constituencies by High Risk ({selected_state})**")
        top_const = const_agg.head(8).sort_values(by="High_Risk", ascending=True)
        fig_const = go.Figure(data=[
            go.Bar(
                y=top_const["Constituency"],
                x=top_const["High_Risk"],
                orientation="h",
                marker=dict(color="#DC2626"),
                text=top_const["High_Risk"],
                textposition="auto"
            )
        ])
        fig_const.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font=dict(family="Inter, sans-serif", size=11, color="#0F172A"),
            xaxis=dict(title="High Risk Works", showgrid=True, gridcolor="#E2E8F0"),
            yaxis=dict(title="")
        )
        st.plotly_chart(fig_const, use_container_width=True, config={"displayModeBar": False})

    with c_tbl_col:
        st.markdown(f"**Constituency Breakdown ({selected_state})**")
        st.dataframe(
            const_agg.head(12),
            column_config={
                "Total_Disbursed": st.column_config.NumberColumn(label="Disbursed", format="₹%d"),
                "High_Risk_%": st.column_config.NumberColumn(label="High Risk %", format="%.1f%%")
            },
            use_container_width=True,
            hide_index=True,
            height=280
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Flagged projects in selected state
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem;">
        <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.4rem;">
            Flagged High-Risk Projects in """ + selected_state + """
        </div>
    """, unsafe_allow_html=True)

    state_flagged = state_subset[state_subset["risk_level"] == "High"].sort_values(by="anomaly_score", ascending=False)
    render_project_roster_table(
        state_flagged,
        key_prefix=f"geo_{selected_state[:4]}",
        page_size=10,
        show_investigation_picker=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
