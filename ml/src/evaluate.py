"""
Comprehensive Evaluation Script for Deep Learning Architecture (PyTorch DNN & Autoencoders).

Loads trained Deep Learning models:
1. PyTorch Deep Neural Network (Supervised Layer)
2. PyTorch Deep Autoencoder (Unsupervised Anomaly Detection Layer)

Evaluates both on the held-out test set, outputs the comparison CSV, and
generates an overlaid PR-Curve plot.
"""

from pathlib import Path
import sys
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import torch
import torch.nn as nn

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    accuracy_score,
)

# Ensure UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Set plotting theme
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.size": 10, "figure.autolayout": True})

PROCESSED_DIR = Path("ml/data/processed")
MODELS_DIR = Path("ml/models")
REPORTS_DIR = Path("ml/reports")
FIGURES_DIR = Path("ml/reports/figures")


# ── PyTorch Neural Network Definition ──────────────────────────────────────────
class FraudDNN(nn.Module):
    """
    PyTorch Deep Neural Network architecture for Fraud Detection.
    """
    def __init__(self, input_dim: int = 30):
        super(FraudDNN, self).__init__()
        self.layer1 = nn.Sequential(nn.Linear(input_dim, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.3))
        self.layer2 = nn.Sequential(nn.Linear(64, 32), nn.BatchNorm1d(32), nn.ReLU(), nn.Dropout(0.3))
        self.layer3 = nn.Sequential(nn.Linear(32, 16), nn.ReLU(), nn.Dropout(0.2))
        self.out = nn.Sequential(nn.Linear(16, 1), nn.Sigmoid())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.out(self.layer3(self.layer2(self.layer1(x))))


class FraudAutoencoder(nn.Module):
    """
    PyTorch Autoencoder architecture for Unsupervised Fraud Anomaly Detection.
    """
    def __init__(self, input_dim: int = 30):
        super(FraudAutoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 20),
            nn.ReLU(),
            nn.Linear(20, 14),
            nn.ReLU(),
            nn.Linear(14, 8),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(8, 14),
            nn.ReLU(),
            nn.Linear(14, 20),
            nn.ReLU(),
            nn.Linear(20, input_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.decoder(self.encoder(x))


def run_evaluation() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" DEEP LEARNING ARCHITECTURE EVALUATION (PYTORCH DNN & AUTOENCODER)")
    print("=" * 80)

    # 1. Load Test Set
    print("\n[1] Loading test set (X_test.pkl, y_test.pkl) ...")
    X_test = joblib.load(PROCESSED_DIR / "X_test.pkl")
    y_test = joblib.load(PROCESSED_DIR / "y_test.pkl")
    print(f"    Test set size: {len(y_test):,} samples (Fraud cases: {int(y_test.sum())})")

    # 2. Define Model Variants
    model_configs = [
        {"name": "PyTorch DNN (SMOTE)", "file": "dnn_smote.pt", "type": "pytorch"},
        {"name": "PyTorch Autoencoder (Baseline)", "file": "autoencoder_baseline.pt", "type": "autoencoder"},
    ]

    results = []
    fig, ax = plt.subplots(figsize=(8, 5))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("\n[2] Evaluating Deep Learning models on held-out test set ...")
    for config in model_configs:
        model_path = MODELS_DIR / config["file"]
        if not model_path.exists():
            print(f"    [SKIP] Model not found: {model_path}")
            continue

        if config["type"] == "pytorch":
            dnn_model = FraudDNN(input_dim=30).to(device)
            dnn_model.load_state_dict(torch.load(model_path, map_location=device))
            dnn_model.eval()

            X_test_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)

            start_time = time.perf_counter()
            with torch.no_grad():
                y_probs_tensor = dnn_model(X_test_tensor)
                y_probs = y_probs_tensor.cpu().numpy().flatten()
            inference_time_ms = (time.perf_counter() - start_time) * 1000.0
            y_preds = (y_probs >= 0.5).astype(int)

        elif config["type"] == "autoencoder":
            checkpoint = torch.load(model_path, map_location=device)
            ae_model = FraudAutoencoder(input_dim=30).to(device)
            if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
                ae_model.load_state_dict(checkpoint["state_dict"])
                threshold = checkpoint.get("threshold", 0.05)
            else:
                ae_model.load_state_dict(checkpoint)
                threshold = 0.05
            ae_model.eval()

            X_test_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)

            start_time = time.perf_counter()
            with torch.no_grad():
                recons_tensor = ae_model(X_test_tensor)
                recons = recons_tensor.cpu().numpy()
            inference_time_ms = (time.perf_counter() - start_time) * 1000.0

            reconstruction_errors = np.mean((X_test - recons) ** 2, axis=1)
            y_probs = reconstruction_errors
            y_preds = (reconstruction_errors >= threshold).astype(int)

        # Compute metrics
        acc = accuracy_score(y_test, y_preds)
        prec = precision_score(y_test, y_preds, zero_division=0)
        rec = recall_score(y_test, y_preds, zero_division=0)
        f1 = f1_score(y_test, y_preds, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_probs)
        pr_auc = average_precision_score(y_test, y_probs)
        tn, fp, fn, tp = confusion_matrix(y_test, y_preds).ravel()

        results.append({
            "Model Variant": config["name"],
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1,
            "ROC-AUC": roc_auc,
            "PR-AUC": pr_auc,
            "TN": tn,
            "FP": fp,
            "FN": fn,
            "TP": tp,
            "Inference Time (ms)": inference_time_ms
        })

        # Precision-Recall Curve
        precision_arr, recall_arr, _ = precision_recall_curve(y_test, y_probs)
        ax.plot(recall_arr, precision_arr, label=f"{config['name']} (PR-AUC = {pr_auc:.4f})", lw=2)

    # 3. Save PR Curve Figure
    ax.set_title("Precision-Recall Curves — Deep Learning Benchmark", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Recall", fontsize=11)
    ax.set_ylabel("Precision", fontsize=11)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.legend(loc="lower left", frameon=True)

    fig_path = FIGURES_DIR / "all_models_pr_curves.png"
    fig.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved Deep Learning PR-Curve plot -> {fig_path}")

    # 4. Save CSV Reports
    df_results = pd.DataFrame(results)
    csv_all_path = REPORTS_DIR / "model_comparison_all.csv"
    df_results.to_csv(csv_all_path, index=False)
    print(f"    Saved combined comparison CSV -> {csv_all_path}")

    # 5. Print Combined Comparison Table
    print("\n" + "=" * 110)
    print(" DEEP LEARNING BENCHMARK PERFORMANCE COMPARISON")
    print("=" * 110)

    header = f"{'Model Variant':<35} | {'Accuracy':>8} | {'ROC-AUC':>8} | {'PR-AUC':>8} | {'Precision':>9} | {'Recall':>8} | {'F1-Score':>8} | {'FP':>4} | {'FN':>4}"
    sep = "-" * len(header)
    print("\n" + sep)
    print(header)
    print(sep)

    for r in results:
        print(
            f"{r['Model Variant']:<35} | {r['Accuracy']*100:>7.2f}% | {r['ROC-AUC']:>8.4f} | "
            f"{r['PR-AUC']:>8.4f} | {r['Precision']:>9.4f} | {r['Recall']:>8.4f} | "
            f"{r['F1-Score']:>8.4f} | {r['FP']:>4} | {r['FN']:>4}"
        )
    print(sep)


if __name__ == "__main__":
    try:
        run_evaluation()
    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}", file=sys.stderr)
        sys.exit(1)
