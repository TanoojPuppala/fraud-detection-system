"""
XGBoost Classifier Training & Hyperparameter Tuning Script.

Trains an XGBoost classifier on the SMOTE-resampled training dataset:
1. Loads X_train_smote.pkl, y_train_smote.pkl.
2. Performs RandomizedSearchCV (20 iterations, 3-fold CV) optimizing PR-AUC (average_precision).
3. Retrains the final model on the full SMOTE training set using best hyperparameters.
4. Records training wall-clock time.
5. Saves the final model to ml/models/xgboost_smote.pkl using joblib.
"""

from pathlib import Path
import sys
import time
import joblib
import xgboost as xgb
from sklearn.model_selection import RandomizedSearchCV

# Ensure UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROCESSED_DIR = Path("ml/data/processed")
MODELS_DIR = Path("ml/models")


def run_xgboost_training() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(" XGBOOST CLASSIFIER HYPERPARAMETER TUNING & TRAINING")
    print("=" * 70)

    # 1. Load SMOTE Dataset
    print("\n[1] Loading SMOTE dataset from ml/data/processed/ ...")
    X_train_smote = joblib.load(PROCESSED_DIR / "X_train_smote.pkl")
    y_train_smote = joblib.load(PROCESSED_DIR / "y_train_smote.pkl")
    print(f"    - X_train_smote shape: {X_train_smote.shape}")
    print(f"    - y_train_smote shape: {y_train_smote.shape} (Fraud cases: {y_train_smote.sum():,})")

    # 2. Define Parameter Space for RandomizedSearchCV
    param_dist = {
        "n_estimators": [100, 200, 300],
        "max_depth": [3, 5, 7, 9],
        "learning_rate": [0.01, 0.05, 0.1, 0.2],
        "subsample": [0.7, 0.8, 0.9, 1.0],
        "colsample_bytree": [0.7, 0.8, 0.9, 1.0]
    }

    base_xgb = xgb.XGBClassifier(
        random_state=42,
        eval_metric="logloss",
        n_jobs=-1,
        tree_method="hist"  # Fast histogram algorithm for speed
    )

    print("\n[2] Setting up RandomizedSearchCV (20 iterations, 3-fold CV, PR-AUC scoring) ...")
    search = RandomizedSearchCV(
        estimator=base_xgb,
        param_distributions=param_dist,
        n_iter=20,
        scoring="average_precision",
        cv=3,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )

    print("    Running hyperparameter search on 453,204 SMOTE samples ...")
    search_start = time.perf_counter()
    search.fit(X_train_smote, y_train_smote)
    search_time = time.perf_counter() - search_start

    print(f"\n[3] Search complete in {search_time:.2f} seconds.")
    print(f"    - Best CV PR-AUC Score: {search.best_score_:.4f}")
    print("    - Best Hyperparameters:")
    for k, v in search.best_params_.items():
        print(f"      * {k}: {v}")

    # 3. Retrain Final Model on Full SMOTE Training Set
    print("\n[4] Retraining final XGBoost model with best hyperparameters ...")
    fit_start = time.perf_counter()
    best_xgb = xgb.XGBClassifier(
        **search.best_params_,
        random_state=42,
        eval_metric="logloss",
        n_jobs=-1,
        tree_method="hist"
    )
    best_xgb.fit(X_train_smote, y_train_smote)
    train_time = time.perf_counter() - fit_start

    total_time = search_time + train_time
    print(f"    - Final training completed in {train_time:.2f} seconds.")
    print(f"    - Total execution wall-clock time: {total_time:.2f} seconds.")

    # 4. Save Trained Model
    model_path = MODELS_DIR / "xgboost_smote.pkl"
    joblib.dump(best_xgb, model_path)
    print(f"\n[5] Saved XGBoost model -> {model_path}")

    print("\n" + "=" * 70)
    print(" [OK] XGBOOST TRAINING & TUNING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    try:
        run_xgboost_training()
    except Exception as e:
        print(f"\n[ERROR] XGBoost training failed: {e}", file=sys.stderr)
        sys.exit(1)
