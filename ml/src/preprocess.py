"""
Leakage-Safe Preprocessing Pipeline for Credit Card Fraud Detection.

WHY THE SPLIT HAPPENS BEFORE SCALING AND RESAMPLING:
-----------------------------------------------------
Data leakage occurs when information from the test set influences the training
process, causing over-optimistic evaluation metrics that don't generalise to
real-world data.

  1. Scaling leakage: If we fit StandardScaler on the FULL dataset (train +
     test), the scaler learns the global mean and std — which includes test-set
     statistics. The test set then quietly informs how training features are
     transformed. By fitting the scaler ONLY on X_train and then calling
     .transform() on X_test, the test set remains a true held-out set whose
     distribution was never seen during preprocessing.

  2. Resampling leakage: SMOTE generates synthetic fraud samples by interpolating
     between real minority-class neighbours. If applied before splitting, some
     synthetic points would be interpolated from real test-set fraud cases,
     effectively embedding test-set information into the training distribution.
     RandomUnderSampler has the same issue: the majority samples it removes are
     chosen based on the full dataset's neighbourhood structure. By resampling
     ONLY after splitting — and ONLY on X_train/y_train — X_test/y_test reflect
     the true real-world class imbalance (~0.17% fraud) and provide an honest
     benchmark.

Correct order: Split → Scale (fit on train only) → Resample (train only) → Save
"""

from pathlib import Path
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

# Ensure UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── Paths ──────────────────────────────────────────────────────────────────────
RAW_CSV       = Path("ml/data/raw/creditcard.csv")
PROCESSED_DIR = Path("ml/data/processed")
MODELS_DIR    = Path("ml/models")


def _fraud_summary(y: np.ndarray, label: str) -> dict:
    """Return a summary dict for a label array."""
    total = len(y)
    fraud = int(y.sum())
    legit = total - fraud
    pct   = fraud / total * 100
    return {"Variant": label, "Total Rows": total, "Fraud": fraud,
            "Legitimate": legit, "Fraud %": pct}


