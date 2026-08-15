# AI Usage & Development Process

This document transparently describes how AI assistance (Claude) was used throughout this project, and — just as importantly — what was done independently.

## Philosophy

AI was used as a **debugging partner, code reviewer, and concept explainer** — not as a replacement for understanding or decision-making. Every architectural choice, every experiment run, and every interpretation of results in this project reflects my own reasoning, verified and often independently re-derived, not blindly accepted output.

## What AI Was Used For

- **Debugging syntax and runtime errors** — e.g., diagnosing SQLAlchemy version incompatibilities, pandas method misuse, and Streamlit-specific rendering issues.
- **Code review** — catching subtle bugs I wrote myself (e.g., incorrect variable reuse, leakage-prone logic, redundant SQL computation) before they silently produced wrong results.
- **Concept explanation** — for genuinely new techniques (SQL window functions, SHAP, calibration methods, permutation importance), AI explained the underlying concept before I wrote the implementation myself.
- **Structural planning** — outlining phase scope and dashboard section structure, which I then implemented and adapted independently.

## What Was Done Independently

- **All core decision-making**: choice of dataset, feature engineering strategy, which experiments to run (SMOTE vs. scale_pos_weight, hyperparameter tuning, V-column expansion), and how to interpret every result.
- **The majority of the codebase**, particularly Phases 3, 4, and the Streamlit dashboard (Phase 7), where I wrote the substantial majority of the implementation myself and used AI primarily for review rather than generation.
- **Every statistical and business interpretation** in this project's documentation — including identifying methodology risks myself (e.g., questioning whether a stale decision threshold was being reused incorrectly after a feature change), which AI then helped confirm and fix.
- **All final decisions on scope** — including when to stop expanding