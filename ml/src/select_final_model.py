"""
Final Model Selection and Production Packaging Script.

Loads evaluation metrics from ml/reports/model_comparison_all.csv, calculates
business cost based on FP/FN cost assumptions, identifies champion models,
generates a formal selection report (ml/reports/final_model_selection.md),
and packages the chosen model into ml/models/production/.
"""

import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
import pandas as pd

# Ensure UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Directory Definitions
BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = BASE_DIR / "ml" / "reports"
MODELS_DIR = BASE_DIR / "ml" / "models"
PROD_DIR = MODELS_DIR / "production"
CSV_PATH = REPORTS_DIR / "model_comparison_all.csv"
REPORT_MD_PATH = REPORTS_DIR / "final_model_selection.md"

# Illustrative dollar cost assumptions for demonstrating cost-aware model selection
# Note: These figures are illustrative placeholder assumptions for cost analysis, not real industry figures.
FP_COST_USD = 5.0    # $5 analyst triage cost per false alarm
FN_COST_USD = 500.0  # $500 average loss per undetected fraud transaction

# Mapping of Model Variant names to original filename in ml/models/
MODEL_FILE_MAP = {
    "Logistic Regression (Baseline)": "logistic_regression_baseline.pkl",
    "Logistic Regression (SMOTE)": "logistic_regression_smote.pkl",
    "Logistic Regression (Undersampled)": "logistic_regression_undersampled.pkl",
    "XGBoost (SMOTE)": "xgboost_smote.pkl",
    "PyTorch DNN (SMOTE)": "dnn_smote.pt",
    "PyTorch Autoencoder (Baseline)": "autoencoder_baseline.pt",
}


