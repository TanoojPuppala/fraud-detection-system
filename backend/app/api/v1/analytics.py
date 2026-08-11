"""
Analytics & History Endpoints (/api/v1/history, /api/v1/statistics).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.database import get_db
from backend.app.db.models import Transaction, Prediction
from backend.app.services.ml_service import ml_service
from backend.app.schemas.analytics import SystemStatistics

router = APIRouter(tags=["Analytics & History"])


@router.get("/statistics", response_model=SystemStatistics)
def get_system_statistics(db: Session = Depends(get_db)):
    total_tx = db.query(func.count(Transaction.id)).scalar() or 0
    total_fraud = db.query(func.count(Prediction.id)).filter(Prediction.is_fraud_predicted == True).scalar() or 0

    low_risk = db.query(func.count(Prediction.id)).filter(Prediction.risk_band == "Low").scalar() or 0
    med_risk = db.query(func.count(Prediction.id)).filter(Prediction.risk_band == "Medium").scalar() or 0
    high_risk = db.query(func.count(Prediction.id)).filter(Prediction.risk_band == "High").scalar() or 0

    fraud_pct = (total_fraud / total_tx * 100.0) if total_tx > 0 else 0.0
    cost_saved = float(total_fraud * 500.0)  # Estimated savings per caught fraud

    return {
        "total_transactions": total_tx,
        "total_fraud_detected": total_fraud,
        "fraud_percentage": round(fraud_pct, 2),
        "total_estimated_cost_saved_usd": cost_saved,
        "risk_distribution": {
            "Low": low_risk,
            "Medium": med_risk,
            "High": high_risk
        },
        "model_performance": ml_service.metadata
    }


@router.get("/history")
def get_transaction_history(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    risk_band: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Prediction).join(Transaction)

    if risk_band:
        query = query.filter(Prediction.risk_band == risk_band)

    total_count = query.count()
    predictions = query.order_by(Prediction.created_at.desc()).offset(offset).limit(limit).all()

    items = []
    for p in predictions:
        items.append({
            "prediction_id": p.id,
            "transaction_id": p.transaction_id,
            "amount": p.transaction.amount if p.transaction else 0.0,
            "raw_probability": p.raw_probability,
            "is_fraud": p.is_fraud_predicted,
            "risk_band": p.risk_band,
            "inference_time_ms": p.inference_time_ms,
            "created_at": p.created_at
        })

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "items": items
    }
