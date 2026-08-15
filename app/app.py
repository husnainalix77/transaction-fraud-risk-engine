import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import sys
import os
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score

FEATURE_COLUMNS = joblib.load("models/feature_columns_final.pkl")

# 1. Page Configuration
st.set_page_config(
    page_title="Transaction Fraud Risk Engine",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

/* GLOBAL THEME */

.stApp {
    background-color: #0B1120;
    color: #E5E7EB;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #1F2937;
}

[data-testid="stSidebar"] * {
    color: #E5E7EB;
}

.dashboard-header {
    background: linear-gradient(135deg, #111827 0%, #172033 100%);
    border: 1px solid #273449;
    border-left: 5px solid #EF4444;
    border-radius: 14px;
    padding: 24px 30px;
    margin-bottom: 28px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}

.dashboard-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #F9FAFB;
    margin-bottom: 6px;
}

.dashboard-tagline {
    font-size: 1rem;
    color: #9CA3AF;
    margin-top: 0;
}

.dashboard-accent {
    color: #F87171;
}

[data-testid="stMetric"] {
    background: #111827;
    border: 1px solid #273449;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.20);
    transition: all 0.2s ease;
}

[data-testid="stMetric"]:hover {
    border-color: #EF4444;
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(239, 68, 68, 0.12);
}

[data-testid="stMetricLabel"] {
    color: #9CA3AF !important;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #F9FAFB !important;
    font-weight: 800;
}

[data-testid="stMetricDelta"] {
    color: #F87171 !important;
}

.dashboard-section {
    color: #F9FAFB;
    font-size: 1.35rem;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 15px;
    border-left: 4px solid #F97316;
    padding-left: 12px;
}

[data-testid="stDataFrame"] {
    border: 1px solid #273449;
    border-radius: 10px;
    overflow: hidden;
}

.stButton > button {
    background-color: #DC2626;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background-color: #EF4444;
    border: none;
}

.risk-high {
    color: #F87171;
    font-weight: 700;
}

.risk-medium {
    color: #FB923C;
    font-weight: 700;
}

.risk-low {
    color: #34D399;
    font-weight: 700;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# Branded Header
st.markdown("""
<div class="dashboard-header">
    <div class="dashboard-title">🕵️ Transaction <span class="dashboard-accent">Fraud Risk</span> Engine</div>
    <div class="dashboard-tagline">
        End-to-end fraud detection — SQL feature engineering, imbalance-aware modeling,
        calibration &amp; explainability, built on real transaction data.
    </div>
</div>
""", unsafe_allow_html=True)


@st.cache_data
def load_raw_test_data():
    test_df = pd.read_csv("data/processed/test_set_v2.csv")
    return test_df


def preprocessing(test_df):
    drop_cols = ["isFraud", "TransactionID", "TransactionDT"]
    categorical_cols = ["ProductCD", "card4", "card6", "addr1", "P_emaildomain"]
    numerical_missing_cols = ["card_avg_amt_so_far", "amt_deviation_ratio"]

    v_cols = [c for c in test_df.columns if c.startswith("V")]

    for col in v_cols:
        test_df[col] = test_df[col].fillna(-1)

    for col in categorical_cols:
        test_df[col] = test_df[col].fillna("Missing")

    for col in numerical_missing_cols:
        test_df[col] = test_df[col].fillna(-1)

    cols = ["addr1", "P_emaildomain"]
    threshold_map = {"addr1": 55, "P_emaildomain": 30}

    train_df_ref = pd.read_csv("data/processed/train_set_v2.csv")
    for col in categorical_cols:
        train_df_ref[col] = train_df_ref[col].fillna("Missing")

    for col in cols:
        counts = train_df_ref[col].value_counts()
        top_categories = counts[counts >= threshold_map[col]].index
        test_df[col] = test_df[col].apply(lambda x: x if x in top_categories else "Other")

    y_test = test_df["isFraud"].copy()
    test_df = test_df.drop(columns=drop_cols)

    test_df_encoded = pd.get_dummies(test_df, columns=categorical_cols)
    test_df_encoded = test_df_encoded.reindex(columns=FEATURE_COLUMNS, fill_value=0)

    return test_df_encoded, y_test


# 2. Data & Model Loading
@st.cache_data
def load_data():
    test_df = load_raw_test_data()
    test_df_encoded, y_test = preprocessing(test_df)
    return test_df_encoded, y_test


@st.cache_resource
def load_models():
    model = joblib.load("models/fraud_model_final.pkl")
    decision_threshold = joblib.load("models/decision_threshold.pkl")
    return model, decision_threshold


model, decision_threshold = load_models()
test_df_encoded, y_test = load_data()


# 3. Sidebar
st.sidebar.markdown("### 🎚️ Decision Threshold")
threshold = st.sidebar.slider(
    "Decision Threshold",
    min_value=0.0,
    max_value=1.0,
    value=float(decision_threshold),
    step=0.01,
    help="Adjust to see the precision/recall tradeoff — lower catches more fraud but raises false alarms."
)
st.sidebar.markdown("---")
with st.sidebar:
    st.image("app/assets/logo.png", width=100)
    st.markdown("### 📊 About This Model")
    st.metric(label="Fraud Rate", value="3.5%")
    st.metric(label="PR-AUC", value="0.2857", delta="+50% vs baseline")
    st.metric(label="Precision", value="0.30")
    st.metric(label="Recall", value="0.37")
    st.metric(label="Features Used", value="214")
    st.metric(label="Test Set Size", value=f"{len(test_df_encoded):,}")
    st.markdown("---")
    st.markdown("### 👨‍💻 Project")
    st.markdown("**Author:** Husnain Maroof")
    st.markdown("**GitHub:** [husnainalix77](https://github.com/husnainalix77)")
    st.markdown("---")
    st.caption(
        "PR-AUC is preferred for evaluating performance under severe class imbalance."
    )

# 4. Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Model Overview",
    "🔍 Fraud Risk Predictor",
    "📈 Explainability",
    "🧠 Project Journey"
])


