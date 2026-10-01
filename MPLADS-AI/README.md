# AI-Powered MPLADS Anomaly & Fraud-Risk Detection System

An end-to-end Machine Learning pipeline designed for public governance oversight in the **Members of Parliament Local Area Development Scheme (MPLADS)**. The system audits developmental work execution data, detecting anomalous funding, timeline deviations, and administrative discrepancies using unsupervised machine learning and auditable decision rules.

---

## 1. Project Objective
Under MPLADS, each Member of Parliament (MP) recommends developmental works within their constituency, which are then reviewed, administratively sanctioned, and executed by designated district authorities. With tens of thousands of projects implemented annually across India, manual auditing of every project is impractical.

**Goal**: Automatically identify high-risk projects that exhibit statistically unusual behavior or administrative discrepancies (e.g., budget overruns, timeline reversals, or unrecorded sanctions) to empower auditors with prioritized investigation queues.

> **Crucial Ethical & Governance Principle**: The model flags projects as **"Potential Anomaly / Requires Investigation"**, and **never** claims confirmed fraud. Missing data is handled neutrally and is never treated as an indicator of fraud.

---

## 2. Dataset Overview
- **Source**: `master.xlsx` (`Sheet1`)
- **Total Genuine Projects**: `34,450` project works (1 embedded portal grand-total export artifact excluded)
- **Original Dimensions**: 34,450 rows × 17 columns
- **Preservation Policy**: **100% of genuine projects are retained** (0 genuine projects dropped). `Work ID` is strictly preserved as an identifier and never used as a machine learning feature.

### Key Fields:
- **Identifiers & Entity**: `Work ID`, `State`, `IDA` (Implementing District Authority), `Constituency`, `Hon'ble Members of Parliament`
- **Work Details**: `Work Category`, `Work Description`, `Work_Status`
- **Milestone Dates**: `Recommended_Date`, `Sanction_Date`, `Completion Date`
- **Financial Details**: `Allocated_Amount` (retained for contextual reporting), `Amount Disbursed ( ₹ )`, `Total_Disbursed`, `Number_of_Payments`, `Recommended_Amount`, `Sanction_Amount`

---

## 3. Data Preparation & Missing Value Handling
A fundamental challenge in public expenditure datasets is that projects exist at different stages of their lifecycle:
1. **Unreached Stages**: If a project has not yet been administratively sanctioned, `Sanction_Amount` and `Sanction_Date` will naturally be missing.
2. **Neutral Treatment**: Under standard audit rules, unreached stages are **not** fraudulent.
3. **Engineering Solution**:
   - Indicator variables (`Has_Recommendation`, `Has_Sanction`, `Has_Completion`, `Has_Disbursement`) explicitly encode which milestones have occurred.
   - Missing duration differences are imputed with `0.0`, accompanied by the indicator flag so the model recognizes process status rather than penalizing missing values.
   - Ratios where denominators are absent default to `1.0` (neutral baseline).

---

## 4. Feature Engineering
The pipeline derives meaningful quantitative features reflecting operational health:

| Feature Name | Description | Calculation / Purpose |
|---|---|---|
| `Recommendation_to_Sanction_Days` | Days between recommendation and sanction | Administrative review speed |
| `Sanction_to_Completion_Days` | Days between sanction and project completion | Execution timeline efficiency |
| `Flag_Negative_Sanction_Completion` | Binary flag for date order anomaly | `1` if completion precedes sanction date |
| `Flag_Negative_Rec_Sanction` | Binary flag for date order anomaly | `1` if sanction precedes recommendation date |
| `Disbursement_vs_Sanction_Ratio` | Disbursed to sanction ratio | Ratio > 1.0 indicates potential budget overrun |
| `Disbursement_Sanction_Difference` | Monetary overrun / savings (₹) | `Total_Disbursed - Sanction_Amount` |
| `Recommended_vs_Sanction_Difference` | Variance between requested and approved (₹) | `Recommended_Amount - Sanction_Amount` |
| `Recommended_vs_Sanction_Ratio` | Ratio of requested to approved funding | Highlights abnormal budget inflation/deflation |
| `Flag_Disbursement_Exceeds_Sanction` | Over-disbursement indicator | `1` if disbursed exceeds sanction by > ₹1,000 |
| `Has_Recommendation`, `Has_Sanction`, `Has_Completion`, `Has_Disbursement` | Lifecycle presence flags (0 or 1) | Prevents missing data misclassification |
| `Has_Payment_Data` | Payment record presence flag (0 or 1) | Distinguishes untracked payment data from true zero payments |
| `Work Category_Freq`, `State_Freq`, `IDA_Freq`, `Constituency_Freq` | Normalized frequency encoding | Captures institutional project density without dimensional explosion |

