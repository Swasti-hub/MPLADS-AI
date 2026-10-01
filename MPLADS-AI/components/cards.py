"""
components/cards.py
-------------------
Enterprise government cards, headers, advisory notices, and audit banners for MPLADS AI.
Strictly light mode, professional typography, left-accented KPI cards, and operational status pills.
"""

import base64
from pathlib import Path
import streamlit as st
from utils.formatting import get_risk_badge_html

# Load static visual assets as data URIs for crisp, reliable HTML image rendering
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

def _load_asset_data_uri(filename: str) -> str:
    path = ASSETS_DIR / filename
    if path.exists():
        try:
            b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
            ext = path.suffix.lower().replace(".", "")
            mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
            return f"data:{mime};base64,{b64}"
        except Exception:
            return ""
    return ""

_HEADER_EMBLEM_URI = _load_asset_data_uri("header_emblem.svg")
_RISK_MONITORING_URI = _load_asset_data_uri("risk_monitoring_visual.svg")
_INVESTIGATION_VISUAL_URI = _load_asset_data_uri("investigation_visual.svg")
_COMMAND_CENTER_BG_URI = _load_asset_data_uri("command_center_bg.png")


def _clean_html(html_str: str) -> str:
    """Strips leading indentation from each line to ensure Streamlit Markdown never treats HTML as preformatted code."""
    return "\n".join(line.strip() for line in html_str.strip().splitlines())


