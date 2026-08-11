"""
Unit tests for ML Data Preprocessing & Vector Construction.
"""

import pytest
import numpy as np
from backend.app.services.ml_service import ml_service


def test_prepare_vector_shape():
    sample_tx = {"time": 100.0, "amount": 250.0}
    for i in range(1, 29):
        sample_tx[f"v{i}"] = 0.1

    vector = ml_service._prepare_vector(sample_tx)
    assert isinstance(vector, np.ndarray)
    assert vector.shape == (1, 30)


def test_predict_risk_bands():
    sample_tx = {"time": 100.0, "amount": 25.0}
    for i in range(1, 29):
        sample_tx[f"v{i}"] = 0.0

    prob, is_fraud, risk_band, latency_ms = ml_service.predict(sample_tx)
    assert 0.0 <= prob <= 1.0
    assert isinstance(is_fraud, bool)
    assert risk_band in ["Low", "Medium", "High"]
    assert latency_ms > 0.0
