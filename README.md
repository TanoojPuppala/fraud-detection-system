# Fraud Detection System

An enterprise-grade, end-to-end Fraud Detection System featuring exploratory data analysis, data preprocessing, machine learning benchmarks (supervised & unsupervised models), real-time inference API backend, and dashboard analytics.

---

## 📌 Project Status

Detailed project status and benchmark comparisons are available in [docs/PROJECT_STATUS.md](file:///c:/Users/Dell/Downloads/fraud-detection-system/docs/PROJECT_STATUS.md).

### Current Benchmark Summary (6 Models Evaluated)

| Model Variant | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Baseline)** | 0.0564 | 0.8737 | 0.1059 | 0.9657 | 0.6719 | ✅ Trained |
| **Logistic Regression (SMOTE)** | 0.0530 | 0.8737 | 0.1000 | 0.9626 | 0.6750 | ✅ Trained |
| **Logistic Regression (Undersampled)** | 0.0504 | 0.8737 | 0.0953 | 0.9571 | 0.5896 | ✅ Trained |
| **XGBoost (SMOTE)** 🏆 | **0.7957** | 0.7789 | **0.7872** | **0.9693** | **0.8186** | ✅ Trained |
| **PyTorch DNN (SMOTE)** | 0.5846 | **0.8000** | 0.6756 | 0.9514 | 0.7172 | ✅ Trained |
| **PyTorch Autoencoder (Baseline)** | 0.1689 | 0.5263 | 0.2558 | 0.9277 | 0.2013 | ✅ Trained |

---

## 📁 Repository Architecture

```
fraud-detection-system/
├── ml/
│   ├── data/
│   │   └── processed/          # Preprocessed baseline, SMOTE, undersampled datasets
│   ├── models/                 # Serialized model weights (.pkl & .pt)
│   ├── reports/                # Evaluation CSVs and figures
│   └── src/                    # Machine learning source code
│       ├── preprocess.py       # Data validation & scaling pipeline
│       ├── eda.py              # Exploratory data analysis
│       ├── train.py            # Logistic Regression training
│       ├── train_xgboost.py    # XGBoost tuning & training
│       ├── train_dnn.py        # PyTorch DNN training
│       ├── train_autoencoder.py# PyTorch Autoencoder training & threshold tuning
│       └── evaluate.py         # 6-model comprehensive benchmark pipeline
├── docs/                       # Project documentation & status reports
├── backend/                    # FastAPI backend service (in progress)
├── frontend/                   # Web dashboard UI (planned)
└── database/                   # Database schemas & migrations (planned)
```

---

## 🚀 Quickstart Guide

### 1. Environment Setup
```bash
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Train Models
```bash
# Train Logistic Regression baselines
python ml/src/train.py

# Tune & train XGBoost
python ml/src/train_xgboost.py

# Train PyTorch DNN
python ml/src/train_dnn.py

# Train PyTorch Autoencoder
python ml/src/train_autoencoder.py
```

### 3. Run Benchmark Evaluation
```bash
python ml/src/evaluate.py
```