def render_header(
    title: str = "MPLADS AI",
    subtitle: str = "AI-Assisted Anomaly & Risk Monitoring System",
    tagline: str = "Monitor implementation • Detect anomalies • Enable investigation",
    show_status: bool = True,
    show_pipeline: bool = None,
    bg_image: bool = None
):
    """
    Renders the official portal header with title, subtitle, tagline, operational status area,
    and subtle enterprise visual assets (Header Emblem and compact Risk Monitoring Pipeline).
    Optionally applies the subtle building photograph background on the Command Center.
    """
    if bg_image is None:
        bg_image = (title == "MPLADS AI" and ("Command" in subtitle or "Monitoring" in subtitle or "Anomaly" in subtitle))

    status_html = """
    <div class="gov-status-badge">
        <div class="gov-status-label">SYSTEM STATUS</div>
        <div class="gov-status-val"><span class="status-dot"></span> Operational</div>
    </div>
    """ if show_status else ""

    # 1. Header Visual: Subtle 2D Parliament & Digital Governance Emblem
    emblem_html = f"""
    <div class="gov-header-emblem" style="flex-shrink: 0; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center;">
        <img src="{_HEADER_EMBLEM_URI}" width="44" height="44" alt="Government Emblem" style="display: block; width: 44px; height: 44px; border-radius: 4px;" />
    </div>
    """ if _HEADER_EMBLEM_URI else ""

    # 2. Risk Monitoring Visual: Compact Project Data -> Risk Detection -> Investigation
    # Displays in available header whitespace for the Risk Monitoring Command Center
    if show_pipeline is None:
        show_pipeline = ("Monitoring" in subtitle or "Command" in subtitle or title == "MPLADS AI")

    pipeline_html = f"""
    <div class="gov-header-pipeline" style="display: flex; align-items: center; justify-content: center;">
        <img src="{_RISK_MONITORING_URI}" height="36" alt="Risk Monitoring Pipeline" style="display: block; max-width: 380px; height: 36px;" />
    </div>
    """ if (show_pipeline and _RISK_MONITORING_URI) else ""

    custom_bg_style = ""
    extra_class = ""
    if bg_image and _COMMAND_CENTER_BG_URI:
        extra_class = "gov-header-command-center"
        custom_bg_style = (
            f'style="background-image: linear-gradient(to right, '
            f'rgba(255, 255, 255, 0.98) 0%, '
            f'rgba(255, 255, 255, 0.94) 30%, '
            f'rgba(255, 255, 255, 0.82) 55%, '
            f'rgba(255, 255, 255, 0.70) 78%, '
            f'rgba(255, 255, 255, 0.80) 100%), '
            f'url(\'{_COMMAND_CENTER_BG_URI}\'); '
            f'background-size: cover; '
            f'background-position: right center; '
            f'background-repeat: no-repeat;"'
        )

    html = f"""
    <div class="gov-header-container {extra_class}" {custom_bg_style}>
        <div class="gov-header-left" style="display: flex; align-items: center; gap: 14px;">
            {emblem_html}
            <div>
                <h1 class="gov-title-main">{title}</h1>
                <div class="gov-subtitle-main">{subtitle}</div>
                <div class="gov-tagline-main">{tagline}</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
            {pipeline_html}
            {status_html}
        </div>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)


def render_important_notice(
    title: str = "AI-Assisted Risk Screening",
    text: str = "Anomaly flags indicate potential operational deviations requiring verification. Final administrative verification remains with authorized officials."
):
    """
    Renders the subtle, professional responsible-AI advisory callout box.
    """
    html = f"""
    <div class="gov-advisory-box">
        <div class="gov-advisory-title">{title}</div>
        <div style="color:#CBD5E1; font-size: 0.9rem;">&bull;</div>
        <div class="gov-advisory-text">"{text}"</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_kpi_card(title: str, value: str, caption: str = "", card_type: str = "neutral"):
    """
    Renders a compact, left-accented enterprise KPI card with consistent height.
    card_type: 'high-risk', 'medium-risk', 'low-risk', 'general', 'neutral'
    """
    type_class = f"kpi-{card_type}"
    caption_html = f'<div class="kpi-caption">{caption}</div>' if caption else '<div class="kpi-caption">&nbsp;</div>'
    
    html = f"""
    <div class="kpi-container {type_class}">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {caption_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_audit_alert(tag: str, message: str, level: str = "danger"):
    """
    Renders a professional audit finding alert banner.
    level: 'danger' (red), 'warning' (amber), 'info' (green)
    """
    css_class = f"audit-alert-{level}"
    
    html = f"""
    <div class="{css_class}">
        <strong style="text-transform: uppercase; font-size: 0.76rem; letter-spacing: 0.04em;">{tag}:</strong> {message}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_project_summary_header(
    work_id: str,
    state: str,
    constituency: str,
    mp: str,
    category: str,
    risk_level: str,
    anomaly_score: float,
    priority_label: str
):
    """
    Renders the header dossier block for an individual project investigation in pure enterprise light mode.
    Top: PROJECT INVESTIGATION, Work ID, Risk Level badge, Risk Score, and Human-in-the-Loop Investigation visual.
    """
    badge = get_risk_badge_html(risk_level)
    
    # 3. Investigation Visual: Risk Flag -> Evidence -> Officer Review (Human-in-the-Loop)
    investigation_flow_html = f"""
    <div class="gov-investigation-flow" style="display: flex; align-items: center; justify-content: center; align-self: center; margin: 0 10px;">
        <img src="{_INVESTIGATION_VISUAL_URI}" height="38" alt="Investigation Protocol" style="display: block; max-width: 400px; height: 38px;" />
    </div>
    """ if _INVESTIGATION_VISUAL_URI else ""

    html = f"""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 5px solid #0F2B48; border-radius: 4px; padding: 1.1rem 1.25rem; margin-bottom: 1.1rem; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #64748B; margin-bottom: 2px;">
                    PROJECT INVESTIGATION &bull; CASE FILE
                </div>
                <div style="font-size: 1.45rem; font-weight: 800; color: #0F2B48; letter-spacing: -0.01em; line-height: 1.2;">
                    {work_id}
                </div>
                <div style="font-size: 0.86rem; color: #334155; margin-top: 4px;">
                    <strong>{state}</strong> &bull; Constituency: <strong>{constituency}</strong> &bull; Hon'ble MP: <strong>{mp}</strong>
                </div>
            </div>
            {investigation_flow_html}
            <div style="text-align: right; min-width: 180px;">
                <div style="margin-bottom: 4px;">{badge}</div>
                <div style="font-size: 0.82rem; color: #475569;">
                    Risk Score: <strong style="font-size: 1.05rem; color: #0F2B48;">{anomaly_score:.4f}</strong>
                </div>
                <div style="font-size: 0.72rem; color: #64748B; margin-top: 1px;">{priority_label}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)


def render_stage_indicator(stage_name: str, is_present: bool, note: str = ""):
    """
    Renders an administrative milestone indicator box with professional text styling.
    """
    if is_present:
        color = "#059669"
        bg = "#F0FDF4"
        border = "#BBF7D0"
        status_text = "RECORDED"
    else:
        color = "#DC2626"
        bg = "#FEF2F2"
        border = "#FECACA"
        status_text = "NOT RECORDED"
        
    note_html = f'<div style="font-size: 0.72rem; color: #64748B; margin-top: 2px;">{note}</div>' if note else ""
    
    html = f"""
    <div style="background-color: {bg}; border: 1px solid {border}; border-radius: 4px; padding: 0.6rem 0.5rem; text-align: center;">
        <div style="font-size: 0.72rem; font-weight: 600; color: #334155; text-transform: uppercase; letter-spacing: 0.02em;">{stage_name}</div>
        <div style="font-size: 0.82rem; font-weight: 700; color: {color}; margin-top: 2px; letter-spacing: 0.03em;">{status_text}</div>
        {note_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
