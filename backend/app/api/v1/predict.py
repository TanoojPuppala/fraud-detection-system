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

    # High-speed Vectorized Batch Inference across whole dataset
    probs, is_frauds, risk_bands, total_latency_ms = ml_service.predict_batch(df)

    time_col = cols_map.get("time")
    amount_col = cols_map.get("amount")

    time_series = pd.to_numeric(df[time_col], errors="coerce").fillna(0.0).values if time_col else np.zeros(len(df))
    amount_series = pd.to_numeric(df[amount_col], errors="coerce").fillna(0.0).values

    total_amt = float(np.sum(amount_series))
    fraud_mask = np.array(is_frauds, dtype=bool)
    fraud_amt = float(np.sum(amount_series[fraud_mask]))

    fraud_count = int(np.sum(is_frauds))
    risk_bands_arr = np.array(risk_bands)
    high_count = int(np.sum(risk_bands_arr == "High"))
    med_count = int(np.sum(risk_bands_arr == "Medium"))
    low_count = int(np.sum(risk_bands_arr == "Low"))

    # Vectorized extraction of prioritized records for UI results table (fraud cases + high risk + legitimate records up to 1000 items)
    fraud_indices = np.where(fraud_mask)[0]
    high_risk_indices = np.where(risk_bands_arr == "High")[0]
    other_indices = np.where((~fraud_mask) & (risk_bands_arr != "High"))[0]

    max_preview = min(1000, len(df))
    combined_indices = []
    seen = set()
    for idx in np.concatenate([fraud_indices, high_risk_indices, other_indices]):
        idx_int = int(idx)
        if idx_int not in seen:
            seen.add(idx_int)
            combined_indices.append(idx_int)
            if len(combined_indices) >= max_preview:
                break

    selected_indices = np.array(combined_indices, dtype=int)
    now = datetime.utcnow()
    per_txn_latency = round(total_latency_ms / max(1, len(df)), 3)

    results = []
    # Fast database persistence for prioritized records
    for idx in selected_indices:
        t_val = float(time_series[idx])
        a_val = float(amount_series[idx])
        prob_val = float(probs[idx])
        is_f_val = bool(is_frauds[idx])
        rb_val = str(risk_bands[idx])

        db_tx = Transaction(
            transaction_time=t_val,
            amount=a_val,
            features_json=f'{{"row_index": {idx}, "amount": {a_val}, "time": {t_val}}}'
        )
        db.add(db_tx)
        db.flush()

        db_pred = Prediction(
            transaction_id=db_tx.id,
            raw_probability=prob_val,
            is_fraud_predicted=is_f_val,
            risk_band=rb_val,
            threshold_used=ml_service.threshold,
            model_version=ml_service.model_version,
            inference_time_ms=per_txn_latency
        )
        db.add(db_pred)
        db.flush()

        if is_f_val or rb_val == "High":
            db_alert = FraudAlert(
                prediction_id=db_pred.id,
                risk_score=prob_val,
                status="New"
            )
            db.add(db_alert)

        results.append({
            "prediction_id": db_pred.id,
            "transaction_id": db_tx.id,
            "amount": a_val,
            "time": t_val,
            "raw_probability": prob_val,
            "is_fraud": is_f_val,
            "risk_band": rb_val,
            "decision_threshold": ml_service.threshold,
            "model_version": ml_service.model_version,
            "inference_time_ms": per_txn_latency,
            "top_shap_features": None,
            "created_at": now
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
