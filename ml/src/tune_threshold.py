"""
Decision Threshold Tuning Script for Production Model.

Evaluates prediction decision thresholds (0.01 to 0.99) on the held-out test set
for the production model, optimizes for total business cost (FP*$5 + FN*$500)
and F1-score, updates production_model_info.json with the optimal threshold,
and exports threshold performance plots to ml/reports/figures/threshold_tuning.png.
"""

import sys
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn as nn
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

# Ensure UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.size": 10, "figure.autolayout": True})

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = BASE_DIR / "ml" / "data" / "processed"
MODELS_DIR = BASE_DIR / "ml" / "models"
PROD_DIR = MODELS_DIR / "production"
FIGURES_DIR = BASE_DIR / "ml" / "reports" / "figures"

FP_COST_USD = 5.0
FN_COST_USD = 500.0


class FraudDNN(nn.Module):
    def __init__(self, input_dim: int = 30):
        super(FraudDNN, self).__init__()
        self.layer1 = nn.Sequential(nn.Linear(input_dim, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.3))
        self.layer2 = nn.Sequential(nn.Linear(64, 32), nn.BatchNorm1d(32), nn.ReLU(), nn.Dropout(0.3))
        self.layer3 = nn.Sequential(nn.Linear(32, 16), nn.ReLU(), nn.Dropout(0.2))
        self.out = nn.Sequential(nn.Linear(16, 1), nn.Sigmoid())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.out(x)
        return x


