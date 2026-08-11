"""
Explainability & Model Info Endpoints (/api/v1/explain, /api/v1/model-info).
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Prediction
from backend.app.services.ml_service import ml_service

router = APIRouter(tags=["Explainability & Metadata"])


@router.get("/model-info")
def get_production_model_info():
    return {
        "status": "online",
        "model_version": ml_service.model_version,
        "decision_threshold": ml_service.threshold,
        "is_pytorch": ml_service.is_pytorch,
        "metadata": ml_service.metadata
    }


@router.get("/explain/{prediction_id}")
def get_prediction_explanation(prediction_id: int, db: Session = Depends(get_db)):
    pred = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction ID not found")

    shap_data = json.loads(pred.shap_explanation_json) if pred.shap_explanation_json else []

    return {
        "prediction_id": pred.id,
        "raw_probability": pred.raw_probability,
        "is_fraud": pred.is_fraud_predicted,
        "risk_band": pred.risk_band,
        "model_version": pred.model_version,
        "top_shap_features": shap_data
    }
