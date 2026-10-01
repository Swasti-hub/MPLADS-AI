"""
app.py
------
Main application router for the MPLADS AI Risk Monitoring Platform.
Provides clean enterprise government styling, clickable sidebar navigation,
and seamless project case dossier state management.
"""

import sys
from pathlib import Path
import streamlit as st

# Configure page metadata
st.set_page_config(
    page_title="MPLADS AI - Risk Monitoring & Investigation Platform",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Strict Light Theme & Government Enterprise CSS
from components.styles import apply_custom_styles
apply_custom_styles()

# Import view modules
from views.command_center import render_command_center
from views.risk_investigation import render_risk_investigation
from views.project_details import render_project_details
from views.analyze_new_data import render_analyze_new_data
from views.geographic_risk import render_geographic_risk
from views.analytics import render_analytics
from views.reports import render_reports
from views.about import render_about


PAGES = [
    "Command Center",
    "Risk Investigation",
    "Project Details",
    "Analyze New Data",
    "Geographic Risk",
    "Analytics",
    "Reports",
    "About System"
]


def main():
    # Initialize session state for navigation and selection
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Command Center"
        
    if "selected_work_id" not in st.session_state:
        st.session_state["selected_work_id"] = None

    # Normalization of page name if necessary
    for p in PAGES:
        if p.lower() in st.session_state["current_page"].lower():
            st.session_state["current_page"] = p
            break

    # Sidebar Header & Clickable Navigation Items
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">
                MPLADS AI
            </div>
            <div class="sidebar-brand-sub">
                Risk Monitoring & Investigation Platform
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='sidebar-nav-header'>Navigation</div>", unsafe_allow_html=True)

        # Proper Clickable Navigation Items (Replacing Radio Buttons)
        for page_name in PAGES:
            is_active = (st.session_state["current_page"] == page_name)
            btn_type = "primary" if is_active else "secondary"
            if st.button(
                page_name,
                key=f"nav_btn_{page_name.replace(' ', '_')}",
                use_container_width=True,
                type=btn_type
            ):
                if st.session_state["current_page"] != page_name:
                    st.session_state["current_page"] = page_name
                    st.rerun()

        st.markdown("---")

        # Sidebar Operational Facts Badge
        st.markdown("""
        <div class="sidebar-card">
            <div class="sidebar-card-label">Operational Baseline</div>
            <div class="sidebar-card-title">Isolation Forest &bull; 20 Features</div>
            <div class="sidebar-card-text">Universe: <strong>34,450 genuine works</strong></div>
            <div class="sidebar-card-text">Flagged: <strong>1,719 anomalies (4.99%)</strong></div>
            <div class="sidebar-card-danger">High Risk: <strong>1,727 (5.01%)</strong></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Official Disclaimer Footer
        st.markdown("""
        <div class="sidebar-disclaimer">
            <strong>Notice:</strong> AI-assisted preliminary screening. Anomaly scores indicate operational deviation, not confirmed fraud. Final verification remains with authorized officials.
        </div>
        """, unsafe_allow_html=True)

    # Dispatch to Selected View
    curr = st.session_state["current_page"]

    try:
        if curr == "Command Center":
            render_command_center()
        elif curr == "Risk Investigation":
            render_risk_investigation()
        elif curr == "Project Details":
            render_project_details()
        elif curr == "Analyze New Data":
            render_analyze_new_data()
        elif curr == "Geographic Risk":
            render_geographic_risk()
        elif curr == "Analytics":
            render_analytics()
        elif curr == "Reports":
            render_reports()
        elif curr == "About System":
            render_about()
        else:
            render_command_center()
    except Exception as e:
        st.error(f"Display error: {str(e)}")
        st.info("Please return to the Command Center.")


if __name__ == "__main__":
    main()
