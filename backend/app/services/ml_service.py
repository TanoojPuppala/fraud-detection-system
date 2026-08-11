"""
ML Production Model Inference Service & Risk Categorization Engine.
"""

import time
import json
import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict, Any, Tuple, List

from backend.app.core.config import settings

FEATURE_ORDER = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]


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


class MLInferenceService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_dir = settings.PROD_MODEL_DIR
        self.scaler_path = settings.SCALER_PATH

        # Load Metadata
        info_path = self.model_dir / "production_model_info.json"
        if info_path.exists():
            with open(info_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            self.model_version = self.metadata.get("original_model_variant", "PyTorch DNN (SMOTE)")
            self.threshold = float(self.metadata.get("optimal_threshold", 0.50))
        else:
            self.metadata = {}
            self.model_version = "PyTorch DNN (SMOTE)"
            self.threshold = 0.50

        # Load Scaler
        if self.scaler_path.exists():
            self.scaler = joblib.load(self.scaler_path)
        else:
            self.scaler = None

        # Load Production Model
        model_file = self.model_dir / "production_model.pt"
        if not model_file.exists():
            model_file = settings.BASE_DIR / "ml" / "models" / "dnn_smote.pt"

        if model_file.suffix == ".pt":
            self.model = FraudDNN(input_dim=30).to(self.device)
            self.model.load_state_dict(torch.load(model_file, map_location=self.device))
            self.model.eval()
            self.is_pytorch = True
        else:
            self.model = joblib.load(model_file)
            self.is_pytorch = False

    def _prepare_vector(self, tx_dict: Dict[str, float]) -> np.ndarray:
        """
        Converts feature dictionary into standard 30-dim scaled vector [Time, V1..V28, Amount].
        """
        raw_vals = [float(tx_dict.get(col.lower(), tx_dict.get(col, 0.0))) for col in FEATURE_ORDER]
        raw_arr = np.array(raw_vals, dtype=np.float32).reshape(1, -1)

        # Scale Time & Amount if scaler available (columns 0 and 29)
        if self.scaler is not None:
            # Scaler was fit on full 30-dim matrix (Time and Amount were scaled)
            scaled_arr = self.scaler.transform(raw_arr)
            return scaled_arr
        return raw_arr

    def predict(self, tx_dict: Dict[str, float]) -> Tuple[float, bool, str, float]:
        """
        Predicts fraud probability, is_fraud boolean flag, risk band, and inference latency in ms.
        """
        start_time = time.perf_counter()
        X_scaled = self._prepare_vector(tx_dict)

        if self.is_pytorch:
            tensor_input = torch.tensor(X_scaled, dtype=torch.float32).to(self.device)
            with torch.no_grad():
                prob = float(self.model(tensor_input).cpu().numpy().flatten()[0])
        else:
            prob = float(self.model.predict_proba(X_scaled)[:, 1][0])

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        is_fraud = prob >= self.threshold

        # Determine Risk Band
        if prob < 0.30:
            risk_band = "Low"
        elif prob < 0.70:
            risk_band = "Medium"
        else:
            risk_band = "High"

        return prob, is_fraud, risk_band, latency_ms

    def get_shap_contributions(self, tx_dict: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Calculates heuristic feature attribution impact based on absolute z-scores / weights.
        """
        X_scaled = self._prepare_vector(tx_dict)[0]
        contributions = []

        for name, val in zip(FEATURE_ORDER, X_scaled):
            abs_val = float(abs(val))
            impact = "Increases Fraud Risk" if val < -1.5 or val > 1.5 else "Neutral"
            contributions.append({
                "feature": name,
                "value": float(val),
                "shap_value": float(round(val * 0.15, 4)),
                "impact": impact
            })

        contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        return contributions[:8]


ml_service = MLInferenceService()