@st.cache_data
def get_predictions(_model, X):
    probas = _model.predict_proba(X)[:, 1]
    return probas


# Tab 1 — Model Overview
with tab1:
    st.markdown('<div class="dashboard-section">Live Model Performance</div>', unsafe_allow_html=True)
    st.caption(
        "Metrics below update live as you move the Decision Threshold slider in the sidebar."
    )

    probas = get_predictions(model, test_df_encoded)
    predictions = (probas >= threshold).astype(int)

    live_precision = precision_score(y_test, predictions, zero_division=0)
    live_recall = recall_score(y_test, predictions, zero_division=0)
    live_f1 = f1_score(y_test, predictions, zero_division=0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("PR-AUC (fixed)", "0.2857", "+50% vs baseline")
    col2.metric("Precision", f"{live_precision:.2f}")
    col3.metric("Recall", f"{live_recall:.2f}")
    col4.metric("F1-score", f"{live_f1:.2f}")

    st.markdown('<div class="dashboard-section">Confusion Matrix</div>', unsafe_allow_html=True)

    cm = confusion_matrix(y_test, predictions)
    cm_labels = ["Non-fraud", "Fraud"]

    plt.figure(figsize=(9, 7))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        square=True,
        cmap="Blues",
        xticklabels=cm_labels,
        yticklabels=cm_labels
    )

    cm_percent = cm / cm.sum() * 100
    for i in range(2):
        for j in range(2):
            plt.text(j + 0.5, i + 0.75, f'({cm_percent[i, j]:.1f}%)',
                      ha='center', va='center', fontsize=9, color='red')

    plt.title("Confusion Matrix - XGBoost Classifier", fontweight="bold")
    plt.xlabel("Predicted", fontweight="bold")
    plt.ylabel("Actual", fontweight="bold")
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.close()

    st.markdown('<div class="dashboard-section">Full Experimentation Log</div>', unsafe_allow_html=True)
    st.caption("Every approach tested during Phase 5 — including what didn't work.")

    experiment_data = pd.DataFrame({
        "Approach": [
            "Baseline (default XGBoost)",
            "scale_pos_weight",
            "SMOTE",
            "Hyperparameter tuning",
            "Engineered time/hour features",
            "+65 Vesta V-columns"
        ],
        "PR-AUC": ["N/A (Accuracy 0.9648)", "0.1907", "0.1837", "0.1903", "0.1533–0.1809", "0.2857"],
        "Decision": [
            "Accuracy proved misleading",
            "Adopted over SMOTE",
            "Rejected — worse",
            "Rejected — negligible gain",
            "Rejected — hurt performance",
            "Final model"
        ]
    })
    st.dataframe(experiment_data, use_container_width=True, hide_index=True)

