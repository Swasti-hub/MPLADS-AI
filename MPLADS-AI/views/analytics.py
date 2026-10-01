"""
views/analytics.py
------------------
Operational analytics and pattern diagnostics for MPLADS risk oversight.
Provides purpose-driven analytical perspectives supporting vigilance inquiries:
  - Work Category distribution & high-risk density
  - Financial parity (Sanction vs Disbursement)
  - Payment tranche frequency patterns
  - Execution duration benchmarks
  - Administrative milestone coverage
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from services.data_service import load_master_data
from components.cards import render_header, render_important_notice
from components.charts import (
    plot_disbursement_vs_sanction,
    plot_category_risk_bar,
    BORDER_GRAY,
    COLOR_HIGH,
    COLOR_LOW
)
from utils.formatting import format_inr, format_count


def render_analytics():
    """Renders the comprehensive operational analytics module."""
    
    # Header
    render_header(
        title="Operational Pattern Analytics",
        subtitle="Vigilance Diagnostics & Implementation Trends",
        tagline="Diagnostics on expenditure compliance, execution duration, and milestone records",
        show_status=True
    )

    # Advisory Notice
    render_important_notice(
        title="Operational Analytics Purpose",
        text="These diagnostic views reveal structural patterns across categories, disbursements, and execution timelines across the verified 34,450-project baseline."
    )

    df = load_master_data()

    # Tabbed Analytical Perspectives
    tab_cat, tab_fin, tab_pmt, tab_time, tab_admin = st.tabs([
        "Work Category Risk",
        "Disbursement vs Sanction",
        "Payment Tranche Patterns",
        "Execution Timelines",
        "Administrative Completeness"
    ])

    # TAB 1: WORK CATEGORY RISK
    with tab_cat:
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-top: 0.5rem; margin-bottom: 1rem;">
            <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.2rem;">
                Work Category Anomaly Concentration
            </div>
            <div style="font-size: 0.78rem; color: #64748B; margin-bottom: 0.6rem;">
                Comparison of total projects against High-Risk projects across functional categories:
            </div>
        """, unsafe_allow_html=True)

        c_col1, c_col2 = st.columns([1.5, 1])
        with c_col1:
            fig_cat = plot_category_risk_bar(df)
            st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})

        with c_col2:
            cat_table = df.groupby("Work Category").agg(
                Total=("Work ID", "count"),
                High_Risk=("risk_level", lambda s: (s == "High").sum()),
                Total_Disbursed=("Total_Disbursed", "sum")
            ).reset_index()
            cat_table["High_Risk_%"] = (cat_table["High_Risk"] / cat_table["Total"] * 100).round(1)
            cat_table = cat_table.sort_values(by="High_Risk_%", ascending=False)

            st.markdown("**Category Risk Breakdown Table**")
            st.dataframe(
                cat_table,
                column_config={
                    "Total_Disbursed": st.column_config.NumberColumn(label="Disbursed", format="₹%d"),
                    "High_Risk_%": st.column_config.NumberColumn(label="High Risk %", format="%.1f%%")
                },
                use_container_width=True,
                hide_index=True,
                height=260
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # TAB 2: DISBURSEMENT VS SANCTION
    with tab_fin:
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-top: 0.5rem; margin-bottom: 1rem;">
            <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.2rem;">
                Expenditure Compliance: Sanction vs Total Disbursed
            </div>
            <div style="font-size: 0.78rem; color: #64748B; margin-bottom: 0.6rem;">
                Scatter plot of projects with documented sanction and disbursement. Points above the 45-degree dashed line represent potential over-disbursement:
            </div>
        """, unsafe_allow_html=True)

        fig_scatter = plot_disbursement_vs_sanction(df)
        st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

        # Over-disbursement quick facts
        over_disb = df[(df["Sanction_Amount"] > 0) & (df["Total_Disbursed"] > df["Sanction_Amount"] + 1000)]
        st.info(
            f"Audit Finding: Exactly {len(over_disb):,} projects exhibit recorded total disbursement "
            "exceeding recorded sanctioned expenditure. These cases represent priority verification files."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # TAB 3: PAYMENT TRANCHE PATTERNS
    with tab_pmt:
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-top: 0.5rem; margin-bottom: 1rem;">
            <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.2rem;">
                Payment Installment Tranche Distribution
            </div>
            <div style="font-size: 0.78rem; color: #64748B; margin-bottom: 0.6rem;">
                Frequency of disbursement payment installments comparing Normal works against Flagged Anomalies:
            </div>
        """, unsafe_allow_html=True)

        pmt_df = df[df["Number_of_Payments"].notna()].copy()
        pmt_df["Payments_Capped"] = pmt_df["Number_of_Payments"].clip(upper=6).astype(int).astype(str)
        pmt_df["Payments_Capped"] = pmt_df["Payments_Capped"].replace({"6": "6+"})
        pmt_df["Status"] = np.where(pmt_df["anomaly_flag"] == 1, "Flagged Anomaly", "Normal Inlier")

        pmt_counts = pmt_df.groupby(["Payments_Capped", "Status"]).size().unstack(fill_value=0).reset_index()

        fig_pmt = go.Figure()
        if "Normal Inlier" in pmt_counts.columns:
            fig_pmt.add_trace(go.Bar(
                x=pmt_counts["Payments_Capped"],
                y=pmt_counts["Normal Inlier"],
                name="Normal Projects",
                marker=dict(color="#0F2B48")
            ))
        if "Flagged Anomaly" in pmt_counts.columns:
            fig_pmt.add_trace(go.Bar(
                x=pmt_counts["Payments_Capped"],
                y=pmt_counts["Flagged Anomaly"],
                name="Flagged Anomalies",
                marker=dict(color=COLOR_HIGH)
            ))

        fig_pmt.update_layout(
            barmode="group",
            height=300,
            xaxis=dict(title="Payment Installment Count", showgrid=True, gridcolor=BORDER_GRAY),
            yaxis=dict(title="Project Count", showgrid=True, gridcolor=BORDER_GRAY),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font=dict(family="Inter, sans-serif", size=11, color="#0F172A"),
            margin=dict(l=10, r=10, t=25, b=15)
        )
        st.plotly_chart(fig_pmt, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # TAB 4: EXECUTION TIMELINES
    with tab_time:
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-top: 0.5rem; margin-bottom: 1rem;">
            <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.2rem;">
                Execution Timeline Benchmarks
            </div>
            <div style="font-size: 0.78rem; color: #64748B; margin-bottom: 0.6rem;">
                Distribution of duration in days from Administrative Sanction to Project Completion:
            </div>
        """, unsafe_allow_html=True)

        dur_df = df[(df["Sanction_to_Completion_Days"] > 0) & (df["Sanction_to_Completion_Days"] < 1500)]

        fig_hist = px.histogram(
            dur_df,
            x="Sanction_to_Completion_Days",
            color="risk_level",
            color_discrete_map={"High": COLOR_HIGH, "Medium": "#D97706", "Low": COLOR_LOW},
            nbins=35,
            labels={"Sanction_to_Completion_Days": "Days from Sanction to Completion", "risk_level": "Risk Tier"}
        )
        fig_hist.update_layout(
            height=300,
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font=dict(family="Inter, sans-serif", size=11, color="#0F172A"),
            xaxis=dict(showgrid=True, gridcolor=BORDER_GRAY),
            yaxis=dict(showgrid=True, gridcolor=BORDER_GRAY, title="Projects"),
            margin=dict(l=10, r=10, t=25, b=15)
        )
        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # TAB 5: ADMINISTRATIVE COMPLETENESS
    with tab_admin:
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.85rem 1rem; margin-top: 0.5rem; margin-bottom: 1rem;">
            <div style="font-size: 0.95rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.2rem;">
                Administrative Milestone Coverage Audit
            </div>
            <div style="font-size: 0.78rem; color: #64748B; margin-bottom: 0.6rem;">
                System-wide presence of essential administrative workflow records:
            </div>
        """, unsafe_allow_html=True)

        admin_rates = {
            "MP Recommendation": float(df["Has_Recommendation"].mean() * 100),
            "Administrative Sanction": float(df["Has_Sanction"].mean() * 100),
            "Completion Record": float(df["Has_Completion"].mean() * 100),
            "Disbursement Record": float(df["Has_Disbursement"].mean() * 100),
            "Payment Installment Ledger": float(df["Has_Payment_Data"].mean() * 100),
        }

        fig_admin = go.Figure(data=[
            go.Bar(
                x=list(admin_rates.keys()),
                y=list(admin_rates.values()),
                marker=dict(color=["#0F2B48", "#1E3A8A", "#2563EB", "#3B82F6", "#60A5FA"]),
                text=[f"{v:.1f}%" for v in admin_rates.values()],
                textposition="auto"
            )
        ])
        fig_admin.update_layout(
            height=300,
            yaxis=dict(title="Recorded (%)", range=[0, 105], showgrid=True, gridcolor=BORDER_GRAY),
            xaxis=dict(title=""),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font=dict(family="Inter, sans-serif", size=11, color="#0F172A"),
            margin=dict(l=10, r=10, t=20, b=15)
        )
        st.plotly_chart(fig_admin, use_container_width=True, config={"displayModeBar": False})

        missing_sanc_disb = df[(df["Has_Disbursement"] == 1) & (df["Has_Sanction"] == 0)]
        st.warning(
            f"Administrative Gap Notice: Exactly {len(missing_sanc_disb):,} projects have recorded disbursements "
            "without documented administrative sanctions in official portal records. These require district documentation reconciliation."
        )
        st.markdown("</div>", unsafe_allow_html=True)
