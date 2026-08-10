"""
Evaluation Script for Logistic Regression Baseline Models.

Loads trained models and test set, computes key metrics (Precision, Recall, F1,
ROC-AUC, PR-AUC, Confusion Matrix, Latency), generates an overlaid PR-Curve plot,
exports a CSV report, and prints a summary comparison table.
"""

from pathlib import Path
import sys
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
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


def run_evaluation() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(" LOGISTIC REGRESSION MODEL EVALUATION")
    print("=" * 70)

    # 1. Load Test Set
    print("\n[1] Loading test set (X_test.pkl, y_test.pkl) ...")
    X_test = joblib.load(PROCESSED_DIR / "X_test.pkl")
    y_test = joblib.load(PROCESSED_DIR / "y_test.pkl")
    print(f"    Test set size: {len(y_test):,} samples (Fraud cases: {int(y_test.sum())})")

    # 2. Define Model Variants
    model_configs = [
        {"name": "Baseline (Class-Weighted)", "file": "logistic_regression_baseline.pkl"},
        {"name": "SMOTE (Oversampled)", "file": "logistic_regression_smote.pkl"},
        {"name": "Undersampled", "file": "logistic_regression_undersampled.pkl"},
    ]

    results = []
    pr_curve_data = []

    print("\n[2] Evaluating models on test set ...")
    fig, ax = plt.subplots(figsize=(8, 6))

    for config in model_configs:
        model_path = MODELS_DIR / config["file"]
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        clf = joblib.load(model_path)

        # Measure inference latency
        start_time = time.perf_counter()
        y_probs = clf.predict_proba(X_test)[:, 1]
        inference_time_ms = (time.perf_counter() - start_time) * 1000.0

        y_preds = clf.predict(X_test)

        # Compute metrics
        prec = precision_score(y_test, y_preds, zero_division=0)
        rec = recall_score(y_test, y_preds, zero_division=0)
        f1 = f1_score(y_test, y_preds, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_probs)
        pr_auc = average_precision_score(y_test, y_probs)
        tn, fp, fn, tp = confusion_matrix(y_test, y_preds).ravel()

        results.append({
            "Variant": config["name"],
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

        # Precision-Recall Curve Plotting
        precision_arr, recall_arr, _ = precision_recall_curve(y_test, y_probs)
        ax.plot(recall_arr, precision_arr, label=f"{config['name']} (PR-AUC = {pr_auc:.4f})", lw=2)

    # Finalize and Save PR-Curve Plot
    ax.set_title("Precision-Recall Curves — Logistic Regression Variants", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Recall", fontsize=11)
    ax.set_ylabel("Precision", fontsize=11)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.legend(loc="lower left", frameon=True)

    fig_path = FIGURES_DIR / "logistic_regression_pr_curves.png"
    fig.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved PR-Curve plot -> {fig_path}")

    # 3. Create Summary Dataframe & Save CSV
    df_results = pd.DataFrame(results)
    csv_path = REPORTS_DIR / "logistic_regression_comparison.csv"
    df_results.to_csv(csv_path, index=False)
    print(f"    Saved comparison metrics CSV -> {csv_path}")

    # 4. Print Summary Table
    print("\n" + "=" * 85)
    print(" LOGISTIC REGRESSION PERFORMANCE COMPARISON")
    print("=" * 85)
    
    header = f"{'Variant':<28} | {'Precision':>9} | {'Recall':>9} | {'F1-Score':>9} | {'ROC-AUC':>9} | {'PR-AUC':>9} | {'FP':>5} | {'FN':>4}"
    sep = "-" * len(header)
    print("\n" + sep)
    print(header)
    print(sep)

    for r in results:
        print(
            f"{r['Variant']:<28} | {r['Precision']:>9.4f} | {r['Recall']:>9.4f} | "
            f"{r['F1-Score']:>9.4f} | {r['ROC-AUC']:>9.4f} | {r['PR-AUC']:>9.4f} | "
            f"{r['FP']:>5} | {r['FN']:>4}"
        )
    print(sep)

    # 5. Determine Best Performers
    best_pr_auc_row = df_results.loc[df_results["PR-AUC"].idxmax()]
    best_f1_row = df_results.loc[df_results["F1-Score"].idxmax()]

    print("\n" + "=" * 85)
    print(" CONCLUSION & RECOMMENDATION")
    print("=" * 85)
    print(f" [*] Best PR-AUC  : {best_pr_auc_row['Variant']} with PR-AUC = {best_pr_auc_row['PR-AUC']:.4f}")
    print(f" [*] Best F1-Score: {best_f1_row['Variant']} with F1-Score = {best_f1_row['F1-Score']:.4f}")
    print("\n [STRATEGY DECISION]")
    if best_pr_auc_row["Variant"] == best_f1_row["Variant"]:
        print(f"     '{best_pr_auc_row['Variant']}' clearly dominates across both PR-AUC and F1-Score.")
        print(f"     Recommended for standardization in upcoming XGBoost and Deep Neural Network models.")
    else:
        print(f"     PR-AUC champion is '{best_pr_auc_row['Variant']}', while F1 champion is '{best_f1_row['Variant']}'.")
        print(f"     PR-AUC is prioritized for imbalanced fraud detection. Recommended strategy: '{best_pr_auc_row['Variant']}'.")
    print("=" * 85)


if __name__ == "__main__":
    try:
        run_evaluation()
    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}", file=sys.stderr)
        sys.exit(1)