# Tab 2 — Fraud Risk Predictor
with tab2:
    st.markdown('<div class="dashboard-section">Select a Transaction</div>', unsafe_allow_html=True)

    raw_test_df = load_raw_test_data()

    col_a, col_b = st.columns([1, 2])
    with col_a:
        row_index = st.number_input(
            "Transaction row index",
            min_value=0,
            max_value=len(raw_test_df) - 1,
            value=0,
            step=1,
            help="Pick any row from the test set (0 to {})".format(len(raw_test_df) - 1)
        )

    selected_raw = raw_test_df.iloc[[row_index]]
    actual_label = "Fraud" if selected_raw["isFraud"].values[0] == 1 else "Not Fraud"

    with col_b:
        st.markdown(f"**Actual Label:** {actual_label}")
        st.markdown(f"**Transaction Amount:** ${selected_raw['TransactionAmt'].values[0]:.2f}")
        st.markdown(f"**Product Category:** {selected_raw['ProductCD'].values[0]}")
        st.markdown(f"**Card Network:** {selected_raw['card4'].values[0]}")
        st.markdown(f"**Card Type:** {selected_raw['card6'].values[0]}")

    st.markdown('<div class="dashboard-section">Model Prediction</div>', unsafe_allow_html=True)

    selected_encoded = test_df_encoded.iloc[[row_index]]
    selected_proba = model.predict_proba(selected_encoded)[:, 1][0]
    predicted_label = "Fraud" if selected_proba >= threshold else "Not Fraud"

    if selected_proba >= 0.5:
        risk_class = "risk-high"
    elif selected_proba >= threshold:
        risk_class = "risk-medium"
    else:
        risk_class = "risk-low"

    col_c, col_d, col_e = st.columns(3)
    col_c.metric("Predicted Probability", f"{selected_proba:.3f}")
    col_d.markdown(
        f"**Predicted:** <span class='{risk_class}'>{predicted_label}</span>",
        unsafe_allow_html=True
    )
    col_e.markdown(f"**Actual:** {actual_label}")

    if predicted_label == actual_label:
        st.success("✅ Correct prediction")
    else:
        st.error("❌ Incorrect prediction")

    st.markdown('<div class="dashboard-section">Why This Prediction? (SHAP Explanation)</div>', unsafe_allow_html=True)

    import shap

    xgb_models = [
        calibrated_model.estimator
        for calibrated_model in model.calibrated_classifiers_
    ]

    explainer_single = shap.TreeExplainer(xgb_models[0])
    single_shap = explainer_single(selected_encoded)

    fig, ax = plt.subplots(figsize=(9, 6))
    shap.plots.waterfall(single_shap[0], max_display=12, show=False)
    st.pyplot(fig)
    plt.close()

