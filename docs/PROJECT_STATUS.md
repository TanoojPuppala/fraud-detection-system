# Fraud Detection System — Project Status Report

**Last Updated**: August 10, 2026  
**Status**: ML Pipeline & 6-Model Benchmark Complete | Backend & Frontend Architecture Ready

---

## Executive Summary

The **Fraud Detection System** is an end-to-end machine learning and software pipeline designed for real-time and batch transaction fraud detection on highly imbalanced financial datasets.

The ML engineering module is fully complete, featuring data validation, exploratory data analysis, preprocessing (scaling & resampling), and a benchmark suite of **6 distinct model variants** across supervised and unsupervised paradigms.

---

## Current Project Modules Status

| Module | Status | Highlights / Deliverables |
| :--- | :---: | :--- |
| **Data Ingestion & Preprocessing** | ✅ Complete | Stratified splitting, StandardScaler normalization, SMOTE & Undersampling techniques ([preprocess.py](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/src/preprocess.py)) |
| **Exploratory Data Analysis (EDA)** | ✅ Complete | Class imbalance analysis, feature distribution plots, correlation heatmaps ([eda.py](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/src/eda.py)) |
| **Baseline Linear Models** | ✅ Complete | Logistic Regression (Baseline, SMOTE, Undersampled) ([train.py](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/src/train.py)) |
| **Gradient Boosting Classifier** | ✅ Complete | XGBoost with RandomizedSearchCV hyperparameter tuning (**Champion Model: PR-AUC 0.8186**) ([train_xgboost.py](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/src/train_xgboost.py)) |
| **Supervised Deep Learning** | ✅ Complete | PyTorch Multi-Layer Perceptron (MLP) with Early Stopping (**PR-AUC 0.7172**) ([train_dnn.py](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/src/train_dnn.py)) |
| **Unsupervised Anomaly Detection** | ✅ Complete | PyTorch Autoencoder trained on legitimate transactions with F1 threshold tuning ([train_autoencoder.py](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/src/train_autoencoder.py)) |
| **Comprehensive Benchmark** | ✅ Complete | 6-model evaluation script, PR-curves figure, CSV report export ([evaluate.py](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/src/evaluate.py)) |
| **Backend API Service** | ⏳ Planned | FastAPI framework dependencies defined ([requirements.txt](file:///c:/Users/Dell/Downloads/fraud-detection-system/backend/requirements.txt)) |
| **Frontend Dashboard** | ⏳ Planned | Web interface for fraud monitoring and model analytics |
| **Database & Analytics** | ⏳ Planned | Transaction storage and audit logs |

---

## 6-Model Benchmark Performance Matrix

Evaluated on the held-out test dataset (`X_test.pkl`, `y_test.pkl` — 56,746 samples, 95 fraud cases):

| Model Variant | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | TN | FP | FN | TP | Inference Time (ms) | Artifact Path |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Logistic Regression (Baseline)** | 0.0564 | **0.8737** | 0.1059 | 0.9657 | 0.6719 | 55,262 | 1,389 | 12 | 83 | 9.50 | [logistic_regression_baseline.pkl](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/models/logistic_regression_baseline.pkl) |
| **Logistic Regression (SMOTE)** | 0.0530 | **0.8737** | 0.1000 | 0.9626 | 0.6750 | 55,169 | 1,482 | 12 | 83 | 4.94 | [logistic_regression_smote.pkl](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/models/logistic_regression_smote.pkl) |
| **Logistic Regression (Undersampled)** | 0.0504 | **0.8737** | 0.0953 | 0.9571 | 0.5896 | 55,088 | 1,563 | 12 | 83 | 4.43 | [logistic_regression_undersampled.pkl](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/models/logistic_regression_undersampled.pkl) |
| **XGBoost (SMOTE)** 🏆 | **0.7957** | 0.7789 | **0.7872** | **0.9693** | **0.8186** | 56,632 | 19 | 21 | 74 | 44.87 | [xgboost_smote.pkl](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/models/xgboost_smote.pkl) |
| **PyTorch DNN (SMOTE)** | 0.5846 | 0.8000 | 0.6756 | 0.9514 | 0.7172 | 56,597 | 54 | 19 | 76 | 17.96 | [dnn_smote.pt](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/models/dnn_smote.pt) |
| **PyTorch Autoencoder (Baseline)** | 0.1689 | 0.5263 | 0.2558 | 0.9277 | 0.2013 | 56,405 | 246 | 45 | 50 | 3.30 | [autoencoder_baseline.pt](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/models/autoencoder_baseline.pt) |

---

## Machine Learning Key Takeaways

1. **Supervised Champion**: **XGBoost (SMOTE)** achieved the top PR-AUC (**0.8186**) and F1-score (**0.7872**), dramatically reducing false positives (only 19 FP out of 56,746 test transactions).
2. **Deep Learning Alternative**: **PyTorch DNN (SMOTE)** achieved **0.7172 PR-AUC** with high recall (80.00%), providing fast GPU-accelerated inference.
3. **Unsupervised Safety Net**: The **PyTorch Autoencoder** provides zero-day fraud detection capability by learning normal transaction behavior without needing historical fraud labels.

---

## Key Artifacts & Reports

- **Model Comparison CSV**: [model_comparison_all.csv](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/reports/model_comparison_all.csv)
- **Precision-Recall Benchmark Plot**: [all_models_pr_curves.png](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/reports/figures/all_models_pr_curves.png)
- **Autoencoder Analysis Plot**: [autoencoder_analysis.png](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/reports/figures/autoencoder_analysis.png)
- **DNN Training Curves**: [dnn_training_curves.png](file:///c:/Users/Dell/Downloads/fraud-detection-system/ml/reports/figures/dnn_training_curves.png)
