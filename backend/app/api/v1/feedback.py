"""
Feedback & Fraud Alerts Endpoints (/api/v1/feedback, /api/v1/alerts).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Feedback, FraudAlert, Prediction
from backend.app.schemas.analytics import FeedbackCreate, FeedbackResponse

router = APIRouter(tags=["Analyst Feedback & Alerts"])


@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_analyst_feedback(feedback_in: FeedbackCreate, db: Session = Depends(get_db)):
    pred = db.query(Prediction).filter(Prediction.id == feedback_in.prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    new_fb = Feedback(
        prediction_id=feedback_in.prediction_id,
        actual_label=feedback_in.actual_label,
        analyst_notes=feedback_in.analyst_notes
    )
    db.add(new_fb)

    # Update FraudAlert status if exists
    if pred.fraud_alert:
        if feedback_in.actual_label == 1:
            pred.fraud_alert.status = "Resolved"
        else:
            pred.fraud_alert.status = "False Alarm"

    db.commit()
    db.refresh(new_fb)
    return new_fb


@router.get("/alerts")
def get_fraud_alerts(status_filter: str = "New", limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(FraudAlert)
    if status_filter != "All":
        query = query.filter(FraudAlert.status == status_filter)

    alerts = query.order_by(FraudAlert.created_at.desc()).limit(limit).all()

    items = []
    for a in alerts:
        items.append({
            "alert_id": a.id,
            "prediction_id": a.prediction_id,
            "risk_score": a.risk_score,
            "status": a.status,
            "assigned_analyst": a.assigned_analyst,
            "created_at": a.created_at
        })
    return items
