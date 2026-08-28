# Phase 7 Log — Streamlit Dashboard (Updated for Corrected Model)

**Original date:** 2026-08-14

**Updated date:** 2026-08-17 (reflects the Phase 4/5 methodology correction)

**Purpose:** Deploy the corrected Phase 5 final model as an interactive, explainable, honestly-reported dashboard.

## What Changed From the Original Version

- **Data source path:** category-grouping reference now loads `train_final_v2.csv` (the corrected training file) instead of the original `train_set_v2.csv`.
- **Model artifacts:** all `.pkl` files reference the corrected model (212 features, threshold 0.15).
- **All displayed metrics:** updated to show the honest, single-evaluation **test** PR-AUC (0.2565) as the primary headline number, rather than the original flawed 0.2857.
- **Experimentation log table (Tab 1):** restructured to show validation PR-AUC for every development decision, with the final row explicitly labeled as the one-time test-set result — making the validation/test distinction visible to anyone using the dashboard, not just documented in the README.
- **Project Journey tab (Tab 4):** Phase 4 and Phase 5 descriptions rewritten to explain the 3-way split and the methodology correction directly within the dashboard's narrative.
- **Correlation figure:** updated from 0.81 to 0.79 in the Explainability tab's write-up.

## Structure (Unchanged)

**Page Configuration:** Custom dark navy/red theme, branded header with custom logo, hidden default Streamlit chrome.

**Data & Model Loading:** Cached loading, reusing the corrected Phase 5 preprocessing pipeline exactly.

**Sidebar:** Live decision threshold slider, "About This Model" stats block now showing test-set PR-AUC as the primary figure.

**Tabs:**
1. **Model Overview** — live-reactive metrics + confusion matrix + the full validation-based experimentation log with the final test-set result clearly separated.
2. **Fraud Risk Predictor** — transaction picker, live prediction, live SHAP waterfall.
3. **Explainability** — cached global SHAP + permutation importance, updated correlation figure.
4. **Project Journey** — updated phase narrative including the methodology correction story, honest limitations updated to reference the corrected test PR-AUC.

## Key Design Decision (New)

**Why show the test PR-AUC prominently, not the higher validation number:** the dashboard is meant to represent the model's honest, defensible real-world performance to anyone reviewing it — using the validation number (which was involved in development decisions) would repeat the same methodological issue the project corrected. The test PR-AUC (0.2565), evaluated exactly once, is the number a viewer should trust.

## Conclusion
Phase 7 (updated) presents the corrected, honestly-evaluated model, with the methodology correction itself made visible and explained directly within the dashboard — not just in the README — so anyone interacting with the live tool understands exactly what number they're looking at and why it's trustworthy.

**Phase 7 status: Complete (updated for corrected model).**