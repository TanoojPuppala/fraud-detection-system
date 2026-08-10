"""
Training Script for Logistic Regression Baseline Models.

Trains Logistic Regression models on three preprocessed training set variants:
1. Baseline (imbalanced dataset, trained with class_weight='balanced')
2. SMOTE (oversampled dataset, trained with default class_weight)
3. Undersampled (random undersampled dataset, trained with default class_weight)

Saves trained model objects into ml/models/ as .pkl files.
"""

from pathlib import Path
import sys
import joblib
from sklearn.linear_model import LogisticRegression

# Ensure UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROCESSED_DIR = Path("ml/data/processed")
MODELS_DIR = Path("ml/models")


def run_training() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(" LOGISTIC REGRESSION MODEL TRAINING")
    print("=" * 70)

    # 1. Load Datasets
    print("\n[1] Loading preprocessed dataset variants from ml/data/processed/ ...")
    
    X_train_base = joblib.load(PROCESSED_DIR / "X_train_baseline.pkl")
    y_train_base = joblib.load(PROCESSED_DIR / "y_train_baseline.pkl")
    
    X_train_smote = joblib.load(PROCESSED_DIR / "X_train_smote.pkl")
    y_train_smote = joblib.load(PROCESSED_DIR / "y_train_smote.pkl")
    
    X_train_under = joblib.load(PROCESSED_DIR / "X_train_undersampled.pkl")
    y_train_under = joblib.load(PROCESSED_DIR / "y_train_undersampled.pkl")

    print(f"    - Baseline train shape    : {X_train_base.shape}")
    print(f"    - SMOTE train shape       : {X_train_smote.shape}")
    print(f"    - Undersampled train shape: {X_train_under.shape}")

    # 2. Train Models
    variants = [
        {
            "name": "baseline",
            "X": X_train_base,
            "y": y_train_base,
            "class_weight": "balanced",
            "file": "logistic_regression_baseline.pkl"
        },
        {
            "name": "smote",
            "X": X_train_smote,
            "y": y_train_smote,
            "class_weight": None,
            "file": "logistic_regression_smote.pkl"
        },
        {
            "name": "undersampled",
            "X": X_train_under,
            "y": y_train_under,
            "class_weight": None,
            "file": "logistic_regression_undersampled.pkl"
        }
    ]

    print("\n[2] Training Logistic Regression models ...")
    for var in variants:
        print(f"    - Training '{var['name']}' variant (class_weight={var['class_weight']}) ...")
        clf = LogisticRegression(
            class_weight=var["class_weight"],
            random_state=42,
            max_iter=1000
        )
        clf.fit(var["X"], var["y"])
        
        save_path = MODELS_DIR / var["file"]
        joblib.dump(clf, save_path)
        print(f"      Saved model -> {save_path}")

    print("\n" + "=" * 70)
    print(" [OK] LOGISTIC REGRESSION TRAINING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    try:
        run_training()
    except Exception as e:
        print(f"\n[ERROR] Training failed: {e}", file=sys.stderr)
        sys.exit(1)