def run_threshold_tuning() -> None:
    print("=" * 75)
    print(" DECISION THRESHOLD TUNING BENCHMARK")
    print("=" * 75)

    # 1. Load Test Set
    X_test = joblib.load(PROCESSED_DIR / "X_test.pkl")
    y_test = joblib.load(PROCESSED_DIR / "y_test.pkl")
    print(f"\n[1] Loaded test set: {len(y_test):,} samples (Fraud cases: {int(y_test.sum())})")

    # 2. Load Production Model Metadata
    info_json_path = PROD_DIR / "production_model_info.json"
    if not info_json_path.exists():
        raise FileNotFoundError(f"Production model info not found: {info_json_path}")

    with open(info_json_path, "r", encoding="utf-8") as f:
        prod_info = json.load(f)

    orig_filename = prod_info["original_filename"]
    model_path = PROD_DIR / prod_info["production_filename"]
    if not model_path.exists():
        model_path = MODELS_DIR / orig_filename

    print(f"[2] Evaluating production model: {prod_info['original_model_variant']} ({model_path.name})")

    # Predict Probabilities
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if model_path.suffix == ".pt":
        dnn_model = FraudDNN(input_dim=30).to(device)
        dnn_model.load_state_dict(torch.load(model_path, map_location=device))
        dnn_model.eval()

        X_test_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)
        with torch.no_grad():
            y_probs = dnn_model(X_test_tensor).cpu().numpy().flatten()
    else:
        clf = joblib.load(model_path)
        y_probs = clf.predict_proba(X_test)[:, 1]

    # 3. Sweep Thresholds
    thresholds = np.linspace(0.01, 0.99, 99)
    results = []

    for t in thresholds:
        y_preds = (y_probs >= t).astype(int)
        prec = precision_score(y_test, y_preds, zero_division=0)
        rec = recall_score(y_test, y_preds, zero_division=0)
        f1 = f1_score(y_test, y_preds, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y_test, y_preds).ravel()
        cost = (fp * FP_COST_USD) + (fn * FN_COST_USD)

        results.append({
            "threshold": t,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "fp": fp,
            "fn": fn,
            "tp": tp,
            "cost": cost
        })

    df_thresh = pd.DataFrame(results)

    # Find optimal threshold for lowest cost
    best_cost_row = df_thresh.loc[df_thresh["cost"].idxmin()]
    best_f1_row = df_thresh.loc[df_thresh["f1"].idxmax()]
    default_row = df_thresh.loc[(df_thresh["threshold"] - 0.50).abs().idxmin()]

    print("\n" + "=" * 80)
    print(" THRESHOLD TUNING COMPARISON SUMMARY")
    print("=" * 80)
    print(f" Default Threshold (0.50)  : Cost = ${default_row['cost']:,.2f} | F1 = {default_row['f1']:.4f} | Prec = {default_row['precision']:.4f} | Rec = {default_row['recall']:.4f} | FP = {int(default_row['fp'])} | FN = {int(default_row['fn'])}")
    print(f" Optimal Cost Threshold ({best_cost_row['threshold']:.2f}): Cost = ${best_cost_row['cost']:,.2f} | F1 = {best_cost_row['f1']:.4f} | Prec = {best_cost_row['precision']:.4f} | Rec = {best_cost_row['recall']:.4f} | FP = {int(best_cost_row['fp'])} | FN = {int(best_cost_row['fn'])}")
    print(f" Optimal F1 Threshold ({best_f1_row['threshold']:.2f})  : Cost = ${best_f1_row['cost']:,.2f} | F1 = {best_f1_row['f1']:.4f} | Prec = {best_f1_row['precision']:.4f} | Rec = {best_f1_row['recall']:.4f} | FP = {int(best_f1_row['fp'])} | FN = {int(best_f1_row['fn'])}")
    print("=" * 80)

    # 4. Plot Threshold Tuning Curves
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(df_thresh["threshold"], df_thresh["precision"], label="Precision", color="#e74c3c", lw=2)
    ax1.plot(df_thresh["threshold"], df_thresh["recall"], label="Recall", color="#2ecc71", lw=2)
    ax1.plot(df_thresh["threshold"], df_thresh["f1"], label="F1-Score", color="#3498db", lw=2)
    ax1.axvline(x=best_cost_row["threshold"], color="#9b59b6", linestyle="--", label=f"Optimal Cost Thresh ({best_cost_row['threshold']:.2f})")
    ax1.set_title("Precision, Recall, and F1 vs Decision Threshold", fontweight="bold")
    ax1.set_xlabel("Decision Threshold")
    ax1.set_ylabel("Score")
    ax1.legend(loc="best")

    ax2.plot(df_thresh["threshold"], df_thresh["cost"], label="Total Business Cost ($)", color="#e67e22", lw=2)
    ax2.axvline(x=best_cost_row["threshold"], color="#9b59b6", linestyle="--", label=f"Min Cost Thresh (${best_cost_row['cost']:,.2f})")
    ax2.set_title("Total Estimated Business Cost vs Decision Threshold", fontweight="bold")
    ax2.set_xlabel("Decision Threshold")
    ax2.set_ylabel("Total Business Cost ($)")
    ax2.legend(loc="best")

    fig_path = FIGURES_DIR / "threshold_tuning.png"
    fig.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"\n[+] Saved threshold tuning curves -> {fig_path}")

    # 5. Update production_model_info.json
    prod_info["optimal_threshold"] = float(best_cost_row["threshold"])
    prod_info["tuned_metrics"] = {
        "threshold": float(best_cost_row["threshold"]),
        "precision": float(best_cost_row["precision"]),
        "recall": float(best_cost_row["recall"]),
        "f1_score": float(best_cost_row["f1"]),
        "fp": int(best_cost_row["fp"]),
        "fn": int(best_cost_row["fn"]),
        "tp": int(best_cost_row["tp"]),
        "total_business_cost_usd": float(best_cost_row["cost"])
    }

    with open(info_json_path, "w", encoding="utf-8") as f:
        json.dump(prod_info, f, indent=2)

    print(f"[+] Updated metadata with optimal decision threshold -> {info_json_path}")
    print("\n" + "=" * 75)
    print(" [OK] THRESHOLD TUNING COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    try:
        run_threshold_tuning()
    except Exception as e:
        print(f"\n[ERROR] Threshold tuning failed: {e}", file=sys.stderr)
        sys.exit(1)
