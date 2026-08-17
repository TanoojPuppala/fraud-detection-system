# Fraud Detection System

An enterprise-grade, end-to-end Deep Learning Fraud Detection System featuring exploratory data analysis, leakage-safe data preprocessing, deep neural network and autoencoder benchmarks, real-time FastAPI inference backend with SHAP explainability, and React dashboard analytics.

---

## 📌 Project Status

Detailed project status and benchmark comparisons are available in [docs/PROJECT_STATUS.md](file:///c:/Users/Dell/Downloads/fraud-detection-system/docs/PROJECT_STATUS.md).

### Deep Learning Architecture Benchmark Summary

| Model Architecture | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **PyTorch DNN (SMOTE)** 🏆 | **0.5846** | **0.8000** | **0.6756** | **0.9514** | **0.7172** | ✅ Production Champion |
| **PyTorch Autoencoder (Baseline)** | 0.1689 | 0.5263 | 0.2558 | 0.9277 | 0.2013 | ✅ Trained |

---

## 📁 Repository Architecture

```
fraud-detection-system/
├── ml/
│   ├── data/
│   │   └── processed/          # Preprocessed baseline and SMOTE datasets
│   ├── models/                 # Serialized model weights (.pt) & production packaging
│   ├── reports/                # Evaluation CSVs, metrics, and PR-curve figures
│   └── src/                    # Machine learning source code
│       ├── preprocess.py       # Data validation & scaling pipeline
│       ├── eda.py              # Exploratory data analysis
│       ├── train_dnn.py        # PyTorch DNN (MLP) training with early stopping
│       ├── train_autoencoder.py# PyTorch Autoencoder anomaly detection training
│       ├── evaluate.py         # Deep Learning benchmark evaluation pipeline
│       └── explainability.py   # SHAP feature attribution & explainability
├── docs/                       # Project documentation & status reports
├── backend/                    # FastAPI backend REST API service
├── frontend/                   # React + TypeScript web dashboard UI
└── database/                   # SQLite database storage & audit logs
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

### 2. Train Deep Learning Models
```bash
# Train PyTorch Deep Neural Network (MLP)
python ml/src/train_dnn.py

# Train PyTorch Autoencoder (Anomaly Detection)
python ml/src/train_autoencoder.py
```

### 3. Run Benchmark Evaluation & Package Production Model
```bash
# Run Deep Learning benchmark evaluation
python ml/src/evaluate.py

# Package champion model for backend deployment
python ml/src/select_final_model.py
```

### 4. Run Application (Backend + Frontend)
```bash
python backend/app/main.py
```
Open **http://localhost:8000** in your browser.
