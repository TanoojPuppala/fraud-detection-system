"""
Prediction Endpoints (/api/v1/predict, /api/v1/batch_predict).
"""

import json
import io
from datetime import datetime
import numpy as np
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
        "amount": db_tx.amount,
        "time": db_tx.transaction_time,
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
    cols_map = {str(col).lower(): col for col in df.columns}
    if "amount" not in cols_map:
        raise HTTPException(status_code=400, detail="CSV must contain 'Amount' (and optionally 'Time', V1..V28) columns")

    # High-speed Vectorized Batch Inference
    probs, is_frauds, risk_bands, total_latency_ms = ml_service.predict_batch(df)

    time_col = cols_map.get("time")
    amount_col = cols_map.get("amount")

    total_amt = float(pd.to_numeric(df[amount_col], errors="coerce").fillna(0.0).sum()) if amount_col else 0.0
    fraud_mask = np.array(is_frauds, dtype=bool)
    fraud_amt = float(pd.to_numeric(df[amount_col], errors="coerce").fillna(0.0)[fraud_mask].sum()) if amount_col else 0.0

    results = []
    fraud_count = int(np.sum(is_frauds))
    high_count = sum(1 for rb in risk_bands if rb == "High")
    med_count = sum(1 for rb in risk_bands if rb == "Medium")
    low_count = sum(1 for rb in risk_bands if rb == "Low")

    # Persist batch records to Database (in single atomic transaction)
    for i in range(len(df)):
        row_dict = df.iloc[i].to_dict()
        row_time = float(df.iloc[i][time_col]) if time_col and pd.notnull(df.iloc[i][time_col]) else 0.0
        row_amt = float(df.iloc[i][amount_col]) if amount_col and pd.notnull(df.iloc[i][amount_col]) else 0.0

        db_tx = Transaction(
            transaction_time=row_time,
            amount=row_amt,
            features_json=json.dumps({str(k).lower(): float(v) for k, v in row_dict.items() if pd.notnull(v) and str(k).lower() != "class"})
        )
        db.add(db_tx)
        db.flush()

        prob = float(probs[i])
        is_f = bool(is_frauds[i])
        rb = risk_bands[i]

        db_pred = Prediction(
            transaction_id=db_tx.id,
            raw_probability=prob,
            is_fraud_predicted=is_f,
            risk_band=rb,
            threshold_used=ml_service.threshold,
            model_version=ml_service.model_version,
            inference_time_ms=round(total_latency_ms / len(df), 3)
        )
        db.add(db_pred)
        db.flush()

        if is_f or rb == "High":
            db_alert = FraudAlert(
                prediction_id=db_pred.id,
                risk_score=prob,
                status="New"
            )
            db.add(db_alert)

        results.append({
            "prediction_id": db_pred.id,
            "transaction_id": db_tx.id,
            "amount": row_amt,
            "time": row_time,
            "raw_probability": prob,
            "is_fraud": is_f,
            "risk_band": rb,
            "decision_threshold": ml_service.threshold,
            "model_version": ml_service.model_version,
            "inference_time_ms": round(total_latency_ms / len(df), 3),
            "top_shap_features": None,
            "created_at": db_pred.created_at
        })

    db.commit()

    return {
        "total_processed": len(df),
        "fraud_detected_count": fraud_count,
        "high_risk_count": high_count,
        "medium_risk_count": med_count,
        "low_risk_count": low_count,
        "total_amount_processed_usd": round(total_amt, 2),
        "total_fraud_amount_usd": round(fraud_amt, 2),
        "batch_inference_time_ms": round(total_latency_ms, 2),
        "predictions": results
    }
