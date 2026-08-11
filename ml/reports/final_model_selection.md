# Final Model Selection & Backend Deployment Report

## Executive Summary

This report presents the final evaluation and model selection across all **6 trained models** for the Fraud Detection System backend (`/predict` endpoint). 

Evaluated on the identical held-out test set (`X_test.pkl` / `y_test.pkl`, containing **56,963 total transactions** and **95 fraud cases**), each model's predictive performance and estimated financial impact were benchmarked under cost-aware evaluation metrics.

---

## 1. Comprehensive Model Comparison Matrix

The table below summarizes all 6 model variants, sorted by **PR-AUC descending**.

*Note on Business Cost calculation*: Estimated business cost is computed using illustrative placeholder cost assumptions:
- **False Positive (FP) Cost**: **$5.00** per transaction (cost of fraud analyst review time for a false alarm)
- **False Negative (FN) Cost**: **$500.00** per transaction (average financial loss of an undetected fraud transaction)
- **Total Business Cost** = `(FP * $5) + (FN * $500)`

> [!NOTE]
> These dollar figures ($5 FP / $500 FN) are illustrative placeholder assumptions used to demonstrate cost-aware model selection logic in an imbalanced domain and do not represent real proprietary industry financial data.

| Model Variant | PR-AUC | ROC-AUC | Precision | Recall | F1-Score | FP | FN | Total Business Cost ($) | Inference Time (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **XGBoost (SMOTE)** | 0.8186 | 0.9693 | 0.7957 | 0.7789 | 0.7872 | 19 | 21 | **$10,595.00** | 44.87 ms |
| **PyTorch DNN (SMOTE)** | 0.7172 | 0.9514 | 0.5846 | 0.8000 | 0.6756 | 54 | 19 | **$9,770.00** | 17.96 ms |
| **Logistic Regression (SMOTE)** | 0.6750 | 0.9626 | 0.0530 | 0.8737 | 0.1000 | 1482 | 12 | **$13,410.00** | 4.94 ms |
| **Logistic Regression (Baseline)** | 0.6719 | 0.9657 | 0.0564 | 0.8737 | 0.1059 | 1389 | 12 | **$12,945.00** | 9.50 ms |
| **Logistic Regression (Undersampled)** | 0.5896 | 0.9571 | 0.0504 | 0.8737 | 0.0953 | 1563 | 12 | **$13,815.00** | 4.43 ms |
| **PyTorch Autoencoder (Baseline)** | 0.2013 | 0.9277 | 0.1689 | 0.5263 | 0.2558 | 246 | 45 | **$23,730.00** | 3.30 ms |

---

## 2. Model Performance & Divergence Analysis

- **Best Model by PR-AUC**: `XGBoost (SMOTE)` (PR-AUC = **0.8186**, Business Cost = **$10,595.00**)
- **Best Model by Business Cost**: `PyTorch DNN (SMOTE)` (Business Cost = **$9,770.00**, PR-AUC = **0.7172**)
- **Divergence Status**: **Different Models Identified**

### Explanatory Breakdown:

The model winning on PR-AUC (XGBoost (SMOTE), PR-AUC=0.8186) differs from the model winning on business cost (PyTorch DNN (SMOTE), Cost=$9,770.00).
Reason: PR-AUC evaluates ranking quality across all thresholds, prioritizing high Precision at high Recall thresholds.
However, under our asymmetric cost matrix ($5 FP vs $500 FN), false negatives are 100x more costly than false positives.
PyTorch DNN (SMOTE) recorded fewer False Negatives (19 FN vs 21 FN for XGBoost (SMOTE)), saving $1,000.00 in undetected fraud losses, which more than offset its higher false alarm volume.

---

## 3. Final Production Recommendation & Rationale

> [!IMPORTANT]
> **Production Recommendation for `/predict` Endpoint**:
> 
> We formally recommend deploying **PyTorch DNN (SMOTE)** to the backend `/predict` endpoint. It delivers the lowest total estimated business cost of **$9,770.00** on held-out test data, achieving a high recall of **80.0%** (76 caught frauds vs 19 missed frauds) and a rapid inference latency of **17.96 ms**. While `XGBoost (SMOTE)` achieved the top PR-AUC score (0.8186), `PyTorch DNN (SMOTE)` saves **$825.00** in financial losses by reducing catastrophic false negative fraud escapes ($500 per undetected fraud).

---

## 4. Production Artifact Packaging

The selected model has been exported to the backend deployment directory `ml/models/production/`:
- **Production Model File**: `ml/models/production/production_model.pt`
- **Model Info Metadata**: `ml/models/production/production_model_info.json`
- **Selection Timestamp**: `2026-08-11 23:24:12`
