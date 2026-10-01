"""
components/charts.py
--------------------
Plotly visualization components for the MPLADS AI Risk Monitoring Platform.
Adheres strictly to a professional government theme: clean margins, no distracting
animations, muted harmonious colors, high contrast in light mode, and clear data labels.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


# Government enterprise color palette
NAVY_PRIMARY = "#0F2B48"
BLUE_ACCENT = "#2563EB"
SLATE_MUTED = "#64748B"
BORDER_GRAY = "#E2E8F0"

COLOR_HIGH = "#DC2626"
COLOR_MED = "#D97706"
COLOR_LOW = "#059669"


def _apply_gov_theme(fig: go.Figure, height: int = 280) -> go.Figure:
    """Applies clean enterprise styling to any Plotly figure in strict light mode."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", size=11, color="#0F172A"),
        hoverlabel=dict(bgcolor="#0F2B48", font_color="#FFFFFF", font_size=11),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color="#334155")
        )
    )
    return fig


def plot_risk_donut(high: int, medium: int, low: int) -> go.Figure:
    """
    Renders an enterprise donut chart of risk level stratification.
    Centered text displays the exact total project universe (e.g. 34,450 Projects).
    """
    labels = ["High Risk", "Medium Risk", "Low Risk"]
    values = [high, medium, low]
    colors = [COLOR_HIGH, COLOR_MED, COLOR_LOW]
    total = sum(values)

    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            hole=0.62,
            marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
            textinfo="label+percent",
            textposition="outside",
            textfont=dict(size=10, color="#1E293B", family="Inter, sans-serif"),
            direction="clockwise",
            sort=False,
            hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>"
        )
    ])
    
    fig.add_annotation(
        text=f"<span style='font-size:16px; font-weight:800; color:#0F2B48;'>{total:,}</span><br><span style='font-size:10px; font-weight:600; color:#64748B; text-transform:uppercase;'>Projects</span>",
        x=0.5, y=0.5,
        font=dict(family="Inter, sans-serif"),
        showarrow=False
    )
    
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    return _apply_gov_theme(fig, height=270)


def plot_anomaly_categories(cat_counts: dict) -> go.Figure:
    """
    Renders a clean horizontal bar chart of anomaly root cause categories among flagged projects.
    """
    df_cat = pd.DataFrame(list(cat_counts.items()), columns=["Category", "Count"])
    df_cat = df_cat.sort_values(by="Count", ascending=True)

    # Color palette tailored for categories
    bar_colors = ["#334155", "#1E3A8A", "#2563EB", "#D97706", "#DC2626"]
    if len(df_cat) != len(bar_colors):
        bar_colors = ["#2563EB"] * len(df_cat)

    fig = go.Figure(data=[
        go.Bar(
            x=df_cat["Count"],
            y=df_cat["Category"],
            orientation="h",
            marker=dict(
                color=bar_colors,
                line=dict(color="#FFFFFF", width=1)
            ),
            text=df_cat["Count"],
            textposition="outside",
            textfont=dict(size=10, color="#0F172A", family="Inter, sans-serif"),
            hovertemplate="<b>%{y}</b><br>Flagged Projects: %{x:,}<extra></extra>"
        )
    ])
    
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor=BORDER_GRAY, title="Flagged Count", title_font=dict(size=10)),
        yaxis=dict(showgrid=False, title="", tickfont=dict(size=10)),
        margin=dict(l=10, r=40, t=15, b=15)
    )
    return _apply_gov_theme(fig, height=270)


def plot_state_risk_overview_compact(df: pd.DataFrame, top_n: int = 7) -> go.Figure:
    """
    Renders a compact horizontal stacked bar chart of top states by risk breakdown.
    Designed to fit seamlessly in the right column of the Command Center analytics row.
    """
    state_counts = df.groupby(["State", "risk_level"]).size().unstack(fill_value=0)
    for col in ["High", "Medium", "Low"]:
        if col not in state_counts.columns:
            state_counts[col] = 0
            
    top_states = state_counts.sort_values(by="High", ascending=False).head(top_n).sort_values(by="High", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_states.index,
        x=top_states["High"],
        name="High",
        orientation="h",
        marker=dict(color=COLOR_HIGH),
        hovertemplate="<b>%{y}</b><br>High Risk: %{x:,}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        y=top_states.index,
        x=top_states["Medium"],
        name="Medium",
        orientation="h",
        marker=dict(color=COLOR_MED),
        hovertemplate="<b>%{y}</b><br>Medium Risk: %{x:,}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        y=top_states.index,
        x=top_states["Low"],
        name="Low",
        orientation="h",
        marker=dict(color=COLOR_LOW),
        hovertemplate="<b>%{y}</b><br>Low Risk: %{x:,}<extra></extra>"
    ))

    fig.update_layout(
        barmode="stack",
        xaxis=dict(showgrid=True, gridcolor=BORDER_GRAY, title="Projects", title_font=dict(size=10)),
        yaxis=dict(showgrid=False, title="", tickfont=dict(size=10)),
        margin=dict(l=10, r=10, t=25, b=15),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9)
        )
    )
    return _apply_gov_theme(fig, height=270)


