"""
Pydantic Schemas for Analytics, Statistics, and Feedback.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class SystemStatistics(BaseModel):
    model_config = {"protected_namespaces": ()}

    total_transactions: int
    total_fraud_detected: int
    fraud_percentage: float
    total_estimated_cost_saved_usd: float
    risk_distribution: dict  # {'Low': count, 'Medium': count, 'High': count}
    model_performance: dict  # Model metrics from production_model_info.json


class FeedbackCreate(BaseModel):
    prediction_id: int
    actual_label: int  # 1 for fraud, 0 for legitimate
    analyst_notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    prediction_id: int
    actual_label: int
    analyst_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SimulatorControl(BaseModel):
    action: str  # 'start', 'stop', 'speed'
    interval_seconds: Optional[float] = 2.0


class SimulatorStatus(BaseModel):
    is_running: bool
    interval_seconds: float
    total_simulated_transactions: int
    fraud_alerts_generated: int