def run_preprocessing() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(" LEAKAGE-SAFE PREPROCESSING PIPELINE")
    print("=" * 70)

    # ── Step 1: Load ──────────────────────────────────────────────────────────
    print(f"\n[1] Loading raw dataset: {RAW_CSV.resolve()} ...")
    if not RAW_CSV.exists():
        raise FileNotFoundError(f"Dataset not found at {RAW_CSV.resolve()}")
    df = pd.read_csv(RAW_CSV)
    print(f"    Loaded  : {len(df):,} rows x {df.shape[1]} columns")

    # ── Step 2: Drop duplicates ───────────────────────────────────────────────
    before = len(df)
    df = df.drop_duplicates()
    dropped = before - len(df)
    print(f"\n[2] Deduplication:")
    print(f"    Dropped  : {dropped:,} duplicate rows")
    print(f"    Remaining: {len(df):,} rows")

    # ── Step 3: Separate features and target ──────────────────────────────────
    print("\n[3] Separating features (X) and target (y = Class) ...")
    X = df.drop(columns=["Class"]).values
    y = df["Class"].values
    print(f"    X shape : {X.shape}")
    print(f"    y shape : {y.shape}  |  Fraud cases: {int(y.sum()):,}  ({y.mean()*100:.4f}%)")

    # ── Step 4: Stratified 80/20 split ────────────────────────────────────────
    print("\n[4] Stratified 80/20 train/test split (random_state=42) ...")
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )
    print(f"    Train   : {len(X_train_raw):,} rows  |  Fraud: {int(y_train.sum()):,}  ({y_train.mean()*100:.4f}%)")
    print(f"    Test    : {len(X_test_raw):,} rows  |  Fraud: {int(y_test.sum()):,}  ({y_test.mean()*100:.4f}%)")

    # ── Step 5: Scale (fit ONLY on train) ─────────────────────────────────────
    print("\n[5] Fitting StandardScaler on X_train only ...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_raw)   # fit + transform train
    X_test_scaled  = scaler.transform(X_test_raw)        # transform only — no fit
    print(f"    Scaler fitted on {scaler.n_samples_seen_:,} training samples")
    print(f"    (Test set was NEVER seen by the scaler — no leakage)")

    # ── Step 6: Save scaler ───────────────────────────────────────────────────
    scaler_path = MODELS_DIR / "scaler.pkl"
    joblib.dump(scaler, scaler_path)
    print(f"\n[6] Scaler saved -> {scaler_path}")

    # ── Step 7a: Baseline (original imbalanced) ───────────────────────────────
    print("\n[7a] Baseline training set (original imbalance, no resampling) ...")
    X_train_baseline = X_train_scaled
    y_train_baseline = y_train
    print(f"     Rows   : {len(X_train_baseline):,}  |  Fraud: {int(y_train_baseline.sum()):,}  ({y_train_baseline.mean()*100:.4f}%)")

    # ── Step 7b: SMOTE ────────────────────────────────────────────────────────
    print("\n[7b] Applying SMOTE to training set (random_state=42) ...")
    smote = SMOTE(random_state=42)
    X_train_smote, y_train_smote = smote.fit_resample(X_train_scaled, y_train)
    print(f"     Rows   : {len(X_train_smote):,}  |  Fraud: {int(y_train_smote.sum()):,}  ({y_train_smote.mean()*100:.4f}%)")

    # ── Step 7c: Random Undersampling ─────────────────────────────────────────
    print("\n[7c] Applying RandomUnderSampler to training set (random_state=42) ...")
    rus = RandomUnderSampler(random_state=42)
    X_train_under, y_train_under = rus.fit_resample(X_train_scaled, y_train)
    print(f"     Rows   : {len(X_train_under):,}  |  Fraud: {int(y_train_under.sum()):,}  ({y_train_under.mean()*100:.4f}%)")

    # ── Step 8: Save all arrays ───────────────────────────────────────────────
    print("\n[8] Saving processed arrays to ml/data/processed/ ...")
    save_map = {
        "X_train_baseline.pkl"    : X_train_baseline,
        "y_train_baseline.pkl"    : y_train_baseline,
        "X_train_smote.pkl"       : X_train_smote,
        "y_train_smote.pkl"       : y_train_smote,
        "X_train_undersampled.pkl": X_train_under,
        "y_train_undersampled.pkl": y_train_under,
        "X_test.pkl"              : X_test_scaled,
        "y_test.pkl"              : y_test,
    }
    for fname, arr in save_map.items():
        path = PROCESSED_DIR / fname
        joblib.dump(arr, path)
        print(f"    Saved: {path}  ({arr.shape})")

    # ── Step 9: Summary table ─────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(" PREPROCESSING SUMMARY")
    print("=" * 70)

    summaries = [
        _fraud_summary(y_train_baseline, "Train - Baseline (imbalanced)"),
        _fraud_summary(y_train_smote,    "Train - SMOTE (oversampled)"),
        _fraud_summary(y_train_under,    "Train - Undersampled"),
        _fraud_summary(y_test,           "Test  - Held-out (NEVER resampled)"),
    ]

    header = (
        f"{'Variant':<38} | {'Total Rows':>11} | "
        f"{'Fraud':>8} | {'Legitimate':>12} | {'Fraud %':>8}"
    )
    sep = "-" * len(header)
    print("\n" + sep)
    print(header)
    print(sep)
    for s in summaries:
        print(
            f"{s['Variant']:<38} | {s['Total Rows']:>11,} | {s['Fraud']:>8,} | "
            f"{s['Legitimate']:>12,} | {s['Fraud %']:>7.4f}%"
        )
    print(sep)

    print("\n[OK] Preprocessing complete. No data leakage - test set reflects")
    print("     true real-world imbalance (~0.17% fraud) throughout.")
    print("=" * 70)


if __name__ == "__main__":
    try:
        run_preprocessing()
    except Exception as e:
        print(f"\n[ERROR] Preprocessing failed: {e}", file=sys.stderr)
        sys.exit(1)
