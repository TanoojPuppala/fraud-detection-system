"""
SHAP Explainability Module for Fraud Detection System.

Calculates SHAP (SHapley Additive exPlanations) values for global model interpretability
and local per-prediction explanations (feature attribution scores). Provides a FraudExplainer
class for seamless integration into the FastAPI backend service.
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
import shap

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

FEATURE_NAMES = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]


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


class FraudExplainer:
    """
    SHAP Explainer wrapper providing local and global feature attribution scores.
    """
    def __init__(self, bg_samples: int = 100):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = PROD_DIR / "production_model.pt"
        if not self.model_path.exists():
            self.model_path = MODELS_DIR / "dnn_smote.pt"

        # Load background data for SHAP KernelExplainer
        X_train = joblib.load(PROCESSED_DIR / "X_train_baseline.pkl")
        np.random.seed(42)
        idx = np.random.choice(len(X_train), size=min(bg_samples, len(X_train)), replace=False)
        self.bg_data = X_train[idx]

        if self.model_path.suffix == ".pt":
            self.model = FraudDNN(input_dim=30).to(self.device)
            self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            self.model.eval()

            def predict_fn(x_arr: np.ndarray) -> np.ndarray:
                x_tensor = torch.tensor(x_arr, dtype=torch.float32).to(self.device)
                with torch.no_grad():
                    return self.model(x_tensor).cpu().numpy().flatten()

            self.predict_fn = predict_fn
        else:
            self.model = joblib.load(self.model_path)
            self.predict_fn = lambda x: self.model.predict_proba(x)[:, 1]

        # Initialize KernelExplainer
        self.explainer = shap.KernelExplainer(self.predict_fn, self.bg_data)

    def explain_instance(self, feature_vector: np.ndarray, top_k: int = 10) -> dict:
        """
        Calculates SHAP feature attribution scores for a single transaction vector.
        """
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)

        shap_vals = self.explainer.shap_values(feature_vector, nsamples=100)
        if isinstance(shap_vals, list):
            shap_vals = shap_vals[0]
        if shap_vals.ndim == 2:
            shap_vals = shap_vals[0]

        base_val = float(self.explainer.expected_value)
        feature_contributions = []

        for name, val, shap_v in zip(FEATURE_NAMES, feature_vector[0], shap_vals):
            feature_contributions.append({
                "feature": name,
                "value": float(val),
                "shap_value": float(shap_v),
                "abs_shap": abs(float(shap_v)),
                "impact": "Increases Fraud Risk" if shap_v > 0 else "Decreases Fraud Risk"
            })

        # Sort by absolute SHAP impact
        feature_contributions.sort(key=lambda x: x["abs_shap"], reverse=True)

        return {
            "base_value": base_val,
            "prediction_probability": float(self.predict_fn(feature_vector)[0]),
            "top_features": feature_contributions[:top_k],
            "all_features": feature_contributions
        }

    def generate_global_summary_plot(self, n_samples: int = 200, save_path: Path = None) -> None:
        """
        Generates and saves global SHAP summary plot across test set samples.
        """
        X_test = joblib.load(PROCESSED_DIR / "X_test.pkl")
        idx = np.random.choice(len(X_test), size=min(n_samples, len(X_test)), replace=False)
        test_sample = X_test[idx]

        shap_values = self.explainer.shap_values(test_sample, nsamples=100)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]

        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, test_sample, feature_names=FEATURE_NAMES, show=False)
        plt.title("SHAP Global Feature Importance Summary — Production Model", fontsize=12, fontweight="bold", pad=12)

        if save_path is None:
            save_path = FIGURES_DIR / "shap_summary.png"

        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"[+] Saved SHAP global summary plot -> {save_path}")


def run_explainability() -> None:
    print("=" * 75)
    print(" SHAP EXPLAINABILITY BENCHMARK & SUMMARY GENERATION")
    print("=" * 75)

    explainer = FraudExplainer(bg_samples=50)

    # 1. Generate Global Summary Plot
    explainer.generate_global_summary_plot(n_samples=100)

    # 2. Test Local Explanation on Sample Fraud Case
    X_test = joblib.load(PROCESSED_DIR / "X_test.pkl")
    y_test = joblib.load(PROCESSED_DIR / "y_test.pkl")
    fraud_indices = np.where(y_test == 1)[0]

    sample_idx = fraud_indices[0] if len(fraud_indices) > 0 else 0
    sample_vector = X_test[sample_idx]

    explanation = explainer.explain_instance(sample_vector, top_k=5)
    print(f"\n[+] Sample Fraud Explanation (Predicted Prob: {explanation['prediction_probability']:.4f}):")
    for feat in explanation["top_features"]:
        print(f"    - {feat['feature']:<8} = {feat['value']:>8.4f} | SHAP: {feat['shap_value']:>+8.4f} ({feat['impact']})")

    print("\n" + "=" * 75)
    print(" [OK] SHAP EXPLAINABILITY MODULE READY")
    print("=" * 75)


if __name__ == "__main__":
    try:
        run_explainability()
    except Exception as e:
        print(f"\n[ERROR] SHAP Explainability script failed: {e}", file=sys.stderr)
        sys.exit(1)