---

## 5. ML Methodology: Isolation Forest
An unsupervised learning strategy is required because public expenditure data lacks verified labels of fraudulent projects.

### Why Isolation Forest?
- Operates on the principle that anomalies are "few and different".
- Isolates anomalous instances near the root of decision trees (fewer splits required) compared to normal clustered inliers.
- Efficiently processes multidimensional interactions without assuming Gaussian distributions.
- Scaled using `RobustScaler` to prevent extreme budget outliers from distorting median representations.

### Model Parameters:
- `n_estimators = 150`
- `contamination = 0.05` (5% baseline anomaly contamination rate)
- `random_state = 42` (ensuring 100% deterministic reproducibility)

---

## 6. Risk Scoring & Stratification
1. **Raw Decision Function**: `raw_score = -model.score_samples(X_scaled)` (higher values represent higher abnormality).
2. **Normalized Anomaly Score**: Min-Max mapped into `[0.0, 1.0]`.
3. **Risk Tier Stratification**:
   - **High Risk**: Scores in the **Top 5%** (>= 95th percentile). Priority investigation required.
   - **Medium Risk**: Scores between the **85th and 95th percentiles**. Secondary review recommended.
   - **Low Risk**: Scores below the **85th percentile**. Typical and standard project execution.

---

## 7. Human-in-the-Loop Risk Explanation
Machine learning scores alone are insufficient for public accountability. The `risk_explanation.py` module evaluates domain rules to translate statistical anomalies into actionable human-readable explanations:
- **Budget Overrun**: Total disbursed exceeds sanction amount.
- **Timeline Discrepancies**: Completion precedes sanction or sanction precedes recommendation.
- **Extended Process Duration**: Completion duration exceeding the 99th percentile (> 2 years).
- **Tranche Discrepancies**: Unusually high payment counts (e.g. >= 10 installments) or positive disbursements with 0 installments.
- **Missing Stage Discrepancy**: Funds disbursed without documented administrative sanction.
- **Financial Exposure**: Project funding in the extreme 99.5th percentile.

---

## 8. Installation & Usage

### Prerequisites
- Python 3.10+
- Install dependencies:
```bash
pip install -r requirements.txt
```

### Launch Streamlit Risk Monitoring Web Application
To run the enterprise government risk monitoring web portal:
```bash
streamlit run app.py
```
Access the application locally at `http://localhost:8501`.
The portal is styled strictly in **Light Mode** (`#FFFFFF` / `#F8FAFC`) with deep navy typography (`#0F2B48`), subtle borders, compact KPI cards, and custom clickable navigation tabs.

### Run Full End-to-End Pipeline
To ingest data, run EDA, engineer features, train the Isolation Forest, score all records, and generate audit reports with a single command:
```bash
python train_pipeline.py
```

### Score New Data via CLI
To score a new batch of MPLADS data using the persisted model from the command line:
```bash
python predict.py --input "path/to/new_projects.xlsx" --output "outputs/new_predictions.csv"
```

---

