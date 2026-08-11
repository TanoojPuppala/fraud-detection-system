"""
Prediction Endpoints (/api/v1/predict, /api/v1/batch_predict).
"""

import json
import io
import pandas as pd
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Transaction, Prediction, FraudAlert
from backend.app.services.ml_service import ml_service
from backend.app.schemas.predict import TransactionInput, PredictionResponse, BatchPredictionSummary

router = APIRouter(tags=["Predictions"])


@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def predict_single_transaction(tx_input: TransactionInput, db: Session = Depends(get_db)):
    tx_dict = tx_input.model_dump()

    # 1. Save Transaction record
    db_tx = Transaction(
        transaction_time=tx_input.time,
        amount=tx_input.amount,
        features_json=json.dumps(tx_dict)
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)

    # 2. Run Model Inference
    prob, is_fraud, risk_band, latency_ms = ml_service.predict(tx_dict)
    shap_contributions = ml_service.get_shap_contributions(tx_dict)

    # 3. Save Prediction record
    db_pred = Prediction(
        transaction_id=db_tx.id,
        raw_probability=prob,
        is_fraud_predicted=is_fraud,
        risk_band=risk_band,
        threshold_used=ml_service.threshold,
        model_version=ml_service.model_version,
        inference_time_ms=latency_ms,
        shap_explanation_json=json.dumps(shap_contributions)
    )
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)

    # 4. Create FraudAlert if High Risk or Fraud Predicted
    if is_fraud or risk_band == "High":
        db_alert = FraudAlert(
            prediction_id=db_pred.id,
            risk_score=prob,
            status="New"
        )
        db.add(db_alert)
        db.commit()

    return {
        "prediction_id": db_pred.id,
        "transaction_id": db_tx.id,
        "raw_probability": prob,
        "is_fraud": is_fraud,
        "risk_band": risk_band,
        "decision_threshold": ml_service.threshold,
        "model_version": ml_service.model_version,
        "inference_time_ms": latency_ms,
        "top_shap_features": shap_contributions,
        "created_at": db_pred.created_at
    }


@router.post("/batch_predict", response_model=BatchPredictionSummary)
async def predict_batch_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {e}")

    # Column verification (case-insensitive)
    cols_map = {col.lower(): col for col in df.columns}
    if "amount" not in cols_map or "time" not in cols_map:
        raise HTTPException(status_code=400, detail="CSV must contain 'Time' and 'Amount' columns along with V1..V28")

    results = []
    fraud_count = 0
    high_count = 0
    med_count = 0
    low_count = 0

    for _, row in df.iterrows():
        tx_dict = row.to_dict()
        tx_dict_clean = {str(k).lower(): float(v) for k, v in tx_dict.items() if pd.notnull(v) and str(k).lower() != "class"}

        db_tx = Transaction(
            transaction_time=tx_dict_clean.get("time", 0.0),
            amount=tx_dict_clean.get("amount", 0.0),
            features_json=json.dumps(tx_dict_clean)
        )
        db.add(db_tx)
        db.commit()
        db.refresh(db_tx)

        prob, is_fraud, risk_band, latency_ms = ml_service.predict(tx_dict_clean)

        if is_fraud:
            fraud_count += 1
        if risk_band == "High":
            high_count += 1
        elif risk_band == "Medium":
            med_count += 1
        else:
            low_count += 1

        db_pred = Prediction(
            transaction_id=db_tx.id,
            raw_probability=prob,
            is_fraud_predicted=is_fraud,
            risk_band=risk_band,
            threshold_used=ml_service.threshold,
            model_version=ml_service.model_version,
            inference_time_ms=latency_ms
        )
        db.add(db_pred)
        db.commit()
        db.refresh(db_pred)

        results.append({
            "prediction_id": db_pred.id,
            "transaction_id": db_tx.id,
            "raw_probability": prob,
            "is_fraud": is_fraud,
            "risk_band": risk_band,
            "decision_threshold": ml_service.threshold,
            "model_version": ml_service.model_version,
            "inference_time_ms": latency_ms,
            "top_shap_features": None,
            "created_at": db_pred.created_at
        })

    return {
        "total_processed": len(results),
        "fraud_detected_count": fraud_count,
        "high_risk_count": high_count,
        "medium_risk_count": med_count,
        "low_risk_count": low_count,
        "predictions": results[:100]  # Limit payload size for UI table preview
    }