def plot_state_risk_distribution(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """
    Full horizontal stacked bar chart showing top states by project volume and risk breakdown.
    Used on the Geographic Risk page.
    """
    state_counts = df.groupby(["State", "risk_level"]).size().unstack(fill_value=0)
    for col in ["High", "Medium", "Low"]:
        if col not in state_counts.columns:
            state_counts[col] = 0
            
    state_counts["Total"] = state_counts.sum(axis=1)
    top_states = state_counts.sort_values(by="High", ascending=False).head(top_n).sort_values(by="Total", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_states.index,
        x=top_states["High"],
        name="High Risk",
        orientation="h",
        marker=dict(color=COLOR_HIGH),
        hovertemplate="<b>%{y}</b><br>High Risk: %{x:,}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        y=top_states.index,
        x=top_states["Medium"],
        name="Medium Risk",
        orientation="h",
        marker=dict(color=COLOR_MED),
        hovertemplate="<b>%{y}</b><br>Medium Risk: %{x:,}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        y=top_states.index,
        x=top_states["Low"],
        name="Low Risk",
        orientation="h",
        marker=dict(color=COLOR_LOW),
        hovertemplate="<b>%{y}</b><br>Low Risk: %{x:,}<extra></extra>"
    ))

    fig.update_layout(
        barmode="stack",
        xaxis=dict(showgrid=True, gridcolor=BORDER_GRAY, title="Number of Projects"),
        yaxis=dict(showgrid=False, title="")
    )
    return _apply_gov_theme(fig, height=360)


def plot_disbursement_vs_sanction(df: pd.DataFrame) -> go.Figure:
    """
    Scatter plot comparing Sanction Amount to Total Disbursed.
    Features a 45-degree parity line; projects above the line represent over-disbursement.
    """
    plot_df = df[(df["Sanction_Amount"] > 0) & (df["Total_Disbursed"] > 0)].copy()
    if len(plot_df) > 3000:
        plot_df = plot_df.sample(3000, random_state=42)

    fig = go.Figure()

    color_map = {"High": COLOR_HIGH, "Medium": COLOR_MED, "Low": COLOR_LOW}
    for level in ["Low", "Medium", "High"]:
        sub = plot_df[plot_df["risk_level"] == level]
        if not sub.empty:
            fig.add_trace(go.Scatter(
                x=sub["Sanction_Amount"] / 100_000,
                y=sub["Total_Disbursed"] / 100_000,
                mode="markers",
                name=f"{level} Risk",
                marker=dict(color=color_map[level], size=5, opacity=0.6),
                hovertemplate="<b>%{text}</b><br>Sanction: ₹%{x:.2f} L<br>Disbursed: ₹%{y:.2f} L<extra></extra>",
                text=sub["Work ID"]
            ))

    max_val = max(plot_df["Sanction_Amount"].max(), plot_df["Total_Disbursed"].max()) / 100_000
    max_val = min(max_val, 200)
    fig.add_trace(go.Scatter(
        x=[0, max_val],
        y=[0, max_val],
        mode="lines",
        name="Parity (Disbursed = Sanction)",
        line=dict(color="#475569", dash="dash", width=1.5),
        hoverinfo="none"
    ))

    fig.update_layout(
        xaxis=dict(title="Sanction Amount (₹ Lakhs)", range=[0, max_val], showgrid=True, gridcolor=BORDER_GRAY),
        yaxis=dict(title="Total Disbursed (₹ Lakhs)", range=[0, max_val], showgrid=True, gridcolor=BORDER_GRAY)
    )
    return _apply_gov_theme(fig, height=340)


def plot_category_risk_bar(df: pd.DataFrame) -> go.Figure:
    """
    Horizontal grouped bar chart showing project count and anomaly rate across Work Categories.
    """
    cat_summary = df.groupby("Work Category").agg(
        Total=("Work ID", "count"),
        High_Risk=("risk_level", lambda s: (s == "High").sum()),
        Anomalies=("anomaly_flag", "sum")
    ).reset_index()

    cat_summary["High_Risk_%"] = (cat_summary["High_Risk"] / cat_summary["Total"] * 100).round(1)
    cat_summary = cat_summary.sort_values(by="High_Risk", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=cat_summary["Work Category"],
        x=cat_summary["Total"],
        name="Total Projects",
        orientation="h",
        marker=dict(color="#0F2B48")
    ))
    fig.add_trace(go.Bar(
        y=cat_summary["Work Category"],
        x=cat_summary["High_Risk"],
        name="High Risk Projects",
        orientation="h",
        marker=dict(color=COLOR_HIGH)
    ))

    fig.update_layout(
        barmode="group",
        xaxis=dict(title="Number of Projects", showgrid=True, gridcolor=BORDER_GRAY),
        yaxis=dict(title="")
    )
    return _apply_gov_theme(fig, height=290)
