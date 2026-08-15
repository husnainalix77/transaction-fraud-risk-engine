# Phase 7 Log — Streamlit Dashboard

**Date:** 2026-08-14
**Purpose:** Deploy the Phase 5 final model as an interactive, explainable dashboard — making the project's results tangible and explorable, not just documented in notebooks.

## Structure

**Page Configuration:** Custom dark navy/red theme via injected CSS, branded header with custom-designed logo, hidden default Streamlit chrome for a polished, non-generic appearance.

**Data & Model Loading:** Cached loading of the final calibrated model, feature columns, and decision threshold (`@st.cache_resource`); cached loading and preprocessing of the test set, exactly replicating Phase 5's pipeline (imputation, rare-category grouping fit on training data, one-hot encoding, column reindexing) to guarantee consistency with the deployed model.

**Sidebar:** Interactive decision threshold slider (live-reactive across the app), full "About This Model" stats block (PR-AUC, precision, recall, features used, test set size, fraud rate), custom logo, author/GitHub links.

**Tabs:**
1. **Model Overview** — live-recalculating precision/recall/F1 and confusion matrix as the threshold slider moves, plus the full 6-approach experimentation log (baseline, scale_pos_weight, SMOTE, tuning, failed features, V-columns).
2. **Fraud Risk Predictor** — pick any test-set transaction by row index, view its raw details, get a live prediction at the current threshold, and see a live single-transaction SHAP waterfall explanation.
3. **Explainability** — cached global SHAP summary plot and permutation importance chart (2,000-row sample), with written explanation of the SHAP-vs-permutation ranking discrepancies tied directly to Phase 5's multicollinearity finding.
4. **Project Journey** — phase-by-phase expandable summary, honest limitations section, links to the full repository.

## Key Design Decisions

- **Threshold slider is interactive across the whole app**, not just Tab 1 — Tab 2's individual predictions also respect the current slider value, making the precision/recall tradeoff genuinely explorable rather than a static, pre-baked number.
- **Two-tier caching strategy:** cheap, threshold-dependent calculations (predictions, confusion matrix) recompute live on every interaction; expensive, threshold-independent calculations (SHAP, permutation importance) are cached once via `@st.cache_data`/`@st.cache_resource`.
- **Single-row SHAP (Tab 2) computed live**, since it's fast enough; full-dataset SHAP (Tab 3) is sampled and cached, since it's not.
- **Preprocessing logic is fully reused from Phase 5/6**, not reimplemented — the dashboard's predictions are guaranteed consistent with the notebook-evaluated model, not a simplified approximation.

## Issues Encountered & Resolved

- **Relative path errors** (`FileNotFoundError`): notebook-style `../` paths don't apply to Streamlit, which runs from the invocation directory (project root), not the script's own folder. Fixed by removing `../` prefixes throughout.
- **`plt.show()` silently does nothing in Streamlit**: matplotlib figures require `st.pyplot(plt.gcf())` to actually render on the page.
- **Sidebar stats initially failed to render**: an early draft assigned Python variables (`label=..., value=...`) instead of actually calling `st.metric(...)` — valid syntax, but functionally dead code.
- **Variable shadowing risk**: a local `labels = ["Non-fraud", "Fraud"]` variable inside Tab 1 shadowed an earlier `labels` variable holding the actual `isFraud` Series — renamed to avoid ambiguity.

## Conclusion
Phase 7 is complete. The dashboard is a fully interactive, explainable deployment of the final model, reusing every phase's work (SQL features, statistical validation, the time-aware split, the calibrated model, and both explainability methods) in one cohesive, professional interface — closing out the full 7-phase project.