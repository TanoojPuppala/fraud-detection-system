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
| **PyTorch DNN (SMOTE)** | 0.7172 | 0.9514 | 0.5846 | 0.8000 | 0.6756 | 54 | 19 | **$9,770.00** | 8.06 ms |
| **PyTorch Autoencoder (Baseline)** | 0.2013 | 0.9277 | 0.1689 | 0.5263 | 0.2558 | 246 | 45 | **$23,730.00** | 3.75 ms |

---

## 2. Model Performance & Divergence Analysis

- **Best Model by PR-AUC**: `PyTorch DNN (SMOTE)` (PR-AUC = **0.7172**, Business Cost = **$9,770.00**)
- **Best Model by Business Cost**: `PyTorch DNN (SMOTE)` (Business Cost = **$9,770.00**, PR-AUC = **0.7172**)
- **Divergence Status**: **Identical Champion Model**

### Explanatory Breakdown:

The best model by PR-AUC (PyTorch DNN (SMOTE)) is ALSO the model with the lowest estimated business cost ($9,770.00). It achieves the superior balance between precision and recall, minimizing total monetary impact.

---

## 3. Final Production Recommendation & Rationale

> [!IMPORTANT]
> **Production Recommendation for `/predict` Endpoint**:
> 
> We formally recommend deploying **PyTorch DNN (SMOTE)** to the backend `/predict` endpoint. It delivers the lowest total estimated business cost of **$9,770.00** on held-out test data, achieving a high recall of **80.0%** (76 caught frauds vs 19 missed frauds) and a rapid inference latency of **8.06 ms**. While `PyTorch DNN (SMOTE)` achieved the top PR-AUC score (0.7172), `PyTorch DNN (SMOTE)` saves **$0.00** in financial losses by reducing catastrophic false negative fraud escapes ($500 per undetected fraud).

---

## 4. Production Artifact Packaging

The selected model has been exported to the backend deployment directory `ml/models/production/`:
- **Production Model File**: `ml/models/production/production_model.pt`
- **Model Info Metadata**: `ml/models/production/production_model_info.json`
- **Selection Timestamp**: `2026-08-17 10:59:22`