## 9. Project Directory Structure
```
e:\sih project\
├── app.py                     # Main Streamlit application entry point & router
├── config.py                  # Central paths, hyperparameters, and thresholds
├── data_analysis.py           # Ingestion, validation, type cleaning & EDA report
├── feature_engineering.py     # Timeline, ratio, indicator, and frequency engineering
├── anomaly_model.py           # Isolation Forest training, normalization, and joblib saving
├── risk_explanation.py        # Audit-grade explanations and summary generation
├── train_pipeline.py          # End-to-end reproducible orchestrator
├── predict.py                 # Batch scoring CLI for new records
├── requirements.txt           # Python dependencies
├── .streamlit/
│   └── config.toml            # Enforces strict light mode theme and server options
├── components/                # Modular UI components
│   ├── cards.py               # Compact KPI cards & non-accusatory alert banners
│   ├── charts.py              # Plotly light-mode charts (Donut, Bars, Scatter)
│   ├── tables.py              # Enterprise project roster with Action column
│   └── styles.py              # Government enterprise CSS stylesheet
├── services/                  # Business logic & data access services
│   ├── data_service.py        # Cached data loader, KPI calculator & filters
│   ├── investigation_service.py # Dossier synthesis & rule-based audit actions
│   └── prediction_service.py  # Inference on uploaded CSV/XLSX without retraining
├── views/                     # Multi-page application views
│   ├── command_center.py      # Landing dashboard (KPIs, Donut, Bar, Top Priority, Upload)
│   ├── risk_investigation.py  # Multi-parameter filtering & case lookup workbench
│   ├── project_details.py     # Full case dossier (Financial, Payments, Timeline, Actions)
│   ├── analyze_new_data.py    # Inference hub with step-by-step validation & demo batch
│   ├── geographic_risk.py     # State & Constituency risk drilldown
│   ├── analytics.py           # Diagnostics on expenditure compliance & timelines
│   ├── reports.py             # Export center (CSV dockets & printable case memos)
│   └── about.py               # 20 operational features & SIH demo guide
├── outputs/                   # Generated artifacts
│   ├── cleaned_data.csv       # 34,450 cleaned genuine projects
│   ├── feature_engineered_data.csv # Projects with 20 ML features
│   ├── master_with_risk.csv   # Complete dataset with anomaly scores, risk levels & reasons
│   ├── anomaly_summary.csv    # Aggregated risk distribution by State and Category
│   └── trained_model.joblib   # Persisted model, scaler, and learned preprocessing mappings
└── README.md                  # Comprehensive system documentation
```

---

## 10. SIH 3–5 Minute Demonstration Script
1. **Command Center (1 min)**:
   - Point out national metrics: 34,450 genuine projects, 1,727 High Risk (5.01%), 1,719 Flagged Anomalies (4.99%), ₹1,669.50 Cr disbursed.
   - Explain the operational paradigm: **MONITOR &rarr; DETECT &rarr; EXPLAIN &rarr; INVESTIGATE**.
   - Show the two central charts: Risk Stratification Donut and Root Cause Classification Bar.
2. **Priority Investigations (1 min)**:
   - Show the table with `Work ID`, `State`, `Sanction Amount`, `Total Disbursed`, `Payments`, `Risk Score`, `Risk Level`, `Primary Reason`, and `Action`.
   - Select a project and click **View / Investigate &rarr;**.
3. **Project Case Dossier (1.5 min)**:
   - Walk through the evidence:
     - **Financial Check**: Over-disbursement amount or unrecorded sanction.
     - **Payment Analysis**: Multi-tranche installment count against 95th percentile benchmark.
     - **Timeline Check**: Milestone dates and chronology reversals.
     - **Administrative Check**: Presence of MP proposal, sanction, completion, and payment data.
     - **Recommended Actions**: Specific procedural verification steps for the investigating officer.
4. **Analyze New Data (1 min)**:
   - Navigate to **Analyze New Data** (or use the upload section on the Command Center).
   - Click **"Load Demo Batch (50 Records)"** &rarr; **"Execute Risk Screening with Deployed Model"**.
   - Show newly generated anomaly scores, risk tiers, and explanations generated **instantly without retraining the model**.

---

## 11. Limitations & Governance Safeguards
1. **Unsupervised Nature**: Isolation Forest flags statistical deviations, not verified legal culpability.
2. **Data Entry Errors vs Malpractice**: An anomalous score may result from clerical errors in date entries rather than intentional fraud.
3. **Mandatory Human-in-the-Loop**: High-risk flags serve strictly as triage mechanisms for human vigilance officers and auditors, never as automated disciplinary determinations.
4. **Strict Audit Terminology**: Terms like *"Confirmed Fraud"* or *"Fraud Detected"* are strictly prohibited; the platform uses *"Requires Investigation"*, *"Potential Anomaly"*, and *"Potential Over-Disbursement"*.
