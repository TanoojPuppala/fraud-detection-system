"""
Integration Tests for FastAPI Backend Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data


def test_model_info_endpoint():
    response = client.get("/api/v1/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "decision_threshold" in data


def test_statistics_endpoint():
    response = client.get("/api/v1/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "total_transactions" in data
    assert "risk_distribution" in data


def test_predict_endpoint():
    sample_tx = {"time": 406.0, "amount": 125.50}
    for i in range(1, 29):
        sample_tx[f"v{i}"] = -0.5 if i in [14, 10] else 0.05

    response = client.post("/api/v1/predict", json=sample_tx)
    assert response.status_code == 201
    data = response.json()
    assert "prediction_id" in data
    assert "raw_probability" in data
    assert "risk_band" in data
    assert data["risk_band"] in ["Low", "Medium", "High"]
