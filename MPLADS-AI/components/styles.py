"""
components/styles.py
--------------------
Enterprise Government Portal CSS theme for MPLADS AI Platform.
Strictly LIGHT MODE with deep navy primary typography, subtle borders,
left-accented KPI cards, operational status indicators, and clean sidebar navigation.
"""

import streamlit as st


def apply_custom_styles():
    """Injects high-authority government enterprise CSS into the Streamlit app."""
    custom_css = """
    <style>
        /* Force Light Theme Colors Globally */
        :root {
            --primary: #0F2B48;
            --primary-light: #1E3A8A;
            --primary-accent: #2563EB;
            --surface: #FFFFFF;
            --background: #F8FAFC;
            --border: #E2E8F0;
            --border-hover: #CBD5E1;
            --text-main: #0F172A;
            --text-muted: #334155;
            --text-sub: #64748B;
            --danger: #DC2626;
            --warning: #D97706;
            --success: #059669;
        }

        html, body, [class*="css"], .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            background-color: #F8FAFC !important;
            color: #0F172A !important;
        }

        /* Container Spacing */
        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 1440px !important;
        }

        /* Executive Header Block */
        .gov-header-container {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 5px solid #0F2B48;
            border-radius: 4px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.85rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }
        
        .gov-header-command-center {
            position: relative;
            overflow: hidden;
            border: 1px solid #CBD5E1 !important;
            border-left: 5px solid #0F2B48 !important;
            box-shadow: 0 1px 4px rgba(15, 23, 42, 0.05) !important;
        }
        .gov-header-command-center .gov-status-badge {
            background: rgba(248, 250, 252, 0.94) !important;
            border: 1px solid #E2E8F0 !important;
            backdrop-filter: blur(4px) !important;
        }
        .gov-header-command-center .gov-header-pipeline {
            filter: drop-shadow(0 1px 2px rgba(15, 23, 42, 0.04));
        }
        
        .gov-header-left {
            flex: 1;
            min-width: 280px;
        }

        .gov-title-main {
            color: #0F2B48;
            font-size: 1.45rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.01em;
            line-height: 1.2;
        }
        
        .gov-subtitle-main {
            color: #334155;
            font-size: 0.92rem;
            font-weight: 600;
            margin-top: 0.2rem;
            margin-bottom: 0;
        }

        .gov-tagline-main {
            color: #64748B;
            font-size: 0.8rem;
            font-weight: 500;
            margin-top: 0.25rem;
        }

        .gov-status-badge {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 4px;
            padding: 0.45rem 0.85rem;
            text-align: right;
            min-width: 140px;
        }

        .gov-header-emblem svg {
            width: 44px;
            height: 44px;
            display: block;
        }

        .gov-header-pipeline svg {
            max-width: 420px;
            height: 40px;
            display: block;
        }

        .gov-investigation-flow svg {
            max-width: 420px;
            height: 40px;
            display: block;
        }

        .gov-status-label {
            font-size: 0.68rem;
            font-weight: 700;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 2px;
        }

        .gov-status-val {
            font-size: 0.84rem;
            font-weight: 700;
            color: #059669;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 6px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #10B981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
        }

        /* Responsible AI Advisory Callout */
        .gov-advisory-box {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 3px solid #2563EB;
            border-radius: 4px;
            padding: 0.65rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .gov-advisory-title {
            font-size: 0.78rem;
            font-weight: 700;
            color: #1E3A8A;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            white-space: nowrap;
        }

        .gov-advisory-text {
            font-size: 0.8rem;
            color: #475569;
            line-height: 1.4;
            margin: 0;
        }

        /* 4-Step Operational Flow Indicator */
        .workflow-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 4px;
            padding: 0.55rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        }
        .workflow-step {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.76rem;
            font-weight: 600;
            color: #475569;
        }
        .workflow-step-num {
            color: #0F2B48;
            font-weight: 700;
            font-size: 0.76rem;
        }
        .workflow-arrow {
            color: #94A3B8;
            font-size: 0.82rem;
        }

        /* Left-Accented KPI Cards with Consistent Height */
        .kpi-container {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 4px;
            padding: 0.75rem 0.9rem;
            min-height: 98px;
            height: 100%;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
            box-sizing: border-box;
        }
        
        .kpi-high-risk {
            border-left: 4px solid #DC2626 !important;
        }
        .kpi-medium-risk {
            border-left: 4px solid #D97706 !important;
        }
        .kpi-low-risk {
            border-left: 4px solid #059669 !important;
        }
        .kpi-general {
            border-left: 4px solid #2563EB !important;
        }
        .kpi-neutral {
            border-left: 4px solid #0F2B48 !important;
        }

        .kpi-title {
            color: #64748B;
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .kpi-value {
            color: #0F2B48;
            font-size: 1.4rem;
            font-weight: 700;
            line-height: 1.15;
            letter-spacing: -0.02em;
            margin: 2px 0;
        }
        .kpi-caption {
            color: #64748B;
            font-size: 0.72rem;
            font-weight: 500;
            line-height: 1.2;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* Section Panel Containers (Equal Height) */
        .gov-panel {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 4px;
            padding: 0.85rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
            height: 100%;
            box-sizing: border-box;
        }
        
        .gov-panel-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            padding-bottom: 0.4rem;
            margin-bottom: 0.6rem;
            border-bottom: 1px solid #F1F5F9;
        }

        .gov-panel-title {
            color: #0F2B48;
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: -0.01em;
        }

        .gov-panel-subtitle {
            color: #64748B;
            font-size: 0.74rem;
            font-weight: 500;
        }

        /* Audit Finding Alert Banners */
        .audit-alert-danger {
            background-color: #FEF2F2;
            border: 1px solid #FECACA;
            border-left: 4px solid #DC2626;
            color: #991B1B;
            padding: 0.65rem 0.85rem;
            border-radius: 4px;
            margin-bottom: 0.65rem;
            font-size: 0.84rem;
            line-height: 1.45;
        }
        .audit-alert-warning {
            background-color: #FFFBEB;
            border: 1px solid #FDE68A;
            border-left: 4px solid #D97706;
            color: #92400E;
            padding: 0.65rem 0.85rem;
            border-radius: 4px;
            margin-bottom: 0.65rem;
            font-size: 0.84rem;
            line-height: 1.45;
        }
        .audit-alert-info {
            background-color: #F0FDF4;
            border: 1px solid #BBF7D0;
            border-left: 4px solid #059669;
            color: #166534;
            padding: 0.65rem 0.85rem;
            border-radius: 4px;
            margin-bottom: 0.65rem;
            font-size: 0.84rem;
            line-height: 1.45;
        }

        /* SIDEBAR STYLING - DARK NAVY ENTERPRISE / REFERENCE STYLE */
        section[data-testid="stSidebar"] {
            background-color: #10273E !important;
            border-right: 1px solid #2A4963 !important;
        }
        section[data-testid="stSidebar"] > div:first-child,
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            background-color: #10273E !important;
            color: #C7D2DE !important;
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 1rem !important;
            padding-left: 0.9rem !important;
            padding-right: 0.9rem !important;
        }

        .sidebar-brand {
            padding-bottom: 0.75rem;
            margin-bottom: 0.75rem;
            border-bottom: 1px solid #2A4963 !important;
        }
        .sidebar-brand-title {
            font-size: 1.25rem;
            font-weight: 800;
            color: #FFFFFF !important;
            letter-spacing: -0.01em;
            line-height: 1.2;
        }
        .sidebar-brand-sub {
            font-size: 0.74rem;
            color: #C7D2DE !important;
            margin-top: 2px;
            font-weight: 500;
            line-height: 1.3;
        }

        .sidebar-nav-header {
            font-size: 0.72rem;
            font-weight: 700;
            color: #8FA3B8 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
            padding-left: 2px;
        }

        /* Sidebar Navigation Buttons */
        section[data-testid="stSidebar"] .stButton {
            margin-bottom: 0.25rem !important;
        }
        section[data-testid="stSidebar"] .stButton > button {
            border-radius: 6px !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            padding: 0.5rem 0.8rem !important;
            margin-bottom: 0.1rem !important;
            text-align: left !important;
            justify-content: flex-start !important;
            box-shadow: none !important;
            border: 1px solid transparent !important;
            width: 100% !important;
        }

        /* Inactive Navigation Item (sits directly on dark navy background) */
        section[data-testid="stSidebar"] .stButton > button[kind="secondary"],
        section[data-testid="stSidebar"] .stButton > button[data-testid*="secondary"],
        section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):not([data-testid*="primary"]) {
            background-color: transparent !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            color: #C7D2DE !important;
            box-shadow: none !important;
        }
        section[data-testid="stSidebar"] .stButton > button[kind="secondary"] *,
        section[data-testid="stSidebar"] .stButton > button[data-testid*="secondary"] *,
        section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):not([data-testid*="primary"]) * {
            color: #C7D2DE !important;
        }
        section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover,
        section[data-testid="stSidebar"] .stButton > button[data-testid*="secondary"]:hover,
        section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):not([data-testid*="primary"]):hover {
            background-color: #173756 !important;
            background: #173756 !important;
            border-color: #2A4963 !important;
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover *,
        section[data-testid="stSidebar"] .stButton > button[data-testid*="secondary"]:hover *,
        section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):not([data-testid*="primary"]):hover * {
            color: #FFFFFF !important;
        }

        /* Active Navigation Item (bright blue rounded rectangle) */
        section[data-testid="stSidebar"] .stButton > button[kind="primary"],
        section[data-testid="stSidebar"] .stButton > button[data-testid*="primary"] {
            background-color: #2068E0 !important;
            background: #2068E0 !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            border: 1px solid #2068E0 !important;
            border-radius: 6px !important;
            box-shadow: none !important;
        }
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] *,
        section[data-testid="stSidebar"] .stButton > button[data-testid*="primary"] * {
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover,
        section[data-testid="stSidebar"] .stButton > button[data-testid*="primary"]:hover {
            background-color: #2068E0 !important;
            background: #2068E0 !important;
            border-color: #2068E0 !important;
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover *,
        section[data-testid="stSidebar"] .stButton > button[data-testid*="primary"]:hover * {
            color: #FFFFFF !important;
        }

        /* Sidebar Collapse / Toggle Header Buttons */
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,
        section[data-testid="stSidebar"] button[data-testid="baseButton-header"],
        section[data-testid="stSidebar"] button[data-testid="stBaseButton-header"] {
            color: #C7D2DE !important;
            background-color: transparent !important;
            border: none !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button:hover,
        section[data-testid="stSidebar"] button[data-testid="baseButton-header"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stBaseButton-header"]:hover {
            color: #FFFFFF !important;
            background-color: rgba(255, 255, 255, 0.08) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg,
        section[data-testid="stSidebar"] button[data-testid="baseButton-header"] svg,
        section[data-testid="stSidebar"] button[data-testid="stBaseButton-header"] svg {
            fill: #C7D2DE !important;
            stroke: #C7D2DE !important;
        }

        /* Sidebar Dividers & Cards */
        section[data-testid="stSidebar"] hr {
            border: none !important;
            border-top: 1px solid #2A4963 !important;
            margin: 0.85rem 0 !important;
        }
        .sidebar-card {
            background-color: #0c1f32 !important;
            border: 1px solid #2A4963 !important;
            border-radius: 4px !important;
            padding: 0.75rem !important;
            font-size: 0.76rem !important;
        }
        .sidebar-card-label {
            color: #8FA3B8 !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            margin-bottom: 4px !important;
        }
        .sidebar-card-title {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        .sidebar-card-text {
            color: #C7D2DE !important;
            margin-top: 4px !important;
        }
        .sidebar-card-danger {
            color: #F87171 !important;
            font-weight: 600 !important;
            margin-top: 4px !important;
        }
        .sidebar-disclaimer {
            font-size: 0.72rem !important;
            color: #8FA3B8 !important;
            line-height: 1.4 !important;
            border-top: 1px solid #2A4963 !important;
            padding-top: 0.6rem !important;
        }

        /* Fallback for inline styled sidebar elements */
        section[data-testid="stSidebar"] div[style*="background-color: #FFFFFF"] {
            background-color: #0c1f32 !important;
            border-color: #2A4963 !important;
        }
        section[data-testid="stSidebar"] div[style*="background-color: #FFFFFF"] div[style*="color: #0F2B48"] {
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] div[style*="background-color: #FFFFFF"] div[style*="color: #475569"] {
            color: #C7D2DE !important;
        }
        section[data-testid="stSidebar"] div[style*="border-top: 1px solid #E2E8F0"] {
            border-top-color: #2A4963 !important;
            color: #8FA3B8 !important;
        }

        /* General Buttons */
        .stButton > button {
            border-radius: 4px !important;
            font-weight: 600 !important;
            font-size: 0.84rem !important;
            padding: 0.38rem 0.85rem !important;
            border: 1px solid #CBD5E1 !important;
            background-color: #FFFFFF !important;
            color: #0F2B48 !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
            transition: all 0.15s ease !important;
        }
        .stButton > button:hover {
            background-color: #F8FAFC !important;
            border-color: #0F2B48 !important;
            color: #0F2B48 !important;
        }
        .stButton > button[kind="primary"] {
            background-color: #0F2B48 !important;
            border-color: #0F2B48 !important;
            color: #FFFFFF !important;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #1E3A8A !important;
            border-color: #1E3A8A !important;
            color: #FFFFFF !important;
        }

        /* Input Fields and Selects */
        input[type="text"], select, textarea {
            border-radius: 4px !important;
            border: 1px solid #CBD5E1 !important;
            font-size: 0.85rem !important;
            color: #0F172A !important;
            background-color: #FFFFFF !important;
        }
        input[type="text"]:focus, select:focus, textarea:focus {
            border-color: #2563EB !important;
            box-shadow: 0 0 0 1px #2563EB !important;
        }

        /* Table Styling */
        div[data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0 !important;
            border-radius: 4px !important;
            background: #FFFFFF !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.02) !important;
        }

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px !important;
            border-bottom: 1px solid #E2E8F0 !important;
            background-color: transparent !important;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 4px 4px 0 0 !important;
            font-size: 0.84rem !important;
            font-weight: 600 !important;
            color: #475569 !important;
            padding: 0.5rem 1rem !important;
            background-color: #F1F5F9 !important;
            border: 1px solid transparent !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF !important;
            color: #0F2B48 !important;
            border: 1px solid #E2E8F0 !important;
            border-bottom: 1px solid #FFFFFF !important;
        }

        /* Expanders */
        div[data-testid="stExpander"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 4px !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.02) !important;
            margin-bottom: 0.75rem !important;
        }

        /* Form & Search Container Styling */
        div[data-testid="stForm"] {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 4px !important;
            padding: 0.75rem 1rem !important;
            margin-bottom: 0.85rem !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03) !important;
            overflow: visible !important;
        }

        .details-search-section {
            padding-top: 0.25rem;
            margin-bottom: 0.65rem;
            position: relative;
            z-index: 10;
        }

        /* Clean Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {
            background: transparent !important;
            background-color: transparent !important;
            pointer-events: none !important;
        }
        header[data-testid="stHeader"] * {
            pointer-events: auto !important;
        }
        .viewerBadge_container__1QSob {display: none !important;}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