def run_model_selection() -> None:
    print("=" * 85)
    print(" FINAL MODEL SELECTION & PRODUCTION PACKAGING BENCHMARK")
    print("=" * 85)

    # 1. Load comparison CSV
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Model comparison file not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    print(f"\n[1] Loaded comparison metrics from {CSV_PATH.name} ({len(df)} models)")

    # Ensure required columns exist
    required_cols = {"Model Variant", "Precision", "Recall", "F1-Score", "ROC-AUC", "PR-AUC", "FP", "FN", "Inference Time (ms)"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns in CSV: {missing}")

    # Add Training Time column if missing
    if "Training Time (s)" not in df.columns and "Training Time" not in df.columns:
        df["Training Time"] = "N/A"
    elif "Training Time (s)" in df.columns:
        df["Training Time"] = df["Training Time (s)"].apply(lambda x: f"{x:.2f}s" if pd.notnull(x) else "N/A")

    # 2. Compute Business Cost
    # total_cost = (FP * 5) + (FN * 500)
    df["Total Business Cost ($)"] = (df["FP"] * FP_COST_USD) + (df["FN"] * FN_COST_USD)

    # Sort by PR-AUC descending
    df_sorted = df.sort_values(by="PR-AUC", ascending=False).reset_index(drop=True)

    # 3. Print Clean Comparison Table to Console
    print("\n" + "=" * 115)
    print(" BENCHMARK MODEL COMPARISON TABLE (SORTED BY PR-AUC DESCENDING)")
    print("=" * 115)
    
    header = (
        f"{'Model Variant':<35} | {'PR-AUC':>7} | {'ROC-AUC':>7} | {'Precision':>9} | "
        f"{'Recall':>7} | {'F1':>7} | {'FP':>5} | {'FN':>4} | {'Cost ($)':>10} | {'Infer (ms)':>10}"
    )
    sep = "-" * len(header)
    print(header)
    print(sep)

    for _, row in df_sorted.iterrows():
        print(
            f"{row['Model Variant']:<35} | {row['PR-AUC']:>7.4f} | {row['ROC-AUC']:>7.4f} | "
            f"{row['Precision']:>9.4f} | {row['Recall']:>7.4f} | {row['F1-Score']:>7.4f} | "
            f"{int(row['FP']):>5} | {int(row['FN']):>4} | ${row['Total Business Cost ($)']:>9,.2f} | "
            f"{row['Inference Time (ms)']:>10.2f}"
        )
    print(sep)

    # 4. Identify Champion Models (Best PR-AUC vs Lowest Business Cost)
    best_prauc_row = df_sorted.loc[df_sorted["PR-AUC"].idxmax()]
    lowest_cost_row = df_sorted.loc[df_sorted["Total Business Cost ($)"].idxmin()]

    best_prauc_model_name = best_prauc_row["Model Variant"]
    lowest_cost_model_name = lowest_cost_row["Model Variant"]

    print("\n" + "=" * 85)
    print(" MODEL PERFORMANCE EVALUATION & DIVERGENCE ANALYSIS")
    print("=" * 85)
    print(f" [*] Champion Model by PR-AUC         : {best_prauc_model_name} (PR-AUC = {best_prauc_row['PR-AUC']:.4f}, Cost = ${best_prauc_row['Total Business Cost ($)']:,.2f})")
    print(f" [*] Champion Model by Business Cost  : {lowest_cost_model_name} (Cost = ${lowest_cost_row['Total Business Cost ($)']:,.2f}, PR-AUC = {lowest_cost_row['PR-AUC']:.4f})")

    same_model = (best_prauc_model_name == lowest_cost_model_name)
    if same_model:
        divergence_explanation = (
            f"The best model by PR-AUC ({best_prauc_model_name}) is ALSO the model with the lowest estimated "
            f"business cost (${best_prauc_row['Total Business Cost ($)']:,.2f}). It achieves the superior balance "
            f"between precision and recall, minimizing total monetary impact."
        )
        print(f"\n [RESULT]: Single unified champion identified! ({best_prauc_model_name})")
    else:
        divergence_explanation = (
            f"The model winning on PR-AUC ({best_prauc_model_name}, PR-AUC={best_prauc_row['PR-AUC']:.4f}) "
            f"differs from the model winning on business cost ({lowest_cost_model_name}, Cost=${lowest_cost_row['Total Business Cost ($)']:,.2f}).\n"
            f"Reason: PR-AUC evaluates ranking quality across all thresholds, prioritizing high Precision at high Recall thresholds.\n"
            f"However, under our asymmetric cost matrix ($5 FP vs $500 FN), false negatives are 100x more costly than false positives.\n"
            f"{lowest_cost_model_name} recorded fewer False Negatives ({int(lowest_cost_row['FN'])} FN vs {int(best_prauc_row['FN'])} FN for {best_prauc_model_name}), "
            f"saving ${abs(int(best_prauc_row['FN']) - int(lowest_cost_row['FN'])) * 500:,.2f} in undetected fraud losses, which more than offset its higher false alarm volume."
        )
        print(f"\n [RESULT]: Divergence Detected!\n{divergence_explanation}")

    # 5. Production Model Selection Rationale
    # Primary objective in financial fraud production system: Minimize total business cost while maintaining solid PR-AUC.
    selected_row = lowest_cost_row if not same_model else best_prauc_row
    selected_model_name = selected_row["Model Variant"]

    recommendation_text = (
        f"RECOMMENDED DEPLOYMENT MODEL FOR /predict ENDPOINT:\n"
        f"We select '{selected_model_name}' for backend production deployment. "
        f"It achieves the lowest total estimated business cost of ${selected_row['Total Business Cost ($)']:,.2f} on held-out test data, "
        f"capturing {selected_row['Recall']*100:.1f}% of fraud cases ({int(selected_row['TP'])} TP / {int(selected_row['FN'])} FN) "
        f"with a fast inference time of {selected_row['Inference Time (ms)']:.2f} ms per batch. "
        f"While {best_prauc_model_name} achieves a higher PR-AUC ({best_prauc_row['PR-AUC']:.4f}), '{selected_model_name}' saves "
        f"${(best_prauc_row['Total Business Cost ($)'] - lowest_cost_row['Total Business Cost ($)']):,.2f} in total financial losses "
        f"by minimizing catastrophic undetected false negatives ($500 loss per uncaught fraud event)."
    )

    print("\n" + "=" * 85)
    print(" FINAL PRODUCTION RECOMMENDATION")
    print("=" * 85)
    print(recommendation_text)
    print("=" * 85)

    # 6. Generate Markdown Selection Report
    md_content = f"""# Final Model Selection & Backend Deployment Report

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
"""

    for _, row in df_sorted.iterrows():
        md_content += (
            f"| **{row['Model Variant']}** | {row['PR-AUC']:.4f} | {row['ROC-AUC']:.4f} | "
            f"{row['Precision']:.4f} | {row['Recall']:.4f} | {row['F1-Score']:.4f} | "
            f"{int(row['FP'])} | {int(row['FN'])} | **${row['Total Business Cost ($)']:,.2f}** | "
            f"{row['Inference Time (ms)']:.2f} ms |\n"
        )

    md_content += f"""
---

## 2. Model Performance & Divergence Analysis

- **Best Model by PR-AUC**: `{best_prauc_model_name}` (PR-AUC = **{best_prauc_row['PR-AUC']:.4f}**, Business Cost = **${best_prauc_row['Total Business Cost ($)']:,.2f}**)
- **Best Model by Business Cost**: `{lowest_cost_model_name}` (Business Cost = **${lowest_cost_row['Total Business Cost ($)']:,.2f}**, PR-AUC = **{lowest_cost_row['PR-AUC']:.4f}**)
- **Divergence Status**: **{"Identical Champion Model" if same_model else "Different Models Identified"}**

### Explanatory Breakdown:

{divergence_explanation}

---

## 3. Final Production Recommendation & Rationale

> [!IMPORTANT]
> **Production Recommendation for `/predict` Endpoint**:
> 
> We formally recommend deploying **{selected_model_name}** to the backend `/predict` endpoint. It delivers the lowest total estimated business cost of **${selected_row['Total Business Cost ($)']:,.2f}** on held-out test data, achieving a high recall of **{selected_row['Recall']*100:.1f}%** ({int(selected_row['TP'])} caught frauds vs {int(selected_row['FN'])} missed frauds) and a rapid inference latency of **{selected_row['Inference Time (ms)']:.2f} ms**. While `{best_prauc_model_name}` achieved the top PR-AUC score ({best_prauc_row['PR-AUC']:.4f}), `{selected_model_name}` saves **${(best_prauc_row['Total Business Cost ($)'] - lowest_cost_row['Total Business Cost ($)']):,.2f}** in financial losses by reducing catastrophic false negative fraud escapes ($500 per undetected fraud).

---

## 4. Production Artifact Packaging

The selected model has been exported to the backend deployment directory `ml/models/production/`:
- **Production Model File**: `ml/models/production/{"production_model.pt" if selected_model_name.startswith("PyTorch") else "production_model.pkl"}`
- **Model Info Metadata**: `ml/models/production/production_model_info.json`
- **Selection Timestamp**: `{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}`
"""

    REPORT_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD_PATH.write_text(md_content, encoding="utf-8")
    print(f"\n[+] Saved final model selection report -> {REPORT_MD_PATH}")

    # 7. Package Production Model to ml/models/production/
    PROD_DIR.mkdir(parents=True, exist_ok=True)

    original_filename = MODEL_FILE_MAP.get(selected_model_name)
    if not original_filename:
        raise ValueError(f"Could not map model variant '{selected_model_name}' to filename.")

    src_file_path = MODELS_DIR / original_filename
    if not src_file_path.exists():
        raise FileNotFoundError(f"Source model file does not exist: {src_file_path}")

    ext = src_file_path.suffix
    dest_filename = f"production_model{ext}"
    dest_file_path = PROD_DIR / dest_filename

    shutil.copy2(src_file_path, dest_file_path)
    print(f"[+] Copied production model binary -> {dest_file_path}")

    # Create production_model_info.json
    prod_info = {
        "original_model_variant": selected_model_name,
        "original_filename": original_filename,
        "production_filename": dest_filename,
        "selection_date": datetime.now().isoformat(),
        "selection_criteria": "Lowest total business cost (FP=$5, FN=$500) under held-out test evaluation",
        "metrics": {
            "Precision": float(selected_row["Precision"]),
            "Recall": float(selected_row["Recall"]),
            "F1-Score": float(selected_row["F1-Score"]),
            "ROC-AUC": float(selected_row["ROC-AUC"]),
            "PR-AUC": float(selected_row["PR-AUC"]),
            "TN": int(selected_row["TN"]),
            "FP": int(selected_row["FP"]),
            "FN": int(selected_row["FN"]),
            "TP": int(selected_row["TP"]),
            "Total Business Cost ($)": float(selected_row["Total Business Cost ($)"]),
            "Inference Time (ms)": float(selected_row["Inference Time (ms)"])
        }
    }

    info_json_path = PROD_DIR / "production_model_info.json"
    with open(info_json_path, "w", encoding="utf-8") as f:
        json.dump(prod_info, f, indent=2)

    print(f"[+] Created metadata file -> {info_json_path}")
    print("\n" + "=" * 85)
    print(" [OK] MODEL SELECTION AND PRODUCTION PACKAGING COMPLETE")
    print("=" * 85)


if __name__ == "__main__":
    try:
        run_model_selection()
    except Exception as e:
        print(f"\n[ERROR] Model selection script failed: {e}", file=sys.stderr)
        sys.exit(1)
