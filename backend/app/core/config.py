"""
Backend Application Configuration & Settings.
"""

import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseModel):
    PROJECT_NAME: str = "Credit Card Fraud Detection & Risk Analysis System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT Auth Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_fraud_detection_jwt_key_change_in_production_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database Configuration (SQLite default with PostgreSQL support)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'database' / 'fraud_detection.db'}")

    # ML Artifact Paths
    PROD_MODEL_DIR: Path = BASE_DIR / "ml" / "models" / "production"
    SCALER_PATH: Path = BASE_DIR / "ml" / "models" / "scaler.pkl"
    PROCESSED_DATA_DIR: Path = BASE_DIR / "ml" / "data" / "processed"


settings = Settings()
