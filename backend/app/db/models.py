"""
SQLAlchemy Database Models.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="analyst")  # 'admin' or 'analyst'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    feedback_entries = relationship("Feedback", back_populates="analyst")
    audit_logs = relationship("AuditLog", back_populates="user")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_time = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    features_json = Column(Text, nullable=False)  # JSON string of V1..V28
    true_label = Column(Integer, nullable=True)   # 1 for fraud, 0 for legit, null if unknown
    created_at = Column(DateTime, default=datetime.utcnow)

    prediction = relationship("Prediction", back_populates="transaction", uselist=False)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    raw_probability = Column(Float, nullable=False)
    is_fraud_predicted = Column(Boolean, nullable=False)
    risk_band = Column(String, nullable=False)  # 'Low', 'Medium', 'High'
    threshold_used = Column(Float, nullable=False)
    model_version = Column(String, nullable=False)
    inference_time_ms = Column(Float, nullable=False)
    shap_explanation_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="prediction")
    fraud_alert = relationship("FraudAlert", back_populates="prediction", uselist=False)
    feedback = relationship("Feedback", back_populates="prediction", uselist=False)


class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    status = Column(String, default="New")  # 'New', 'Under Investigation', 'Resolved', 'False Alarm'
    risk_score = Column(Float, nullable=False)
    assigned_analyst = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    prediction = relationship("Prediction", back_populates="fraud_alert")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    analyst_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    actual_label = Column(Integer, nullable=False)  # 1 for fraud, 0 for legit
    analyst_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    prediction = relationship("Prediction", back_populates="feedback")
    analyst = relationship("User", back_populates="feedback_entries")


class AuditLog(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
