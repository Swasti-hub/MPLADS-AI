"""
views/about.py
--------------
System architecture, methodology documentation, and governance safeguards.
Organized into 6 clean informational sections:
  1. Problem Statement & Background
  2. How It Works (System Architecture & Operational Pipeline)
  3. AI Model & The 20 Operational Features
  4. Risk Interpretation & Score Calibration
  5. Human-in-the-Loop & Audit Protocol
  6. Governance & Limitations
"""

import streamlit as st
from components.cards import render_header, render_important_notice


def render_about():
    """Renders the About System and Methodology documentation page."""
    
    # Header
    render_header(
        title="About MPLADS AI System",
        subtitle="Operational Methodology, Model Specifications & Governance",
        tagline="AI-Assisted Detection of Anomalies, Risk Indicators & Inefficiencies in MPLADS Implementation",
        show_status=True
    )

    # Advisory Notice
    render_important_notice(
        title="Prototype Governance Specification",
        text="Developed as an operational technology demonstration for government-facing vigilance and expenditure oversight. All algorithms prioritize operational transparency and human-in-the-loop audit verification."
    )

    # SECTION 1: PROBLEM
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #0F2B48; border-radius: 4px; padding: 0.9rem 1.1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 1rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.35rem;">
            1. Problem Statement & Operational Challenge
        </div>
        <div style="font-size: 0.85rem; color: #334155; line-height: 1.5;">
            The Members of Parliament Local Area Development Scheme (MPLADS) handles thousands of community development 
            projects annually across 543 Lok Sabha and Rajya Sabha constituencies. Traditional oversight relies heavily on manual, 
            periodic post-completion sample audits, which face significant bottlenecks:
        </div>
        <ul style="font-size: 0.84rem; color: #475569; margin-top: 6px; margin-bottom: 0;">
            <li><strong>Delayed Anomaly Detection:</strong> Irregularities or over-disbursements are frequently discovered months after fund exhaustion.</li>
            <li><strong>Volume Bottleneck:</strong> Manually reviewing 34,000+ works with multiple payment tranches exceeds administrative capacity.</li>
            <li><strong>Information Gaps:</strong> Incomplete administrative milestones (missing sanction orders or completion records) complicate compliance verification.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # SECTION 2: HOW IT WORKS
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #2563EB; border-radius: 4px; padding: 0.9rem 1.1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 1rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.35rem;">
            2. How It Works (End-to-End Operational Pipeline)
        </div>
        <div style="font-size: 0.85rem; color: #334155; line-height: 1.5; margin-bottom: 0.6rem;">
            The system operates as an active decision-support copilot for authorized audit officers:
        </div>
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 4px; padding: 0.75rem; font-family: monospace; font-size: 0.8rem; color: #0F2B48; line-height: 1.5;">
            [1. Portal Data Ingestion] &rarr; 34,450 genuine works extracted from official portal records<br>
            [2. Feature Engineering]   &rarr; 20 operational features (sanctions, disbursements, tranches, timelines)<br>
            [3. Baseline Scoring]      &rarr; Unsupervised Isolation Forest detects multidimensional outliers<br>
            [4. Rule-Based Explainer]  &rarr; Generates human-readable audit findings (e.g. Over-Disbursement)<br>
            [5. Field Dossier Triage]  &rarr; Audit officers investigate prioritized dockets with procedural steps
        </div>
    </div>
    """, unsafe_allow_html=True)

    # SECTION 3: AI MODEL & 20 FEATURES
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #0F2B48; border-radius: 4px; padding: 0.9rem 1.1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 1rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.35rem;">
            3. AI Model & The 20 Operational Feature Dimensions
        </div>
        <div style="font-size: 0.85rem; color: #334155; line-height: 1.5; margin-bottom: 0.6rem;">
            The deployed model is an unsupervised <strong>Isolation Forest</strong> algorithm calibrated at a 5% baseline anomaly rate. 
            <strong>Macro Constituency Allocated Amount is strictly excluded</strong> to ensure scoring assesses project implementation 
            integrity rather than constituency allocation size:
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        **Financial Compliance Dimensions:**
        1. `Total_Disbursed`: Cumulative releases recorded for work
        2. `Number_of_Payments`: Installment tranches utilized
        3. `Disbursement_vs_Sanction_Ratio`: Disbursed / Sanctioned
        4. `Disbursement_Sanction_Difference`: Disbursed minus Sanctioned
        5. `Recommended_vs_Sanction_Difference`: Recommended minus Sanctioned
        6. `Recommended_vs_Sanction_Ratio`: Recommended / Sanctioned
        7. `Flag_Disbursement_Exceeds_Sanction`: Cost overrun binary indicator

        **Lifecycle Timeline Dimensions:**
        8. `Recommendation_to_Sanction_Days`: Milestone duration (median-imputed)
        9. `Sanction_to_Completion_Days`: Execution duration (median-imputed)
        10. `Flag_Negative_Sanction_Completion`: Chronology reversal indicator
        11. `Flag_Negative_Rec_Sanction`: Proposal reversal indicator
        """)
    with c2:
        st.markdown("""
        **Administrative Milestone Stages:**
        12. `Has_Recommendation`: Recommendation date documented
        13. `Has_Sanction`: Administrative sanction documented
        14. `Has_Completion`: Completion certificate documented
        15. `Has_Disbursement`: Treasury disbursement documented
        16. `Has_Payment_Data`: Installment tranche ledger documented

        **Contextual Jurisdictional Encoders:**
        17. `Work Category_Freq`: Relative frequency of category
        18. `State_Freq`: Jurisdiction project density
        19. `IDA_Freq`: Implementing District Authority frequency
        20. `Constituency_Freq`: Parliamentary constituency representation
        """)
    st.markdown("</div>", unsafe_allow_html=True)

    # SECTION 4: RISK INTERPRETATION
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #D97706; border-radius: 4px; padding: 0.9rem 1.1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 1rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.35rem;">
            4. Risk Interpretation & Threshold Stratification
        </div>
        <div style="font-size: 0.85rem; color: #334155; line-height: 1.5; margin-bottom: 0.5rem;">
            Raw Isolation Forest decision scores are calibrated to a normalized <strong>[0.0, 1.0]</strong> scale:
        </div>
        <table style="width: 100%; font-size: 0.82rem; border-collapse: collapse; margin-top: 4px;">
            <tr style="border-bottom: 1px solid #E2E8F0; text-align: left; color: #64748B;">
                <th style="padding: 6px;">Tier</th>
                <th style="padding: 6px;">Threshold</th>
                <th style="padding: 6px;">Baseline Universe</th>
                <th style="padding: 6px;">Procedural Action</th>
            </tr>
            <tr style="border-bottom: 1px solid #F1F5F9;">
                <td style="padding: 6px; font-weight: 700; color: #DC2626;">High Risk</td>
                <td style="padding: 6px;">Score &ge; 0.65</td>
                <td style="padding: 6px;">1,727 projects (5.01%)</td>
                <td style="padding: 6px;">Immediate priority audit file requisition & voucher reconciliation</td>
            </tr>
            <tr style="border-bottom: 1px solid #F1F5F9;">
                <td style="padding: 6px; font-weight: 700; color: #D97706;">Medium Risk</td>
                <td style="padding: 6px;">0.50 &le; Score &lt; 0.65</td>
                <td style="padding: 6px;">3,442 projects (9.99%)</td>
                <td style="padding: 6px;">Targeted administrative review during routine district inspections</td>
            </tr>
            <tr>
                <td style="padding: 6px; font-weight: 700; color: #059669;">Low Risk</td>
                <td style="padding: 6px;">Score &lt; 0.50</td>
                <td style="padding: 6px;">29,281 projects (85.00%)</td>
                <td style="padding: 6px;">Standard automated quarterly expenditure monitoring</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # SECTION 5: HUMAN-IN-THE-LOOP
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #059669; border-radius: 4px; padding: 0.9rem 1.1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 1rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.35rem;">
            5. Human-in-the-Loop Verification Protocol
        </div>
        <div style="font-size: 0.85rem; color: #334155; line-height: 1.5;">
            The platform adheres strictly to government audit jurisprudence:
        </div>
        <ul style="font-size: 0.84rem; color: #475569; margin-top: 6px; margin-bottom: 0;">
            <li><strong>Screening, Not Conviction:</strong> Anomaly flags indicate statistical deviations, not confirmed fraud. Legitimate administrative reasons (such as revised offline sanction orders) may explain deviations.</li>
            <li><strong>Audit File Reconciliation:</strong> Field verification steps are provided as procedural guidance to retrieve specific voucher numbers and sanction orders.</li>
            <li><strong>Human Prerogative:</strong> All administrative, financial, or legal findings remain solely with competent statutory authorities.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # SECTION 6: LIMITATIONS
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #64748B; border-radius: 4px; padding: 0.9rem 1.1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
        <div style="font-size: 1rem; font-weight: 700; color: #0F2B48; margin-bottom: 0.35rem;">
            6. System Limitations & Future Enhancements
        </div>
        <ul style="font-size: 0.84rem; color: #475569; margin-top: 6px; margin-bottom: 0;">
            <li><strong>Data Dependency:</strong> Screening accuracy is bounded by the quality and timeliness of portal data entry by District Implementing Authorities.</li>
            <li><strong>Offline Approvals:</strong> Sanctions or revisions approved offline but not updated in portal records will generate informational flags until updated.</li>
            <li><strong>Future Scope:</strong> Geo-tagged site photo verification via computer vision and contractor tax identification cross-referencing.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
