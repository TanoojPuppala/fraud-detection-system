"""
Comprehensive Evaluation Script for All Models (Logistic Regression & XGBoost).

Loads trained models (3 Logistic Regression variants + 1 XGBoost variant),
evaluates them on the shared test set, outputs a combined comparison CSV,
generates an overlaid PR-Curve plot across all 4 models, and displays XGBoost's
top 10 feature importances.
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

    print("=" * 75)
    print(" COMPREHENSIVE MODEL EVALUATION BENCHMARK (4 MODELS)")
    print("=" * 75)

    # 1. Load Test Set
    print("\n[1] Loading test set (X_test.pkl, y_test.pkl) ...")
    X_test = joblib.load(PROCESSED_DIR / "X_test.pkl")
    y_test = joblib.load(PROCESSED_DIR / "y_test.pkl")
    print(f"    Test set size: {len(y_test):,} samples (Fraud cases: {int(y_test.sum())})")

    # Feature Names (Time, V1..V28, Amount)
    feature_names = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]

    # 2. Define Model Variants
    model_configs = [
        {"name": "Logistic Regression (Baseline)", "file": "logistic_regression_baseline.pkl"},
        {"name": "Logistic Regression (SMOTE)", "file": "logistic_regression_smote.pkl"},
        {"name": "Logistic Regression (Undersampled)", "file": "logistic_regression_undersampled.pkl"},
        {"name": "XGBoost (SMOTE)", "file": "xgboost_smote.pkl"},
    ]

    results = []
    fig, ax = plt.subplots(figsize=(9, 6))

    xgb_model = None

    print("\n[2] Evaluating models on held-out test set ...")
    for config in model_configs:
        model_path = MODELS_DIR / config["file"]
        if not model_path.exists():
            print(f"    [SKIP] Model not found: {model_path}")
            continue

        clf = joblib.load(model_path)
        if config["name"] == "XGBoost (SMOTE)":
            xgb_model = clf

        # Measure latency
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
            "Model Variant": config["name"],
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
    ax.set_title("Precision-Recall Curves — All Models Benchmark", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Recall", fontsize=11)
    ax.set_ylabel("Precision", fontsize=11)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.legend(loc="lower left", frameon=True)

    fig_path = FIGURES_DIR / "all_models_pr_curves.png"
    fig.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved 4-model PR-Curve plot -> {fig_path}")

    # 4. Save CSV Reports
    df_results = pd.DataFrame(results)
    csv_all_path = REPORTS_DIR / "model_comparison_all.csv"
    df_results.to_csv(csv_all_path, index=False)
    print(f"    Saved combined comparison CSV -> {csv_all_path}")

    # 5. Print Combined Comparison Table
    print("\n" + "=" * 92)
    print(" ALL MODELS BENCHMARK PERFORMANCE COMPARISON")
    print("=" * 92)

    header = f"{'Model Variant':<38} | {'Precision':>9} | {'Recall':>9} | {'F1-Score':>9} | {'ROC-AUC':>9} | {'PR-AUC':>9} | {'FP':>5} | {'FN':>4}"
    sep = "-" * len(header)
    print("\n" + sep)
    print(header)
    print(sep)

    for r in results:
        print(
            f"{r['Model Variant']:<38} | {r['Precision']:>9.4f} | {r['Recall']:>9.4f} | "
            f"{r['F1-Score']:>9.4f} | {r['ROC-AUC']:>9.4f} | {r['PR-AUC']:>9.4f} | "
            f"{r['FP']:>5} | {r['FN']:>4}"
        )
    print(sep)

    # 6. Feature Importance Table (XGBoost)
    if xgb_model is not None:
        importances = xgb_model.feature_importances_
        feat_imp_df = pd.DataFrame({
            "Feature": feature_names,
            "Importance": importances
        }).sort_values(by="Importance", ascending=False)

        print("\n" + "=" * 75)
        print(" XGBOOST FEATURE IMPORTANCE (TOP 10 FEATURES)")
        print("=" * 75)
        top10 = feat_imp_df.head(10)
        print(f"{'Rank':<5} | {'Feature':<12} | {'Importance Score':>18}")
        print("-" * 42)
        for idx, (_, row) in enumerate(top10.iterrows(), 1):
            print(f"{idx:<5} | {row['Feature']:<12} | {row['Importance']:>18.6f}")
        print("-" * 42)

    # 7. Winner Analysis
    lr_best_pr_auc = df_results[df_results["Model Variant"].str.startswith("Logistic")]["PR-AUC"].max()
    xgb_row = df_results[df_results["Model Variant"] == "XGBoost (SMOTE)"].iloc[0]
    xgb_pr_auc = xgb_row["PR-AUC"]
    diff = xgb_pr_auc - lr_best_pr_auc

    print("\n" + "=" * 75)
    print(" XGBOOST VS LOGISTIC REGRESSION COMPARISON SUMMARY")
    print("=" * 75)
    print(f" [*] Best Logistic Regression PR-AUC : {lr_best_pr_auc:.4f}")
    print(f" [*] XGBoost (SMOTE) PR-AUC          : {xgb_pr_auc:.4f}")
    if diff > 0:
        print(f" [*] Result: XGBoost BEAT Logistic Regression by +{diff:.4f} PR-AUC (+{diff/lr_best_pr_auc*100:.2f}%)!")
    else:
        print(f" [*] Result: XGBoost underperformed Logistic Regression by {diff:.4f} PR-AUC.")
    print("=" * 75)


if __name__ == "__main__":
    try:
        run_evaluation()
    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}", file=sys.stderr)
        sys.exit(1)
