"""
Pydantic Schemas for Single & Batch Predictions.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TransactionInput(BaseModel):
    time: float = Field(..., description="Seconds elapsed since first transaction")
    v1: float
    v2: float
    v3: float
    v4: float
    v5: float
    v6: float
    v7: float
    v8: float
    v9: float
    v10: float
    v11: float
    v12: float
    v13: float
    v14: float
    v15: float
    v16: float
    v17: float
    v18: float
    v19: float
    v20: float
    v21: float
    v22: float
    v23: float
    v24: float
    v25: float
    v26: float
    v27: float
    v28: float
    amount: float = Field(..., ge=0.0, description="Transaction monetary amount")


class FeatureContribution(BaseModel):
    feature: str
    value: float
    shap_value: float
    impact: str


class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    prediction_id: int
    transaction_id: int
    amount: float = 0.0
    time: float = 0.0
    raw_probability: float
    is_fraud: bool
    risk_band: str  # 'Low', 'Medium', 'High'
    decision_threshold: float
    model_version: str
    inference_time_ms: float
    top_shap_features: Optional[List[FeatureContribution]] = None
    created_at: datetime


class BatchPredictionSummary(BaseModel):
    total_processed: int
    fraud_detected_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    total_amount_processed_usd: float = 0.0
    total_fraud_amount_usd: float = 0.0
    batch_inference_time_ms: float = 0.0
    predictions: List[PredictionResponse]