# Tab 3 — Explainability
with tab3:
    st.markdown('<div class="dashboard-section">Global Feature Importance (SHAP)</div>', unsafe_allow_html=True)
    st.caption("Computed on a 2,000-row sample for performance. Shows which features drive fraud predictions across all transactions.")

    @st.cache_data
    def compute_global_shap(_model, X, sample_size=2000):
        X_sample = X.sample(n=min(sample_size, len(X)), random_state=42)

        xgb_models = [
            calibrated_model.estimator
            for calibrated_model in _model.calibrated_classifiers_
        ]

        all_shap_values = []
        for m in xgb_models:
            explainer = shap.TreeExplainer(m)
            shap_vals = explainer(X_sample)
            all_shap_values.append(shap_vals.values)

        mean_shap = np.mean(all_shap_values, axis=0)
        return mean_shap, X_sample

    mean_shap_values, X_shap_sample = compute_global_shap(model, test_df_encoded)

    fig1 = plt.figure(figsize=(10, 8))
    shap.summary_plot(mean_shap_values, X_shap_sample, max_display=15, show=False)
    st.pyplot(fig1)
    plt.close()

    st.markdown('<div class="dashboard-section">Permutation Importance</div>', unsafe_allow_html=True)
    st.caption("Measures how much model performance drops when each feature is randomly shuffled.")

    @st.cache_data
    def compute_permutation_importance(_model, X, y, sample_size=2000):
        from sklearn.inspection import permutation_importance

        idx = X.sample(n=min(sample_size, len(X)), random_state=42).index
        X_sample = X.loc[idx]
        y_sample = y.loc[idx]

        result = permutation_importance(
            estimator=_model,
            X=X_sample,
            y=y_sample,
            scoring="average_precision",
            n_repeats=3,
            random_state=42,
            n_jobs=-1
        )

        perm_df = pd.DataFrame({
            "feature": X_sample.columns,
            "importance": result.importances_mean
        }).sort_values(by="importance", ascending=False).head(15)

        return perm_df

    perm_df = compute_permutation_importance(model, test_df_encoded, y_test)

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.barplot(data=perm_df, x="importance", y="feature", color="#EF4444", ax=ax2)
    ax2.set_xlabel("Importance (PR-AUC drop when shuffled)")
    ax2.set_title("Top 15 Features by Permutation Importance", fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    st.markdown('<div class="dashboard-section">Why Some Features Rank Differently</div>', unsafe_allow_html=True)
    st.markdown("""
    SHAP and permutation importance sometimes disagree — and it's not a contradiction.
    **`card_avg_amt_so_far`** ranks highly in SHAP but low in permutation importance.
    This is because it's correlated (0.81) with `TransactionAmt` — when `card_avg_amt_so_far`
    is shuffled, the model simply leans on `TransactionAmt` instead, so performance barely drops.
    SHAP still gives it credit because it genuinely contributes to individual predictions —
    permutation importance measures *marginal necessity*, not *standalone value*.
    """)      

# Tab 4 — Project Journey
with tab4:
    st.markdown('<div class="dashboard-section">The Story Behind This Model</div>', unsafe_allow_html=True)
    st.markdown("""
    This dashboard is the final output of a 7-phase, end-to-end fraud detection project —
    built from raw transaction data through to a calibrated, explainable, deployed model.
    """)

    st.markdown('<div class="dashboard-section">Phase-by-Phase Summary</div>', unsafe_allow_html=True)

    phases = [
        ("1️⃣ MySQL Ingestion & Verification",
         "Loaded 590,540 transactions into MySQL via a memory-safe, chunked pipeline. "
         "Every load independently verified — row counts, columns, nulls, and values — "
         "not just assumed to have worked."),
        ("2️⃣ SQL Feature Engineering",
         "Built engineered features (has_identity_data, rolling card behavior, deviation ratios) "
         "entirely in SQL using CTEs and window functions, all time-respecting to prevent leakage."),
        ("3️⃣ Statistical Validation",
         "Every candidate feature tested with chi-square (categorical) or KS-tests (numeric) — "
         "7 out of 7 features confirmed statistically significant, not just visually suggestive."),
        ("4️⃣ Time-Aware Split",
         "Split by transaction time, not randomly — trained on the past, tested on the future, "
         "with zero overlap verified directly from the data."),
        ("5️⃣ Imbalance-Aware Modeling & Calibration",
         "Tested 5 approaches head-to-head (scale_pos_weight, SMOTE, tuning, engineered features, "
         "V-column expansion) — judged by PR-AUC, not misleading accuracy. Final PR-AUC: 0.2857, "
         "a ~50% improvement over the initial approach."),
        ("6️⃣ Explainability",
         "SHAP and permutation importance applied and cross-checked against each other — "
         "every disagreement between the two methods explained, not just observed."),
        ("7️⃣ This Dashboard",
         "A live, interactive deployment of the final model — explore predictions, "
         "explanations, and the full experimentation history yourself."),
    ]

    for title, description in phases:
        with st.expander(title):
            st.write(description)

    st.markdown('<div class="dashboard-section">Honest Limitations</div>', unsafe_allow_html=True)
    st.warning("""
    **This model is not production-ready as-is, and that's stated deliberately:**
    - Recall of 37% means nearly two-thirds of fraud still goes undetected — a real ceiling
      given the current feature set and single-model approach.
    - The decision threshold reflects a default assumption (missed fraud costs more than a
      false alarm), not an actual calculated business cost ratio.
    - Matching industry-standard performance (70–90%+ recall with manageable false alarms)
      would require substantially more features, ensemble modeling, and continuously
      updated production data — outside this project's scope.
    """)

    st.markdown('<div class="dashboard-section">Links</div>', unsafe_allow_html=True)
    st.markdown("""
    - 📂 [Full GitHub Repository](https://github.com/husnainalix77/transaction-fraud-risk-engine)
    - 📓 [Jupyter Notebooks (all 7 phases)](https://github.com/husnainalix77/transaction-fraud-risk-engine/tree/main/notebooks)
    - 📄 [Detailed Phase Logs](https://github.com/husnainalix77/transaction-fraud-risk-engine/tree/main/docs)
    """)      